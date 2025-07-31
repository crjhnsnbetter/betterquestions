# mock_query_pubmed.py

def query_pubmed(symptoms, conditions, age=None, sex=None):
    return {
        "esearchresult": {
            "idlist": ["12345678", "98765432"]
        }
    }
