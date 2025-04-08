This repo is a book recommend system: you can find interesting books by describe your wished ones.

All the dependencies is placed in `requirements.txt` file.

The repo consists of five components that have to be run **in order**:

- Scrape data from goodreads site (see `scrape_data.py`).
- Text data cleaning and data downloading (see `data-exploration.ipynb`).
- Build vector database from the dataset that user can get suggestion from (see `vector-search.ipynb`).
- Classify books to 'fiction' or 'non-fiction' category by using Huggingface's zero-shot classification (see `text-classification.ipynb`). This allows user to filter the recommendations.
- Analysis books based on the tone of descriptions (see `sentiment-analysis.ipynb`). This can help user to sort books by the tone.
- Create a web application using `gradio` for user to get recommendations (see `gradio-dashboard.py`).
