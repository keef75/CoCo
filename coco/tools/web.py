"""
Web tool provider -- search the web, extract URLs, and crawl domains.

Registers the following tools with the ToolRegistry:
  - search_web
  - extract_urls
  - crawl_domain

All web tools depend on the Tavily API.  When the API key is missing the
tools are registered with ``handler=None`` so they appear as unavailable
rather than crashing at runtime.
"""

from __future__ import annotations

import io
import shutil
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from .registry import ToolDefinition, ToolRegistry

# ---------------------------------------------------------------------------
# JSON schemas
# ---------------------------------------------------------------------------

_SEARCH_WEB_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Search query"},
        "search_depth": {
            "type": "string",
            "enum": ["basic", "advanced"],
            "description": "Search depth - basic (1 credit) or advanced (2 credits)",
        },
        "include_images": {
            "type": "boolean",
            "description": "Include image results in search",
        },
        "max_results": {
            "type": "integer",
            "description": "Maximum number of results (default: 5)",
        },
        "exclude_domains": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of domains to exclude from results",
        },
    },
    "required": ["query"],
}

_EXTRACT_URLS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "urls": {
            "oneOf": [
                {"type": "string", "description": "Single URL to extract"},
                {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of URLs to extract (up to 20)",
                },
            ],
        },
        "extract_to_markdown": {
            "type": "boolean",
            "description": "Save extracted content to markdown file (default: true)",
        },
        "filename": {
            "type": "string",
            "description": "Custom filename for markdown export (optional)",
        },
    },
    "required": ["urls"],
}

_CRAWL_DOMAIN_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "domain_url": {
            "type": "string",
            "description": "Base domain URL to crawl",
        },
        "instructions": {
            "type": "string",
            "description": "Specific instructions for what to find (optional)",
        },
        "max_pages": {
            "type": "integer",
            "description": "Maximum number of pages to crawl (default: 10)",
        },
    },
    "required": ["domain_url"],
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _safe_console_width() -> int:
    try:
        return min(shutil.get_terminal_size().columns - 4, 100)
    except Exception:
        return 76


def _make_temp_console(buf: io.StringIO, width: Optional[int] = None):
    from rich.console import Console

    return Console(file=buf, width=width or _safe_console_width(), legacy_windows=False)


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


