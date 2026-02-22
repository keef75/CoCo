"""
Background music player for CoCo.

Uses macOS native ``afplay`` command for audio playback with automatic
playlist advancement.  This is a fully standalone class -- it does not
depend on any other CoCo module.

Extracted verbatim from ``cocoa.py`` (lines 145-334) with only the
addition of top-level imports (the original embedded them inside methods).
"""

import signal
import subprocess
import threading
import time
from pathlib import Path


class BackgroundMusicPlayer:
    """Continuous background music player using macOS native afplay command with auto-advance"""

    def __init__(self):
        self.is_playing = False
        self.current_track = None
        self.playlist = []
        self.current_index = 0
        self.current_process = None
        self.continuous_mode = False
        self.monitor_thread = None
        self._stop_monitoring = False

    def initialize(self):
        """No initialization needed for afplay - it's built into macOS"""
        return True

    def load_playlist(self, audio_dir: Path):
        """Load all MP3 files from the audio directory"""
        if not audio_dir.exists():
            return []

        self.playlist = list(audio_dir.glob("*.mp3"))
        self.current_index = 0
        return self.playlist

    def cycle_starting_song(self):
        """Cycle to a different starting song for variety - good UX!"""
        if not self.playlist or len(self.playlist) <= 1:
            return  # Nothing to cycle

        # Cycle through the playlist for variety
        if not hasattr(self, '_last_start_index'):
            self._last_start_index = -1

        # Move to next song, wrapping around
        self._last_start_index = (self._last_start_index + 1) % len(self.playlist)
        self.current_index = self._last_start_index

    def play(self, track_path: Path = None, continuous: bool = False):
        """Start playing music using macOS afplay command with optional continuous mode"""
        # Stop any current playback first
        self.stop()

        # Set continuous mode
        self.continuous_mode = continuous

        # Determine which track to play
        if track_path:
            track = track_path
        elif self.playlist and len(self.playlist) > 0:
            track = self.playlist[self.current_index]
        else:
            return False

        # Start the track
        if self._start_track(track):
            self.is_playing = True

            # Start monitoring thread for continuous playback
            if continuous and self.playlist and len(self.playlist) > 1:
                self._stop_monitoring = False
                self.monitor_thread = threading.Thread(target=self._monitor_playback, daemon=True)
                self.monitor_thread.start()

            return True
        else:
            return False

    def _monitor_playback(self):
        """Monitor playback and auto-advance to next track in continuous mode"""
        while not self._stop_monitoring and self.continuous_mode:
            if self.current_process:
                # Check if process is still running
                poll_result = self.current_process.poll()
                if poll_result is not None:  # Process has finished
                    # Auto-advance to next track
                    if self.playlist and len(self.playlist) > 1:
                        self.current_index = (self.current_index + 1) % len(self.playlist)
                        next_track = self.playlist[self.current_index]

                        # Start next track using internal method (no thread management)
                        self._start_track(next_track)
                        # Continue monitoring
                        if not self._stop_monitoring:
                            time.sleep(0.5)  # Small delay
                            continue
                    else:
                        # No more tracks or single track mode - stop monitoring
                        self._stop_monitoring = True
                        break
            else:
                break

            time.sleep(1)  # Check every second

    def _start_track(self, track_path: Path):
        """Internal method to start a track without thread management"""
        # Clean up previous process if exists
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=0.5)
            except Exception:
                try:
                    self.current_process.kill()
                except Exception:
                    pass

        try:
            # Launch afplay subprocess
            self.current_process = subprocess.Popen(
                ['afplay', str(track_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            self.current_track = track_path
            return True

        except Exception:
            return False

    def stop(self):
        """Stop music playback and monitoring"""
        # Stop monitoring first
        self._stop_monitoring = True
        self.continuous_mode = False

        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=1)  # Wait for clean shutdown
            except Exception:
                # Force kill if it doesn't terminate cleanly
                try:
                    self.current_process.kill()
                except Exception:
                    pass
            finally:
                self.current_process = None

        # Wait for monitor thread to finish (only if not calling from within the thread)
        if self.monitor_thread and self.monitor_thread.is_alive():
            current_thread = threading.current_thread()
            if current_thread != self.monitor_thread:
                self.monitor_thread.join(timeout=2)

        self.is_playing = False

    def pause(self):
        """Pause music playback using SIGSTOP"""
        if self.current_process and self.is_playing:
            try:
                self.current_process.send_signal(signal.SIGSTOP)
            except Exception:
                pass

    def resume(self):
        """Resume music playback using SIGCONT"""
        if self.current_process:
            try:
                self.current_process.send_signal(signal.SIGCONT)
            except Exception:
                pass

    def next_track(self):
        """Skip to next track in playlist, preserving continuous mode"""
        if not self.playlist:
            return False

        current_continuous = self.continuous_mode
        self.current_index = (self.current_index + 1) % len(self.playlist)
        return self.play(continuous=current_continuous)

    def get_current_track_name(self) -> str:
        """Get current track name"""
        if self.current_track:
            return self.current_track.stem
        return "No track playing"
