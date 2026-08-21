# RAG Chunking Strategies

A hands-on study of different **document chunking strategies for Retrieval-Augmented Generation (RAG)**.

This repository explores how chunking changes depending on the type and structure of the source data. Rather than relying on one universal splitter, the project experiments with multiple approaches for normal text, structured documents, semantic content, source code, and complex PDFs.

The goal is to understand **when each chunking strategy is useful, how it works, and what trade-offs it introduces in a RAG pipeline.**

---

## Chunking Approaches

| Section                                         | Approach                        | Main Idea                                                                                     |
| ----------------------------------------------- | ------------------------------- | --------------------------------------------------------------------------------------------- |
| [LangChain Chunking](./Langchain_chunking/)     | Text & structure-aware chunking | Character, recursive, token-aware, Markdown, HTML, JSON, and language-aware splitting         |
| [Semantic Chunking](./semantic-chunking-demo/)  | Meaning-based chunking          | Uses embeddings and semantic similarity to detect natural topic boundaries                    |
| [AST-Aware Code Chunking](./ast-code-chunking/) | Structure-aware code chunking   | Uses Tree-sitter to preserve functions, classes, methods, and other code structures           |
| [Unstructured](./Unstructured/)                 | Document-aware PDF chunking     | Partitions PDFs into elements such as titles, text, tables, lists, and images before chunking |

---

## 1. LangChain Chunking

The LangChain section explores several commonly used text-splitting strategies, starting from basic character splitting and progressing toward structure-aware chunking.

Topics include:

* Character-based chunking
* Recursive character chunking
* Token-aware chunking
* Markdown-aware chunking
* HTML-aware chunking
* JSON-aware chunking
* Language-aware code splitting
* Chunk overlap
* Metadata preservation
* Retrieval evaluation with ChromaDB

It also includes a small RAG retrieval experiment comparing chunking configurations.

**Explore:** [Langchain_chunking](./Langchain_chunking/)

---

## 2. Semantic Chunking

Semantic chunking creates boundaries based on **changes in meaning** rather than relying only on a fixed number of characters or tokens.

The implementation uses embeddings to compare nearby sentence groups and detects semantic breakpoints when the topic changes significantly.

The experiment includes:

* PDF loading
* Local Hugging Face embeddings
* Semantic breakpoint detection
* LlamaIndex `SemanticSplitterNodeParser`
* ChromaDB vector storage
* Retrieval evaluation using Hit@K and MRR

**Explore:** [semantic-chunking-demo](./semantic-chunking-demo/)

---

## 3. AST-Aware Code Chunking

Source code has structural boundaries that normal text splitters do not fully understand.

This section uses **Tree-sitter** to parse Python code and chunk it according to actual programming structures.

The chunker attempts to preserve:

* Classes
* Functions
* Methods
* Statements
* Parent scopes
* Line ranges
* Syntax structure

Large structures are recursively divided only when necessary, with smaller fallbacks used for oversized nodes.

**Explore:** [ast-code-chunking](./ast-code-chunking/)

---

## 4. Unstructured Document Chunking

Complex documents such as research papers, reports, and books may contain more than plain text.

The Unstructured section first partitions a PDF into document elements such as:

* Titles
* Narrative text
* List items
* Tables
* Images
* Figure captions

The detected elements are then chunked using approaches such as:

* Basic element chunking
* By-title chunking

By-title chunking is especially useful when preserving the logical organization of structured documents such as research papers and books.

**Explore:** [Unstructured](./Unstructured/)

---

## Repository Structure

```text
rag-chunking-strategies/
│
├── Langchain_chunking/
│   └── Text, token and structure-aware chunking
│
├── semantic-chunking-demo/
│   └── Embedding-based semantic chunking
│
├── ast-code-chunking/
│   └── Tree-sitter based code chunking
│
├── Unstructured/
│   └── Element-aware PDF parsing and chunking
│
├── README.md
└── LICENSE
```

Each section contains its own implementation, examples, documentation, and experiment-specific details.

---

## What This Repository Explores

The experiments are built around one central idea:

> **There is no single best chunking strategy for every type of document.**

Different data requires different boundaries.

```text
Plain Text
    ↓
Recursive / Token-Aware Chunking

Structured Markdown / HTML / JSON
    ↓
Structure-Aware Chunking

Semantically Dense Text
    ↓
Semantic Chunking

Source Code
    ↓
AST / Syntax-Aware Chunking

Complex PDFs
    ↓
Element-Aware Document Chunking
```

Choosing a chunking strategy therefore depends on the document structure, retrieval task, embedding model, context requirements, and the type of information that needs to be preserved.

---

## RAG Perspective

Chunking sits between document processing and retrieval:

```text
Raw Document
      ↓
Document Parsing
      ↓
Chunking
      ↓
Metadata
      ↓
Embeddings
      ↓
Vector Database
      ↓
Retrieval
      ↓
LLM Context
```

Poor chunk boundaries can separate related information, destroy useful structure, or introduce unnecessary context.

Good chunking attempts to balance:

* semantic coherence
* chunk size
* structural boundaries
* metadata preservation
* retrieval quality
* model token limits

---

## Technologies Used

The experiments across this repository use tools including:

* Python
* LangChain
* LlamaIndex
* Unstructured
* Tree-sitter
* Hugging Face embeddings
* Sentence Transformers
* ChromaDB
* tiktoken
* PyPDF

Different sections use different tools depending on the chunking problem being explored.

---

## Project Goal

This repository is a practical learning and experimentation project focused on understanding **chunking as an engineering decision in RAG systems**.

The implementations are intentionally separated by strategy so that each approach can be studied, tested, and evaluated independently before deciding where it fits in a production RAG pipeline.

---

## License

This project is available under the [MIT License](./LICENSE).
