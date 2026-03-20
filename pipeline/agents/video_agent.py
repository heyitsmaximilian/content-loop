"""
Video Agent — Animates still images into short video clips.
Uses Kling 2.6 (volume) or Runway Gen-4.5 (hero content).
"""

from pathlib import Path
from typing import List

from models.schemas import Script, GeneratedAsset


class VideoAgent:
    def __init__(self, product_config: dict, character_config: dict):
        self.product = product_config
        self.character = character_config

    def animate_scenes(
        self, script: Script, images: List[GeneratedAsset], run_dir: Path
    ) -> List[GeneratedAsset]:
        """Animate each scene image into a short video clip.

        Strategy: short shots (4-8s each), stitched later.
        This matches how video models actually work — they perform
        better on short clips with strong reference images.

        TODO: Wire to Kling 2.6 API or Runway Gen-4.5 API.
        """
        videos = []
        for scene, image in zip(script.scenes, images):
            motion_prompt = self._compile_motion_prompt(scene)

            # TODO: Replace with actual API call
            #
            # Kling 2.6 (volume — $10/mo, good for daily content):
            #   response = kling.create_video(
            #       image_url=image.file_path,
            #       prompt=motion_prompt,
            #       duration=min(scene.duration_s, 8),
            #       aspect_ratio="9:16",
            #   )
            #
            # Runway Gen-4.5 (hero content — better character consistency):
            #   response = runway.image_to_video(
            #       image=image.file_path,
            #       prompt=motion_prompt,
            #       duration=min(scene.duration_s, 10),
            #       ratio="9:16",
            #       character_ref=self.character.get("visual", {}).get("reference_sheet"),
            #   )
            #
            # Sora 2 (cinematic quality, longer clips up to 25s):
            #   response = openai.video.create(
            #       model="sora-2",
            #       input=[{"type": "image", "image": image.file_path}],
            #       prompt=motion_prompt,
            #       duration=min(scene.duration_s, 12),
            #       resolution="720p",
            #       aspect_ratio="9:16",
            #   )

            asset = GeneratedAsset(
                scene_index=scene.index,
                asset_type="video",
                file_path=str(run_dir / f"scene_{scene.index:02d}.mp4"),
                prompt_used=motion_prompt,
                model_used="placeholder",
                duration_s=scene.duration_s,
            )
            videos.append(asset)

        return videos

    def _compile_motion_prompt(self, scene) -> str:
        """Build motion prompt for video generation.

        Key principles from Sora prompting guide:
        - Use temporal anchoring ("remains still, then gradually...")
        - Describe motion intensity explicitly
        - Use cinematic terms for camera movement
        - Keep motion minimal for character consistency
        """
        motion = getattr(scene, "motion_direction", "")
        parts = [
            f"Animated character scene: {scene.description}",
            f"The character {motion}" if motion else "Subtle idle animation, gentle breathing motion",
            "Smooth, deliberate movement. Soft lighting.",
            "9:16 vertical format, social media style.",
        ]
        return " ".join(parts)
