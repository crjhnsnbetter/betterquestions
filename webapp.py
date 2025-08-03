# webapp.py
print("🧪 Entered webapp.py")

from waitress import serve
from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from itertools import chain, combinations
from question_framer import frame_questions
from pubmed_query_agent import query_pubmed as search_pubmed
print("🧠 using query_pubmed alias")

load_dotenv()
app = Flask(__name__)

def get_subsets(items):
    """Return all non-empty subsets of a list (max 3 items)."""
    return list(chain.from_iterable(combinations(items, r) for r in range(1, len(items)+1)))

@app.route("/", methods=["GET", "POST"])
def index():
    questions = None
    if request.method == "POST":
        symptoms = request.form.get("symptoms", "").split(",")
        conditions = request.form.get("conditions", "").split(",")

        # Clean and enforce input limits
        symptoms = [s.strip() for s in symptoms if s.strip()][:3]
        conditions = [c.strip() for c in conditions if c.strip()][:3]

        symptom_subsets = get_subsets(symptoms)
        condition_subsets = get_subsets(conditions)

        all_articles = []
        for s_group in symptom_subsets:
            for c_group in condition_subsets:
                result = search_pubmed(s_group, c_group)
                if result and "esearchresult" in result and result["esearchresult"].get("idlist"):
                    questions = frame_questions(result, list(s_group), list(c_group))
                    break  # Use first valid result for now (optional: remove to combine all)
            if questions:
                break

    return render_template("index.html", questions=questions)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    print("🚀 Starting Flask server")
    serve(app, host="0.0.0.0", port=8080)
