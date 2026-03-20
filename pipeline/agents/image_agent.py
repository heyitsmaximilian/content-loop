"""
Image Agent — Generates character-consistent scene images.
Uses Leonardo AI (LoRA) as primary, GPT-image-1.5 as fallback.
"""

from pathlib import Path
from typing import List

from models.schemas import Script, GeneratedAsset


class ImageAgent:
    def __init__(self, product_config: dict, character_config: dict):
        self.product = product_config
        self.character = character_config
        self.prompt_fragments = character_config.get("prompt_fragments", {})

    def generate_scenes(self, script: Script, run_dir: Path) -> List[GeneratedAsset]:
        """Generate one image per scene using character LoRA.

        TODO: Wire to Leonardo AI API or GPT-image-1.5 API.
        """
        images = []
        for scene in script.scenes:
            prompt = self._compile_prompt(scene)
            # TODO: Replace with actual API call
            #
            # Leonardo AI (primary — uses trained LoRA):
            #   response = leonardo.post("/generations", json={
            #       "prompt": prompt,
            #       "modelId": self.character.get("visual", {}).get("lora_model"),
            #       "width": 576,   # 9:16 vertical
            #       "height": 1024,
            #       "num_images": 1,
            #       "transparency": "enabled",
            #   })
            #
            # GPT-image-1.5 (fallback):
            #   response = openai.images.generate(
            #       model="gpt-image-1.5",
            #       prompt=prompt,
            #       size="1024x1536",
            #       quality="high",
            #       background="transparent",
            #       output_format="png",
            #   )

            asset = GeneratedAsset(
                scene_index=scene.index,
                asset_type="image",
                file_path=str(run_dir / f"scene_{scene.index:02d}.png"),
                prompt_used=prompt,
                model_used="placeholder",
            )
            images.append(asset)

        return images

    def _compile_prompt(self, scene) -> str:
        """Compile a generation prompt from character config + scene description.

        Prompts are assembled from structured components, never written ad-hoc.
        This prevents drift and keeps character consistency.
        """
        char_base = self.prompt_fragments.get("character_base", "")
        style = self.prompt_fragments.get("style_anchor", "")
        lora_trigger = self.character.get("visual", {}).get("lora_trigger", "")

        # Find expression and pose descriptions from character config
        expression_desc = ""
        for expr in self.character.get("expressions", []):
            if expr["name"] == getattr(scene, "expression", "neutral"):
                expression_desc = expr["description"]
                break

        pose_desc = ""
        for pose in self.character.get("poses", []):
            if pose["name"] == getattr(scene, "pose", "standing"):
                pose_desc = pose["description"]
                break

        parts = [
            lora_trigger,
            char_base,
            f"Expression: {expression_desc}" if expression_desc else "",
            f"Pose: {pose_desc}" if pose_desc else "",
            f"Scene: {scene.description}",
            f"Environment: {getattr(scene, 'environment', '')}" if getattr(scene, "environment", "") else "",
            style,
        ]

        return ". ".join(p for p in parts if p).strip()
