"""
Content Loop Pipeline — Core Data Models
All pipeline data flows through these objects.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ComplianceTier(Enum):
    LOW = "low"                     # Entertainment, general tips
    MEDIUM = "medium"               # Consumer product, soft claims
    HIGH = "high"                   # Health/wellness, financial
    REGULATED = "regulated"         # Requires legal review


class PipelineStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    FAILED = "failed"
    DISCARDED = "discarded"


# ── Stage 1: Topic ────────────────────────────────────────────

@dataclass
class TopicBrief:
    """What to make content about."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    product: str = ""               # Product slug from config
    topic: str = ""                 # The subject
    format: str = "explainer"       # Format slug from formats/library.yaml
    hook_angle: str = ""            # Specific angle for the hook
    target_claim: Optional[str] = None  # Claim to make (triggers compliance check)
    compliance_tier: ComplianceTier = ComplianceTier.LOW
    source: str = "manual"          # manual | trending | backlog | research
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ── Stage 2: Script ───────────────────────────────────────────

@dataclass
class SceneScript:
    """One scene/shot in the video."""
    index: int = 0
    description: str = ""           # What happens visually
    dialogue: str = ""              # What the character says
    duration_s: int = 5
    expression: str = "neutral"     # Character expression to use
    pose: str = "standing"          # Character pose to use
    motion_direction: str = ""      # Camera/character motion hint for video gen
    environment: str = ""           # Background/setting for this scene


@dataclass
class Script:
    """Full script for one piece of content."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    topic_id: str = ""
    product: str = ""
    character: str = ""             # Character slug
    hook: str = ""                  # The opening line (0-3s)
    scenes: list[SceneScript] = field(default_factory=list)
    cta: str = ""                   # Call-to-action
    caption: str = ""               # Post caption text
    hashtags: list[str] = field(default_factory=list)
    total_duration_s: int = 0
    compliance_flags: list[str] = field(default_factory=list)
    version: int = 1


# ── Stage 3: Assets ───────────────────────────────────────────

@dataclass
class GeneratedAsset:
    """A single generated image or video file."""
    scene_index: int = 0
    asset_type: str = ""            # "image" | "video" | "audio"
    file_path: str = ""
    prompt_used: str = ""
    model_used: str = ""            # e.g. "leonardo-flux-jab-lora", "kling-2.6"
    duration_s: Optional[float] = None
    generation_id: str = ""         # Provider's job ID for debugging


@dataclass
class AssetManifest:
    """All generated assets for one content piece."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    script_id: str = ""
    product: str = ""
    images: list[GeneratedAsset] = field(default_factory=list)
    videos: list[GeneratedAsset] = field(default_factory=list)
    voiceover: Optional[GeneratedAsset] = None
    music: Optional[GeneratedAsset] = None
    final_video_path: str = ""


# ── Stage 4: QA ───────────────────────────────────────────────

@dataclass
class QAReport:
    """Quality assessment before publishing."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    asset_manifest_id: str = ""
    product: str = ""

    # Scores (0.0 - 1.0)
    hook_strength: float = 0.0
    character_consistency: float = 0.0
    visual_quality: float = 0.0
    pacing: float = 0.0
    brand_fit: float = 0.0
    caption_quality: float = 0.0
    overall_score: float = 0.0

    # Compliance
    compliance_pass: bool = False
    claim_risks: list[str] = field(default_factory=list)
    policy_flags: list[str] = field(default_factory=list)

    # Decision
    decision: str = ""              # "publish" | "review" | "regenerate" | "discard"
    flags: list[str] = field(default_factory=list)
    reviewer_notes: str = ""

    # Auto-fail criteria
    auto_fail_reasons: list[str] = field(default_factory=list)


# ── Stage 5: Publish ──────────────────────────────────────────

@dataclass
class PublishRecord:
    """Record of a published piece of content."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    asset_manifest_id: str = ""
    product: str = ""
    platform: str = ""              # tiktok | youtube_shorts | instagram_reels
    post_id: str = ""               # Platform's post ID
    post_url: str = ""
    published_at: str = ""
    format: str = ""
    hook_category: str = ""
    character: str = ""


# ── Stage 6: Performance ─────────────────────────────────────

@dataclass
class PerformanceRecord:
    """Post-publish metrics. Feeds back into content-loop analysis engine."""
    publish_id: str = ""
    product: str = ""
    platform: str = ""
    format: str = ""
    hook_category: str = ""
    character: str = ""

    # Metrics (updated 24h and 48h post-publish)
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    watch_time_avg_s: float = 0.0
    conversions: int = 0

    measured_at: str = ""
