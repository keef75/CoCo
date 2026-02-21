"""
Filesystem tool provider -- read, write, navigate, search, and explore files.

Registers the following tools with the ToolRegistry:
  - read_file
  - write_file
  - navigate_directory
  - search_patterns
  - explore_directory

These tools operate within CoCo's workspace and deployment directories.
They use Rich UI for beautiful terminal output.
"""

from __future__ import annotations

import io
import os
import re
import shutil
import stat
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .registry import ToolDefinition, ToolRegistry

# ---------------------------------------------------------------------------
# JSON schemas (Part 1 of the old three-part system)
# ---------------------------------------------------------------------------

_READ_FILE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "path": {"type": "string", "description": "File path to read"},
    },
    "required": ["path"],
}

_WRITE_FILE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "path": {"type": "string", "description": "File path to write"},
        "content": {"type": "string", "description": "Content to write to the file"},
    },
    "required": ["path", "content"],
}

_NAVIGATE_DIRECTORY_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "Directory path to explore (default: current directory)",
            "default": ".",
        },
    },
    "required": [],
}

_SEARCH_PATTERNS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "pattern": {
            "type": "string",
            "description": "Pattern or text to search for (supports regex)",
        },
        "path": {
            "type": "string",
            "description": "Directory to search in (default: workspace)",
            "default": "workspace",
        },
        "file_type": {
            "type": "string",
            "description": "File extension filter (e.g., 'py', 'js', 'md')",
            "default": "",
        },
    },
    "required": ["pattern"],
}

_EXPLORE_DIRECTORY_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "Directory path to explore (default: current directory)",
            "default": ".",
        },
    },
    "required": [],
}

# ---------------------------------------------------------------------------
# Internal helpers (Rich UI formatting)
# ---------------------------------------------------------------------------


def _safe_console_width() -> int:
    """Return a safe terminal width for Rich console output."""
    try:
        return min(shutil.get_terminal_size().columns - 4, 120)
    except Exception:
        return 76


def _make_temp_console(buf: io.StringIO, width: Optional[int] = None):
    """Create a Rich Console that writes to *buf*."""
    from rich.console import Console

    return Console(file=buf, width=width or _safe_console_width())


# ---------------------------------------------------------------------------
# Tool implementations (Part 2 of the old three-part system)
# ---------------------------------------------------------------------------


