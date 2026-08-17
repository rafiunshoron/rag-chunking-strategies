from pathlib import Path
import json

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "BAAI/bge-small-en-v1.5"

COLLECTION_NAME = "semantic_chunks"

TOP_K = 3


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

QUESTIONS_PATH = (
    PROJECT_ROOT
    / "evaluation"
    / "questions.json"
)

CHROMA_PATH = (
    PROJECT_ROOT
    / "chroma_db"
)

RESULTS_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "evaluation_results.json"
)


# ============================================================
# 2. CHECK REQUIRED FILES / FOLDERS
# ============================================================

if not QUESTIONS_PATH.exists():
    raise FileNotFoundError(
        f"Questions file not found:\n{QUESTIONS_PATH}"
    )


if not CHROMA_PATH.exists():
    raise FileNotFoundError(
        f"Chroma database not found:\n{CHROMA_PATH}"
    )


# ============================================================
# 3. LOAD EVALUATION QUESTIONS
# ============================================================

print("=" * 80)
print("LOADING EVALUATION QUESTIONS")
print("=" * 80)


with open(
    QUESTIONS_PATH,
    "r",
    encoding="utf-8"
) as file:

    questions = json.load(file)


print(f"Questions loaded: {len(questions)}")


# ============================================================
# 4. LOAD EMBEDDING MODEL
# ============================================================

print("\n" + "=" * 80)
print("LOADING EMBEDDING MODEL")
print("=" * 80)

print(f"Embedding model: {MODEL_NAME}")


embedding_model = HuggingFaceEmbeddings(
    model_name=MODEL_NAME,
    model_kwargs={
        "device": "cpu"
    },
    encode_kwargs={
        "normalize_embeddings": True
    }
)


print("Embedding model loaded successfully.")


# ============================================================
# 5. OPEN EXISTING CHROMA DATABASE
# ============================================================

print("\n" + "=" * 80)
print("OPENING CHROMA VECTOR STORE")
print("=" * 80)


vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embedding_model,
    persist_directory=str(CHROMA_PATH)
)


print("Chroma vector store loaded successfully.")


# ============================================================
# 6. EVALUATION VARIABLES
# ============================================================

total_hits = 0

reciprocal_rank_sum = 0.0

evaluation_results = []


# ============================================================
# 7. EVALUATE EACH QUESTION
# ============================================================

print("\n" + "=" * 80)
print("RUNNING RETRIEVAL EVALUATION")
print("=" * 80)


for item in questions:

    question_id = item["id"]

    question = item["question"]

    relevant_pages = [
        str(page)
        for page in item["relevant_pages"]
    ]


    # --------------------------------------------------------
    # Retrieve Top-K semantic chunks
    # --------------------------------------------------------

    retrieved_documents = vector_store.similarity_search(
        question,
        k=TOP_K
    )


    # --------------------------------------------------------
    # Extract retrieved metadata
    # --------------------------------------------------------

    retrieved_results = []

    first_relevant_rank = None


    for rank, document in enumerate(
        retrieved_documents,
        start=1
    ):

        page_label = str(
            document.metadata.get(
                "page_label",
                ""
            )
        )

        chunk_id = document.metadata.get(
            "chunk_id"
        )


        is_relevant = page_label in relevant_pages


        if (
            is_relevant
            and first_relevant_rank is None
        ):
            first_relevant_rank = rank


        retrieved_results.append(
            {
                "rank": rank,
                "chunk_id": chunk_id,
                "page_label": page_label,
                "relevant": is_relevant,
                "text_preview": document.page_content[:300]
            }
        )


    # --------------------------------------------------------
    # Calculate Hit@K
    # --------------------------------------------------------

    if first_relevant_rank is not None:
        hit = 1
    else:
        hit = 0


    # --------------------------------------------------------
    # Calculate Reciprocal Rank
    # --------------------------------------------------------

    if first_relevant_rank is not None:
        reciprocal_rank = 1 / first_relevant_rank
    else:
        reciprocal_rank = 0.0


    total_hits += hit

    reciprocal_rank_sum += reciprocal_rank


    # --------------------------------------------------------
    # Save result for this question
    # --------------------------------------------------------

    evaluation_results.append(
        {
            "question_id": question_id,
            "question": question,
            "relevant_pages": relevant_pages,
            "hit_at_3": hit,
            "first_relevant_rank": first_relevant_rank,
            "reciprocal_rank": reciprocal_rank,
            "retrieved_results": retrieved_results
        }
    )


    # --------------------------------------------------------
    # Print question result
    # --------------------------------------------------------

    print("\n" + "-" * 80)

    print(
        f"Question {question_id}: "
        f"{question}"
    )

    print(
        f"Relevant page(s): "
        f"{relevant_pages}"
    )


    for result in retrieved_results:

        status = (
            "HIT"
            if result["relevant"]
            else "MISS"
        )

        print(
            f"Rank {result['rank']} | "
            f"Chunk {result['chunk_id']} | "
            f"Page {result['page_label']} | "
            f"{status}"
        )


    print(
        f"Hit@{TOP_K}: {hit}"
    )

    print(
        f"Reciprocal Rank: "
        f"{reciprocal_rank:.4f}"
    )


# ============================================================
# 8. CALCULATE FINAL METRICS
# ============================================================

number_of_questions = len(questions)


hit_at_k = (
    total_hits
    / number_of_questions
)


mrr = (
    reciprocal_rank_sum
    / number_of_questions
)


# ============================================================
# 9. PRINT FINAL RESULTS
# ============================================================

print("\n" + "=" * 80)
print("FINAL RETRIEVAL EVALUATION")
print("=" * 80)

print(
    f"Questions evaluated : "
    f"{number_of_questions}"
)

print(
    f"Top-K               : "
    f"{TOP_K}"
)

print(
    f"Successful hits     : "
    f"{total_hits}"
)

print(
    f"Hit@{TOP_K}              : "
    f"{hit_at_k:.4f}"
)

print(
    f"MRR                 : "
    f"{mrr:.4f}"
)


# ============================================================
# 10. SAVE EVALUATION RESULTS
# ============================================================

RESULTS_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


final_output = {
    "configuration": {
        "embedding_model": MODEL_NAME,
        "collection_name": COLLECTION_NAME,
        "top_k": TOP_K
    },

    "metrics": {
        f"hit_at_{TOP_K}": hit_at_k,
        "mrr": mrr,
        "successful_hits": total_hits,
        "number_of_questions": number_of_questions
    },

    "questions": evaluation_results
}


with open(
    RESULTS_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        final_output,
        file,
        ensure_ascii=False,
        indent=2
    )


print("\n" + "=" * 80)
print("EVALUATION RESULTS SAVED")
print("=" * 80)

print(
    f"Results saved to:\n"
    f"{RESULTS_PATH}"
)