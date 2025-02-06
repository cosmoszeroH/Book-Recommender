This repo is a book recommend system that would suggest books from ```https://www.kaggle.com/datasets/dylanjcastillo/7k-books-with-metadata```.

Below is the dependencies to run the code:

```
pip install kagglehub
pip install pandas
pip install matplotlib
pip install seaborn
pip install langchain-community
pip install langchain-huggingface
pip install langchain-chroma
pip install transformers
pip install gradio
```

The repo consists of five components that have to be run **in order**:
- Text data cleaning and data downloading (see ```data-exploration.ipynb```).
- Build vector database from the dataset that user can get suggestion from (see ```vector-search.ipynb```).
- Classify books to 'fiction' or 'non-fiction' category by using Huggingface's zero-shot classification (see ```text-classification.ipynb```). This allows user to filter the recommendations.
- Analysis books based on the tone of descriptions (see ```sentiment-analysis.ipynb```). This can help user to sort books by the tone.
- Create a web application using ```gradio``` for user to get recommendations (see ```gradio-dashboard.py```).
