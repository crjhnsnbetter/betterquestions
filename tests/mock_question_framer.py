# mock_question_framer.py

from legal_disclaimer import get_disclaimer_text

def frame_questions(pubmed_json, symptoms, conditions):
    questions = (
        "Could fatigue and dizziness be early signs of anemia?\n"
        "Related articles: PMID 12345678, PMID 98765432"
    )
    return questions, get_disclaimer_text()
