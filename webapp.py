#webapp.py
print("🧪 Entered webapp.py")

from waitress import serve
from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from question_framer import frame_questions
from pubmed_query_agent import query_pubmed as search_pubmed
print("🧠 using query_pubmed alias")


load_dotenv()
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    questions = None
    if request.method == "POST":
        symptoms = request.form.get("symptoms", "").split(",")
        conditions = request.form.get("conditions", "").split(",")
        pubmed_results = search_pubmed(symptoms, conditions)
        questions = frame_questions(pubmed_results, symptoms, conditions)

    return render_template("index.html", questions=questions)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    print("🚀 Starting Flask server")
    serve(app, host="0.0.0.0", port=8080)

