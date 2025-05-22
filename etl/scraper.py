# scraper.py


import os
from urllib.parse import urljoin, urlparse

import bs4
import requests
from bs4.element import Tag
from loguru import logger

from etl.db import Paper

ARXIV_BASE_URL = "https://arxiv.org/"


def scrape_arxiv() -> list[Paper]:
    """
    Main function to scrape arXiv papers.
    """
    logger.info("Starting the scraper")
    scraper = ArxivScraper()

    # Fetch papers from the specified category
    papers = scraper.fetch_papers_by_category(
        category_path="list/cs/recent", max_results=10
    )
    logger.success(f"Fetched {len(papers)} papers")
    return papers


### Decorator for caching HTML responses


def cached_html(func):
    """
    A caching decorator that stores results as plain text in the file system.
    """
    cache_dir = ".cache"
    os.makedirs(cache_dir, exist_ok=True)

    def build_cache_path(url):
        parsed = urlparse(url)
        cachename = f"{parsed.netloc}{parsed.path}".replace("/", "-") + ".html"
        return os.path.join(cache_dir, cachename)

    def wrapper(url):
        cache_path = build_cache_path(url)
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                logger.info(f"Cache hit for {func.__name__} with url: {url}")
                return f.read()

        logger.info(f"Cache miss for {func.__name__} with url: {url}")
        result = func(url)
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(result)
        return result

    return wrapper


### Functions for fetching data from arXiv


@cached_html
def get_page(url: str) -> str:
    """
    Fetches data from the given URL and returns the response as a dictionary.
    """
    logger.info(f"Fetching data from {url}")
    response = requests.get(url)
    if response.status_code == 200:
        logger.info(f"Data fetched successfully from {url}")
        return response.text
    else:
        raise Exception(
            f"Failed to fetch data from {url}. Status code: {response.status_code}"
        )


class ArxivScraper:
    """
    A class to scrape papers from arXiv.
    """

    @classmethod
    def fetch_page_by_path(
        cls,
        path: str = "/",
        url: str = ARXIV_BASE_URL,
    ) -> bs4.BeautifulSoup:
        """
        Fetches the category page of arXiv.
        """
        logger.info(f"Fetching category page for {path}")
        url = urljoin(ARXIV_BASE_URL, path)
        raw_page = get_page(url)
        soup = bs4.BeautifulSoup(raw_page, "html.parser")
        return soup

    @classmethod
    def fetch_papers_by_category(
        cls,
        category_path: str = "list/cs/recent",
        max_results: int = 10,
    ) -> list[Paper]:
        """
        Fetches papers from the specified category.
        """
        soup = cls.fetch_page_by_path(path=category_path)

        papers = []
        for dt, dd in zip(soup.find_all("dt"), soup.find_all("dd")):
            if len(papers) >= max_results:
                break
            if not isinstance(dt, Tag) or not isinstance(dd, Tag):
                continue

            # ID
            link = dt.find("a", title="Abstract")
            if link is None:
                continue
            paper_id = link.text.strip()

            logger.debug(f"Paper ID: {paper_id}")

            # Title
            title_div = dd.find("div", class_="list-title mathjax")
            if title_div is None:
                logger.warning(f"Title not found for paper ID: {paper_id}")
                continue
            title = title_div.text.replace("Title:", "").strip()

            logger.debug(f"Paper title: {title}")

            # Authors
            author_div = dd.find("div", class_="list-authors")

            if author_div is None:
                logger.warning(f"Title not found for paper ID: {paper_id}")
                continue

            authors = author_div.text.replace("Authors:", "").strip()
            logger.debug(f"Paper authors: {authors}")

            # Categories
            category_div = dd.find("div", class_="list-subjects")

            if category_div is None:
                logger.warning(f"Category not found for paper ID: {paper_id}")
                continue
            categories = category_div.text.replace("Subjects:", "").strip()
            categories_list = [cat.strip() for cat in categories.split(";")]

            logger.debug(f"Paper categories: {categories_list}")

            # Abstract
            abstract = cls.fetch_abstract(paper_id)
            logger.debug(f"Paper abstract: {abstract}")

            papers.append(
                Paper(
                    id=paper_id,
                    title=title,
                    authors=authors,
                    categories=categories_list,
                    abstract=abstract,
                ),
            )

        return papers

    @classmethod
    def fetch_abstract(cls, paper_id: str) -> str:
        """
        Fetches the abstract of a paper given its ID.
        """
        abstract_path = f"/abs/{paper_id}"

        logger.info(f"Fetching abstract for {paper_id}")

        soup = cls.fetch_page_by_path(path=abstract_path)

        abstract_div = soup.find("blockquote", class_="abstract mathjax")
        if abstract_div:
            return abstract_div.text.strip()
        else:
            raise Exception(f"Failed to fetch abstract for {paper_id}")


def main():
    logger.info("Starting the scraper")
    scraper = ArxivScraper()

    papers = scraper.fetch_papers_by_category()

    logger.success(f"Fetched {len(papers)} papers")


if __name__ == "__main__":
    main()
