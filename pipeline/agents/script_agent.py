"""
Script Agent — Generates structured scripts from topic briefs.
Uses Claude API with product voice rules and format templates.
"""

import json
import os
from pathlib import Path
from typing import Optional

from models.schemas import TopicBrief, Script, SceneScript


class ScriptAgent:
    def __init__(self, product_config: dict, character_config: dict):
        self.product = product_config
        self.character = character_config
        self.formats = self._load_formats()

    def _load_formats(self) -> dict:
        """Load content format library."""
        formats_path = Path(__file__).parent.parent.parent / "formats" / "library.yaml"
        if formats_path.exists():
            try:
                import yaml
                with open(formats_path) as f:
                    data = yaml.safe_load(f)
                return data.get("formats", {})
            except ImportError:
                return {}
        return {}

    def generate(self, topic: TopicBrief) -> Script:
        """Generate a script from a topic brief using Claude API.

        TODO: Wire to Claude API. Current implementation returns a placeholder.
        """
        format_spec = self.formats.get(topic.format, {})
        voice = self.product.get("voice", {})
        char_personality = self.character.get("personality", {})

        # Build the system prompt from product + character + format config
        system_prompt = self._build_system_prompt(format_spec, voice, char_personality)
        user_prompt = self._build_user_prompt(topic, format_spec)

        # TODO: Replace with actual Claude API call
        # response = anthropic.messages.create(
        #     model="claude-sonnet-4-6",
        #     max_tokens=2000,
        #     system=system_prompt,
        #     messages=[{"role": "user", "content": user_prompt}]
        # )
        # script_data = json.loads(response.content[0].text)

        # Placeholder — returns empty script structure
        script = Script(
            topic_id=topic.id,
            product=topic.product,
            character=self.character.get("slug", ""),
            hook=f"[PLACEHOLDER HOOK for: {topic.topic}]",
            scenes=[
                SceneScript(
                    index=0,
                    description="Opening scene",
                    dialogue="[Script generation not yet wired to Claude API]",
                    duration_s=5,
                )
            ],
            cta="Follow for more",
            total_duration_s=30,
        )
        return script

    def _build_system_prompt(self, format_spec: dict, voice: dict, personality: dict) -> str:
        """Assemble system prompt from structured config — not ad-hoc."""
        parts = [
            "You are a short-form social media scriptwriter.",
            "",
            "## Brand Voice",
            f"Tone: {', '.join(voice.get('tone', ['friendly']))}",
            f"Never use: {', '.join(voice.get('never', []))}",
            f"Preferred vocabulary: {', '.join(voice.get('vocabulary', {}).get('prefer', []))}",
            f"Avoid vocabulary: {', '.join(voice.get('vocabulary', {}).get('avoid', []))}",
        ]

        if personality:
            parts.extend([
                "",
                "## Character Personality",
                f"Name: {self.character.get('name', 'Character')}",
                f"Traits: {', '.join(personality.get('traits', []))}",
                f"Speaking style: {personality.get('speaking_style', '')}",
                f"Humor level: {personality.get('humor_level', 'moderate')}",
                f"Knowledge domain: {personality.get('knowledge_domain', '')}",
            ])

        compliance = self.product.get("compliance", {})
        if compliance.get("claim_rules"):
            parts.extend([
                "",
                "## Compliance Rules (MUST follow)",
                *[f"- {rule}" for rule in compliance["claim_rules"]],
            ])

        parts.extend([
            "",
            "## Output Format",
            "Return a JSON object with this exact structure:",
            '{"hook": "...", "scenes": [{"description": "...", "dialogue": "...", '
            '"duration_s": N, "expression": "...", "pose": "...", "motion_direction": "..."}], '
            '"cta": "...", "caption": "...", "hashtags": [...], "total_duration_s": N, '
            '"compliance_flags": [...]}',
            "",
            "Rules:",
            "- One idea per video. No tangents.",
            "- Hook must create curiosity in under 3 seconds.",
            "- Each scene should be 4-8 seconds.",
            "- Total duration should match the format guidelines.",
            "- If any dialogue could be interpreted as a medical/financial/legal claim, "
            "add it to compliance_flags.",
        ])

        return "\n".join(parts)

    def _build_user_prompt(self, topic: TopicBrief, format_spec: dict) -> str:
        """Build the generation prompt from topic + format."""
        structure = format_spec.get("structure", [])
        hooks = format_spec.get("hook_formulas", [])
        duration = format_spec.get("ideal_duration_s", [20, 45])

        parts = [
            f"Write a {format_spec.get('name', topic.format)} script about: {topic.topic}",
            "",
            f"Target duration: {duration[0]}-{duration[1]} seconds",
            f"Hook angle: {topic.hook_angle}" if topic.hook_angle else "",
            "",
            "Structure to follow:",
        ]

        for beat in structure:
            parts.append(f"- {beat.get('beat', '')}: {beat.get('notes', '')} ({beat.get('duration_s', 5)}s)")

        if hooks:
            parts.extend(["", "Example hook formulas (adapt, don't copy):", *[f"- {h}" for h in hooks]])

        if topic.target_claim:
            parts.extend([
                "",
                f"Target claim to include: {topic.target_claim}",
                "Flag this in compliance_flags if it could be interpreted as a health/financial claim.",
            ])

        return "\n".join(parts)
