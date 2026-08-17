# Semantic Chunking for RAG

A small demo project to understand how **semantic chunking** works in a Retrieval-Augmented Generation (RAG) pipeline.

The project uses **LlamaIndex** for semantic chunking, a free local **Hugging Face embedding model**, **LangChain**, and **ChromaDB** for retrieval evaluation.

## How It Works

```text
PDF
 ↓
PDFReader
 ↓
LlamaIndex Documents
 ↓
SemanticSplitterNodeParser
 ↓
Hugging Face Embeddings
 ↓
Semantic Breakpoints
 ↓
Semantic Chunks
 ↓
ChromaDB
 ↓
Retrieval Evaluation
```

Semantic chunking differs from fixed-size chunking because it creates boundaries based on **changes in meaning**, rather than only character or token limits.

## Configuration

```text
Embedding model: BAAI/bge-small-en-v1.5
Buffer size: 1
Breakpoint percentile: 95
```

The embedding model runs locally and does not require a paid API.

## Chunking Results

| Metric             |  Result |
| ------------------ | ------: |
| Semantic chunks    |      95 |
| Average characters | 1120.48 |
| Median characters  |    1024 |
| Minimum characters |       6 |
| Maximum characters |    3075 |

Manual inspection showed that many larger chunks remained semantically coherent. Some very small chunks were caused by PDF artifacts such as page labels and figure text.

## Retrieval Evaluation

The semantic chunks were stored in **ChromaDB** and evaluated using 10 manually created questions.

Metrics:

```text
Hit@3 = 0.8000
MRR   = 0.5667
```

This means a relevant page appeared in the Top 3 retrieved chunks for **8 out of 10 queries**.

These results are only a small experimental baseline and should not be interpreted as universal semantic-chunking accuracy.

## Project Structure

```text
semantic-chunking-demo/
│
├── data/
├── src/
│   ├── load_pdf.py
│   ├── semantic_chunking.py
│   ├── inspect_chunks.py
│   ├── build_vector_store.py
│   └── evaluate.py
│
├── evaluation/
│   └── questions.json
│
├── outputs/
├── chroma_db/
└── README.md
```

## Key Learning

The main goal of this project was to understand the semantic chunking process:

```text
Sentence groups
 ↓
Embeddings
 ↓
Semantic similarity
 ↓
Semantic distance
 ↓
Breakpoint detection
 ↓
Meaning-aware chunks
```

The experiment also showed that chunking quality depends heavily on **document parsing**. PDF artifacts such as page numbers, headers, figures, tables, and images should be handled properly before chunking.

For more complex PDFs containing text, tables, and images, a document-processing framework such as **Unstructured** can be used before semantic chunking.

## Tech Stack

* Python
* LlamaIndex
* Hugging Face
* `BAAI/bge-small-en-v1.5`
* LangChain
* ChromaDB
* NIST AI RMF 1.0 PDF

## Run

```bash
python src/semantic_chunking.py
python src/inspect_chunks.py
python src/build_vector_store.py
python src/evaluate.py
```

## Result

This project demonstrates a simple end-to-end workflow for **embedding-based semantic chunking and retrieval evaluation in RAG**.
