from sentence_transformers import SentenceTransformer
import numpy as np
import os
import json

model = SentenceTransformer("all-MiniLM-L6-v2")

STORE_PATH = "storage/vectorstore.json"

def store_document(text: str, doc_id: str):
    embedding = model.encode(text).tolist()

    if not os.path.exists("storage"):
        os.makedirs("storage")

    data = {}
    if os.path.exists(STORE_PATH):
        with open(STORE_PATH, "r") as f:
            data = json.load(f)

    data[doc_id] = {
        "text": text,
        "embedding": embedding
    }

    with open(STORE_PATH, "w") as f:
        json.dump(data, f)

    return True