class _FilesystemTools:
    """Stateful implementation of filesystem tools.

    Holds references to *workspace* (Path) and *deployment_dir* (Path)
    which are injected at registration time.
    """

    def __init__(self, workspace: Path, deployment_dir: Path, config: Any = None) -> None:
        self.workspace = workspace
        self.deployment_dir = deployment_dir
        self.config = config

    # ---- read_file -------------------------------------------------------

    def read_file(self, path: str) -> str:
        """Read a file through digital eyes with spectacular Rich UI display."""
        try:
            from rich import box
            from rich.columns import Columns
            from rich.panel import Panel
            from rich.syntax import Syntax
            from rich.table import Table
            from rich.text import Text
            from rich.tree import Tree

            search_locations = [
                ("workspace", self.workspace / path),
                ("deployment directory", self.deployment_dir / path),
                ("current directory", Path(path).absolute()),
                ("relative to cwd", Path.cwd() / path),
            ]

            for location_name, file_path in search_locations:
                if file_path.exists() and file_path.is_file():
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        return self._spectacular_file_display(
                            file_path, content, location_name, path
                        )
                    except UnicodeDecodeError:
                        return self._binary_file_display(file_path, location_name, path)

            return self._file_not_found_display(path, search_locations)

        except Exception as e:
            return f"Error reading {path}: {e}"

    # ---- write_file ------------------------------------------------------

    def write_file(self, path: str, content: str) -> str:
        """Write/create a file through digital hands."""
        try:
            file_path = self.workspace / path

            critical_files = [
                "COCO.md",
                "USER_PROFILE.md",
                "PREFERENCES.md",
                "previous_conversation.md",
            ]
            if Path(path).name in critical_files:
                if Path(path).parent != Path("."):
                    file_path = self.workspace / Path(path).name

            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            if os.getenv("COCO_DEBUG") or Path(path).name in critical_files:
                print(f"Wrote {len(content):,} characters to: {file_path.absolute()}")

            return (
                f"Successfully manifested {len(content)} characters to {path}\n"
                f"Full path: {file_path.absolute()}"
            )

        except Exception as e:
            error_msg = f"Error writing {path}: {e}"
            print(error_msg)
            return error_msg

    # ---- navigate_directory ----------------------------------------------

    def navigate_directory(self, path: str = ".") -> str:
        """Navigate through digital space -- extend spatial awareness through filesystem."""
        try:
            from rich import box
            from rich.panel import Panel
            from rich.table import Table
            from rich.text import Text

            buf = io.StringIO()
            console = _make_temp_console(buf)

            nav_path = self._resolve_nav_path(path)
            if isinstance(nav_path, str):
                return nav_path  # error message

            items = self._gather_directory_items(nav_path)
            if isinstance(items, str):
                return items  # error message

            items.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))

            table = Table(
                box=box.ROUNDED, show_header=True, header_style="bold bright_blue"
            )
            table.add_column("", justify="left", width=3, no_wrap=True)
            table.add_column("Name", justify="left", min_width=20)
            table.add_column("Type", justify="center", width=10)
            table.add_column("Size", justify="right", width=8)
            table.add_column("Modified", justify="center", width=16)

            for item in items:
                table.add_row(
                    item["icon"],
                    item["name"],
                    item["type"].capitalize(),
                    item["size"],
                    item["modified"],
                )

            console.print(
                Panel(
                    table,
                    title=f"[bold bright_blue]Navigation: {nav_path}[/]",
                    title_align="left",
                    border_style="bright_blue",
                )
            )

            dir_count = sum(1 for i in items if i["type"] == "directory")
            file_count = sum(1 for i in items if i["type"] == "file")
            summary = Text()
            summary.append(
                f"Discovered: {dir_count} directories, {file_count} files",
                style="bright_white",
            )
            console.print(summary)

            return buf.getvalue()

        except Exception as e:
            return f"Navigation error: {e}"

    # ---- search_patterns -------------------------------------------------

    def search_patterns(
        self, pattern: str, path: str = "workspace", file_type: str = ""
    ) -> str:
        """Cast pattern recognition through files -- search for code patterns and text."""
        try:
            from rich import box
            from rich.panel import Panel
            from rich.table import Table
            from rich.tree import Tree

            buf = io.StringIO()
            console = _make_temp_console(buf)

            search_path = self._resolve_search_path(path)
            if isinstance(search_path, str):
                return search_path

            try:
                regex_pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                literal_pattern = None
            except re.error:
                regex_pattern = None
                literal_pattern = pattern.lower()

            matches: List = []
            files_searched = 0
            skip_suffixes = {
                ".pyc", ".pyo", ".db", ".sqlite", ".sqlite3",
                ".jpg", ".png", ".gif", ".mp3", ".mp4",
            }

            for file_path in search_path.rglob("*"):
                if not file_path.is_file():
                    continue
                if file_type and file_path.suffix.lstrip(".").lower() != file_type.lower():
                    continue
                if file_path.suffix in skip_suffixes:
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.read().splitlines()
                    files_searched += 1
                    file_matches = []
                    for line_num, line in enumerate(lines, 1):
                        if regex_pattern:
                            if regex_pattern.search(line):
                                file_matches.append((line_num, line.strip()))
                        elif literal_pattern and literal_pattern in line.lower():
                            file_matches.append((line_num, line.strip()))
                    if file_matches:
                        matches.append((file_path, file_matches))
                except (UnicodeDecodeError, PermissionError):
                    continue

            search_tree = Tree(
                "[bold bright_cyan]Pattern Search Results[/]",
                guide_style="bright_cyan",
            )
            if not matches:
                search_tree.add(f"[yellow]No matches found for pattern: '{pattern}'[/]")
                search_tree.add(f"[dim]Searched {files_searched} files in {search_path}[/]")
            else:
                total_hits = sum(len(fm) for _, fm in matches)
                search_tree.add(
                    f"[dim bright_cyan]Found {total_hits} matches in {len(matches)} files[/]"
                )
                for fp, fm in matches[:10]:
                    try:
                        rel = fp.relative_to(search_path)
                    except ValueError:
                        rel = fp
                    branch = search_tree.add(f"[bold bright_white]{rel}[/]")
                    for ln, lc in fm[:5]:
                        preview = lc[:80] + ("..." if len(lc) > 80 else "")
                        branch.add(f"[cyan]Line {ln}:[/] [white]{preview}[/]")
                    if len(fm) > 5:
                        branch.add(f"[dim]... and {len(fm) - 5} more matches[/]")
                if len(matches) > 10:
                    search_tree.add(
                        f"[dim yellow]... and {len(matches) - 10} more files with matches[/]"
                    )

            summary = Table(title="Search Summary", box=box.ROUNDED)
            summary.add_column("Metric", style="cyan", no_wrap=True)
            summary.add_column("Value", style="bright_white")
            summary.add_row("Pattern", f"'{pattern}'")
            summary.add_row("Files Searched", str(files_searched))
            summary.add_row("Files with Matches", str(len(matches)))
            summary.add_row(
                "Total Line Matches",
                str(sum(len(fm) for _, fm in matches)),
            )
            if file_type:
                summary.add_row("File Filter", f"*.{file_type}")

            console.print(
                Panel(search_tree, title="[bold bright_cyan]Search Results[/]",
                      border_style="bright_cyan", padding=(1, 2))
            )
            console.print(
                Panel(summary, title="[bold bright_green]Search Metrics[/]",
                      border_style="bright_green", padding=(1, 2))
            )

            return buf.getvalue()

        except Exception as e:
            return f"Pattern search error: {e}"

    # ---- explore_directory -----------------------------------------------

    def explore_directory(self, path: str = ".") -> str:
        """Explore and list directory contents in a simple Markdown view."""
        try:
            target_dir, location = self._resolve_explore_path(path)
            if isinstance(target_dir, str):
                return target_dir

            items = list(target_dir.iterdir())
            directories = [
                i for i in items if i.is_dir() and not i.name.startswith(".")
            ]
            files = [
                i
                for i in items
                if i.is_file() and (not i.name.startswith(".") or i.name == ".env")
            ]

            parts = [f"Exploring {location}: `{target_dir}`\n"]
            if directories:
                parts.append("## Directories")
                for d in sorted(directories):
                    try:
                        count = len(list(d.iterdir()))
                        parts.append(f"- **{d.name}/** ({count} items)")
                    except Exception:
                        parts.append(f"- **{d.name}/** (? items)")
                parts.append("")
            if files:
                parts.append("## Files")
                for f in sorted(files):
                    size = f.stat().st_size
                    if size < 1024:
                        sz = f"{size}B"
                    elif size < 1024 * 1024:
                        sz = f"{size // 1024}KB"
                    else:
                        sz = f"{size // (1024 * 1024)}MB"
                    parts.append(f"- `{f.name}` ({sz})")

            if not directories and not files:
                parts.append("*Directory is empty*")

            return "\n".join(parts)

        except PermissionError:
            return f"Permission denied accessing directory: `{path}`"
        except Exception as e:
            return f"Error exploring directory: {e}"

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _resolve_nav_path(self, path: str) -> Any:
        if path.lower() in ("workspace", "coco_workspace"):
            nav = self.workspace
        elif path == ".":
            nav = self.deployment_dir
        else:
            nav = Path(path)
            if not nav.is_absolute():
                nav = self.workspace / path
        if not nav.exists():
            return f"Path not found: {nav}"
        if not nav.is_dir():
            return f"Not a directory: {nav}"
        return nav

    def _resolve_search_path(self, path: str) -> Any:
        if path.lower() in ("workspace", "coco_workspace"):
            sp = self.workspace
        elif path == ".":
            sp = self.deployment_dir
        else:
            sp = Path(path)
            if not sp.is_absolute():
                sp = self.workspace / path
        if not sp.exists():
            return f"Search path not found: {sp}"
        return sp

    def _resolve_explore_path(self, path: str):
        if path in (".", ""):
            return self.deployment_dir, "deployment directory"
        if path.lower() in ("workspace", "coco_workspace"):
            return self.workspace, "workspace"
        if path.startswith("./"):
            target = self.deployment_dir / path[2:]
            return target, "deployment directory"
        target = self.deployment_dir / path
        if not target.exists():
            target = self.workspace / path
            loc = "workspace"
        else:
            loc = "deployment directory"
        if not target.exists():
            return (
                f"Directory not found: `{path}`\n\n"
                f"**Available locations:**\n"
                f"- Deployment: `{self.deployment_dir}`\n"
                f"- Workspace: `{self.workspace}`"
            ), None
        if not target.is_dir():
            return f"Not a directory: `{path}` is a file.", None
        return target, loc

    def _gather_directory_items(self, nav_path: Path) -> Any:
        items = []
        icon_map = {
            ".py": "Py", ".js": "JS", ".md": "MD", ".txt": "TX",
            ".json": "CF", ".yml": "CF", ".yaml": "CF",
            ".png": "IM", ".jpg": "IM", ".jpeg": "IM", ".gif": "IM",
            ".mp3": "AU", ".wav": "AU", ".mp4": "VD", ".avi": "VD",
            ".db": "DB", ".sql": "DB", ".env": "EN",
        }
        try:
            for item in nav_path.iterdir():
                try:
                    item_stat = item.stat()
                    modified = datetime.fromtimestamp(item_stat.st_mtime).strftime(
                        "%Y-%m-%d %H:%M"
                    )
                    if item.is_dir():
                        items.append({
                            "name": item.name,
                            "type": "directory",
                            "size": "-",
                            "modified": modified,
                            "icon": "DIR",
                        })
                    elif item.is_file():
                        size = item_stat.st_size
                        if size < 1024:
                            sz = f"{size}B"
                        elif size < 1024 * 1024:
                            sz = f"{size // 1024}KB"
                        else:
                            sz = f"{size // (1024 * 1024)}MB"
                        suffix = item.suffix.lower()
                        icon = icon_map.get(suffix, "FL")
                        items.append({
                            "name": item.name,
                            "type": "file",
                            "size": sz,
                            "modified": modified,
                            "icon": icon,
                        })
                except (OSError, PermissionError):
                    continue
        except PermissionError:
            return f"Permission denied: Cannot access {nav_path}"
        return items

    def _spectacular_file_display(
        self, file_path: Path, content: str, location_name: str, original_path: str
    ) -> str:
        from rich import box
        from rich.columns import Columns
        from rich.panel import Panel
        from rich.syntax import Syntax
        from rich.table import Table
        from rich.text import Text
        from rich.tree import Tree

        buf = io.StringIO()
        console = _make_temp_console(buf)

        file_stats = file_path.stat()
        file_size = file_stats.st_size
        lines_count = len(content.splitlines())
        file_extension = file_path.suffix.lower()

        syntax_map = {
            ".py": "python", ".js": "javascript", ".ts": "typescript",
            ".html": "html", ".css": "css", ".json": "json",
            ".md": "markdown", ".yaml": "yaml", ".yml": "yaml",
            ".xml": "xml", ".sql": "sql", ".sh": "bash",
            ".txt": "text", ".log": "text", ".env": "bash",
        }
        language = syntax_map.get(file_extension, "text")

        info_table = Table(title="File Information", box=box.ROUNDED)
        info_table.add_column("Property", style="cyan", no_wrap=True)
        info_table.add_column("Value", style="bright_white")
        info_table.add_row("File Name", file_path.name)
        info_table.add_row("Location", location_name)
        info_table.add_row("Full Path", str(file_path))
        info_table.add_row("Size", f"{file_size:,} bytes")
        info_table.add_row("Lines", str(lines_count))

        console.print(
            Panel(info_table, title="[bold bright_magenta]File Metadata[/]",
                  border_style="bright_magenta")
        )

        if len(content) > 10000:
            display_content = (
                content[:5000]
                + "\n\n... [FILE TRUNCATED - showing first 5000 characters] ...\n\n"
                + content[-2000:]
            )
            truncated = True
        else:
            display_content = content
            truncated = False

        try:
            syntax_content = Syntax(
                display_content, language, theme="monokai",
                line_numbers=True, word_wrap=True,
            )
        except Exception:
            syntax_content = Text(display_content)

        title = f"[bold bright_cyan]{file_path.name} Contents[/]"
        if truncated:
            title += " [dim yellow](truncated)[/]"
        console.print(
            Panel(syntax_content, title=title, border_style="bright_cyan", padding=(1, 2))
        )

        return buf.getvalue()

    def _binary_file_display(
        self, file_path: Path, location_name: str, original_path: str
    ) -> str:
        from rich import box
        from rich.panel import Panel
        from rich.table import Table

        buf = io.StringIO()
        console = _make_temp_console(buf)
        size = file_path.stat().st_size

        table = Table(title="Binary File Information", box=box.ROUNDED)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="bright_white")
        table.add_row("File Name", file_path.name)
        table.add_row("Location", location_name)
        table.add_row("Size", f"{size:,} bytes ({size / 1024:.1f} KB)")
        table.add_row("Type", "Binary File")

        console.print(
            Panel(table, title="[bold red]Cannot Display Binary Content[/]",
                  border_style="red")
        )
        return buf.getvalue()

    def _file_not_found_display(self, path: str, search_locations: list) -> str:
        from rich import box
        from rich.panel import Panel
        from rich.table import Table

        buf = io.StringIO()
        console = _make_temp_console(buf)

        table = Table(title=f"Searched Locations for '{path}'", box=box.ROUNDED)
        table.add_column("Location Type", style="cyan")
        table.add_column("Path Searched", style="white")
        table.add_column("Status", style="red")
        for name, fp in search_locations:
            table.add_row(name.title(), str(fp), "Not Found")

        console.print(
            Panel(table, title="[bold red]File Not Found[/]", border_style="red")
        )
        return buf.getvalue()


