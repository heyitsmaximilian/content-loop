"""
QA Agent — Evaluates content quality before publishing.
Scores multiple dimensions and makes publish/review/regenerate/discard decisions.
"""

from models.schemas import AssetManifest, Script, QAReport, ComplianceTier


class QAAgent:
    def __init__(self, product_config: dict):
        self.product = product_config
        self.compliance_tier = ComplianceTier(
            product_config.get("compliance", {}).get("tier", "low")
        )

    def evaluate(self, manifest: AssetManifest, script: Script) -> QAReport:
        """Run all QA checks and produce a publish decision.

        Scoring dimensions (0.0 - 1.0):
        - hook_strength: Does the first 3s create curiosity?
        - character_consistency: Does the character look the same across scenes?
        - visual_quality: Are images/videos clean, well-lit, on-brand?
        - pacing: Does the video match the format's beat structure?
        - brand_fit: Does tone/voice match product config?
        - caption_quality: Are captions clear, well-timed, typo-free?

        TODO: Wire scoring to Claude API for automated evaluation.
        Currently returns placeholder scores for pipeline testing.
        """
        report = QAReport(
            asset_manifest_id=manifest.id,
            product=manifest.product,
        )

        # ── Auto-fail checks (hard gates) ─────────────────────
        auto_fails = []

        # Check script has a hook
        if not script.hook or len(script.hook) < 5:
            auto_fails.append("Missing or empty hook")

        # Check minimum scene count
        if len(script.scenes) < 2:
            auto_fails.append("Script has fewer than 2 scenes")

        # Check duration bounds
        if script.total_duration_s < 10:
            auto_fails.append(f"Video too short: {script.total_duration_s}s (min 10s)")
        if script.total_duration_s > 90:
            auto_fails.append(f"Video too long: {script.total_duration_s}s (max 90s)")

        # Check compliance flags on regulated content
        if script.compliance_flags and self.compliance_tier in (
            ComplianceTier.HIGH, ComplianceTier.REGULATED
        ):
            auto_fails.append(f"Compliance flags on regulated content: {script.compliance_flags}")

        report.auto_fail_reasons = auto_fails

        # ── Scoring (placeholder — wire to Claude for real eval) ──
        # TODO: Send script + image descriptions to Claude and ask it to score
        # each dimension on 0-1 scale with reasoning.
        report.hook_strength = 0.5
        report.character_consistency = 0.5
        report.visual_quality = 0.5
        report.pacing = 0.5
        report.brand_fit = 0.5
        report.caption_quality = 0.5

        # Weighted overall score
        report.overall_score = (
            report.hook_strength * 0.25 +
            report.character_consistency * 0.20 +
            report.visual_quality * 0.15 +
            report.pacing * 0.15 +
            report.brand_fit * 0.15 +
            report.caption_quality * 0.10
        )

        # ── Decision logic ────────────────────────────────────
        if auto_fails:
            report.decision = "discard"
        elif report.overall_score >= 0.7 and self.compliance_tier == ComplianceTier.LOW:
            report.decision = "publish"
        elif report.overall_score >= 0.7:
            report.decision = "review"  # Good quality but needs human sign-off
        elif report.overall_score >= 0.4:
            report.decision = "regenerate"  # Worth retrying
        else:
            report.decision = "discard"

        # ── Human review triggers ─────────────────────────────
        if self.product.get("compliance", {}).get("requires_human_review", False):
            report.decision = "review"
            report.flags.append("Product requires human review for all content")

        if script.compliance_flags:
            report.flags.append(f"Script flagged: {', '.join(script.compliance_flags)}")
            if report.decision == "publish":
                report.decision = "review"

        return report