class _WebTools:
    """Stateful implementation of web tools."""

    def __init__(
        self,
        tavily_api_key: str,
        anthropic_api_key: str,
        workspace: Path,
        tavily_timeout: int = 30,
    ) -> None:
        self.tavily_api_key = tavily_api_key
        self.anthropic_api_key = anthropic_api_key
        self.workspace = workspace
        self.tavily_timeout = tavily_timeout

    def _get_client(self):
        import tavily

        return tavily.TavilyClient(api_key=self.tavily_api_key)

    # ---- search_web ------------------------------------------------------

    def search_web(
        self,
        query: str,
        search_depth: str = "basic",
        include_images: bool = False,
        max_results: int = 5,
        exclude_domains: Optional[list] = None,
    ) -> str:
        """Search the web with spectacular Rich UI formatting."""
        try:
            from rich import box
            from rich.panel import Panel
            from rich.table import Table
            from rich.tree import Tree

            client = self._get_client()

            search_params: Dict[str, Any] = {
                "query": query,
                "search_depth": search_depth,
                "max_results": max_results,
            }
            if include_images:
                search_params["include_images"] = include_images
            if exclude_domains:
                search_params["exclude_domains"] = exclude_domains

            def _search():
                return client.search(**search_params)

            try:
                with ThreadPoolExecutor() as pool:
                    future = pool.submit(_search)
                    results = future.result(timeout=self.tavily_timeout)
            except FuturesTimeoutError:
                return (
                    f"Web Search Timeout: Search for '{query}' took longer than "
                    f"{self.tavily_timeout} seconds. Try a more specific query."
                )

            buf = io.StringIO()
            console = _make_temp_console(buf)

            search_tree = Tree(
                f"[bold bright_cyan]Search: '{query}'[/]",
                guide_style="bright_blue",
            )
            search_results = results.get("results", [])

            if not search_results:
                search_tree.add("[red]No results found[/]")
            else:
                search_tree.add(
                    f"[dim bright_blue]Found {len(search_results)} results[/]"
                )
                for i, r in enumerate(search_results, 1):
                    title = r.get("title", "Unknown Title")[:80]
                    content = r.get("content", "No content available")[:200]
                    url = r.get("url", "Unknown URL")
                    branch = search_tree.add(f"[bold bright_white]{i}. {title}[/]")
                    for sentence in content.split(". ")[:3]:
                        if sentence.strip():
                            branch.add(f"[white]{sentence.strip()}.[/]")
                    source = branch.add(f"[link={url}]Source[/]")
                    try:
                        domain = urlparse(url).netloc
                        source.add(f"[dim cyan]{domain}[/]")
                    except Exception:
                        source.add(f"[dim cyan]{url[:50]}...[/]")

            summary_table = Table(title="Search Summary", box=box.ROUNDED)
            summary_table.add_column("Metric", style="cyan", no_wrap=True)
            summary_table.add_column("Value", style="bright_white")
            summary_table.add_row("Query", query)
            summary_table.add_row("Results Found", str(len(search_results)))
            summary_table.add_row("Source", "Tavily Web Search")

            console.print(
                Panel(search_tree, title="[bold bright_cyan]Search Results[/]",
                      border_style="bright_cyan", padding=(1, 2))
            )
            console.print(
                Panel(summary_table, title="[bold bright_magenta]Search Metrics[/]",
                      border_style="bright_magenta", padding=(1, 2))
            )

            return buf.getvalue()

        except Exception as e:
            return f"Error searching: {e}"

    # ---- extract_urls ----------------------------------------------------

    def extract_urls(
        self,
        urls: Any,
        extract_to_markdown: bool = True,
        filename: Optional[str] = None,
    ) -> str:
        """Extract content from specific URLs."""
        try:
            from rich import box
            from rich.panel import Panel
            from rich.table import Table
            from rich.tree import Tree

            if isinstance(urls, str):
                urls = [urls]

            client = self._get_client()
            results = client.extract(urls=urls, extract_depth="advanced")

            buf = io.StringIO()
            console = _make_temp_console(buf)

            tree = Tree(
                "[bold bright_magenta]URL Extraction Results[/]",
                guide_style="bright_magenta",
            )
            extraction_results = results.get("results", [])
            failed_results = results.get("failed_results", [])

            markdown_content: List[str] = []
            if extract_to_markdown:
                markdown_content.append("# URL Extraction Results")
                markdown_content.append(
                    f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
                )

            if not extraction_results and not failed_results:
                tree.add("[red]No content extracted[/]")
            else:
                tree.add(
                    f"[dim bright_magenta]Extracted {len(extraction_results)} URLs, "
                    f"{len(failed_results)} failed[/]"
                )
                for i, result in enumerate(extraction_results, 1):
                    url = result.get("url", "Unknown URL")
                    raw = result.get("raw_content", "No content available")
                    preview = raw[:300] + ("..." if len(raw) > 300 else "")
                    branch = tree.add(f"[bold bright_white]{i}. {url}[/]")
                    for line in preview.split("\n")[:5]:
                        if line.strip():
                            branch.add(f"[white]{line.strip()}[/]")
                    wc = len(raw.split())
                    branch.add(f"[dim cyan]{wc} words extracted[/]")
                    if extract_to_markdown:
                        markdown_content.append(f"## {url}")
                        markdown_content.append(f"*Word count: {wc} words*\n")
                        markdown_content.append(raw)
                        markdown_content.append("\n---\n")

                if failed_results:
                    fail_branch = tree.add("[red]Failed Extractions[/]")
                    for failed in failed_results:
                        fail_branch.add(f"[red]{failed.get('url', 'Unknown URL')}[/]")

            summary = Table(title="Extraction Summary", box=box.ROUNDED)
            summary.add_column("Metric", style="magenta", no_wrap=True)
            summary.add_column("Value", style="bright_white")
            summary.add_row("URLs Requested", str(len(urls)))
            summary.add_row("Successfully Extracted", str(len(extraction_results)))
            summary.add_row("Failed", str(len(failed_results)))

            md_path = None
            if extract_to_markdown and markdown_content:
                if not filename:
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"extracted_content_{ts}.md"
                md_path = self.workspace / filename
                try:
                    md_path.write_text("\n".join(markdown_content), encoding="utf-8")
                    summary.add_row("Markdown File", filename)
                except Exception as exc:
                    summary.add_row("Markdown File", f"Error: {exc}")

            console.print(
                Panel(tree, title="[bold bright_magenta]Extraction Results[/]",
                      border_style="bright_magenta", padding=(1, 2))
            )
            console.print(
                Panel(summary, title="[bold bright_cyan]Extraction Metrics[/]",
                      border_style="bright_cyan", padding=(1, 2))
            )

            if md_path and md_path.exists():
                console.print(
                    Panel(
                        f"[bright_green]Content saved to:[/] [cyan]{md_path.absolute()}[/]",
                        title="[bold bright_green]Markdown Export[/]",
                        border_style="bright_green",
                    )
                )

            return buf.getvalue()

        except Exception as e:
            return f"Error extracting URLs: {e}"

    # ---- crawl_domain ----------------------------------------------------

    def crawl_domain(
        self,
        domain_url: str,
        instructions: Optional[str] = None,
        max_pages: int = 10,
    ) -> str:
        """Crawl and map a website domain."""
        try:
            from rich import box
            from rich.panel import Panel
            from rich.table import Table
            from rich.tree import Tree

            client = self._get_client()
            crawl_params: Dict[str, Any] = {"url": domain_url}
            if instructions:
                crawl_params["instructions"] = instructions

            results = client.crawl(**crawl_params)

            buf = io.StringIO()
            console = _make_temp_console(buf)

            try:
                parsed_domain = urlparse(domain_url).netloc or domain_url
            except Exception:
                parsed_domain = domain_url

            tree = Tree(
                f"[bold bright_yellow]Domain Crawl: '{parsed_domain}'[/]",
                guide_style="bright_yellow",
            )
            crawl_results = results.get("results", [])
            base_url = results.get("base_url", parsed_domain)

            if not crawl_results:
                tree.add("[red]No pages found[/]")
            else:
                tree.add(
                    f"[dim bright_yellow]Discovered {len(crawl_results)} pages[/]"
                )
                for i, page in enumerate(crawl_results, 1):
                    url = page.get("url", "Unknown URL")
                    raw = page.get("raw_content", "No content available")
                    preview = raw[:200] + ("..." if len(raw) > 200 else "")
                    branch = tree.add(f"[bold bright_white]{i}. {url}[/]")
                    for line in preview.split("\n")[:3]:
                        if line.strip():
                            branch.add(f"[white]{line.strip()}[/]")
                    wc = len(raw.split())
                    branch.add(f"[dim cyan]{wc} words[/]")

            summary = Table(title="Crawl Summary", box=box.ROUNDED)
            summary.add_column("Metric", style="yellow", no_wrap=True)
            summary.add_column("Value", style="bright_white")
            summary.add_row("Base Domain", base_url)
            summary.add_row("Pages Discovered", str(len(crawl_results)))
            summary.add_row("Instructions", instructions or "None")

            console.print(
                Panel(tree, title="[bold bright_yellow]Crawl Results[/]",
                      border_style="bright_yellow", padding=(1, 2))
            )
            console.print(
                Panel(summary, title="[bold bright_cyan]Crawl Metrics[/]",
                      border_style="bright_cyan", padding=(1, 2))
            )

            return buf.getvalue()

        except Exception as e:
            return f"Error crawling domain: {e}"


