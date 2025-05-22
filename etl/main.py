"""
Main entry point for the ETL pipeline.
This script orchestrates the entire ETL process, including scraping, translating,
and analyzing papers.
"""

from etl import analytics, processor, scraper, translator, db


def etl_pipeline():
    """
    Main function to run the ETL pipeline.
    """
    # Step 1: Extract
    papers = scraper.scrape_arxiv()

    # Step 2: Transform
    papers = translator.translate_abstracts(papers)
    processor.analyze_papers(papers)

    # Step 3: Load
    db.insert_papers(papers)

    # Step 4: Generate Report
    analytics.generate_report(papers)


if __name__ == "__main__":
    etl_pipeline()
