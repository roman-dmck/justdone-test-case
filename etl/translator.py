import os
import re

from loguru import logger
from openai import OpenAI

from etl.db import Paper

client = OpenAI()


def cached(func):
    """
    A caching decorator that stores results as plain text in the file system.
    """
    cache_dir = ".cache/translator"
    os.makedirs(cache_dir, exist_ok=True)

    def build_cache_path(text):
        cachename = f"{text[:15]}.txt"
        return os.path.join(cache_dir, cachename)

    def wrapper(text):
        cache_path = build_cache_path(text)
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                logger.info(f"Cache hit for {cache_path}")
                return f.read()

        logger.info(f"Cache miss for {cache_path}")
        result = func(text)
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(result)
        return result

    return wrapper


def clean_latex(text: str) -> str:
    return re.sub(r"\\(?:textit|emph|textbf)\{([^}]+)\}", r"\1", text)


@cached
def translate(text: str) -> str | None:
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful translator that translates English to Ukrainian.",
            },
            {
                "role": "user",
                "content": f"Translate the following abstract to Ukrainian:\n\n{text}",
            },
        ],
        temperature=0.3,
    )
    translated = response.choices[0].message.content
    if translated:
        return clean_latex(translated)


def translate_abstracts(papers: list[Paper]) -> list[Paper]:
    for paper in papers:
        translated = translate(paper.abstract)
        logger.debug(f"Translated abstract for {paper.id}: {translated}")
        paper.abstract_uk = translated
    logger.success(
        f"Translated {len(papers)} abstracts to Ukrainian and saved to cache."
    )
    return papers