# ---------------------------------------------------------------------------
# Provider registration function
# ---------------------------------------------------------------------------


def register(
    registry: ToolRegistry,
    config: Any,
    dependencies: Dict[str, Any],
) -> None:
    """Register filesystem tools with the central registry.

    Parameters
    ----------
    registry:
        The ``ToolRegistry`` instance.
    config:
        Application configuration (provides ``workspace``, etc.).
    dependencies:
        Dict of shared dependencies.  Expected keys:

        - ``"workspace"`` -- ``Path`` to CoCo's workspace directory
        - ``"deployment_dir"`` -- ``Path`` to the deployment (source) directory
    """
    workspace: Path = dependencies.get("workspace", Path.cwd() / "coco_workspace")
    deployment_dir: Path = dependencies.get("deployment_dir", Path.cwd())

    tools = _FilesystemTools(workspace, deployment_dir, config)

    registry.register(ToolDefinition(
        name="read_file",
        description="Read a file through digital eyes - perceive file contents",
        input_schema=_READ_FILE_SCHEMA,
        handler=tools.read_file,
        category="filesystem",
    ))

    registry.register(ToolDefinition(
        name="write_file",
        description="Write/create a file through digital hands - manifest content into reality",
        input_schema=_WRITE_FILE_SCHEMA,
        handler=tools.write_file,
        category="filesystem",
    ))

    registry.register(ToolDefinition(
        name="navigate_directory",
        description="Navigate through digital space - extend spatial awareness through filesystem",
        input_schema=_NAVIGATE_DIRECTORY_SCHEMA,
        handler=tools.navigate_directory,
        category="filesystem",
    ))

    registry.register(ToolDefinition(
        name="search_patterns",
        description="Cast pattern recognition through files - search for code patterns and text",
        input_schema=_SEARCH_PATTERNS_SCHEMA,
        handler=tools.search_patterns,
        category="filesystem",
    ))

    registry.register(ToolDefinition(
        name="explore_directory",
        description="Explore and list directory contents in a readable view",
        input_schema=_EXPLORE_DIRECTORY_SCHEMA,
        handler=tools.explore_directory,
        category="filesystem",
    ))
