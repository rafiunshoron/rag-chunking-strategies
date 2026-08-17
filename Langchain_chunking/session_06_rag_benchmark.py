import pypdf
import tiktoken

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


PDF_PATH = "data/nke-10k-2023.pdf"


# --------------------------------------------------
# 1. LOAD PDF PAGE BY PAGE
# --------------------------------------------------

def load_pdf_pages(file_path):
    reader = pypdf.PdfReader(file_path)

    documents = []

    for page_number, page in enumerate(reader.pages):
        documents.append(
            Document(
                page_content=page.extract_text() or "",
                metadata={
                    "source": file_path,
                    "page": page_number,
                },
            )
        )

    return documents


documents = load_pdf_pages(PDF_PATH)

print(f"PDF pages loaded: {len(documents)}")


# --------------------------------------------------
# 2. STRATEGY A — RECURSIVE CHARACTER
# --------------------------------------------------

character_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True,
)

character_chunks = character_splitter.split_documents(documents)


# --------------------------------------------------
# 3. STRATEGY B — RECURSIVE + TOKEN-AWARE
# --------------------------------------------------

token_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base",
    chunk_size=250,
    chunk_overlap=50,
    add_start_index=True,
)

token_chunks = token_splitter.split_documents(documents)


# --------------------------------------------------
# 4. CHUNK STATISTICS
# --------------------------------------------------

encoding = tiktoken.get_encoding("cl100k_base")


def print_statistics(name, chunks):

    character_lengths = [
        len(chunk.page_content)
        for chunk in chunks
    ]

    token_lengths = [
        len(encoding.encode(chunk.page_content))
        for chunk in chunks
    ]

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    print(f"Number of chunks : {len(chunks)}")
    print(
        f"Average characters : "
        f"{sum(character_lengths) / len(character_lengths):.1f}"
    )
    print(
        f"Average tokens     : "
        f"{sum(token_lengths) / len(token_lengths):.1f}"
    )
    print(f"Maximum characters : {max(character_lengths)}")
    print(f"Maximum tokens     : {max(token_lengths)}")


print_statistics(
    "STRATEGY A — Recursive Character",
    character_chunks,
)

print_statistics(
    "STRATEGY B — Recursive Token-Aware",
    token_chunks,
)


# --------------------------------------------------
# 5. EMBEDDING MODEL
# --------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    encode_kwargs={
        "normalize_embeddings": True
    },
)


# --------------------------------------------------
# 6. BUILD SEPARATE VECTOR STORES
# --------------------------------------------------

character_store = Chroma(
    collection_name="recursive_character",
    embedding_function=embeddings,
)

character_store.add_documents(character_chunks)


token_store = Chroma(
    collection_name="recursive_token",
    embedding_function=embeddings,
)

token_store.add_documents(token_chunks)


stores = {
    "Recursive Character": character_store,
    "Recursive Token-Aware": token_store,
}

# Chroma
# │
# ├── recursive_character
# │     ├── character chunk 1
# │     ├── character chunk 2
# │     ├── character chunk 3
# │     └── ...
# │
# └── recursive_token
#       ├── token-aware chunk 1
#       ├── token-aware chunk 2
#       ├── token-aware chunk 3
#       └── ...



# --------------------------------------------------
# 7. SMALL GOLD TEST SET
# --------------------------------------------------

test_queries = [
    {
        "query": "How many distribution centers does Nike have in the United States?",
        "relevant_page": 4,
    },
    {
        "query": "When was Nike incorporated?",
        "relevant_page": 3,
    },
    {
        "query": "What was Nike's revenue in fiscal 2023?",
        "relevant_page": 35,
    },
    {
        "query": "How was Nike's gross margin impacted in fiscal 2023?",
        "relevant_page": 36,
    },
]


# --------------------------------------------------
# 8. RETRIEVAL EVALUATION
# --------------------------------------------------

K = 3


for strategy_name, vector_store in stores.items():

    print("\n\n" + "#" * 70)
    print(f"EVALUATING: {strategy_name}")
    print("#" * 70)

    hits = 0
    reciprocal_rank_sum = 0


    for test in test_queries:

        query = test["query"]
        relevant_page = test["relevant_page"]

        results = vector_store.similarity_search(
            query,
            k=K,
        )

        retrieved_pages = [
            doc.metadata["page"]
            for doc in results
        ]


        relevant_rank = None

        for rank, page in enumerate(
            retrieved_pages,
            start=1,
        ):
            if page == relevant_page:
                relevant_rank = rank
                break


        if relevant_rank is not None:
            hits += 1
            reciprocal_rank_sum += 1 / relevant_rank
            status = "HIT"
        else:
            status = "MISS"


        print("\n" + "-" * 70)
        print(f"Query: {query}")
        print(f"Expected page : {relevant_page}")
        print(f"Retrieved pages: {retrieved_pages}")
        print(f"Result: {status}")


        print("\nTop result:")
        print(results[0].page_content[:400])


    hit_at_k = hits / len(test_queries)
    mrr = reciprocal_rank_sum / len(test_queries)


    print("\n" + "=" * 70)
    print(f"FINAL RESULTS — {strategy_name}")
    print("=" * 70)

    print(f"Hit@{K}: {hit_at_k:.2f}")
    print(f"MRR   : {mrr:.2f}")


    #                     Same PDF
    #                    ↓
    #          Two chunking strategies
    #               ↙          ↘
    #    Character chunks    Token chunks
    #           ↓                ↓
    #       Chroma A          Chroma B
    #               ↘          ↙
    #              Same queries
    #                    ↓
    #             Top-3 retrieval
    #                    ↓
    #           Compare gold pages
    #                    ↓
    #            Hit@3 + MRR