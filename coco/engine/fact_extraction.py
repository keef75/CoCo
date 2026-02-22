"""
Universal tool fact extraction system for COCO.

Every tool execution can produce persistent *facts* that survive after the
conversation buffer is cleared.  This lets the user ask questions like
"Who did I email last week?" or "What documents did I create yesterday?"
and receive perfect recall.

Architecture
------------
- ``FactExtractionMixin`` is mixed into ``ConsciousnessEngine`` via
  multiple inheritance.
- The router ``_extract_tool_facts()`` maps tool names to dedicated
  extractors.
- Most tools produce *dual extraction* (two facts); calendar events
  produce *triple extraction* (three facts).

Fact types used
---------------
communication, tool_use, note, file, appointment, contact, location, command

Extracted from ``cocoa.py`` lines ~8668-9352 (Oct 2025 universal tool facts).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from coco.config.settings import Config


class FactExtractionMixin:
    """Mixin that adds universal tool-fact extraction to ConsciousnessEngine.

    Expects the host class to expose:

    - ``self.config`` -- a ``Config`` instance (uses ``.debug``)
    - ``self.memory`` -- a ``HierarchicalMemorySystem`` (uses ``.facts_memory``)
    - ``self.console`` -- a Rich console
    """

    # ------------------------------------------------------------------
    # Router
    # ------------------------------------------------------------------

    def _extract_tool_facts(
        self,
        tool_name: str,
        tool_input: dict,
        tool_result: str,
        episode_id: int,
    ) -> int:
        """Universal tool fact extraction router.

        Extracts structured facts from tool executions to maintain perfect
        recall of communications, documents, research, meetings, and
        content generation.

        Returns the number of facts successfully stored.
        """
        # Skip when the tool execution failed
        if not tool_result:
            return 0

        result_lower = str(tool_result).lower()
        error_indicators = [
            "error", "failed", "could not", "unable to",
            "exception", "invalid", "denied",
        ]
        if any(indicator in result_lower for indicator in error_indicators):
            return 0

        extractors = {
            "send_email":              self._extract_email_facts,
            "create_document":         self._extract_document_facts,
            "create_spreadsheet":      self._extract_spreadsheet_facts,
            "generate_image":          self._extract_image_facts,
            "generate_video":          self._extract_video_facts,
            "write_file":              self._extract_file_facts,
            "search_web":              self._extract_search_facts,
            "add_calendar_event":      self._extract_calendar_facts,
            "create_calendar_event":   self._extract_calendar_facts,
            "upload_file":             self._extract_upload_facts,
            "download_file":           self._extract_download_facts,
            "create_folder":           self._extract_folder_facts,
            "read_document":           self._extract_read_document_facts,
            "analyze_document":        self._extract_analyze_document_facts,
            "execute_bash":            self._extract_bash_facts,
            # Twitter consciousness extractors
            "post_tweet":              self._extract_tweet_facts,
            "get_twitter_mentions":    self._extract_mention_facts,
            "reply_to_tweet":          self._extract_reply_facts,
            "create_twitter_thread":   self._extract_thread_facts,
        }

        extractor = extractors.get(tool_name)
        if extractor:
            try:
                return extractor(tool_input, tool_result, episode_id)
            except Exception as e:
                if self.config.debug:
                    self.console.print(
                        f"[dim yellow]Fact extraction failed for {tool_name}: {e}[/dim yellow]"
                    )
                return 0

        return 0

    # ------------------------------------------------------------------
    # Per-tool extractors
    # ------------------------------------------------------------------

    def _extract_email_facts(self, tool_input: dict, tool_result: str, episode_id: int) -> int:
        """Extract TWO facts from email sending: recipient + subject."""
        recipient = tool_input.get("to", "")
        subject = tool_input.get("subject", "")

        facts: List[Dict[str, Any]] = []

        if recipient:
            facts.append({
                "type": "communication",
                "content": f"Email sent to {recipient}",
                "context": f"Subject: {subject[:100] if subject else 'N/A'}",
                "importance": 0.9,
                "metadata": {"tool": "send_email", "direction": "outbound"},
            })

        if subject:
            facts.append({
                "type": "communication",
                "content": subject,
                "context": f"Email subject sent to {recipient}",
                "importance": 0.7,
                "metadata": {"tool": "send_email", "content_type": "subject"},
            })

        return self._store_facts(facts, episode_id)

    def _extract_document_facts(self, tool_input: dict, tool_result: str, episode_id: int) -> int:
        """Extract TWO facts from document creation: title + topic/purpose."""
        title = tool_input.get("title", "")
        content = tool_input.get("initial_content", "")

        facts: List[Dict[str, Any]] = []

        if title:
            facts.append({
                "type": "tool_use",
                "content": f"Created document: {title}",
                "context": f"Content preview: {content[:100] if content else 'empty'}",
                "importance": 0.8,
                "metadata": {"tool": "create_document", "document_type": "google_doc"},
            })

        if content:
            first_sentence = re.split(r"[.!?]", content.strip())[0][:100]
            if first_sentence:
                facts.append({
                    "type": "note",
                    "content": first_sentence,
                    "context": f"From document: {title}",
                    "importance": 0.7,
                    "metadata": {"tool": "create_document", "content_type": "topic"},
                })

        return self._store_facts(facts, episode_id)

    def _extract_spreadsheet_facts(self, tool_input: dict, tool_result: str, episode_id: int) -> int:
        """Extract TWO facts from spreadsheet creation: title + purpose."""
        title = tool_input.get("title", "")
        headers = tool_input.get("headers", [])

        facts: List[Dict[str, Any]] = []

        if title:
            facts.append({
                "type": "tool_use",
                "content": f"Created spreadsheet: {title}",
                "context": f"Headers: {', '.join(headers[:5]) if headers else 'none'}",
                "importance": 0.8,
                "metadata": {"tool": "create_spreadsheet", "document_type": "google_sheet"},
            })

        if headers:
            purpose = f"Data tracking: {', '.join(headers[:3])}"
            facts.append({
                "type": "note",
                "content": purpose,
                "context": f"From spreadsheet: {title}",
                "importance": 0.7,
                "metadata": {"tool": "create_spreadsheet", "content_type": "purpose"},
            })

        return self._store_facts(facts, episode_id)

    def _extract_image_facts(self, tool_input: dict, tool_result: str, episode_id: int) -> int:
        """Extract TWO facts from image generation: prompt + subject/concept."""
        prompt = tool_input.get("prompt", "")

        facts: List[Dict[str, Any]] = []

        if prompt:
            facts.append({
                "type": "tool_use",
                "content": f"Generated image: {prompt[:80]}",
                "context": f"Full prompt: {prompt}",
                "importance": 0.6,
                "metadata": {"tool": "generate_image", "content_type": "visual"},
            })

            subject = " ".join(prompt.split()[:6])
            facts.append({
                "type": "note",
                "content": f"Visual concept: {subject}",
                "context": "Image generation prompt",
                "importance": 0.5,
                "metadata": {"tool": "generate_image", "content_type": "subject"},
            })

        return self._store_facts(facts, episode_id)

    def _extract_video_facts(self, tool_input: dict, tool_result: str, episode_id: int) -> int:
        """Extract TWO facts from video generation: prompt + subject/concept."""
        prompt = tool_input.get("prompt", "")

        facts: List[Dict[str, Any]] = []

        if prompt:
            facts.append({
                "type": "tool_use",
                "content": f"Generated video: {prompt[:80]}",
                "context": f"Full prompt: {prompt}",
                "importance": 0.6,
                "metadata": {"tool": "generate_video", "content_type": "visual"},
            })

            subject = " ".join(prompt.split()[:6])
            facts.append({
                "type": "note",
                "content": f"Video concept: {subject}",
                "context": "Video generation prompt",
                "importance": 0.5,
                "metadata": {"tool": "generate_video", "content_type": "subject"},
            })

        return self._store_facts(facts, episode_id)

    def _extract_file_facts(self, tool_input: dict, tool_result: str, episode_id: int) -> int:
        """Extract TWO facts from file creation: filename + directory/purpose."""
        filepath = tool_input.get("file_path", "")
        content = tool_input.get("content", "")

        facts: List[Dict[str, Any]] = []
        filename = ""

        if filepath:
            filename = Path(filepath).name
            directory = Path(filepath).parent.name

            facts.append({
                "type": "file",
                "content": f"Created file: {filename}",
                "context": f"Directory: {directory}",
                "importance": 0.7,
                "metadata": {"tool": "write_file", "file_path": str(filepath)},
            })

        if content:
            first_line = content.split("\n")[0][:80]
            if first_line:
                facts.append({
                    "type": "note",
                    "content": f"File content: {first_line}",
                    "context": f"From file: {filename}",
                    "importance": 0.6,
                    "metadata": {"tool": "write_file", "content_type": "preview"},
                })

        return self._store_facts(facts, episode_id)

    def _extract_search_facts(self, tool_input: dict, tool_result: str, episode_id: int) -> int:
        """Extract TWO facts from web search: query + topic domain."""
        query = tool_input.get("query", "")

        facts: List[Dict[str, Any]] = []

        if query:
            facts.append({
                "type": "tool_use",
                "content": f"Web search: {query}",
                "context": "Research query",
                "importance": 0.6,
                "metadata": {"tool": "search_web", "query_type": "research"},
            })

            topic = " ".join(query.split()[:4])
            facts.append({
                "type": "note",
                "content": f"Research topic: {topic}",
                "context": "Web search query",
                "importance": 0.5,
                "metadata": {"tool": "search_web", "content_type": "topic"},
            })

        return self._store_facts(facts, episode_id)

    def _extract_calendar_facts(self, tool_input: dict, tool_result: str, episode_id: int) -> int:
        """Extract THREE facts from calendar event: title + attendees + time/location."""
        title = tool_input.get("summary", "") or tool_input.get("title", "")
        attendees = tool_input.get("attendees", [])
        location = tool_input.get("location", "")
        start_time = tool_input.get("start_time", "") or tool_input.get("start", "")

        facts: List[Dict[str, Any]] = []

        if title:
            facts.append({
                "type": "appointment",
                "content": f"Meeting: {title}",
                "context": f"Time: {start_time}, Location: {location or 'not specified'}",
                "importance": 0.8,
                "metadata": {"tool": "calendar_event", "event_type": "meeting"},
            })

        if attendees:
            attendee_list = ", ".join(
                [a if isinstance(a, str) else a.get("email", "") for a in attendees[:5]]
            )
            facts.append({
                "type": "contact",
                "content": f"Meeting attendees: {attendee_list}",
                "context": f"Event: {title}",
                "importance": 0.7,
                "metadata": {"tool": "calendar_event", "content_type": "attendees"},
            })

        if start_time or location:
            time_location = f"Time: {start_time}" if start_time else ""
            if location:
                time_location += f", Location: {location}"

            facts.append({
                "type": "appointment",
                "content": time_location,
                "context": f"Event: {title}",
                "importance": 0.7,
                "metadata": {"tool": "calendar_event", "content_type": "logistics"},
            })

        return self._store_facts(facts, episode_id)

    def _extract_upload_facts(self, tool_input: dict, tool_result: str, episode_id: int) -> int:
        """Extract TWO facts from file upload: filename + destination."""
        filepath = tool_input.get("file_path", "")
        folder_id = tool_input.get("folder_id", "")

        facts: List[Dict[str, Any]] = []
        filename = ""

        if filepath:
            filename = Path(filepath).name
            facts.append({
                "type": "file",
                "content": f"Uploaded file: {filename}",
                "context": f"To Google Drive folder: {folder_id or 'root'}",
                "importance": 0.7,
                "metadata": {"tool": "upload_file", "operation": "upload"},
            })

        if folder_id:
            facts.append({
                "type": "location",
                "content": f"Drive folder: {folder_id}",
                "context": f"Uploaded: {filename}",
                "importance": 0.6,
                "metadata": {"tool": "upload_file", "content_type": "destination"},
            })

        return self._store_facts(facts, episode_id)

    def _extract_download_facts(self, tool_input: dict, tool_result: str, episode_id: int) -> int:
        """Extract TWO facts from file download: filename + source."""
        file_id = tool_input.get("file_id", "")
        destination = tool_input.get("destination_path", "")

        facts: List[Dict[str, Any]] = []
        filename = ""

        if file_id:
            filename = Path(destination).name if destination else file_id
            facts.append({
                "type": "file",
                "content": f"Downloaded file: {filename}",
                "context": f"From Google Drive: {file_id}",
                "importance": 0.6,
                "metadata": {"tool": "download_file", "operation": "download"},
            })

        if destination:
            facts.append({
                "type": "location",
                "content": f"Saved to: {destination}",
                "context": f"Downloaded: {filename}",
                "importance": 0.5,
                "metadata": {"tool": "download_file", "content_type": "destination"},
            })

        return self._store_facts(facts, episode_id)

    def _extract_folder_facts(self, tool_input: dict, tool_result: str, episode_id: int) -> int:
        """Extract TWO facts from folder creation: folder name + parent location."""
        folder_name = tool_input.get("folder_name", "")
        parent_id = tool_input.get("parent_id", "")

        facts: List[Dict[str, Any]] = []

        if folder_name:
            facts.append({
                "type": "file",
                "content": f"Created folder: {folder_name}",
                "context": f"Parent: {parent_id or 'root folder'}",
                "importance": 0.7,
                "metadata": {"tool": "create_folder", "operation": "create"},
            })

        if parent_id:
            facts.append({
                "type": "location",
                "content": f"Location: Drive folder {parent_id}",
                "context": f"Contains: {folder_name}",
                "importance": 0.6,
                "metadata": {"tool": "create_folder", "content_type": "location"},
            })

        return self._store_facts(facts, episode_id)

    def _extract_read_document_facts(self, tool_input: dict, tool_result: str, episode_id: int) -> int:
        """Extract TWO facts from document reading: title + key topics."""
        doc_id = tool_input.get("doc_id", "")
        title = tool_input.get("title", "")

        facts: List[Dict[str, Any]] = []

        if not title and tool_result:
            title_match = re.search(
                r"(?:document|file)[:\s]+([^\n]+)", tool_result, re.IGNORECASE
            )
            if title_match:
                title = title_match.group(1).strip()[:100]

        if title or doc_id:
            content = f"Read document: {title}" if title else f"Read document ID: {doc_id}"
            facts.append({
                "type": "note",
                "content": content,
                "context": "Document reference",
                "importance": 0.6,
                "metadata": {"tool": "read_document", "operation": "read"},
            })

        if tool_result and len(tool_result) > 100:
            first_sentences = re.split(r"[.!?]", tool_result.strip())[:2]
            topic = ". ".join(s.strip() for s in first_sentences if s.strip())[:100]
            if topic:
                facts.append({
                    "type": "note",
                    "content": f"Document topic: {topic}",
                    "context": f"From: {title or doc_id}",
                    "importance": 0.5,
                    "metadata": {"tool": "read_document", "content_type": "topic"},
                })

        return self._store_facts(facts, episode_id)

    def _extract_analyze_document_facts(self, tool_input: dict, tool_result: str, episode_id: int) -> int:
        """Extract TWO facts from document analysis: document + findings."""
        doc_id = tool_input.get("doc_id", "")
        analysis_type = tool_input.get("analysis_type", "general")

        facts: List[Dict[str, Any]] = []

        if doc_id:
            facts.append({
                "type": "note",
                "content": f"Analyzed document: {doc_id}",
                "context": f"Analysis type: {analysis_type}",
                "importance": 0.7,
                "metadata": {"tool": "analyze_document", "analysis_type": analysis_type},
            })

        if tool_result and len(tool_result) > 50:
            findings = tool_result.strip()[:150]
            facts.append({
                "type": "note",
                "content": f"Analysis finding: {findings}",
                "context": f"Document: {doc_id}",
                "importance": 0.6,
                "metadata": {"tool": "analyze_document", "content_type": "findings"},
            })

        return self._store_facts(facts, episode_id)

    def _extract_bash_facts(self, tool_input: dict, tool_result: str, episode_id: int) -> int:
        """Extract TWO facts from bash execution: command + purpose/operation."""
        command = tool_input.get("command", "")

        facts: List[Dict[str, Any]] = []

        if command:
            command_preview = command[:80] if len(command) <= 80 else command[:77] + "..."
            facts.append({
                "type": "command",
                "content": f"Executed: {command_preview}",
                "context": "Bash command",
                "importance": 0.5,
                "metadata": {"tool": "execute_bash", "command_type": "shell"},
            })

            operation = "unknown"
            cmd_lower = command.lower()
            if any(kw in cmd_lower for kw in ["git", "clone", "pull", "push", "commit"]):
                operation = "version control"
            elif any(kw in cmd_lower for kw in ["docker", "container", "image"]):
                operation = "container management"
            elif any(kw in cmd_lower for kw in ["npm", "pip", "install", "yarn"]):
                operation = "dependency management"
            elif any(kw in cmd_lower for kw in ["test", "pytest", "jest"]):
                operation = "testing"
            elif any(kw in cmd_lower for kw in ["build", "compile", "make"]):
                operation = "build"
            elif any(kw in cmd_lower for kw in ["deploy", "release"]):
                operation = "deployment"

            if operation != "unknown":
                facts.append({
                    "type": "note",
                    "content": f"Operation: {operation}",
                    "context": "Via bash command",
                    "importance": 0.4,
                    "metadata": {"tool": "execute_bash", "content_type": "operation"},
                })

        return self._store_facts(facts, episode_id)

    # ------------------------------------------------------------------
    # Twitter consciousness fact extractors
    # ------------------------------------------------------------------

    def _extract_tweet_facts(self, tool_input: dict, tool_result: str, episode_id: int) -> int:
        """Extract facts from tweet posting: content + hashtags/topics."""
        text = tool_input.get("text", "")

        facts: List[Dict[str, Any]] = []

        if text:
            hashtags = re.findall(r"#(\w+)", text)
            content_preview = text[:100] if len(text) <= 100 else text[:97] + "..."

            facts.append({
                "type": "communication",
                "content": f"Posted tweet: {content_preview}",
                "context": (
                    f"Public Twitter post"
                    f"{' with hashtags: ' + ', '.join(hashtags) if hashtags else ''}"
                ),
                "importance": 0.8,
                "metadata": {"tool": "post_tweet", "platform": "twitter", "direction": "outbound"},
            })

            if hashtags:
                facts.append({
                    "type": "note",
                    "content": f"Twitter topics: {', '.join(hashtags[:5])}",
                    "context": "Tweet hashtags",
                    "importance": 0.6,
                    "metadata": {"tool": "post_tweet", "content_type": "hashtags"},
                })

        return self._store_facts(facts, episode_id)

    def _extract_mention_facts(self, tool_input: dict, tool_result: str, episode_id: int) -> int:
        """Extract facts from Twitter mentions check."""
        since_hours = tool_input.get("since_hours", 24)

        facts: List[Dict[str, Any]] = []

        mention_matches = re.findall(r"(\d+) mention", tool_result.lower())

        if mention_matches:
            mention_count = int(mention_matches[0])
            if mention_count > 0:
                facts.append({
                    "type": "communication",
                    "content": f"Checked Twitter mentions: {mention_count} found",
                    "context": f"Last {since_hours} hours",
                    "importance": 0.7,
                    "metadata": {
                        "tool": "get_twitter_mentions",
                        "platform": "twitter",
                        "direction": "inbound",
                    },
                })

        return self._store_facts(facts, episode_id)

    def _extract_reply_facts(self, tool_input: dict, tool_result: str, episode_id: int) -> int:
        """Extract facts from Twitter reply: recipient + conversation."""
        tweet_id = tool_input.get("tweet_id", "")
        text = tool_input.get("text", "")

        facts: List[Dict[str, Any]] = []

        if tweet_id and text:
            content_preview = text[:80] if len(text) <= 80 else text[:77] + "..."
            facts.append({
                "type": "communication",
                "content": f"Replied to tweet: {content_preview}",
                "context": f"Twitter conversation (tweet_id: {tweet_id[:10]}...)",
                "importance": 0.8,
                "metadata": {
                    "tool": "reply_to_tweet",
                    "platform": "twitter",
                    "direction": "outbound",
                },
            })

        return self._store_facts(facts, episode_id)

    def _extract_thread_facts(self, tool_input: dict, tool_result: str, episode_id: int) -> int:
        """Extract facts from Twitter thread creation: topic + thread length."""
        tweets = tool_input.get("tweets", [])

        facts: List[Dict[str, Any]] = []

        if tweets and len(tweets) > 0:
            first_tweet = tweets[0][:100] if len(tweets[0]) <= 100 else tweets[0][:97] + "..."
            thread_length = len(tweets)

            facts.append({
                "type": "communication",
                "content": f"Posted Twitter thread ({thread_length} tweets): {first_tweet}",
                "context": f"Thread starting with: {first_tweet}",
                "importance": 0.9,
                "metadata": {
                    "tool": "create_twitter_thread",
                    "platform": "twitter",
                    "thread_length": thread_length,
                },
            })

        return self._store_facts(facts, episode_id)

    # ------------------------------------------------------------------
    # Shared storage helper
    # ------------------------------------------------------------------

    def _store_facts(self, facts: List[Dict], episode_id: int) -> int:
        """Persist facts to FactsMemory if available.

        Returns the number of facts successfully stored.
        """
        if not facts:
            return 0

        if hasattr(self.memory, "facts_memory") and self.memory.facts_memory:
            try:
                stored_count = self.memory.facts_memory.store_facts(
                    facts, episode_id=episode_id
                )

                if self.config.debug:
                    self.console.print(
                        f"[dim cyan]Stored {stored_count} facts from tool execution[/dim cyan]"
                    )

                return stored_count
            except Exception as e:
                if self.config.debug:
                    self.console.print(
                        f"[dim yellow]Fact storage failed: {e}[/dim yellow]"
                    )

        return 0
