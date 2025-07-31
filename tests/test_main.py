# test_main.py

from mock_query_pubmed import query_pubmed
from mock_question_framer import frame_questions
from legal_disclaimer import get_disclaimer_text

def main():
    print("🧪 Test Mode: Better Questions (offline demo)")

    symptoms = ["fatigue", "dizziness"]
    conditions = ["anemia"]
    age = "45"
    sex = "female"

    pubmed_data = query_pubmed(symptoms, conditions, age, sex)
    questions, disclaimer = frame_questions(pubmed_data, symptoms, conditions)

    print("\n📝 Suggested Questions:")
    print(questions)

    print("\n📜 Legal Disclaimer:")
    print(disclaimer)

if __name__ == "__main__":
    main()
