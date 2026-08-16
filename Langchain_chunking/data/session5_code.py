import json
from pathlib import Path


class DocumentLoader:
    def __init__(self, folder):
        self.folder = folder

    def load_documents(self):
        documents = []

        for file_path in Path(self.folder).glob("*.txt"):
            text = file_path.read_text(encoding="utf-8")
            documents.append(text)

        return documents


def clean_text(text):
    text = text.strip()
    text = text.replace("\n\n\n", "\n\n")
    return text


def calculate_statistics(documents):
    total_documents = len(documents)
    total_characters = sum(len(doc) for doc in documents)

    return {
        "documents": total_documents,
        "characters": total_characters,
    }


class Retriever:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def search(self, query, k=3):
        results = self.vector_store.similarity_search(
            query,
            k=k
        )

        return results


def display_results(results):
    for index, result in enumerate(results, start=1):
        print(f"Result {index}")
        print(result.page_content)
        print("-" * 50)