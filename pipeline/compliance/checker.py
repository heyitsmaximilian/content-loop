"""
Compliance Checker — Pre-screens topics and scripts for policy violations.
Supports tiered compliance from entertainment to regulated content.
"""

from models.schemas import TopicBrief, ComplianceTier


class ComplianceChecker:
    def __init__(self, product_config: dict):
        self.product = product_config
        self.compliance = product_config.get("compliance", {})
        self.tier = ComplianceTier(self.compliance.get("tier", "low"))
        self.forbidden_topics = [t.lower() for t in self.compliance.get("forbidden_topics", [])]
        self.claim_rules = self.compliance.get("claim_rules", [])

    def pre_check(self, topic: TopicBrief) -> dict:
        """Pre-screen a topic before script generation.

        Returns:
            {"blocked": bool, "reason": str, "warnings": list[str]}
        """
        warnings = []
        topic_lower = topic.topic.lower()

        # Check forbidden topics
        for forbidden in self.forbidden_topics:
            if forbidden in topic_lower:
                return {
                    "blocked": True,
                    "reason": f"Topic matches forbidden pattern: '{forbidden}'",
                    "warnings": [],
                }

        # Check if claims need review at this tier
        if topic.target_claim and self.tier in (ComplianceTier.HIGH, ComplianceTier.REGULATED):
            warnings.append(
                f"Claim '{topic.target_claim}' requires evidence review "
                f"(compliance tier: {self.tier.value})"
            )

        # Tier-specific checks
        if self.tier == ComplianceTier.REGULATED:
            warnings.append("Regulated content — all output requires legal/compliance review")

        return {
            "blocked": False,
            "reason": "",
            "warnings": warnings,
        }

    def check_script_claims(self, dialogue: str) -> list[str]:
        """Scan script dialogue for potential claim violations.

        Returns list of flagged phrases.

        TODO: Wire to Claude API for nuanced claim detection.
        Current implementation uses keyword matching.
        """
        flags = []

        # Health claim patterns
        health_triggers = [
            "cures", "treats", "prevents", "heals", "eliminates",
            "guaranteed", "proven to", "clinically proven",
            "will make you", "you will see results",
        ]

        # Financial claim patterns
        finance_triggers = [
            "guaranteed returns", "risk-free", "get rich",
            "financial advice", "you should invest",
        ]

        dialogue_lower = dialogue.lower()
        for trigger in health_triggers + finance_triggers:
            if trigger in dialogue_lower:
                flags.append(f"Potential claim: '{trigger}' found in dialogue")

        return flags
