# article_scorer.py

from datetime import datetime
import re

def score_article(article, query):
    """
    Scores an article based on multiple factors:
    - Contextual Relevance
    - CAV (Clinician Awareness Value)
    - Actionability
    - Evidence Strength
    - Human-centeredness
    - Recency
    - Domain Overlap
    Returns a composite float score.
    """
    score = 0
    abstract = article.get("abstract", "").lower()
    title = article.get("title", "").lower()
    year = int(article.get("pub_year", "2020"))
    text = title + " " + abstract

    symptoms = [s.lower() for s in query.get("symptoms", [])]
    conditions = [c.lower() for c in query.get("conditions", [])]

    # Relevance: keyword match density
    match_score = sum(1 for term in symptoms + conditions if term in text)
    score += match_score * 1.5  # weight relevance

    # Domain Overlap: match both symptom AND condition
    if any(s in text for s in symptoms) and any(c in text for c in conditions):
        score += 2.5

    # CAV (Clinician Awareness Value) — crude proxy via rarity or novelty language
    if re.search(r"(novel|unexpected|first report|rare|underdiagnosed)", abstract):
        score += 2.5
    elif re.search(r"(known|typical|well-established|commonly seen)", abstract):
        score += 0.5
    else:
        score += 1.5  # neutral/default insight

    # Actionability — mentions of treatment, intervention, diagnosis
    if re.search(r"(treatment|diagnosis|management|intervention|outcome)", abstract):
        score += 2.0

    # Evidence Strength — proxy: abstract length + presence of results/analysis
    if len(abstract.split()) > 100:
        score += 1.0
    if re.search(r"(results|analysis|significant|trial|study)", abstract):
        score += 1.0

    # Human-centeredness — patient language in abstract
    if re.search(r"(patients?|case study|quality of life|symptoms?)", abstract):
        score += 1.0

    # Recency: linear scale from 2015 to 2025
    score += max(0.0, (year - 2015) * 0.3)  # max bonus of 3 for recent papers

    return round(score, 2)


def filter_top_articles(articles, query, limit=10):
    """
    Scores and ranks articles, returning the top N (default 10).
    Returns list of tuples: (article_dict, score)
    """
    scored = [(article, score_article(article, query)) for article in articles]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]


