"""
Shared prompts and MiniLM RAG helpers for API batch baselines
(Claude / OpenAI) and local LLM eval.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

SYSTEM_PROMPT = (
    "You are an expert at writing agent instruction files for software "
    "repositories (AGENTS.md, CLAUDE.md, copilot-instructions.md, SKILL.md). "
    "Output only the Markdown instruction file. Use ## headings, bullet lists, "
    "and code blocks where appropriate. Do not add commentary outside the file."
)

# Per-example char budget for RAG few-shots. Generic-intent outputs are short
# bullet files (typical ~1–3k, rarely >5k); 8000 fits a full file so later ##
# sections are not dropped by blunt head-truncation.
DEFAULT_RAG_EXAMPLE_CHARS = 8000

_H2_RE = re.compile(r"^##\s+.+$", re.MULTILINE)


def load_json(path):
    with open(path) as f:
        return json.load(f)


def strip_task_prefix(text: str) -> str:
    prefix = "generate agent instructions: "
    return text[len(prefix) :] if text.startswith(prefix) else text


def _split_md_h2_sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Split markdown into preamble + (## heading line, body) pairs."""
    matches = list(_H2_RE.finditer(text))
    if not matches:
        return text, []
    preamble = text[: matches[0].start()]
    sections: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        heading = m.group(0).rstrip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip("\n")
        sections.append((heading, body))
    return preamble, sections


def _drop_last_line(body: str) -> str:
    lines = body.rstrip("\n").split("\n")
    if len(lines) <= 1:
        return ""
    return "\n".join(lines[:-1]).rstrip()


def format_instruction_for_rag(text: str, max_chars: int = DEFAULT_RAG_EXAMPLE_CHARS) -> str:
    """Format an instruction file for RAG few-shot display.

    Preserves **all** ``##`` section headings. Prefers full section bodies
    (generic-intent outputs are usually short bullets). When ``max_chars`` is
    exceeded, distributes the budget across sections — keep every heading,
    trim bullet lines per section — instead of truncating the whole file from
    the start (which hid later sections).

    Args:
        text: Full instruction markdown (e.g. ``pair["output"]``).
        max_chars: Per-example character budget. Default
            ``DEFAULT_RAG_EXAMPLE_CHARS`` (8000) is sized so typical
            ``generic_output`` files fit in full.
    """
    text = text or ""
    if max_chars <= 0:
        return ""
    if len(text) <= max_chars:
        return text

    preamble, sections = _split_md_h2_sections(text)
    if not sections:
        marker = "\n\n[example truncated]"
        keep = max(0, max_chars - len(marker))
        return text[:keep].rstrip() + marker

    pre = preamble.strip()
    bodies = [b for _, b in sections]
    headings = [h for h, _ in sections]

    def render() -> str:
        parts: list[str] = []
        if pre:
            parts.append(pre)
        for h, b in zip(headings, bodies):
            b = (b or "").strip("\n")
            parts.append(f"{h}\n\n{b}" if b else h)
        return "\n\n".join(parts)

    # Shrink longest bodies (drop trailing lines/bullets) until under budget.
    # Never remove a ## heading.
    while len(render()) > max_chars:
        lengths = [len(b or "") for b in bodies]
        if any(lengths):
            idx = max(range(len(bodies)), key=lambda i: lengths[i])
            bodies[idx] = _drop_last_line(bodies[idx])
            continue
        if pre:
            pre = _drop_last_line(pre)
            if not pre.strip():
                pre = ""
            continue
        # Headings alone still over budget: return all headings packed tightly.
        packed = "\n".join(headings)
        return packed if len(packed) <= max_chars else packed[:max_chars]

    out = render()
    # Mark sections that lost body lines vs the original.
    trimmed_any = any(
        (bodies[i] or "").strip() != (sections[i][1] or "").strip()
        for i in range(len(sections))
    )
    if trimmed_any and not out.rstrip().endswith("…"):
        # Annotate only if we still have a little room; otherwise leave as-is.
        note = "\n\n[section bodies trimmed to fit budget]"
        if len(out) + len(note) <= max_chars:
            out = out + note
    return out


def build_zero_shot_user_prompt(instruction: str) -> str:
    return (
        "Write the instruction file described below.\n\n"
        f"{strip_task_prefix(instruction)}\n\n"
        "Instruction file:"
    )


def build_rag_user_prompt(
    instruction: str,
    retrieved: list,
    example_chars: int = DEFAULT_RAG_EXAMPLE_CHARS,
) -> str:
    """Build a RAG few-shot user prompt.

    Args:
        instruction: Target pair input (may include task prefix).
        retrieved: List of similar train pairs with ``output`` / metadata.
        example_chars: Per-example budget for formatting each retrieved
            instruction file (default ``DEFAULT_RAG_EXAMPLE_CHARS`` = 8000).
            Uses section-aware formatting so all ``##`` headings are kept.
    """
    examples = []
    for i, ex in enumerate(retrieved, 1):
        formatted = format_instruction_for_rag(ex["output"], max_chars=example_chars)
        examples.append(
            f"### Example {i} ({ex['format']}, {ex['language']})\n"
            f"Request:\n{strip_task_prefix(ex['input'])}\n\n"
            f"Instruction file:\n{formatted}"
        )
    example_block = "\n\n".join(examples)
    return (
        "Here are similar instruction files from other repositories:\n\n"
        f"{example_block}\n\n"
        "Now write a new instruction file for this request:\n\n"
        f"{strip_task_prefix(instruction)}\n\n"
        "Instruction file:"
    )


class RagIndex:
    def __init__(
        self,
        train_pairs,
        embed_model_name: str = "all-MiniLM-L6-v2",
        exclude_same_repo: bool = True,
    ):
        self.pairs = train_pairs
        self.exclude_same_repo = exclude_same_repo
        self.embedder = SentenceTransformer(embed_model_name)
        inputs = [p["input"] for p in train_pairs]
        self.embeddings = self.embedder.encode(
            inputs,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        self.repo_names = [p["repo"] for p in train_pairs]

    def retrieve(self, query: str, query_repo=None, top_k: int = 3):
        q_emb = self.embedder.encode(
            [query], convert_to_numpy=True, normalize_embeddings=True
        )[0]
        sims = self.embeddings @ q_emb
        ranked = np.argsort(-sims)
        results = []
        for idx in ranked:
            if (
                self.exclude_same_repo
                and query_repo
                and self.repo_names[idx] == query_repo
            ):
                continue
            results.append(self.pairs[int(idx)])
            if len(results) >= top_k:
                break
        return results


def save_retrieval_cache(path: Path, cache: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(cache, f)


def load_retrieval_cache(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)
