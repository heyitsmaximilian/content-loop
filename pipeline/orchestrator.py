#!/usr/bin/env python3
"""
Content Loop Pipeline — Orchestrator
Runs the full content generation pipeline for one piece of content.

Usage:
    python pipeline/orchestrator.py --product cadence --topic "GLP-1 and muscle loss"
    python pipeline/orchestrator.py --product cadence --topic-file data/backlog.jsonl --next
    python pipeline/orchestrator.py --product mogged --format myth_bust --topic "mewing doesn't work"
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from models.schemas import (
    TopicBrief, Script, AssetManifest, QAReport, PublishRecord,
    ComplianceTier, PipelineStatus
)
from agents.script_agent import ScriptAgent
from agents.image_agent import ImageAgent
from agents.video_agent import VideoAgent
from agents.audio_agent import AudioAgent
from agents.assembly import AssemblyAgent
from agents.qa_agent import QAAgent
from compliance.checker import ComplianceChecker


class Pipeline:
    """Orchestrates the full content generation pipeline."""

    def __init__(self, product_slug: str):
        self.product_slug = product_slug
        self.root = Path(__file__).parent.parent
        self.product_dir = self.root / "products" / product_slug
        self.output_dir = self.root / "data" / "runs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not self.product_dir.exists():
            raise FileNotFoundError(
                f"Product '{product_slug}' not found. "
                f"Create it at products/{product_slug}/ using the template."
            )

        self.product_config = self._load_product_config()
        self.character_config = self._load_character_config()

        # Initialize agents
        self.script_agent = ScriptAgent(self.product_config, self.character_config)
        self.image_agent = ImageAgent(self.product_config, self.character_config)
        self.video_agent = VideoAgent(self.product_config, self.character_config)
        self.audio_agent = AudioAgent(self.product_config, self.character_config)
        self.assembly = AssemblyAgent(self.product_config)
        self.qa_agent = QAAgent(self.product_config)
        self.compliance = ComplianceChecker(self.product_config)

    def _load_product_config(self) -> dict:
        """Load product.yaml for the active product."""
        config_path = self.product_dir / "product.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Missing {config_path}")
        try:
            import yaml
            with open(config_path) as f:
                return yaml.safe_load(f)
        except ImportError:
            raise ImportError("PyYAML required: pip install pyyaml")

    def _load_character_config(self) -> dict:
        """Load the default character config for the product."""
        default_char = self.product_config.get("default_character", "")
        if not default_char:
            return {}
        char_path = self.product_dir / "characters" / f"{default_char}.yaml"
        if not char_path.exists():
            print(f"Warning: Default character '{default_char}' not found at {char_path}")
            return {}
        import yaml
        with open(char_path) as f:
            return yaml.safe_load(f)

    def run(self, topic_brief: TopicBrief, dry_run: bool = False) -> dict:
        """Execute the full pipeline for one content piece.

        Returns a dict with the pipeline result and all intermediate artifacts.
        """
        run_id = f"{self.product_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{topic_brief.id}"
        run_dir = self.output_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        result = {
            "run_id": run_id,
            "product": self.product_slug,
            "topic": topic_brief.topic,
            "format": topic_brief.format,
            "status": PipelineStatus.IN_PROGRESS.value,
            "started_at": datetime.now().isoformat(),
            "stages": {},
        }

        try:
            # ── Stage 1: Compliance pre-check ─────────────────────
            print(f"[1/7] Compliance pre-check...")
            pre_check = self.compliance.pre_check(topic_brief)
            result["stages"]["compliance_precheck"] = pre_check

            if pre_check.get("blocked"):
                result["status"] = PipelineStatus.FAILED.value
                result["failure_reason"] = f"Blocked by compliance: {pre_check['reason']}"
                self._save_result(run_dir, result)
                return result

            # ── Stage 2: Script generation ────────────────────────
            print(f"[2/7] Generating script...")
            script = self.script_agent.generate(topic_brief)
            result["stages"]["script"] = {
                "hook": script.hook,
                "scene_count": len(script.scenes),
                "total_duration_s": script.total_duration_s,
                "compliance_flags": script.compliance_flags,
            }
            self._save_artifact(run_dir, "script.json", script)

            if script.compliance_flags and topic_brief.compliance_tier != ComplianceTier.LOW:
                result["status"] = PipelineStatus.NEEDS_REVIEW.value
                result["review_reason"] = f"Script has compliance flags: {script.compliance_flags}"
                self._save_result(run_dir, result)
                print(f"  ⚠ Compliance flags detected. Needs human review.")
                if not dry_run:
                    return result

            if dry_run:
                result["status"] = "dry_run_complete"
                result["stages"]["note"] = "Dry run — stopped after script generation."
                self._save_result(run_dir, result)
                return result

            # ── Stage 3: Image generation ─────────────────────────
            print(f"[3/7] Generating images ({len(script.scenes)} scenes)...")
            images = self.image_agent.generate_scenes(script, run_dir)
            result["stages"]["images"] = {
                "count": len(images),
                "paths": [img.file_path for img in images],
            }

            # ── Stage 4: Video generation ─────────────────────────
            print(f"[4/7] Generating video clips...")
            videos = self.video_agent.animate_scenes(script, images, run_dir)
            result["stages"]["videos"] = {
                "count": len(videos),
                "total_duration_s": sum(v.duration_s or 0 for v in videos),
            }

            # ── Stage 5: Audio generation ─────────────────────────
            print(f"[5/7] Generating voiceover...")
            voiceover = self.audio_agent.generate_voiceover(script, run_dir)
            result["stages"]["audio"] = {
                "voiceover_path": voiceover.file_path if voiceover else None,
            }

            # ── Stage 6: Assembly ─────────────────────────────────
            print(f"[6/7] Assembling final video...")
            manifest = AssetManifest(
                script_id=script.id,
                product=self.product_slug,
                images=images,
                videos=videos,
                voiceover=voiceover,
            )
            final_path = self.assembly.assemble(manifest, script, run_dir)
            manifest.final_video_path = str(final_path)
            result["stages"]["assembly"] = {"final_video": str(final_path)}

            # ── Stage 7: QA ───────────────────────────────────────
            print(f"[7/7] Running QA checks...")
            qa_report = self.qa_agent.evaluate(manifest, script)
            result["stages"]["qa"] = {
                "overall_score": qa_report.overall_score,
                "decision": qa_report.decision,
                "flags": qa_report.flags,
                "auto_fail_reasons": qa_report.auto_fail_reasons,
            }

            # ── Decision ──────────────────────────────────────────
            if qa_report.auto_fail_reasons:
                result["status"] = PipelineStatus.FAILED.value
                result["failure_reason"] = f"QA auto-fail: {qa_report.auto_fail_reasons}"
            elif qa_report.decision == "publish":
                result["status"] = PipelineStatus.APPROVED.value
            elif qa_report.decision == "review":
                result["status"] = PipelineStatus.NEEDS_REVIEW.value
            elif qa_report.decision == "regenerate":
                result["status"] = PipelineStatus.FAILED.value
                result["failure_reason"] = "QA recommends regeneration"
            else:
                result["status"] = PipelineStatus.NEEDS_REVIEW.value

            result["completed_at"] = datetime.now().isoformat()
            self._save_result(run_dir, result)
            self._log_run(result)

            print(f"\nPipeline complete: {result['status']}")
            print(f"  Output: {run_dir}")
            if manifest.final_video_path:
                print(f"  Video: {manifest.final_video_path}")

            return result

        except Exception as e:
            result["status"] = PipelineStatus.FAILED.value
            result["failure_reason"] = str(e)
            result["completed_at"] = datetime.now().isoformat()
            self._save_result(run_dir, result)
            raise

    def _save_artifact(self, run_dir: Path, filename: str, obj) -> None:
        """Save a pipeline artifact as JSON."""
        import dataclasses
        path = run_dir / filename
        with open(path, "w") as f:
            json.dump(dataclasses.asdict(obj), f, indent=2, default=str)

    def _save_result(self, run_dir: Path, result: dict) -> None:
        """Save the pipeline result summary."""
        with open(run_dir / "result.json", "w") as f:
            json.dump(result, f, indent=2, default=str)

    def _log_run(self, result: dict) -> None:
        """Append run to the central log."""
        log_path = self.root / "data" / "pipeline-runs.jsonl"
        with open(log_path, "a") as f:
            f.write(json.dumps(result, default=str) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Content Loop Pipeline")
    parser.add_argument("--product", required=True, help="Product slug (e.g. cadence, mogged)")
    parser.add_argument("--topic", help="Topic to generate content about")
    parser.add_argument("--format", default="explainer", help="Content format (from formats/library.yaml)")
    parser.add_argument("--compliance", default="low", choices=["low", "medium", "high", "regulated"])
    parser.add_argument("--character", help="Character slug (overrides product default)")
    parser.add_argument("--dry-run", action="store_true", help="Generate script only, skip image/video/audio")
    args = parser.parse_args()

    if not args.topic:
        print("Error: --topic is required")
        sys.exit(1)

    topic = TopicBrief(
        product=args.product,
        topic=args.topic,
        format=args.format,
        compliance_tier=ComplianceTier(args.compliance),
    )

    pipeline = Pipeline(args.product)
    result = pipeline.run(topic, dry_run=args.dry_run)

    if result["status"] == PipelineStatus.APPROVED.value:
        print("\nReady to publish. Run with --publish to post.")
    elif result["status"] == PipelineStatus.NEEDS_REVIEW.value:
        print(f"\nNeeds human review: {result.get('review_reason', 'QA flagged for review')}")
    elif result["status"] == PipelineStatus.FAILED.value:
        print(f"\nFailed: {result.get('failure_reason', 'Unknown error')}")


if __name__ == "__main__":
    main()
