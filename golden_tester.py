# golden_tester.py

import json
from question_framer import frame_questions
from pubmed_query_agent import query_pubmed

GOLDEN_SET_PATH = "golden_sets/golden_set_1.json"


def load_golden_set(path):
    with open(path, "r") as f:
        return json.load(f)


def run_test():
    data = load_golden_set(GOLDEN_SET_PATH)
    symptoms = data["input"]["symptoms"]
    conditions = data["input"]["conditions"]
    expected_pmids = set(q["pmid"] for q in data["expected_questions"])

    print("🔁 Running PubMed search...")
    pubmed_results = query_pubmed(symptoms, conditions)
    if not pubmed_results:
        print("❌ PubMed search failed or returned null.")
        return

    print("🧠 Running GPT question framer...")
    output_blocks = frame_questions(pubmed_results, symptoms, conditions)
    if not output_blocks:
        print("❌ No questions generated.")
        return

    html_output = output_blocks[0]
    found_pmids = set()
    for line in html_output.split("\n"):
        if "pubmed.ncbi.nlm.nih.gov/" in line:
            try:
                pmid = line.split("pubmed.ncbi.nlm.nih.gov/")[1].split("\"")[0].strip("/)")
                found_pmids.add(pmid)
            except IndexError:
                continue

    matched = expected_pmids & found_pmids
    missed = expected_pmids - found_pmids
    extra = found_pmids - expected_pmids

    print("\n📊 Test Results:")
    print(f"✅ Matched PMIDs: {matched if matched else 'None'}")
    print(f"⚠️ Missed Expected PMIDs: {missed if missed else 'None'}")
    print(f"➕ Extra Found PMIDs: {extra if extra else 'None'}")


if __name__ == "__main__":
    run_test()
