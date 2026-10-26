# Mini Search Engine

A small search engine built from scratch in Python, to learn how Google-style search works. Built entirely on an Android phone using Termux.

## What it does
- **Crawler** (`crawl2.py`): downloads pages from one site, follows its links, respects robots.txt, waits 1 second between requests, and saves title, text and links in SQLite.
- **Index and search** (`search.py`): builds an inverted index and ranks results by word count (title words count extra).
- **PageRank** (`pagerank.py`): ranks pages by how many pages link to them.
- **Web page** (`webapp.py`): a Flask search box with ranked results.

## How to run
    python3 crawl2.py https://example.com/ 30
    python3 search.py some words
    python3 pagerank.py
    python3 webapp.py

Then open http://127.0.0.1:5002 in a browser. Only Python 3 is needed, plus Flask for the web page.

## Notes
- Only crawl your own site or sites that allow it in robots.txt.
- Learning notes (in Hinglish) for each step are in NOTES.md.
- It is a learning project, not a replacement for a real search engine.
