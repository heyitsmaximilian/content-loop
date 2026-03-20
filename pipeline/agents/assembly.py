"""
Assembly Agent — Stitches video clips + audio + captions into final video.
Uses FFmpeg for rendering. No external API dependency.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional

from models.schemas import AssetManifest, Script


class AssemblyAgent:
    def __init__(self, product_config: dict):
        self.product = product_config
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """Verify FFmpeg is available."""
        if not shutil.which("ffmpeg"):
            print("Warning: FFmpeg not found. Install with: brew install ffmpeg")

    def assemble(self, manifest: AssetManifest, script: Script, run_dir: Path) -> Path:
        """Assemble final video from clips + voiceover + captions.

        Pipeline:
        1. Concatenate video clips in scene order
        2. Overlay voiceover audio track
        3. Burn in captions (SRT)
        4. Output 9:16 vertical MP4

        TODO: Implement actual FFmpeg assembly. Current implementation is a stub.
        """
        output_path = run_dir / "final.mp4"

        # TODO: Implement when video assets are real
        #
        # Step 1: Create concat file
        # concat_file = run_dir / "concat.txt"
        # with open(concat_file, "w") as f:
        #     for video in sorted(manifest.videos, key=lambda v: v.scene_index):
        #         f.write(f"file '{video.file_path}'\n")
        #
        # Step 2: Concatenate video clips
        # subprocess.run([
        #     "ffmpeg", "-f", "concat", "-safe", "0",
        #     "-i", str(concat_file),
        #     "-c", "copy",
        #     str(run_dir / "concat.mp4")
        # ], check=True)
        #
        # Step 3: Generate SRT captions from script
        # srt_path = self._generate_srt(script, run_dir)
        #
        # Step 4: Merge video + audio + captions
        # cmd = [
        #     "ffmpeg",
        #     "-i", str(run_dir / "concat.mp4"),
        # ]
        # if manifest.voiceover:
        #     cmd.extend(["-i", manifest.voiceover.file_path])
        # cmd.extend([
        #     "-vf", f"subtitles={srt_path}:force_style='FontSize=24,PrimaryColour=&HFFFFFF&'",
        #     "-c:v", "libx264", "-c:a", "aac",
        #     "-shortest",
        #     str(output_path)
        # ])
        # subprocess.run(cmd, check=True)

        print(f"  Assembly stub — would output to {output_path}")
        return output_path

    def _generate_srt(self, script: Script, run_dir: Path) -> Path:
        """Generate SRT caption file from script timing.

        Each scene's dialogue becomes a caption block,
        timed to match scene duration.
        """
        srt_path = run_dir / "captions.srt"
        lines = []
        current_time_ms = 0

        # Hook caption
        if script.hook:
            end_ms = 3000
            lines.append(self._srt_block(1, current_time_ms, end_ms, script.hook))
            current_time_ms = end_ms

        # Scene captions
        for i, scene in enumerate(script.scenes):
            if scene.dialogue:
                end_ms = current_time_ms + (scene.duration_s * 1000)
                lines.append(self._srt_block(i + 2, current_time_ms, end_ms, scene.dialogue))
                current_time_ms = end_ms

        # CTA caption
        if script.cta:
            end_ms = current_time_ms + 3000
            lines.append(self._srt_block(len(lines) + 1, current_time_ms, end_ms, script.cta))

        with open(srt_path, "w") as f:
            f.write("\n\n".join(lines))

        return srt_path

    @staticmethod
    def _srt_block(index: int, start_ms: int, end_ms: int, text: str) -> str:
        """Format one SRT caption block."""
        def ms_to_srt(ms):
            h = ms // 3600000
            m = (ms % 3600000) // 60000
            s = (ms % 60000) // 1000
            ms_rem = ms % 1000
            return f"{h:02d}:{m:02d}:{s:02d},{ms_rem:03d}"

        return f"{index}\n{ms_to_srt(start_ms)} --> {ms_to_srt(end_ms)}\n{text}"
