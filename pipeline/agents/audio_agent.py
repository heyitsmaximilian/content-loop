"""
Audio Agent — Generates voiceover from script dialogue.
Uses ElevenLabs API with per-character voice profiles.
"""

from pathlib import Path
from typing import Optional

from models.schemas import Script, GeneratedAsset


class AudioAgent:
    def __init__(self, product_config: dict, character_config: dict):
        self.product = product_config
        self.character = character_config
        self.voice_config = character_config.get("voice", {})

    def generate_voiceover(self, script: Script, run_dir: Path) -> Optional[GeneratedAsset]:
        """Generate voiceover audio for the full script.

        Concatenates all scene dialogue into one VO track.
        Assembly agent handles syncing to video later.

        TODO: Wire to ElevenLabs API.
        """
        # Combine all dialogue
        full_dialogue = self._combine_dialogue(script)
        if not full_dialogue.strip():
            return None

        voice_id = self.voice_config.get("voice_id", "")
        speed = self.voice_config.get("speed", 1.0)

        # TODO: Replace with actual API call
        #
        # ElevenLabs:
        #   response = elevenlabs.text_to_speech.convert(
        #       voice_id=voice_id,
        #       text=full_dialogue,
        #       model_id="eleven_turbo_v2_5",
        #       voice_settings=VoiceSettings(
        #           stability=0.5,
        #           similarity_boost=0.8,
        #           speed=speed,
        #       ),
        #   )
        #   with open(run_dir / "voiceover.mp3", "wb") as f:
        #       for chunk in response:
        #           f.write(chunk)
        #
        # OpenAI TTS (alternative):
        #   response = openai.audio.speech.create(
        #       model="tts-1-hd",
        #       voice="nova",
        #       input=full_dialogue,
        #       speed=speed,
        #   )
        #   response.stream_to_file(run_dir / "voiceover.mp3")

        asset = GeneratedAsset(
            scene_index=-1,  # Covers all scenes
            asset_type="audio",
            file_path=str(run_dir / "voiceover.mp3"),
            prompt_used=full_dialogue[:200],
            model_used="placeholder",
            duration_s=script.total_duration_s,
        )
        return asset

    def _combine_dialogue(self, script: Script) -> str:
        """Combine scene dialogue into a single VO script.

        Adds natural pauses between scenes using SSML-style markers
        that ElevenLabs can interpret.
        """
        parts = []
        if script.hook:
            parts.append(script.hook)

        for scene in script.scenes:
            if scene.dialogue:
                parts.append(scene.dialogue)

        if script.cta:
            parts.append(script.cta)

        # Join with brief pause markers
        return " ... ".join(parts)
