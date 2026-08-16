
# RAG Chunking Strategies

A hands-on repository for exploring, implementing, and comparing **chunking strategies for Retrieval-Augmented Generation (RAG)**.

The goal of this project is to understand how different chunking approaches affect document structure, chunk boundaries, metadata preservation, token usage, and eventually retrieval quality in a RAG pipeline.

## Current Progress

### LangChain Chunking

Implemented and practiced using `langchain-text-splitters`.

| Session | Strategy                   | LangChain Class / Method                                        | Status |
| ------- | -------------------------- | --------------------------------------------------------------- | ------ |
| 01      | Character Chunking         | `CharacterTextSplitter`                                         | ✅      |
| 01      | Recursive Chunking         | `RecursiveCharacterTextSplitter`                                | ✅      |
| 01      | Token Chunking             | `TokenTextSplitter`                                             | ✅      |
| 01      | Recursive + Token-Aware    | `.from_tiktoken_encoder()`                                      | ✅      |
| 02      | Markdown Structure-Aware   | `MarkdownHeaderTextSplitter`                                    | ✅      |
| 02      | Markdown + Recursive       | `MarkdownHeaderTextSplitter` + `RecursiveCharacterTextSplitter` | ✅      |
| 03      | HTML Header-Aware          | `HTMLHeaderTextSplitter`                                        | ✅      |
| 03      | HTML Section-Aware         | `HTMLSectionSplitter`                                           | ✅      |
| 03      | HTML Semantic Preservation | `HTMLSemanticPreservingSplitter`                                | ✅      |
| 04      | JSON Structure-Aware       | `RecursiveJsonSplitter`                                         | ✅      |
| 04      | JSON List Handling         | `convert_lists=True`                                            | ✅      |
| 05      | Generic Code Chunking      | `RecursiveCharacterTextSplitter`                                | ✅      |
| 05      | Python-Aware Code Chunking | `.from_language(Language.PYTHON)`                               | ✅      |

## Repository Structure

```text
rag-chunking-strategies/
│
├── README.md
│
├── langchain_chunking/
│   ├── README.md
│   ├── requirements.txt
│   │
│   ├── data/
│   │   ├── session1_text.txt
│   │   ├── session2_markdown.md
│   │   ├── session3_html.html
│   │   ├── session4_products.json
│   │   ├── session4_users.json
│   │   └── session5_code.py
│   │
│   ├── session_01_character.py
│   ├── session_01_recursive.py
│   ├── session_01_token.py
│   ├── session_01_recursive_token.py
│   ├── session_02_markdown.py
│   ├── session_02_markdown_recursive.py
│   ├── session_03_html_header.py
│   ├── session_03_html_section.py
│   ├── session_03_html_semantic.py
│   ├── session_04_json.py
│   ├── session_04_json_list.py
│   ├── session_05_normal_recursive.py
│   └── session_05_python_aware.py
│
├── semantic_chunking/          # Planned
├── contextual_chunking/        # Planned
└── ...
```

## What This Repository Focuses On

This repository is not intended to contain only isolated code examples.

Each experiment focuses on understanding:

* how chunk boundaries are selected;
* how `chunk_size` and `chunk_overlap` behave;
* character-based vs token-based sizing;
* recursive fallback separators;
* preservation of document hierarchy;
* metadata propagation;
* structured formats such as Markdown, HTML, and JSON;
* preservation of tables and lists;
* language-aware code chunking;
* limitations and trade-offs of each strategy.

## Example Learning Progression

```text
Raw Document
     ↓
Character Chunking
     ↓
Recursive Chunking
     ↓
Token-Aware Chunking
     ↓
Structure-Aware Chunking
     ├── Markdown
     ├── HTML
     ├── JSON
     └── Code
     ↓
Semantic / Contextual Chunking
     ↓
Retrieval Evaluation
```

## Setup

Clone the repository:

```bash
git clone <your-repository-url>
cd rag-chunking-strategies/langchain_chunking
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run any experiment:

```bash
python session_01_recursive.py
```

## Key Observation

Chunking is not simply about cutting a document into fixed-size pieces.

A useful RAG chunk should balance:

```text
Chunk Size
    +
Natural Boundaries
    +
Document Structure
    +
Context Preservation
    +
Retrieval Quality
```

Different document types therefore require different chunking strategies.

## Planned Work

Future additions will explore:

* [ ] Semantic chunking
* [ ] Embedding-based breakpoint detection
* [ ] Contextual chunking
* [ ] Parent-child / hierarchical chunking
* [ ] Hybrid chunking strategies
* [ ] Chunk enrichment and metadata strategies
* [ ] Real PDF document experiments
* [ ] Chunk-size and overlap experiments
* [ ] Retrieval evaluation
* [ ] Recall@K
* [ ] Precision@K
* [ ] MRR
* [ ] End-to-end RAG comparison

## Technologies

* Python
* LangChain
* `langchain-text-splitters`
* tiktoken
* HTML / Markdown / JSON
* VS Code

## Purpose

This repository is part of a practical study of **production-oriented RAG systems**, with chunking treated as an independent component that should eventually be evaluated rather than selected only by intuition.

The long-term goal is to compare different strategies under the same retrieval pipeline and measure how chunking choices affect retrieval performance and final RAG quality.

## References

Primary documentation used for the LangChain experiments:

* LangChain Text Splitters Overview
* Recursive Character Text Splitter
* Character Text Splitter
* Token-Based Splitting
* Markdown Header Splitting
* HTML Splitting
* Recursive JSON Splitting
* Code Splitting

Official documentation: `https://docs.langchain.com/oss/python/integrations/splitters`

---

**Status:** Active learning and experimentation 🚀
