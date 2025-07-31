# ⚠️ This code performs live queries and may incur API/token usage costs.
# It is intended for real-time access to PubMed search results.

import requests
print("🧠 Using aliased import for query_pubmed → search_pubmed")

def query_pubmed(symptoms, conditions, age=None, sex=None):
    """
    Builds and executes a PubMed search query using provided symptoms and conditions.
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    symptom_query = " AND ".join(symptoms)
    condition_query = " AND ".join(conditions)
    filters = []

    #if age:
       # filters.append(f'"{age} years"[MeSH Terms]')
    #if sex:
    #    filters.append(f'"{sex}"[MeSH Terms]')

    final_query = f"({symptom_query}) AND ({condition_query})"
    if filters:
        final_query += " AND " + " AND ".join(filters)
    print(f"📄 PubMed Search Query: {final_query}")

    params = {
        "db": "pubmed",
        "term": final_query,
        "retmode": "json",
        "retmax": 10
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"PubMed query failed: {response.status_code}"}
    print("🧠 Using aliased import for query_pubmed → search_pubmed")
