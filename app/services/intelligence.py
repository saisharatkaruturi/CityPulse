"""Category suggestion and natural-language service search.

AI output is advisory. Suggestions are validated against active category codes, low-confidence
results go to manual review, and any provider failure falls back to deterministic keyword
matching. Only the minimum text (the resident's description) is passed to a provider.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.classifier import (
    CategoryOption,
    ClassificationResult,
    Classifier,
    KeywordClassifier,
    ProviderError,
    build_classifier,
    normalize,
    tokens,
)
from app.core.config import get_settings
from app.core.time import utcnow
from app.domain.enums import PublicationState
from app.models import AiClassification, Category, Service

logger = logging.getLogger("app.intelligence")

MAX_CLASSIFY_CHARS = 2000

_classifier_override: Classifier | None = None


def set_classifier(classifier: Classifier | None) -> None:
    """Test hook / runtime override."""
    global _classifier_override
    _classifier_override = classifier


def get_classifier() -> Classifier:
    return _classifier_override or build_classifier(get_settings().ai_provider)


@dataclass(frozen=True)
class CategorySuggestion:
    category: Category
    confidence: float


@dataclass(frozen=True)
class SuggestionOutcome:
    best: CategorySuggestion | None
    alternatives: list[CategorySuggestion]
    accepted: bool
    provider: str
    model_version: str
    simulated: bool


def _options(categories: list[Category]) -> list[CategoryOption]:
    return [CategoryOption(c.code, c.label, tuple(c.synonyms or []) + tuple((c.labels_i18n or {}).values()))
            for c in categories]


def suggest_category(db: Session, text: str) -> SuggestionOutcome:
    settings = get_settings()
    categories = list(db.scalars(select(Category).where(Category.is_active.is_(True),
                                                        Category.is_triage.is_(False))).all())
    by_code = {c.code: c for c in categories}
    text = text[:MAX_CLASSIFY_CHARS]
    classifier = get_classifier()
    try:
        result: ClassificationResult = classifier.classify(text, _options(categories))
    except ProviderError as exc:
        logger.warning("classifier_failed_fallback", extra={"provider": classifier.name, "error": str(exc)})
        result = KeywordClassifier().classify(text, _options(categories))
    except Exception:  # unexpected provider bug must not break complaint intake
        logger.exception("classifier_crashed_fallback", extra={"provider": classifier.name})
        result = KeywordClassifier().classify(text, _options(categories))

    valid: list[CategorySuggestion] = []
    for s in result.suggestions:
        cat = by_code.get(s.category_code)
        conf = s.confidence if isinstance(s.confidence, int | float) else 0.0
        if cat is None or not 0 <= conf <= 1:
            logger.info("classifier_output_rejected", extra={"provider": result.provider})
            continue
        valid.append(CategorySuggestion(cat, float(conf)))
    best = valid[0] if valid else None
    accepted = best is not None and best.confidence >= settings.ai_confidence_threshold
    return SuggestionOutcome(best, valid[1:], accepted, result.provider, result.model_version,
                             result.simulated)


def record_classification(db: Session, outcome: SuggestionOutcome, complaint_id: uuid.UUID | None,
                          text: str, final_category_id: uuid.UUID | None) -> AiClassification:
    row = AiClassification(
        complaint_id=complaint_id,
        query_hash=hashlib.sha256(text.encode()).hexdigest() if complaint_id is None else None,
        provider=outcome.provider, model_version=outcome.model_version,
        suggested_category_id=outcome.best.category.id if outcome.best else None,
        confidence=outcome.best.confidence if outcome.best else 0.0,
        accepted=outcome.accepted, final_category_id=final_category_id, created_at=utcnow(),
    )
    db.add(row)
    return row


@dataclass(frozen=True)
class ServiceMatch:
    service: Service
    score: float
    matched_on: list[str]
    matched_category: Category | None = None


# Ranking weights. The kind of problem is the strongest signal: a service that handles the category the
# description most likely belongs to should come first, ahead of services that merely share a word.
W_BEST_CATEGORY = 6.0
W_ALT_CATEGORY = 2.0
W_NAME_PHRASE = 3.0
W_NAME_TERM = 1.5
W_SYNONYM = 2.0
W_DESCRIPTION_TERM = 0.5


def search_services(db: Session, query: str | None, category_id: uuid.UUID | None,
                    service_type: str | None, limit: int) -> list[ServiceMatch]:
    """Deterministic ranking over published/unavailable services. No machine learning is involved.

    Signals, strongest first: the service handles the category the query is most likely about (keyword
    classification over category labels, synonyms and translations); the query appears in the service name;
    service synonyms; words in the summary/instructions. Ties break on name, then code, so order is stable.
    """
    q = select(Service).where(Service.state.in_([PublicationState.published, PublicationState.unavailable]))
    if service_type:
        q = q.where(Service.service_type == service_type)
    services = list(db.scalars(q).all())
    if category_id is not None:
        services = [s for s in services if any(c.id == category_id or c.parent_id == category_id
                                               for c in s.categories)]
    if not query:
        return [ServiceMatch(s, 1.0, ["browse"]) for s in sorted(services, key=lambda s: (s.name, s.code))][:limit]

    qnorm = normalize(query)
    qtok = tokens(query) - _STOPWORDS
    suggested = suggest_category(db, query)
    best_cat = suggested.best.category if suggested.best else None
    alt_ids = {s.category.id for s in suggested.alternatives}

    matches: list[ServiceMatch] = []
    for s in services:
        score = 0.0
        why: list[str] = []
        matched_cat: Category | None = None
        cat_ids = {c.id for c in s.categories}
        if best_cat is not None and best_cat.id in cat_ids:
            score += W_BEST_CATEGORY * (0.5 + suggested.best.confidence / 2)  # type: ignore[union-attr]
            why.append("category")
            matched_cat = best_cat
        elif alt_ids & cat_ids:
            score += W_ALT_CATEGORY
            why.append("related_category")
            matched_cat = next(a.category for a in suggested.alternatives if a.category.id in cat_ids)
        name = normalize(s.name)
        if qnorm and qnorm in name:
            score += W_NAME_PHRASE
            why.append("name")
        elif qtok & tokens(s.name):
            score += W_NAME_TERM * len(qtok & tokens(s.name))
            why.append("name_terms")
        syn_hits = [syn for syn in (s.synonyms or []) if normalize(syn) in qnorm or tokens(syn) & qtok]
        if syn_hits:
            score += W_SYNONYM * len(syn_hits)
            why.append("synonyms")
        summary_hits = qtok & tokens(s.summary + " " + (s.instructions or ""))
        if summary_hits:
            score += W_DESCRIPTION_TERM * len(summary_hits)
            why.append("description")
        if score > 0:
            matches.append(ServiceMatch(s, round(score, 2), why, matched_cat))
    matches.sort(key=lambda m: (-m.score, m.service.name, m.service.code))
    return matches[:limit]


_STOPWORDS = {"the", "a", "an", "is", "in", "on", "of", "my", "to", "and", "or", "for", "not", "near", "at",
              "i", "it", "there", "this", "with", "how", "do", "can", "where", "what"}
