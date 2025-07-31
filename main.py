# main.py

import os
import json

from pubmed_query_agent import query_pubmed
from question_framer import frame_questions
from legal_disclaimer import get_disclaimer_text
from dotenv import load_dotenv
load_dotenv()



try:
    from symptom_normalizer import normalize_symptoms
except ImportError:
    normalize_symptoms = lambda s: s  # fallback: no-op

def main():
    print("🧠 Better Questions: Medical Exploration Tool (MVP)")
    print("--------------------------------------------------")

    # Gather input
    raw_symptoms = input("Enter symptoms (comma-separated): ").strip()
    raw_conditions = input("Enter any known diagnoses (comma-separated): ").strip()
    age = input("Enter your age (optional): ").strip()
    sex = input("Enter your biological sex (optional): ").strip()

    symptoms = [s.strip() for s in raw_symptoms.split(",") if s.strip()]
    conditions = [c.strip() for c in raw_conditions.split(",") if c.strip()]

    if not symptoms:
        print("❌ At least one symptom is required.")
        return

    symptoms = normalize_symptoms(symptoms)  # Optional cleaner

    # Call PubMed
    print("\n🔎 Querying PubMed...")
    pubmed_result = query_pubmed(symptoms, conditions, age=age or None, sex=sex or None)

    if "error" in pubmed_result:
        print(f"❌ PubMed Error: {pubmed_result['error']}")
        return

    # Frame GPT questions
    print("🤖 Framing follow-up questions with GPT...")
    questions_output = frame_questions(pubmed_result, symptoms, conditions)

    print("\n📝 Suggested Questions:")
    print(questions_output[0])  # GPT content

    print("\n📜 Legal Disclaimer:")
    print(questions_output[1])  # Always present

if __name__ == "__main__":
    main()
