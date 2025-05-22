import re
from collections import Counter
from typing import Optional

from loguru import logger

from etl.db import Paper

_RESEARCH_FIELDS = {
    "machine learning": [
        "learning",
        "neural",
        "deep",
        "representation",
        "model",
        "training",
    ],
    "natural language processing": [
        "language",
        "text",
        "translation",
        "linguistic",
        "bert",
        "gpt",
    ],
    "computer vision": [
        "image",
        "vision",
        "video",
        "object",
        "segmentation",
        "detection",
    ],
    "robotics": ["robot", "navigation", "control", "sensor", "manipulation"],
    "theory": ["proof", "theorem", "complexity", "algorithm", "approximation"],
    "physics": ["quantum", "relativity", "particle", "spin", "cosmology"],
    "biology": ["protein", "gene", "cell", "biological", "genome"],
    "mathematics": ["algebra", "topology", "geometry", "combinatorics", "analysis"],
}


def _guess_field(text: str) -> Optional[str]:
    text = text.lower()
    word_counts = Counter(re.findall(r"\w+", text))

    best_field = None
    best_score = 0
    for field, keywords in _RESEARCH_FIELDS.items():
        score = sum(word_counts[word] for word in keywords)
        if score > best_score:
            best_field = field
            best_score = score

    return best_field


def analyze_paper(paper: Paper) -> Paper:
    logger.info(f"Analyzing paper: {paper.id}")
    if paper.abstract:
        paper.word_count = len(re.findall(r"\w+", paper.abstract))
        if paper.abstract_uk:
            paper.word_count_uk = len(re.findall(r"\w+", paper.abstract_uk))
        paper.guessed_field = _guess_field(paper.abstract)

        logger.debug(
            f"Guessed field for {paper.id}: {paper.guessed_field} "
            f"(word count: {paper.word_count})"
        )

    logger.info(f"Analyzed and updated paper: {paper.id}")
    return paper


def analyze_papers(papers: list[Paper]) -> list[Paper]:
    for paper in papers:
        analyze_paper(paper)

    logger.success(f"Analyzed {len(papers)} papers.")
    return papers
