import os

import matplotlib.pyplot as plt
import pandas as pd
from loguru import logger

from etl.db import Paper


def generate_report(papers: list[Paper]) -> None:
    # Convert to DataFrame
    data = []
    for paper in papers:
        for category in paper.categories:
            data.append(
                {
                    "guessed_field": paper.guessed_field,
                    "category": category,
                    "word_count": paper.word_count,
                }
            )
    df = pd.DataFrame(data)

    # Distribution by Field
    field_counts = df["guessed_field"].value_counts()
    logger.info(f"\nDistribution by Field:\n{field_counts.to_string()}")

    # Average Word Count per Field
    field_word_avg = df.groupby("guessed_field")["word_count"].mean().round(1)
    logger.info(f"\nAverage Word Count per Field:\n{field_word_avg.to_string()}")

    # Average Word Count per Category
    cat_word_avg = df.groupby("category")["word_count"].mean().round(1)
    logger.info(
        f"\nAverage Word Count per Category:\n{cat_word_avg.to_string()}",
    )

    # Create directory for saving plots
    os.makedirs("data", exist_ok=True)

    # Plotting
    field_counts.plot(
        kind="bar", figsize=(10, 5), title="Distribution of Research Papers by Field"
    )
    plt.ylabel("Number of Papers")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("data/field_distribution.png")
    plt.close()

    cat_word_avg.plot(
        kind="bar", figsize=(10, 5), title="Average Word Count per Category"
    )
    plt.ylabel("Average Word Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("data/avg_word_count_per_category.png")
    plt.close()
