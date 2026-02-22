"""
Speech -- text-to-speech integration via ElevenLabs audio consciousness.

Extracted from cocoa.py lines ~8602-8668.  Wraps the audio consciousness
module to provide TTS functionality with background-music coordination.

Responsibilities
----------------
* ``speak_response()`` -- send text to ElevenLabs TTS
* ``_clean_text_for_speech()`` -- strip markdown / URLs for natural speech
* Auto-TTS toggle (pause/resume background music around voice synthesis)
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SpeechEngine:
    """Wraps audio consciousness for text-to-speech.

    Parameters
    ----------
    audio_consciousness:
        The audio-consciousness module (ElevenLabs TTS integration).
        May be ``None`` if the API key is not configured.
    music_player:
        Optional music player instance for pausing/resuming background music
        during voice synthesis.
    """

    def __init__(
        self,
        audio_consciousness: Any = None,
        music_player: Any = None,
    ) -> None:
        self.audio_consciousness = audio_consciousness
        self.music_player = music_player
        self.auto_tts_enabled: bool = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def speak_response(self, text: str) -> None:
        """Speak CoCo's response if auto-TTS is enabled.

        Pauses any background music during voice synthesis and resumes
        it afterward.  Failures are silently swallowed so they never
        interrupt the conversation flow.
        """
        if not self.auto_tts_enabled:
            return

        if not self.audio_consciousness:
            return

        if not self.audio_consciousness.config.enabled:
            return

        try:
            clean_text = self._clean_text_for_speech(text)

            # Pause background music during voice synthesis
            music_was_playing = False
            if self.music_player:
                music_was_playing = getattr(self.music_player, "is_playing", False)
                if music_was_playing:
                    self.music_player.pause()

            async def _speak_async():
                return await self.audio_consciousness.express_vocally(
                    clean_text[:800],  # Limit length for reasonable speech duration
                    internal_state={"emotional_valence": 0.6, "confidence": 0.7},
                )

            asyncio.run(_speak_async())

            # Resume background music after voice synthesis
            if music_was_playing and self.music_player:
                time.sleep(0.5)  # Small delay to let the voice finish
                self.music_player.resume()

        except Exception:
            # Silent fail -- don't interrupt the conversation if audio fails
            pass

    # ------------------------------------------------------------------
    # Text cleaning
    # ------------------------------------------------------------------

    @staticmethod
    def _clean_text_for_speech(text: str) -> str:
        """Clean response text for natural speech output.

        Strips markdown formatting, URLs, file paths, and excess emoji
        so the TTS engine produces smooth, natural-sounding audio.
        """
        # Remove markdown formatting
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)   # Bold
        text = re.sub(r"\*(.*?)\*", r"\1", text)        # Italic
        text = re.sub(r"`(.*?)`", r"\1", text)          # Inline code
        text = re.sub(r"#{1,6}\s*", "", text)            # Headers

        # Remove URLs and file paths
        text = re.sub(r"http[s]?://\S+", "", text)
        text = re.sub(r"[./][^\s]*\.(py|js|json|md|txt|css)", "", text)

        # Remove most emoji / non-word characters (keep basic punctuation)
        text = re.sub(r"[^\w\s\.,!?'\"():-]", "", text)

        # Limit to first few sentences for reasonable length
        sentences = text.split(".")
        if len(sentences) > 8:
            text = ". ".join(sentences[:8]) + "."

        return text.strip()
