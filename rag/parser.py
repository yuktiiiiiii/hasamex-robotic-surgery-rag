from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


TIMESTAMP_PATTERN = re.compile(r"^(\d{2}:\d{2})\s*$")


@dataclass
class TranscriptTurn:
    """One timestamped speaker turn from a transcript."""
    expert: str
    role: str
    market: str
    timestamp: str
    speaker: str
    text: str
    source_file: str

    @property
    def id(self) -> str:
        """Create a stable ID for the turn."""
        safe_timestamp = self.timestamp.replace(":", "_")
        return f"{Path(self.source_file).stem}_{safe_timestamp}"


def parse_header(lines: list[str]) -> tuple[str, str, str]:
    """
    Extract expert name, role, and market from the transcript header.

    Expected format:
        Expert 1 – Dr. Jean Martin
        Role: Head of Urology
        Market: France
    """
    expert = "Unknown Expert"
    role = "Unknown Role"
    market = "Unknown Market"

    for line in lines[:10]:
        line = line.strip()

        if line.startswith("Expert ") and "–" in line:
            expert = line.split("–", 1)[1].strip()

        elif line.lower().startswith("role:"):
            role = line.split(":", 1)[1].strip()

        elif line.lower().startswith("market:"):
            market = line.split(":", 1)[1].strip()

    return expert, role, market


def parse_transcript(file_path: str | Path) -> list[TranscriptTurn]:
    """
    Parse a timestamped transcript into individual speaker turns.

    Each turn contains:
        - expert
        - role
        - market
        - timestamp
        - speaker
        - exact text
        - source file
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Transcript not found: {path}")

    raw_text = path.read_text(encoding="utf-8-sig")
    lines = raw_text.splitlines()

    expert, role, market = parse_header(lines)

    turns: list[TranscriptTurn] = []

    current_timestamp: str | None = None
    current_speaker: str | None = None
    current_text: list[str] = []

    def save_current_turn() -> None:
        nonlocal current_timestamp, current_speaker, current_text

        if (
            current_timestamp is not None
            and current_speaker is not None
            and current_text
        ):
            # Preserve the wording while removing only unnecessary
            # whitespace around the complete turn.
            text = "\n".join(current_text).strip()

            turns.append(
                TranscriptTurn(
                    expert=expert,
                    role=role,
                    market=market,
                    timestamp=current_timestamp,
                    speaker=current_speaker,
                    text=text,
                    source_file=path.name,
                )
            )

        current_timestamp = None
        current_speaker = None
        current_text = []

    for raw_line in lines:
        line = raw_line.rstrip()

        timestamp_match = TIMESTAMP_PATTERN.match(line)

        # New timestamp = previous turn is complete.
        if timestamp_match:
            save_current_turn()
            current_timestamp = timestamp_match.group(1)
            continue

        # Ignore header lines and blank lines before the first timestamp.
        if current_timestamp is None:
            continue

        stripped = line.strip()

        if not stripped:
            # Ignore extra blank lines.
            continue

        # First line after timestamp identifies the speaker.
        if current_speaker is None:
            if ":" in stripped:
                current_speaker, first_text = stripped.split(":", 1)
                current_speaker = current_speaker.strip()
                current_text.append(first_text.lstrip())
            else:
                # Fallback if a speaker label is unexpectedly missing.
                current_speaker = "Unknown Speaker"
                current_text.append(stripped)
        else:
            # Continuation of the same speaker's statement.
            current_text.append(stripped)

    # Save the final turn.
    save_current_turn()

    return turns


def parse_multiple_transcripts(folder: str | Path) -> list[TranscriptTurn]:
    """Parse every .txt transcript inside a folder."""
    folder_path = Path(folder)

    if not folder_path.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    all_turns: list[TranscriptTurn] = []

    for file_path in sorted(folder_path.glob("*.txt")):
        all_turns.extend(parse_transcript(file_path))

    return all_turns