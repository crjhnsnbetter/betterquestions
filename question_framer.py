import os
import markdown
from openai import OpenAI
from dotenv import load_dotenv
from pubmed_query_agent import fetch_article_metadata
from token_logger import TokenLogger
from legal_disclaimer import get_disclaimer_text
from article_scorer import filter_top_articles, classify_score, get_label_color
import re

load_dotenv()
print("🧪 question_framer.py loaded")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
logger = TokenLogger(model=OPENAI_MODEL)

ARTICLE_LIMIT = 10  # max articles to use in framing


def extract_pmids_from_links(markdown_text):
    pmids = set()
    matches = re.findall(r"https://pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", markdown_text)
    for pmid in matches:
        pmids.add(pmid.strip("/"))
    return sorted(list(pmids))


def frame_questions(pubmed_json, symptoms, conditions):
    if not pubmed_json or "esearchresult" not in pubmed_json:
        return ["No relevant PubMed results found.", get_disclaimer_text(), ""]

    pmids = pubmed_json["esearchresult"].get("idlist", [])
    if not pmids:
        return ["No articles found for these inputs.", get_disclaimer_text(), ""]

    query_summary = (
        f"Symptoms: {', '.join(symptoms)}\n"
        f"Known Conditions: {', '.join(conditions)}\n"
        f"PubMed Articles: {len(pmids)} recent results"
    )

    query_dict = {"symptoms": symptoms, "conditions": conditions}
    articles = fetch_article_metadata(pmids)

    # Score and filter articles
    scored_articles = filter_top_articles(articles, query_dict, limit=ARTICLE_LIMIT)
    pmid_score_map = {a["pmid"]: s for a, s in scored_articles}
    top_articles = [a for a, _ in scored_articles]
    trimmed = len(scored_articles) < len(articles)

    top_pmids = [a["pmid"] for a in top_articles]
    article_links = "\n".join([
        f"- https://pubmed.ncbi.nlm.nih.gov/{pmid}" for pmid in top_pmids
    ])

    messages = [
        {
            "role": "system",
            "content": (
                "You are a careful and concise medical assistant. Use only the user’s symptoms, known conditions, "
                "and the provided PubMed articles to generate medically relevant questions to ask a doctor. "
                "Only include questions that can be directly supported by one of the PubMed articles. "
                "Format each question in Markdown, using a clickable link in this format: "
                "[PubMed #PMID](https://pubmed.ncbi.nlm.nih.gov/PMID). Do not cite multiple articles per question. "
                "Do not provide medical advice or diagnoses."
            ),
        },
        {
            "role": "user",
            "content": (
                f"{query_summary}\n"
                f"Relevant PubMed Articles (with full links):\n{article_links}\n\n"
                "Please suggest possible questions to ask a doctor. Use exactly one PMID per question."
            ),
        }
    ]

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.5,
            max_tokens=1500,
        )
        reply = response.choices[0].message.content.strip()

        if "pubmed.ncbi.nlm.nih.gov" not in reply:
            return ["No citation-backed questions could be generated from recent PubMed data.", get_disclaimer_text(), ""]

        logger.log(messages[1]["content"], reply, model=OPENAI_MODEL, meta={"symptoms": symptoms, "conditions": conditions})

        # Insert color-coded PubMed tags inline
        for pmid in pmid_score_map:
            score = pmid_score_map[pmid]
            emoji = get_label_color(score, as_emoji=True)
            reply = reply.replace(
                f"[PubMed #{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid})",
                f"{emoji} [PubMed #{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid})"
            )

        reply_html = markdown.markdown(reply)
        pmids_used = extract_pmids_from_links(reply)

        context_msg = f"<p><strong>Note:</strong> Questions below were generated using the combination <code>{', '.join(symptoms)}</code> + <code>{', '.join(conditions)}</code>. You may try removing one or both to explore other patterns.</p>"
        reply_html = context_msg + reply_html

        if trimmed:
            reply_html += "\n<p><em>Only the most relevant articles were used to reduce token cost. Support helps unlock deeper analysis.</em></p>"

        # Provide reference list
        if pmids_used:
            reply_html += "<p><strong>Referenced Articles:</strong></p><ul>"
            for pmid in pmids_used:
                score = pmid_score_map.get(pmid, 0)
                emoji = get_label_color(score, as_emoji=True)
                label = classify_score(score)
                reply_html += f"<li>{emoji} PubMed #{pmid} – {label}</li>"
            reply_html += "</ul>"

        # Add legend
        reply_html += (
            "<p><strong>Question Context Legend:</strong><br>"
            "<span style='color:green;'>🟢 Potentially Valuable Insight</span>: This may point to information your doctor has already considered, or offer a fresh angle worth discussing.<br>"
            "<span style='color:orange;'>🟡 Relevant Research</span>: Linked article may help frame your concern more clearly.<br>"
            "<span style='color:gray;'>⚪ General Reference</span>: Standard or background information — may support basic understanding.</p>"
        )

        # Also provide plaintext version for copying
        reply_plain = f"Better Questions – Generated for: {', '.join(symptoms)} + {', '.join(conditions)}\n\n"
        for line in reply.split("\n"):
            reply_plain += line + "\n"
        if pmids_used:
            reply_plain += "\nReferenced PMIDs: " + ", ".join(pmids_used) + "\n"

        return [reply_html, get_disclaimer_text(), reply_plain.strip()]

    except Exception as e:
        return [f"⚠️ GPT framing failed:\n\n{str(e)}", get_disclaimer_text(), ""]