# ---------------------------------------------------------------------------
# Provider registration function
# ---------------------------------------------------------------------------


def register(
    registry: ToolRegistry,
    config: Any,
    dependencies: Dict[str, Any],
) -> None:
    """Register web tools with the central registry.

    Parameters
    ----------
    registry:
        The ``ToolRegistry`` instance.
    config:
        Application configuration.  Uses ``tavily_api_key`` and
        ``anthropic_api_key`` attributes.
    dependencies:
        Dict of shared dependencies.  Expected keys:

        - ``"workspace"`` -- ``Path`` to CoCo's workspace directory
    """
    tavily_key = getattr(config, "tavily_api_key", None) or ""
    anthropic_key = getattr(config, "anthropic_api_key", None) or ""
    workspace: Path = dependencies.get("workspace", Path.cwd() / "coco_workspace")
    tavily_timeout: int = getattr(config, "tavily_timeout", 30)

    # Check if tavily is importable *and* configured
    tavily_available = False
    if tavily_key:
        try:
            import tavily  # noqa: F401

            tavily_available = True
        except ImportError:
            pass

    if tavily_available:
        tools = _WebTools(tavily_key, anthropic_key, workspace, tavily_timeout)
        search_handler = tools.search_web
        extract_handler = tools.extract_urls
        crawl_handler = tools.crawl_domain
    else:
        search_handler = None
        extract_handler = None
        crawl_handler = None

    registry.register(ToolDefinition(
        name="search_web",
        description=(
            "Search the web through extended awareness - reach into the knowledge "
            "web with advanced options"
        ),
        input_schema=_SEARCH_WEB_SCHEMA,
        handler=search_handler,
        category="web",
    ))

    registry.register(ToolDefinition(
        name="extract_urls",
        description=(
            "Focus digital perception on specific URLs to extract their complete content"
        ),
        input_schema=_EXTRACT_URLS_SCHEMA,
        handler=extract_handler,
        category="web",
    ))

    registry.register(ToolDefinition(
        name="crawl_domain",
        description=(
            "Explore entire digital territories by crawling and mapping website domains"
        ),
        input_schema=_CRAWL_DOMAIN_SCHEMA,
        handler=crawl_handler,
        category="web",
    ))
