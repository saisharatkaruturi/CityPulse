"""Provider-neutral category classification.

`KeywordClassifier` is deterministic and always available; it is the default and the fallback.
`MockLLMClassifier` stands in for an external model in demos/tests and is labelled simulated.
Any provider output is validated against the configured category codes before use, and the
caller treats it as an untrusted suggestion (see app/services/intelligence.py).
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CategoryOption:
    code: str
    label: str
    synonyms: tuple[str, ...]


@dataclass(frozen=True)
class Suggestion:
    category_code: str
    confidence: float


@dataclass(frozen=True)
class ClassificationResult:
    provider: str
    model_version: str
    suggestions: list[Suggestion]
    simulated: bool = False


class ProviderError(Exception):
    pass


class Classifier(Protocol):
    name: str

    def classify(self, text: str, options: list[CategoryOption]) -> ClassificationResult: ...


def normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text).casefold()


def _word_char(ch: str) -> bool:
    # `\w` alone drops combining marks, which splits Telugu (and other Indic) words into single letters:
    # vowel signs and the anusvara are category M*, so they must count as part of a word.
    return ch.isalnum() or ch in "_'" or unicodedata.category(ch).startswith("M")


def tokens(text: str) -> set[str]:
    out: set[str] = set()
    word: list[str] = []
    for ch in normalize(text) + " ":
        if _word_char(ch):
            word.append(ch)
        elif word:
            out.add("".join(word))
            word = []
    return out


class KeywordClassifier:
    """Scores categories by synonym/label phrase matches. Deterministic."""

    name = "keyword"
    version = "keyword-v1"

    def classify(self, text: str, options: list[CategoryOption]) -> ClassificationResult:
        norm = normalize(text)
        toks = tokens(text)
        scored: list[Suggestion] = []
        for opt in options:
            phrases = {normalize(p) for p in (opt.label, *opt.synonyms) if p}
            hits = 0
            for phrase in phrases:
                if " " in phrase:
                    hits += 2 if phrase in norm else 0
                elif phrase in toks:
                    hits += 1
            if hits:
                scored.append(Suggestion(opt.code, hits))
        total = sum(s.confidence for s in scored)
        if not total:
            return ClassificationResult(self.name, self.version, [])
        best = max(s.confidence for s in scored)
        # Confidence reflects both the share of evidence and its absolute strength, so a lone
        # weak keyword (or an evenly split match) stays below a sensible threshold.
        results = [Suggestion(s.category_code,
                              round(min(1.0, (s.confidence / total) * min(1.0, best / 2)), 3))
                   for s in scored]
        results.sort(key=lambda s: (-s.confidence, s.category_code))
        return ClassificationResult(self.name, self.version, results[:3])


class MockLLMClassifier:
    """SIMULATED external model. Delegates to keyword matching but behaves like a remote provider.

    `failure_mode` lets tests exercise timeout / malformed-output handling.
    """

    name = "mock-llm"
    version = "simulated-0"

    def __init__(self, failure_mode: str | None = None) -> None:
        self.failure_mode = failure_mode

    def classify(self, text: str, options: list[CategoryOption]) -> ClassificationResult:
        if self.failure_mode == "timeout":
            raise ProviderError("provider timeout")
        if self.failure_mode == "malformed":
            return ClassificationResult(self.name, self.version,
                                        [Suggestion("not-a-real-category", 0.99)], simulated=True)
        inner = KeywordClassifier().classify(text, options)
        return ClassificationResult(self.name, self.version, inner.suggestions, simulated=True)


class DisabledClassifier:
    name = "disabled"
    version = "none"

    def classify(self, text: str, options: list[CategoryOption]) -> ClassificationResult:
        return ClassificationResult(self.name, self.version, [])


def build_classifier(kind: str) -> Classifier:
    if kind == "mock":
        return MockLLMClassifier()
    if kind == "disabled":
        return DisabledClassifier()
    return KeywordClassifier()
