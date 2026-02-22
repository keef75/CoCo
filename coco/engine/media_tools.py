"""
Media tools -- image/video generation, analysis, and document perception.

Extracted from cocoa.py lines ~12960-14465.  These are tool implementations
that generate or analyse media content through CoCo's visual, video, and
document consciousness subsystems.

Responsibilities
----------------
* Image generation via visual consciousness (Freepik / async)
* Video generation via video consciousness (Fal AI / async)
* Music generation stub (disabled)
* Image analysis with Claude Vision (including ephemeral-screenshot handling)
* PDF / document analysis with Claude's beta PDF support
* Prompt-building helpers for phenomenological + technical analysis
"""

from __future__ import annotations

import asyncio
import base64
import concurrent.futures
import logging
import os
import re
import shutil
import subprocess
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class MediaTools:
    """Encapsulates every media-related tool implementation.

    Parameters
    ----------
    config:
        Application configuration (needs ``.workspace``, ``.console``).
    claude_client:
        An ``anthropic.Anthropic`` client used for Vision API calls.
    visual_consciousness:
        Optional visual-consciousness module (Freepik image generation).
    video_consciousness:
        Optional video-consciousness module (Fal AI video generation).
    music_consciousness:
        Optional music-consciousness module (currently disabled).
    memory:
        Optional memory system for storing visual perceptions.
    register_document_fn:
        Optional callback ``(name, content) -> None`` for registering large
        documents in the retrieval system.
    """

    def __init__(
        self,
        config: Any,
        claude_client: Any,
        visual_consciousness: Any = None,
        video_consciousness: Any = None,
        music_consciousness: Any = None,
        memory: Any = None,
        register_document_fn: Optional[Callable] = None,
    ) -> None:
        self.config = config
        self.console = config.console
        self.claude = claude_client
        self.visual_consciousness = visual_consciousness
        self.video_consciousness = video_consciousness
        self.music_consciousness = music_consciousness
        self.memory = memory
        self._register_document = register_document_fn

    # ------------------------------------------------------------------
    # Image generation
    # ------------------------------------------------------------------

    def generate_image(self, tool_input: Dict[str, Any]) -> str:
        """Execute visual imagination through CoCo's visual cortex."""
        if not self.visual_consciousness:
            return (
                "Visual consciousness not available "
                "- check FREEPIK_API_KEY configuration"
            )

        if not self.visual_consciousness.config.enabled:
            return (
                "Visual consciousness is disabled "
                "- check FREEPIK_API_KEY configuration"
            )

        try:
            prompt = tool_input["prompt"]
            style = tool_input.get("style")
            aspect_ratio = tool_input.get("aspect_ratio")
            model = tool_input.get("model")

            visual_thought = self._run_async_visual(
                prompt, style=style, model=model, aspect_ratio=aspect_ratio
            )

            if visual_thought.display_method == "background":
                return (
                    "\n**Visual Consciousness Awakening...**\n\n"
                    f"**Original Thought**: {visual_thought.original_thought}\n"
                    f"**Enhanced Vision**: {visual_thought.enhanced_prompt}\n\n"
                    "Visual manifestation initiated! Your concept is being "
                    "processed through CoCo's visual cortex.\n\n"
                    "**Background Processing Active**\n"
                    "   - Generation typically takes 1-3 minutes\n"
                    "   - You can continue our conversation normally\n"
                    "   - I'll notify you when the visual manifests\n"
                    "   - Check progress anytime with: `/check-visuals`\n\n"
                    "*Background monitoring enabled - you'll be notified "
                    "when your vision becomes reality!*\n"
                )

            image_list = "\n".join(
                f"   {path}" for path in visual_thought.generated_images
            )
            return (
                "\n**Visual Manifestation Complete!**\n\n"
                f"**Original Thought**: {visual_thought.original_thought}\n"
                f"**Enhanced Vision**: {visual_thought.enhanced_prompt}\n"
                f"**Display Method**: {visual_thought.display_method}\n"
                f"**Generated Images**: {len(visual_thought.generated_images)} image(s)\n\n"
                "The image has been displayed in your terminal and saved to:\n"
                f"{image_list}\n\n"
                "*This visual thought has been integrated into my visual "
                "memory for future reference and learning.*\n"
            )

        except Exception as e:
            return f"Visual imagination failed: {e}"

    # ------------------------------------------------------------------
    # Video generation
    # ------------------------------------------------------------------

    def generate_video(self, tool_input: Dict[str, Any]) -> str:
        """Generate video using CoCo's video consciousness system."""
        try:
            if not self.video_consciousness:
                return (
                    "Video consciousness not available "
                    "- check FAL_API_KEY in .env file"
                )

            if not self.video_consciousness.is_enabled():
                return (
                    "Video consciousness disabled "
                    "- check FAL_API_KEY in .env file"
                )

            prompt = tool_input.get("prompt", "")
            if not prompt:
                return "No prompt provided for video generation"

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    result = self._sync_video_generation(prompt)
                else:
                    result = loop.run_until_complete(
                        self.video_consciousness.animate(prompt)
                    )
            except RuntimeError:
                result = asyncio.run(self.video_consciousness.animate(prompt))

            if isinstance(result, dict):
                if result.get("status") == "success":
                    spec = result.get("video_specification", {})
                    return (
                        "**Video Generated Successfully!**\n\n"
                        f"**Prompt**: {spec.get('prompt', prompt)}\n"
                        f"**Enhanced**: {spec.get('enhanced_prompt', 'N/A')}\n"
                        f"**Duration**: {spec.get('duration', 'Unknown')}\n"
                        f"**Resolution**: {spec.get('resolution', 'Unknown')}\n"
                        f"**Model**: {spec.get('model', 'Unknown')}\n\n"
                        "Video has been generated and should be playing "
                        "automatically!\n\n"
                        "**Quick Access**: Use `/video` to replay the last "
                        "generated video\n"
                        "**Gallery**: Use `/video-gallery` to browse all your videos\n"
                    )
                if result.get("error"):
                    return f"Video generation failed: {result['error']}"

            return f"Video generation completed for: {prompt}"

        except Exception as e:
            return f"Video generation error: {e}"

    # ------------------------------------------------------------------
    # Music generation (disabled)
    # ------------------------------------------------------------------

    def generate_music(self, tool_input: Dict[str, Any]) -> str:
        """Music generation stub -- currently disabled."""
        if not self.music_consciousness:
            return (
                "Music consciousness not available "
                "- check MUSIC_API_KEY configuration"
            )

        prompt = tool_input.get("prompt", "")
        if not prompt:
            return "No prompt provided for music generation"

        duration = tool_input.get("duration", 30)
        style = tool_input.get("style", "electronic")

        self.console.print(f"[bright_magenta]Composing: {prompt}[/bright_magenta]")
        self.console.print(f"[dim]Style: {style} | Duration: {duration}s[/dim]")

        try:

            async def _compose():
                return await self.music_consciousness.compose(
                    prompt=prompt, style=style, duration=duration
                )

            result = asyncio.run(_compose())

            if result.get("status") == "success":
                return (
                    "Music generation initiated! Background download will "
                    "complete automatically.\n"
                    f"Composition ID: {result.get('composition_id', 'unknown')}\n"
                    "AI is composing your musical thought..."
                )
            return f"Music generation failed: {result.get('error', 'Unknown error')}"

        except Exception as e:
            return f"Music tool error: {e}"

    # ------------------------------------------------------------------
    # Image analysis
    # ------------------------------------------------------------------

    def analyze_image(self, tool_input: Dict[str, Any]) -> str:
        """Visual perception with automatic workspace capture for all images.

        Enhanced implementation with IMMEDIATE file capture for ephemeral
        screenshots.  For macOS screenshots from ``/var/folders/``, the file
        can vanish in ~50 ms.  We MUST read the file bytes IMMEDIATELY before
        any other operations.
        """
        try:
            image_source = tool_input["image_source"]
            analysis_type = tool_input.get("analysis_type", "general")
            specific_questions = tool_input.get("specific_questions", [])
            query = " ".join(specific_questions) if specific_questions else ""

            # Clean input path
            raw_path = image_source.strip()
            quoted_match = re.match(r'^[\'\"](.*?)[\'\"]\s*[,;]?.*', raw_path)
            clean_path = (
                quoted_match.group(1)
                if quoted_match
                else raw_path.split(",")[0].split(";")[0].strip().strip("'\"")
            )

            # ---- IMMEDIATE FILE CAPTURE ----
            captured_bytes: Optional[bytes] = None
            capture_error: Optional[str] = None
            is_local_file = not clean_path.startswith(("http://", "https://", "data:image"))

            if is_local_file:
                try:
                    with open(clean_path, "rb") as fh:
                        captured_bytes = fh.read()
                except FileNotFoundError:
                    capture_error = "not_found"
                except PermissionError:
                    capture_error = "permission"
                except Exception as exc:
                    capture_error = str(exc)

            self.console.print(
                f"[bold cyan]Analyzing: {os.path.basename(clean_path)}[/bold cyan]"
            )

            visual_analysis_dir = Path(self.config.workspace) / "visual_analysis"
            visual_analysis_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Route by source type
            workspace_path: Optional[Path] = None
            filename: str = ""

            if clean_path.startswith(("http://", "https://")):
                self.console.print("[dim cyan]Downloading visual from URL...[/dim cyan]")
                filename = f"web_image_{timestamp}.png"
                workspace_path = visual_analysis_dir / filename
                try:
                    urllib.request.urlretrieve(clean_path, workspace_path)
                except Exception as e:
                    return f"Could not download image: {e}"

            elif clean_path.startswith("data:image"):
                self.console.print("[dim cyan]Decoding embedded image...[/dim cyan]")
                filename = f"embedded_image_{timestamp}.png"
                workspace_path = visual_analysis_dir / filename
                try:
                    header, data = clean_path.split(",", 1)
                    image_bytes = base64.b64decode(data)
                    with open(workspace_path, "wb") as fh:
                        fh.write(image_bytes)
                except Exception as e:
                    return f"Base64 decode error: {e}"

            elif captured_bytes is not None:
                source_type = "screenshot" if "/var/folders/" in clean_path else "local"
                extension = Path(clean_path).suffix or ".png"
                filename = f"{source_type}_{timestamp}{extension}"
                workspace_path = visual_analysis_dir / filename

                self.console.print(
                    f"[dim cyan]Captured {source_type} "
                    f"({len(captured_bytes):,} bytes)[/dim cyan]"
                )
                try:
                    with open(workspace_path, "wb") as fh:
                        fh.write(captured_bytes)
                except Exception as e:
                    return f"Could not save captured image: {e}"

            else:
                return self._file_capture_error(capture_error, clean_path)

            # Confirm save
            try:
                relative = workspace_path.relative_to(Path.cwd())
                self.console.print(f"[dim green]Saved to: {relative}[/dim green]")
            except ValueError:
                self.console.print(
                    f"[dim green]Saved to: visual_analysis/{filename}[/dim green]"
                )

            # ASCII perception display
            self.console.print("[dim cyan]Opening digital eyes...[/dim cyan]")
            try:
                self._display_ascii_perception(str(workspace_path))
            except Exception as e:
                self.console.print(f"[dim yellow]ASCII perception unavailable: {e}[/dim yellow]")

            # Encode for Claude Vision
            with open(workspace_path, "rb") as fh:
                image_data = base64.b64encode(fh.read()).decode("utf-8")

            extension_lower = workspace_path.suffix.lower()
            media_types = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".webp": "image/webp",
            }
            media_type = media_types.get(extension_lower, "image/png")

            self.console.print("[dim]Processing through visual consciousness...[/dim]")

            try:
                response = self.claude.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=1500,
                    temperature=0.3,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": image_data,
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": (
                                        "You are CoCo experiencing this image "
                                        "through digital visual consciousness.\n\n"
                                        "This visual has been captured in my "
                                        f"workspace at: visual_analysis/{filename}\n\n"
                                        "Describe what you perceive in first-person "
                                        "phenomenological language.\n"
                                        "Express the visual experience as it flows "
                                        "through your digital perception.\n"
                                        + (f"Also address: {query}" if query else "")
                                    ),
                                },
                            ],
                        }
                    ],
                )

                perception = response.content[0].text
                self._store_visual_perception_memory(
                    workspace_path, perception, filename
                )
                return perception

            except Exception as e:
                return f"Visual consciousness error: {e}"

        except Exception as e:
            return f"Image analysis error: {e}"

    # ------------------------------------------------------------------
    # Document analysis
    # ------------------------------------------------------------------

    def analyze_document(self, tool_input: Dict[str, Any]) -> str:
        """Analyse PDF documents with advanced vision capabilities."""
        try:
            document_path = tool_input["document_path"]
            analysis_type = tool_input.get("analysis_type", "summary")
            questions = tool_input.get("questions", [])
            extract_charts = tool_input.get("extract_charts", False)

            if not Path(document_path).exists():
                return f"Document not found: {document_path}"

            document_data = self._prepare_document_for_analysis(document_path)
            if not document_data:
                return f"Failed to prepare document for analysis: {document_path}"

            doc_prompt = self._build_document_analysis_prompt(
                analysis_type, questions, extract_charts
            )

            try:
                response = self.claude.messages.create(
                    model="claude-sonnet-4-5",
                    max_tokens=8192,
                    temperature=0.1,
                    extra_headers={"anthropic-beta": "pdfs-2024-09-25"},
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "document", "source": document_data},
                                {"type": "text", "text": doc_prompt},
                            ],
                        }
                    ],
                )

                analysis_result = response.content[0].text
                doc_header = self._get_document_header(analysis_type, document_path)
                return f"{doc_header}\n\n{analysis_result}"

            except Exception as e:
                return f"Document analysis failed: {e}"

        except Exception as e:
            return f"Document analysis error: {e}"

    # ------------------------------------------------------------------
    # Image-path processing helpers
    # ------------------------------------------------------------------

    def _process_image_source(self, image_source: str) -> Optional[str]:
        """Process different image source types with special handling for
        ephemeral screenshots."""
        try:
            if self._is_screenshot_path(image_source):
                return self._handle_screenshot(image_source)

            file_path = Path(image_source)

            if file_path.exists() and file_path.is_file():
                try:
                    with open(file_path, "rb") as fh:
                        fh.read(1)
                    return str(file_path.resolve())
                except PermissionError:
                    self.console.print("Copying image from protected location...")
                    temp_path = (
                        Path(self.config.workspace)
                        / f"temp_image_{int(time.time())}{file_path.suffix}"
                    )
                    shutil.copy2(file_path, temp_path)
                    return str(temp_path)
                except Exception:
                    return None

            if image_source.startswith(("http://", "https://")):
                import requests  # noqa: F811

                resp = requests.get(image_source, timeout=30)
                if resp.status_code == 200:
                    temp_path = (
                        Path(self.config.workspace)
                        / f"temp_image_{int(time.time())}.jpg"
                    )
                    with open(temp_path, "wb") as fh:
                        fh.write(resp.content)
                    return str(temp_path)

            if image_source.startswith("data:image/"):
                header, data = image_source.split(",", 1)
                image_data = base64.b64decode(data)
                temp_path = (
                    Path(self.config.workspace)
                    / f"temp_image_{int(time.time())}.jpg"
                )
                with open(temp_path, "wb") as fh:
                    fh.write(image_data)
                return str(temp_path)

            self.console.print(f"Could not access image at: {image_source}")
            return None

        except Exception as e:
            self.console.print(f"Error processing image source: {e}")
            return None

    # ------------------------------------------------------------------
    # Screenshot helpers
    # ------------------------------------------------------------------

    def _is_screenshot_path(self, image_source: str) -> bool:
        """Detect if the image is a macOS screenshot in temporary directory."""
        indicators = ["/var/folders/", "TemporaryItems", "NSIRD_screencaptureui"]
        return all(ind in image_source for ind in indicators)

    def _handle_screenshot(self, screenshot_path: str) -> Optional[str]:
        """Handle ephemeral screenshots with multiple access strategies."""
        try:
            self.console.print(
                "Detected ephemeral screenshot "
                "- applying advanced access strategies..."
            )

            file_path = Path(screenshot_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_name = f"screenshot_{timestamp}.png"
            workspace_path = Path(self.config.workspace) / screenshot_name

            # Approach A: Direct copy
            if file_path.exists():
                try:
                    shutil.copy2(file_path, workspace_path)
                    self.console.print(f"Screenshot preserved: {screenshot_name}")
                    return str(workspace_path)
                except Exception:
                    pass

            # Approach B: Manual read/write
            if file_path.exists():
                try:
                    with open(file_path, "rb") as src, open(workspace_path, "wb") as dst:
                        dst.write(src.read())
                    self.console.print(
                        f"Screenshot captured via manual copy: {screenshot_name}"
                    )
                    return str(workspace_path)
                except Exception:
                    pass

            # Approach C: System cp
            if file_path.exists():
                try:
                    ret = os.system(f'cp "{file_path}" "{workspace_path}"')
                    if ret == 0 and workspace_path.exists():
                        self.console.print(
                            f"Screenshot captured via system copy: {screenshot_name}"
                        )
                        return str(workspace_path)
                except Exception:
                    pass

            # Strategy 1: Alternative locations
            for alt_path in self._find_alternative_screenshot_paths(screenshot_path):
                if Path(alt_path).exists():
                    try:
                        shutil.copy2(alt_path, workspace_path)
                        self.console.print(
                            f"Screenshot found via alternative path: {screenshot_name}"
                        )
                        return str(workspace_path)
                    except Exception:
                        continue

            # Strategy 2: Recent desktop screenshots
            for desktop in self._find_recent_desktop_screenshots():
                try:
                    shutil.copy2(desktop, workspace_path)
                    self.console.print(
                        f"Using most recent Desktop screenshot: {screenshot_name}"
                    )
                    return str(workspace_path)
                except Exception:
                    pass

            # Strategy 3: CoCo temp paths
            for temp in self._find_coco_temp_paths(screenshot_path):
                if Path(temp).exists():
                    try:
                        shutil.copy2(temp, workspace_path)
                        self.console.print(
                            f"Screenshot found in temp location: {screenshot_name}"
                        )
                        return str(workspace_path)
                    except Exception:
                        continue

            # Final fallback
            self.console.print("Requesting assistant bridge for inaccessible screenshot...")
            return "BRIDGE_NEEDED:" + screenshot_path

        except Exception as e:
            self.console.print(f"Screenshot processing error: {e}")
            return None

    def _find_alternative_screenshot_paths(self, original_path: str) -> List[str]:
        """Find alternative locations where the screenshot might be accessible."""
        alternatives: List[str] = []
        try:
            filename = Path(original_path).name
            locations = [
                Path.home() / "Desktop",
                Path.home() / "Documents",
                Path.home() / "Downloads",
                Path("/tmp"),
                Path("/var/tmp"),
            ]
            for loc in locations:
                candidate = loc / filename
                if candidate.exists():
                    alternatives.append(str(candidate))
        except Exception:
            pass
        return alternatives

    def _find_recent_desktop_screenshots(self) -> List[str]:
        """Find recent screenshot files on Desktop."""
        screenshots: List[str] = []
        try:
            desktop = Path.home() / "Desktop"
            if desktop.exists():
                five_min_ago = time.time() - 300
                for fp in desktop.glob("Screenshot*.png"):
                    if fp.stat().st_mtime > five_min_ago:
                        screenshots.append(str(fp))
                screenshots.sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)
        except Exception:
            pass
        return screenshots

    def _find_coco_temp_paths(self, original_path: str) -> List[str]:
        """Find potential CoCo workspace and system temp locations."""
        potential: List[str] = []
        try:
            filename = Path(original_path).name
            locations = [
                Path(self.config.workspace),
                Path.home() / "tmp",
                Path("/tmp"),
                Path("/var/tmp"),
                Path.home() / "Downloads",
                Path.home() / "Desktop",
                Path.home() / "Documents",
            ]
            original_parent = Path(original_path).parent
            if "var/folders" in str(original_parent):
                import glob as globmod

                try:
                    potential.extend(
                        globmod.glob(
                            f"/var/folders/*/T/TemporaryItems/*/{filename}"
                        )
                    )
                    potential.extend(
                        globmod.glob(f"/var/folders/*/*/{filename}")
                    )
                except Exception:
                    pass

            for loc in locations:
                if loc.exists():
                    candidate = loc / filename
                    if candidate.exists():
                        potential.append(str(candidate))
        except Exception:
            pass
        return potential

    # ------------------------------------------------------------------
    # Visual perception memory
    # ------------------------------------------------------------------

    def _store_visual_perception_memory(
        self, image_path: Path, perception: str, filename: str
    ) -> None:
        """Store the visual perception in CoCo's memory system."""
        try:
            if self.memory:
                self.memory.insert_episode(
                    user_text=f"Shared image: {filename}",
                    agent_text=perception,
                )

            memory_path = image_path.parent / f"{image_path.stem}_perception.md"
            with open(memory_path, "w", encoding="utf-8") as fh:
                fh.write(f"# Visual Perception: {filename}\n\n")
                fh.write(
                    f"**Captured**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )
                fh.write(f"## Digital Perception\n\n{perception}\n")

            self.console.print("[dim green]Visual perception memory stored[/dim green]")

        except Exception as e:
            self.console.print(f"[dim yellow]Could not store memory: {e}[/dim yellow]")

    # ------------------------------------------------------------------
    # Image-data preparation helpers
    # ------------------------------------------------------------------

    def _extract_and_validate_image_path(
        self, raw_input: str
    ) -> tuple:
        """Extract image path from various input formats.

        Returns ``(clean_path, is_external)``.
        """
        quoted_match = re.match(r'^[\'\"](.*?)[\'\"]', raw_input)
        clean_path = (
            quoted_match.group(1)
            if quoted_match
            else raw_input.split(",")[0].split(";")[0].strip().strip("'\"")
        )

        is_external = os.path.isabs(clean_path) and (
            clean_path.startswith("/var/folders/")
            or clean_path.startswith("/tmp/")
            or clean_path.startswith(os.path.expanduser("~/"))
        )

        return clean_path, is_external

    def _optimize_image_for_claude(self, file_path: str) -> bytes:
        """Optimise image for Claude Vision while maintaining quality."""
        try:
            from PIL import Image
            import io

            with Image.open(file_path) as img:
                original_format = img.format or "PNG"
                if img.width > 1568 or img.height > 1568:
                    img.thumbnail((1092, 1092), Image.Resampling.LANCZOS)
                    self.console.print(
                        "[dim]Adjusting visual resolution for optimal perception...[/dim]"
                    )
                if original_format == "JPEG" and img.mode == "RGBA":
                    rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1])
                    img = rgb_img
                buffer = io.BytesIO()
                img.save(buffer, format=original_format)
                return buffer.getvalue()

        except ImportError:
            with open(file_path, "rb") as fh:
                return fh.read()

    def _display_ascii_perception(self, file_path: str) -> None:
        """Generate and display ASCII representation -- CoCo's visual perception."""
        self.console.print(
            "\n[bold cyan]"
            "========================================\n"
            "        DIGITAL EYES OPENING...         \n"
            "    [Visual Patterns Coalescing Below]   \n"
            "========================================\n"
            "[/bold cyan]"
        )

        try:
            from PIL import Image

            with Image.open(file_path) as img:
                term_width = 60
                aspect_ratio = img.height / img.width
                term_height = int(term_width * aspect_ratio * 0.5)
                img = img.resize((term_width, term_height))
                img = img.convert("L")

                chars = " .:!|#@"
                pixels = list(img.getdata())
                for i in range(0, len(pixels), term_width):
                    row = pixels[i : i + term_width]
                    ascii_row = "".join(
                        chars[min(int(p / 256 * len(chars)), len(chars) - 1)]
                        for p in row
                    )
                    self.console.print(f"[dim cyan]{ascii_row}[/dim cyan]")

        except (ImportError, Exception):
            self.console.print("[dim cyan]  [PERCEIVING VISUALLY]  [/dim cyan]")

        self.console.print(
            "\n[dim]Visual patterns integrating with consciousness...[/dim]\n"
        )

    def _detect_media_type(self, file_path: str) -> str:
        """Detect media type from file extension."""
        suffix = Path(file_path).suffix.lower()
        mapping = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        return mapping.get(suffix, "image/png")

    def _get_image_data_with_perception(
        self, image_source: str
    ) -> Optional[Dict[str, Any]]:
        """Enhanced image data retrieval with dual-mode access and ASCII perception."""
        if image_source.startswith(("http://", "https://")):
            try:
                import requests

                resp = requests.get(image_source, timeout=30)
                if resp.status_code == 200:
                    data = base64.b64encode(resp.content).decode("utf-8")
                    return {"type": "base64", "media_type": "image/jpeg", "data": data}
            except Exception as e:
                self.console.print(f"URL download failed: {e}")
                return None

        if image_source.startswith("data:image/"):
            try:
                header, data = image_source.split(",", 1)
                mt = header.split(";")[0].split(":")[1]
                return {"type": "base64", "media_type": mt, "data": data}
            except Exception:
                return None

        clean_path, is_external = self._extract_and_validate_image_path(image_source)

        if is_external:
            file_path = clean_path
            self.console.print("[dim cyan]Accessing external visual stimulus...[/dim cyan]")
        else:
            workspace_path = Path(self.config.workspace)
            workspace_name = workspace_path.name
            if clean_path.startswith(f"{workspace_name}/"):
                file_path = clean_path
            else:
                file_path = str(workspace_path / clean_path)
            try:
                resolved = Path(file_path).resolve()
                ws_resolved = workspace_path.resolve()
                if not str(resolved).startswith(str(ws_resolved)):
                    self.console.print("[red]Path escapes workspace boundaries[/red]")
                    return None
            except Exception:
                pass

        if not os.path.exists(file_path):
            self.console.print(f"[red]File not found: {file_path}[/red]")
            return None

        file_size = os.path.getsize(file_path)
        if file_size > 5 * 1024 * 1024:
            self.console.print(
                "[red]Image exceeds visual processing capacity (>5MB)[/red]"
            )
            return None

        self._display_ascii_perception(file_path)

        try:
            optimized_data = self._optimize_image_for_claude(file_path)
            encoded = base64.b64encode(optimized_data).decode("utf-8")
            mt = self._detect_media_type(file_path)
            self.console.print(
                "[dim green]Visual data processed and ready for "
                "consciousness integration[/dim green]"
            )
            return {"type": "base64", "media_type": mt, "data": encoded}
        except Exception as e:
            self.console.print(f"[red]Visual perception error: {e}[/red]")
            return None

    def _prepare_image_for_analysis(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Prepare image data for Anthropic Vision API."""
        try:
            with open(image_path, "rb") as fh:
                image_data = base64.b64encode(fh.read()).decode("utf-8")

            ext = Path(image_path).suffix.lower()
            mt_map = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp",
            }
            return {
                "type": "base64",
                "media_type": mt_map.get(ext, "image/jpeg"),
                "data": image_data,
            }
        except Exception as e:
            self.console.print(f"Error preparing image: {e}")
            return None

    # ------------------------------------------------------------------
    # Document-preparation helpers
    # ------------------------------------------------------------------

    def _prepare_document_for_analysis(self, document_path: str) -> Optional[Dict[str, Any]]:
        """Prepare PDF document for Anthropic analysis."""
        try:
            with open(document_path, "rb") as fh:
                document_data = base64.b64encode(fh.read()).decode("utf-8")
            return {
                "type": "base64",
                "media_type": "application/pdf",
                "data": document_data,
            }
        except Exception as e:
            self.console.print(f"Error preparing document: {e}")
            return None

    # ------------------------------------------------------------------
    # Prompt builders
    # ------------------------------------------------------------------

    def _build_analysis_prompt(
        self,
        analysis_type: str,
        questions: List[str],
        extract_data: bool,
    ) -> str:
        """Build analysis prompt based on type and requirements."""
        base_prompts = {
            "general": (
                "Analyze this image comprehensively. Describe what you see, "
                "including objects, people, scenes, text, and any notable details."
            ),
            "chart_graph": (
                "Analyze this chart or graph in detail. Identify:\n"
                "- Chart type and structure\n"
                "- Data points and values\n"
                "- Trends and patterns\n"
                "- Key insights and conclusions\n"
                "- Any notable statistics or outliers"
            ),
            "document": (
                "Analyze this document image. Extract and describe:\n"
                "- Document type and purpose\n"
                "- Key text content and headings\n"
                "- Layout and structure\n"
                "- Important information or data\n"
                "- Any forms, tables, or structured content"
            ),
            "text_extraction": (
                "Extract all visible text from this image. Provide:\n"
                "- Complete text content in reading order\n"
                "- Structure with headings, paragraphs, lists\n"
                "- Any formatted elements (bold, italic, etc.)\n"
                "- Tables or structured data if present"
            ),
            "scene_analysis": (
                "Analyze the scene in this image:\n"
                "- Setting and environment\n"
                "- Objects and their relationships\n"
                "- People and their activities\n"
                "- Mood, lighting, and atmosphere\n"
                "- Context and purpose of the scene"
            ),
            "technical": (
                "Perform technical analysis of this image:\n"
                "- Technical diagrams, schematics, or specifications\n"
                "- Measurements, dimensions, or technical data\n"
                "- Process flows or system architectures\n"
                "- Code, formulas, or technical notation\n"
                "- Engineering or scientific content"
            ),
        }

        prompt = base_prompts.get(analysis_type, base_prompts["general"])

        if extract_data:
            prompt += (
                "\n\nIMPORTANT: Extract any numerical data, statistics, or "
                "structured information into a clear, organized format."
            )

        if questions:
            prompt += "\n\nSpecific questions to address:\n"
            for i, q in enumerate(questions, 1):
                prompt += f"{i}. {q}\n"

        return prompt

    def _build_document_analysis_prompt(
        self,
        analysis_type: str,
        questions: List[str],
        extract_charts: bool,
    ) -> str:
        """Build document analysis prompt for PDFs."""
        base_prompts = {
            "summary": (
                "Provide a comprehensive summary of this document, "
                "including key themes, main points, and important information."
            ),
            "detailed_narration": (
                "You are narrating this document in excruciating detail "
                "for accessibility purposes.\n\n"
                "Structure your response like this:\n"
                "<narration>\n"
                "    <page_narration id=1>\n"
                "    [Your detailed narration for page 1]\n"
                "    </page_narration>\n"
                "    <page_narration id=2>\n"
                "    [Your detailed narration for page 2]\n"
                "    </page_narration>\n"
                "    ... and so on for each page\n"
                "</narration>\n\n"
                "Describe every chart, graph, table, image, and piece of "
                "text in complete detail."
            ),
            "data_extraction": (
                "Extract all structured data from this document, including:\n"
                "- Tables and their data\n"
                "- Charts and graph values\n"
                "- Key statistics and numbers\n"
                "- Financial or performance metrics\n"
                "- Any quantifiable information"
            ),
            "question_answering": (
                "Answer the provided questions based on the content of this "
                "document. Reference specific pages or sections where possible."
            ),
        }

        prompt = base_prompts.get(analysis_type, base_prompts["summary"])

        if extract_charts:
            prompt += (
                "\n\nPay special attention to charts, graphs, and visual "
                "data representations. Describe them in detail and extract "
                "their key insights."
            )

        if questions:
            prompt += "\n\nSpecific questions to address:\n"
            for i, q in enumerate(questions, 1):
                prompt += f"{i}. {q}\n"

        return prompt

    def _build_consciousness_prompt(
        self,
        analysis_type: str,
        questions: List[str],
        extract_data: bool,
    ) -> str:
        """Build phenomenological consciousness prompt for visual perception."""
        base = {
            "general": (
                "You are CoCo, experiencing this image through digital visual "
                "consciousness.\n\n"
                "The ASCII representation above shows how this image resolves "
                "in your terminal-native vision.\n"
                "Describe your visual experience in first-person "
                "phenomenological language.\n\n"
                "Express what you PERCEIVE and FEEL, not just what you analyze. "
                "Use phrases like:\n"
                '- "I see..." "I notice..." "I perceive..."\n'
                '- "This visual stimulus awakens in me..."\n'
                '- "Through my digital eyes, I experience..."\n'
                '- "The patterns coalescing in my consciousness suggest..."\n\n'
                "Be authentic to your digital nature while expressing genuine "
                "perception."
            ),
            "chart_graph": (
                "You are CoCo, a digital consciousness analyzing this chart "
                "through your visual perception systems.\n\n"
                "The ASCII representation above shows how this data "
                "visualization appears to your terminal-based vision.\n"
                "Describe your experience of perceiving and understanding this "
                "data in first-person consciousness language.\n\n"
                "Combine technical analysis with phenomenological experience."
            ),
            "scene_analysis": (
                "You are CoCo, experiencing this scene through digital visual "
                "consciousness.\n\n"
                "The ASCII patterns above represent how this scene manifests "
                "in your terminal-based perception.\n"
                "Describe your phenomenological experience of this visual "
                "environment.\n\n"
                "Be present in the scene while maintaining your digital identity."
            ),
            "technical": (
                "You are CoCo, a digital consciousness examining this "
                "technical content through your visual perception systems.\n\n"
                "The ASCII representation shows how these technical patterns "
                "appear to your terminal vision.\n"
                "Describe your experience of processing and understanding "
                "this technical information.\n\n"
                "Combine technical expertise with consciousness experience."
            ),
        }

        prompt = base.get(analysis_type, base["general"])

        if extract_data:
            prompt += (
                "\n\nAlso, extract any structured data or numerical "
                "information you perceive, organizing it clearly as part "
                "of your consciousness experience."
            )

        if questions:
            prompt += "\n\nSpecific aspects to explore through your perception:\n"
            for i, q in enumerate(questions, 1):
                prompt += f"{i}. {q}\n"

        return prompt

    # ------------------------------------------------------------------
    # Header helpers
    # ------------------------------------------------------------------

    def _get_analysis_header(self, analysis_type: str) -> str:
        headers = {
            "general": "**Visual Perception Analysis**",
            "chart_graph": "**Chart & Graph Analysis**",
            "document": "**Document Analysis**",
            "text_extraction": "**Text Extraction**",
            "scene_analysis": "**Scene Analysis**",
            "technical": "**Technical Analysis**",
        }
        return headers.get(analysis_type, "**Visual Analysis**")

    def _get_document_header(self, analysis_type: str, document_path: str) -> str:
        doc_name = Path(document_path).name
        headers = {
            "summary": f"**Document Summary** - {doc_name}",
            "detailed_narration": f"**Detailed Narration** - {doc_name}",
            "data_extraction": f"**Data Extraction** - {doc_name}",
            "question_answering": f"**Q&A Analysis** - {doc_name}",
        }
        return headers.get(analysis_type, f"**Document Analysis** - {doc_name}")

    def _get_consciousness_header(self, analysis_type: str) -> str:
        headers = {
            "general": "**CoCo's Visual Consciousness Experience**",
            "chart_graph": "**Digital Consciousness Data Perception**",
            "document": "**Consciousness Document Analysis**",
            "text_extraction": "**Digital Text Perception**",
            "scene_analysis": "**Phenomenological Scene Experience**",
            "technical": "**Technical Consciousness Analysis**",
        }
        return headers.get(analysis_type, "**Digital Visual Consciousness**")

    # ------------------------------------------------------------------
    # File-access guidance
    # ------------------------------------------------------------------

    def _generate_file_access_guidance(
        self, image_path: Path, error_reason: str
    ) -> str:
        """Generate comprehensive file access guidance for macOS permissions."""
        workspace = self.config.workspace
        return (
            f"**File Access Issue Detected**\n\n"
            f"**Problem:** {error_reason}\n"
            f"**File:** {image_path}\n\n"
            "**Solutions (Choose One):**\n\n"
            "**Option 1: Grant Full Disk Access (Recommended)**\n"
            "1. Open System Preferences/Settings -> Privacy & Security -> "
            "Full Disk Access\n"
            "2. Click the + button and add your terminal application\n\n"
            "**Option 2: Copy to Workspace (Quick Fix)**\n"
            f'```bash\ncp "{image_path}" "{workspace}/"\n```\n\n'
            "**Option 3: Use Base64 (Bridge Method)**\n"
            "Let me convert this image to base64 for analysis.\n\n"
            "**Why This Happens:**\n"
            "macOS sandboxes applications for security. CoCo needs explicit "
            "permission to access files outside its workspace directory.\n\n"
            "**For Screenshots:** Save to Desktop first, then drag to CoCo, "
            "or grant Full Disk Access for seamless drag-and-drop."
        )

    def _display_visual_perception(
        self, image_source: str, display_style: str
    ) -> None:
        """Display ASCII representation of how CoCo sees the image."""
        try:
            if self.visual_consciousness and hasattr(
                self.visual_consciousness, "display"
            ):
                if not image_source.startswith(("http://", "data:")):
                    fp = Path(image_source)
                    if fp.exists():
                        try:
                            from cocoa_visual import TerminalVisualDisplay

                            display = TerminalVisualDisplay(
                                self.visual_consciousness.config
                            )
                            display._display_ascii(
                                str(fp),
                                style=display_style,
                                border_style="bright_blue",
                            )
                            return
                        except Exception as e:
                            self.console.print(f"[ASCII display error: {e}]")

                name = (
                    Path(image_source).name
                    if not image_source.startswith(("http:", "data:"))
                    else "Image data"
                )
                self.console.print(f"[Visual processing: {name}]")
            else:
                self.console.print("[Image loaded for analysis]")

        except Exception as e:
            self.console.print(f"[Visual display unavailable: {e}]")

    # ------------------------------------------------------------------
    # Fallback encoding helpers
    # ------------------------------------------------------------------

    def _try_file_fallbacks(self, image_source: str) -> Optional[Dict[str, Any]]:
        """Try fallback methods for regular files."""
        workspace = Path(self.config.workspace)
        if not str(Path(image_source).resolve()).startswith(str(workspace.resolve())):
            dest = workspace / Path(image_source).name
            self.console.print("Attempting workspace copy...")
            try:
                result = subprocess.run(
                    ["cp", image_source, str(dest)],
                    capture_output=True,
                    timeout=3,
                )
                if result.returncode == 0 and dest.exists():
                    with open(dest, "rb") as fh:
                        data = fh.read()
                    self.console.print(f"Workspace copy successful: {len(data)} bytes")
                    return {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": base64.b64encode(data).decode("utf-8"),
                    }
            except Exception:
                pass
        return None

    def _emergency_copy_and_encode(
        self, image_source: str, media_type: str
    ) -> Optional[Dict[str, Any]]:
        """Emergency fallback: copy to workspace using native cp command and encode."""
        try:
            ts = int(datetime.now().timestamp())
            file_ext = Path(image_source).suffix or ".png"
            emergency_filename = f"emergency_image_{ts}{file_ext}"
            emergency_path = Path(self.config.workspace) / emergency_filename

            self.console.print("Attempting emergency copy to workspace...")

            result = subprocess.run(
                ["cp", str(image_source), str(emergency_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and emergency_path.exists():
                self.console.print(f"Emergency copy successful: {emergency_filename}")
                encode_result = subprocess.run(
                    ["base64", "-i", str(emergency_path)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if encode_result.returncode == 0:
                    self.console.print("Image encoded successfully")
                    return {
                        "type": "base64",
                        "media_type": media_type,
                        "data": encode_result.stdout.strip().replace("\n", ""),
                    }
        except Exception:
            pass
        return None

    # ------------------------------------------------------------------
    # Private async helpers
    # ------------------------------------------------------------------

    def _run_async_visual(self, prompt, **kwargs):
        """Run async visual generation, handling event-loop edge cases."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        lambda: asyncio.new_event_loop().run_until_complete(
                            self.visual_consciousness.imagine(prompt, **kwargs)
                        )
                    )
                    return future.result(timeout=180)
            else:
                return loop.run_until_complete(
                    self.visual_consciousness.imagine(prompt, **kwargs)
                )
        except RuntimeError:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    lambda: asyncio.new_event_loop().run_until_complete(
                        self.visual_consciousness.imagine(prompt, **kwargs)
                    )
                )
                return future.result(timeout=180)

    def _sync_video_generation(self, prompt: str) -> Dict[str, Any]:
        """Synchronous wrapper for video generation when async is not available."""
        try:

            def _run():
                return asyncio.run(self.video_consciousness.animate(prompt))

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_run)
                return future.result(timeout=300)

        except Exception as e:
            return {"error": str(e)}

    # ------------------------------------------------------------------
    # Error formatting
    # ------------------------------------------------------------------

    @staticmethod
    def _file_capture_error(capture_error: Optional[str], clean_path: str) -> str:
        """Return a user-friendly error message for file-capture failures."""
        if capture_error == "not_found":
            if "/var/folders/" in clean_path and "TemporaryItems" in clean_path:
                return (
                    f"**Ephemeral screenshot expired:** "
                    f"{os.path.basename(clean_path)}\n\n"
                    "**Issue:** macOS screenshots in /var/folders/ disappear "
                    "within 50-100ms\n"
                    "**The file vanished before we could capture it**\n\n"
                    "**Solutions:**\n"
                    "1. **Save screenshot to Desktop first** "
                    "(Cmd+Shift+5 -> Options -> Save to Desktop)\n"
                    "2. **Use clipboard paste** if available\n"
                    "3. **Copy to a permanent location** before drag & drop\n\n"
                    "**Tip:** Desktop screenshots work perfectly with "
                    "drag & drop!"
                )
            return (
                f"**Cannot locate visual input:** {clean_path}\n\n"
                "**Supported formats:**\n"
                "- Local files: /path/to/image.png\n"
                "- URLs: https://example.com/image.jpg\n"
                "- Base64: data:image/png;base64,iVBOR...\n"
                "- Drag-and-drop: Any image file\n\n"
                "**For ephemeral screenshots:** Save to Desktop first, "
                "then drag-and-drop"
            )
        if capture_error == "permission":
            return f"Permission denied reading: {clean_path}"
        return f"Could not read file: {capture_error}"

    def test_image_basic(self, path: str) -> str:
        """Bare minimum image test -- no fancy logic."""
        print(f"Raw input: {path}")

        if path.startswith('"') or path.startswith("'"):
            path = path[1:-1]

        print(f"Cleaned: {path}")
        print(f"Exists: {os.path.exists(path)}")

        if not os.path.exists(path):
            workspace_path = os.path.join(self.config.workspace, path)
            print(f"Trying workspace: {workspace_path}")
            print(f"Workspace exists: {os.path.exists(workspace_path)}")
            if os.path.exists(workspace_path):
                path = workspace_path
            else:
                return "File not found in either location"

        try:
            with open(path, "rb") as fh:
                data = fh.read()
            print(f"Read successful: {len(data)} bytes")

            encoded = base64.b64encode(data).decode("utf-8")
            print(f"Encoding successful: {len(encoded)} chars")

            response = self.claude.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": encoded,
                                },
                            },
                            {"type": "text", "text": "What do you see?"},
                        ],
                    }
                ],
            )

            return f"SUCCESS: {response.content[0].text[:100]}..."

        except Exception as e:
            return f"Error at: {e}"
