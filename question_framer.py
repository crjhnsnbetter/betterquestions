import os
from openai import OpenAI
from token_logger import log_token_usage
from legal_disclaimer import get_disclaimer_text
from dotenv import load_dotenv
import markdown
load_dotenv()

print("🧪 question_framer.py loaded")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

def frame_questions(pubmed_json, symptoms, conditions):
    if not pubmed_json or "esearchresult" not in pubmed_json:
        return ["No relevant PubMed results found.", get_disclaimer_text()]

    pmids = pubmed_json["esearchresult"].get("idlist", [])
    if not pmids:
        return [
            "❗ **No results found for your input.**<br><br>"
            "This tool avoids hallucinating unsupported suggestions. It only returns questions when it finds a published PubMed article "
            "that matches *all* of the symptoms and conditions you entered.<br><br>"
            "**Try this:**<ul>"
            "<li>Reduce the number of symptoms or conditions entered</li>"
            "<li>Search in smaller chunks to find narrower matches</li></ul>"
            "In future updates, partial matches will be supported—with clear labeling to protect accuracy.",
            get_disclaimer_text()
        ]

    query_summary = (
        f"Symptoms: {', '.join(symptoms)}\n"
        f"Known Conditions: {', '.join(conditions)}\n"
        f"PubMed Articles: {len(pmids)} recent results"
    )

    article_links = "\n".join([f"- https://pubmed.ncbi.nlm.nih.gov/{pmid}" for pmid in pmids])

    messages = [
        {
            "role": "system",
            "content": (
                "You are a careful and concise medical assistant. Use only the user’s symptoms, known conditions, "
                "and the provided PubMed articles to generate medically relevant questions to ask a doctor. "
                "Only include questions that can be directly supported by one of the PubMed articles. "
                "Do not generate any questions that lack a corresponding PubMed citation. "
                "Format each question in Markdown, with a clickable [PubMed Article](https://...) link inline. "
                "Do not provide medical advice or diagnoses."
            ),
        },
        {
            "role": "user",
            "content": (
                f"{query_summary}\n"
                f"Relevant PubMed Articles (with full links):\n{article_links}\n\n"
                "Please suggest possible questions to ask a doctor, and include the full clickable PubMed links for each citation in your response."
            ),
        }
    ]

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.5,
            max_tokens=700,
        )
        reply = response.choices[0].message.content.strip()
        if "pubmed.ncbi.nlm.nih.gov" not in reply:
            return [
                "❗ **No citation-backed questions could be generated.**<br><br>"
                "The system checks all generated questions to make sure they include direct citations to PubMed articles. "
                "If none are present, the response is discarded to avoid hallucinated content.<br><br>"
                "**Try this:**<ul>"
                "<li>Use fewer symptoms or conditions in your input</li>"
                "<li>Ensure inputs are clearly worded and relevant</li></ul>"
                "This safeguard helps maintain accuracy and protect your medical decision-making.",
                get_disclaimer_text()
            ]

        log_token_usage(response)
        reply_html = markdown.markdown(reply)
        return [reply_html, get_disclaimer_text()]
    except Exception as e:
        return [f"⚠️ GPT framing failed:\n\n{str(e)}", get_disclaimer_text()]
