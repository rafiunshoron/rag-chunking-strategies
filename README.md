# RAG Chunking Strategies

A practical implementation and evaluation project for exploring **document chunking strategies in Retrieval-Augmented Generation (RAG)** using LangChain.

The project demonstrates how different chunking approaches handle plain text, tokens, Markdown, HTML, JSON, source code, and real-world PDF documents. It also includes a retrieval benchmark to measure how chunking choices affect search performance in a RAG pipeline.

---

## Project Overview

Chunking is a critical stage in a RAG pipeline because the way documents are divided directly affects:

* retrieval quality
* context preservation
* token usage
* document structure
* metadata preservation
* vector database indexing
* downstream LLM responses

This project implements multiple LangChain chunking strategies and compares their behavior through controlled examples and a final real-world retrieval experiment.

---

## Project Pipeline

```text
Raw Document
      ↓
Document Loading
      ↓
Chunking Strategy
      ↓
Chunk Inspection
      ↓
Embedding Generation
      ↓
Chroma Vector Database
      ↓
Similarity Search
      ↓
Retrieval Evaluation
```

---

## Implemented Chunking Strategies

| Session | Strategy                          | LangChain Class / Method                                        |
| ------- | --------------------------------- | --------------------------------------------------------------- |
| 01      | Character Chunking                | `CharacterTextSplitter`                                         |
| 01      | Recursive Chunking                | `RecursiveCharacterTextSplitter`                                |
| 01      | Token Chunking                    | `TokenTextSplitter`                                             |
| 01      | Recursive Token-Aware Chunking    | `.from_tiktoken_encoder()`                                      |
| 02      | Markdown Structure-Aware Chunking | `MarkdownHeaderTextSplitter`                                    |
| 02      | Markdown + Recursive Chunking     | `MarkdownHeaderTextSplitter` + `RecursiveCharacterTextSplitter` |
| 03      | HTML Header-Aware Chunking        | `HTMLHeaderTextSplitter`                                        |
| 03      | HTML Section-Aware Chunking       | `HTMLSectionSplitter`                                           |
| 03      | HTML Semantic Preservation        | `HTMLSemanticPreservingSplitter`                                |
| 04      | JSON Structure-Aware Chunking     | `RecursiveJsonSplitter`                                         |
| 04      | JSON List Handling                | `convert_lists=True`                                            |
| 05      | Generic Code Chunking             | `RecursiveCharacterTextSplitter`                                |
| 05      | Python-Aware Code Chunking        | `.from_language(Language.PYTHON)`                               |
| 06      | Real PDF Chunking Benchmark       | Recursive Character vs Token-Aware                              |
| 06      | Retrieval Evaluation              | Hit@3 + MRR                                                     |

---

# Repository Structure

```text
rag-chunking-strategies/
│
├── README.md
│
└── Langchain_chunking/
    │
    ├── requirements.txt
    │
    ├── data/
    │   ├── session1_text.txt
    │   ├── session2_markdown.md
    │   ├── session3_html.html
    │   ├── session4_products.json
    │   ├── session4_users.json
    │   ├── session5_code.py
    │   └── nke-10k-2023.pdf
    │
    ├── session_01_character.py
    ├── session_01_recursive.py
    ├── session_01_token.py
    ├── session_01_recursive_token.py
    │
    ├── session_02_markdown.py
    ├── session_02_markdown_recursive.py
    │
    ├── session_03_html_header.py
    ├── session_03_html_section.py
    ├── session_03_html_semantic.py
    │
    ├── session_04_json.py
    ├── session_04_json_list.py
    │
    ├── session_05_normal_recursive.py
    ├── session_05_python_aware.py
    │
    └── session_06_rag_benchmark.py
```

---

# 1. Character-Based Chunking

Implemented using:

```python
CharacterTextSplitter
```

This approach splits text using a configured separator and measures chunk size in characters.

The experiment demonstrates an important limitation: if an oversized piece of text does not contain the configured separator, the resulting chunk may exceed the requested `chunk_size`.

Example:

```text
Configured chunk size: 250 characters

Paragraph size: 524 characters

No configured separator exists inside the paragraph
        ↓
524-character chunk remains
```

---

# 2. Recursive Chunking

Implemented using:

```python
RecursiveCharacterTextSplitter
```

Instead of relying on a single separator, recursive splitting progressively tries smaller boundaries.

```text
Paragraph
   ↓
Newline
   ↓
Space
   ↓
Character
```

This allows the splitter to preserve larger natural boundaries when possible while still controlling oversized chunks.

---

# 3. Token-Based Chunking

Implemented using:

```python
TokenTextSplitter
```

Unlike character-based approaches, chunk size is measured using tokenizer tokens.

This is useful because language models and embedding models operate using **tokens rather than raw character counts**.

The project also combines recursive splitting with token-based measurement:

```python
RecursiveCharacterTextSplitter.from_tiktoken_encoder()
```

This provides:

```text
Natural recursive boundaries
          +
Token-aware size control
```

---

# 4. Markdown Structure-Aware Chunking

Implemented using:

```python
MarkdownHeaderTextSplitter
```

Markdown documents already contain hierarchical structure:

```markdown
# Main Topic
## Section
### Subsection
```

Instead of treating the document as plain text, the splitter preserves this hierarchy as metadata.

Example:

```python
{
    "Header 1": "RAG Systems",
    "Header 2": "Chunking",
    "Header 3": "Recursive Chunking"
}
```

The project also combines Markdown-aware splitting with:

```python
RecursiveCharacterTextSplitter
```

so that large Markdown sections can be recursively divided while retaining their structural metadata.

---

# 5. HTML Structure-Aware Chunking

Three HTML-specific approaches are implemented.

### HTML Header Splitting

```python
HTMLHeaderTextSplitter
```

Uses HTML headings such as:

```html
<h1>
<h2>
<h3>
```

to create logical chunks.

---

### HTML Section Splitting

```python
HTMLSectionSplitter
```

Splits content around larger HTML sections and structural elements.

---

### HTML Semantic Preservation

```python
HTMLSemanticPreservingSplitter
```

This approach can preserve important elements such as:

```html
<table>
<ul>
```

even when they exceed the configured chunk-size target.

Example:

```text
max_chunk_size = 50

Normal text       → split near 50 characters
Preserved table   → may exceed 50 characters
Preserved list    → may exceed 50 characters
```

This prevents important structured information from being broken into meaningless pieces.

The experiment also demonstrates the importance of fallback separators:

```python
["\n\n", "\n", ". ", "! ", "? ", " ", ""]
```

Without smaller fallback separators, ordinary text may also remain larger than the configured maximum.

---

# 6. JSON Structure-Aware Chunking

Implemented using:

```python
RecursiveJsonSplitter
```

Instead of treating JSON as plain text, the splitter works with nested key-value structures.

Example:

```text
user
├── name
├── email
├── address
│   ├── city
│   └── geo
└── company
```

The project also explores:

```python
convert_lists=True
```

which improves splitting behavior for list-heavy JSON structures such as:

```text
users[]
products[]
articles[]
transactions[]
```

---

# 7. Code-Aware Chunking

The project compares generic recursive chunking against Python-aware splitting.

### Generic

```python
RecursiveCharacterTextSplitter
```

### Python-Aware

```python
RecursiveCharacterTextSplitter.from_language(
    Language.PYTHON
)
```

The Python configuration uses language-specific separator rules that give higher priority to code structures such as:

```python
class
def
```

This generally produces more meaningful boundaries for source-code retrieval.

One observed limitation is that language-aware splitting is still **separator-based rather than AST-based**. A large function or class may therefore still be divided when it exceeds the configured chunk size.

---

# 8. Real-World RAG Benchmark

The final experiment evaluates chunking using the **Nike 2023 10-K annual report**, containing 107 PDF pages.

Two chunking configurations are compared under the same retrieval pipeline.

## Benchmark Pipeline

```text
Nike 2023 10-K PDF
        ↓
PDF Text Extraction
        ↓
Chunking
        ↓
SentenceTransformer Embeddings
        ↓
Chroma Vector Database
        ↓
Top-3 Similarity Search
        ↓
Retrieval Evaluation
```

The embedding model, vector database, queries, and retrieval configuration remain unchanged so that the main experimental variable is the **chunking strategy**.

---

## Strategy A — Recursive Character

```python
RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
```

## Strategy B — Recursive Token-Aware

```python
RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base",
    chunk_size=250,
    chunk_overlap=50
)
```

---

## Chunk Statistics

| Metric             | Recursive Character | Recursive Token-Aware |
| ------------------ | ------------------: | --------------------: |
| Number of chunks   |                 516 |                   438 |
| Average characters |               847.2 |                 974.8 |
| Average tokens     |               180.7 |                 208.1 |
| Maximum characters |                 999 |                  1494 |
| Maximum tokens     |                 417 |                   249 |

The results demonstrate an important difference between character-based and token-aware sizing.

```text
Recursive Character
Maximum token count = 417

Recursive Token-Aware
Maximum token count = 249
```

The token-aware strategy produced some chunks with more characters, but maintained a much more predictable token ceiling.

---

# Retrieval Evaluation

The benchmark uses several manually verified questions from the Nike annual report, including:

* How many significant distribution centers does Nike have in the United States?
* When was Nike incorporated?
* What was Nike's revenue in fiscal 2023?
* How was Nike's gross margin impacted in fiscal 2023?

For each query, the system retrieves the top three chunks.

Two metrics are calculated.

### Hit@3

Measures whether expected relevant evidence appears anywhere in the top three retrieved results.

### Mean Reciprocal Rank — MRR

Measures how highly the expected evidence is ranked.

```text
Rank 1 → 1.00
Rank 2 → 0.50
Rank 3 → 0.33
```

---

## Benchmark Results

| Strategy              |    Hit@3 |      MRR |
| --------------------- | -------: | -------: |
| Recursive Character   | **1.00** | **1.00** |
| Recursive Token-Aware | **1.00** | **0.88** |

Both strategies successfully retrieved relevant evidence within the top three results for every benchmark query.

The Recursive Character configuration achieved the higher MRR under the initial page-level ground-truth labels.

However, the experiment also revealed an important evaluation issue.

For the fiscal 2023 revenue question, the token-aware retriever returned a different page at rank 1 that already contained the correct `$51.2 billion` revenue information, while the manually assigned reference page appeared at rank 2.

This demonstrates that a RAG query may have **multiple valid evidence locations**.

Therefore, retrieval metrics should be interpreted together with the quality of the ground-truth annotations.

---

# Key Project Findings

The experiments demonstrate several practical properties of RAG chunking:

1. **Chunk size alone is not enough.**
   Boundary selection strongly affects how much context remains inside each chunk.

2. **Recursive splitting is more flexible than single-separator character splitting.**
   It can progressively fall back to smaller boundaries when needed.

3. **Token-aware chunking provides more predictable model-facing chunk sizes.**
   Character length and token length can differ significantly.

4. **Document structure should be preserved when available.**
   Markdown headings, HTML elements, JSON hierarchy, and programming-language structure can provide better chunk boundaries.

5. **Special document elements sometimes deserve higher priority than strict size limits.**
   Tables and lists may need to remain intact.

6. **Chunking should be evaluated through retrieval.**
   Visually clean chunks do not automatically produce better RAG performance.

7. **Ground-truth quality matters when evaluating retrieval.**
   A question can have multiple relevant passages or pages.

---

# Setup

Clone the repository:

```bash
git clone https://github.com/rafiunshoron/rag-chunking-strategies.git
```

Enter the project:

```bash
cd rag-chunking-strategies/Langchain_chunking
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Running the Experiments

Example:

```bash
python session_01_recursive.py
```

Run the Markdown experiment:

```bash
python session_02_markdown_recursive.py
```

Run the HTML semantic-preservation experiment:

```bash
python session_03_html_semantic.py
```

Run the code-aware experiment:

```bash
python session_05_python_aware.py
```

Run the complete PDF retrieval benchmark:

```bash
python session_06_rag_benchmark.py
```

---

# Technologies

* Python
* LangChain
* `langchain-text-splitters`
* `langchain-huggingface`
* `langchain-chroma`
* Sentence Transformers
* ChromaDB
* tiktoken
* PyPDF
* Markdown
* HTML
* JSON
* VS Code

---

# References

The chunking implementations are based primarily on official LangChain documentation.

* [LangChain Text Splitters Overview](https://docs.langchain.com/oss/python/integrations/splitters)
* [Recursive Character Text Splitter](https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter)
* [Character Text Splitter](https://docs.langchain.com/oss/python/integrations/splitters/character_text_splitter)
* [Token-Based Splitting](https://docs.langchain.com/oss/python/integrations/splitters/split_by_token)
* [Markdown Header Splitting](https://docs.langchain.com/oss/python/integrations/splitters/markdown_header_metadata_splitter)
* [HTML Splitting](https://docs.langchain.com/oss/python/integrations/splitters/split_html)
* [Recursive JSON Splitting](https://docs.langchain.com/oss/python/integrations/splitters/recursive_json_splitter)
* [Code Splitting](https://docs.langchain.com/oss/python/integrations/splitters/code_splitter)

---

## Project Summary

This project implements and evaluates multiple chunking strategies for structured and unstructured data within a Retrieval-Augmented Generation pipeline.

The final architecture connects chunking directly to retrieval evaluation:

```text
Document
   ↓
Chunking
   ↓
Embedding
   ↓
Vector Search
   ↓
Retrieval Evaluation
```

This makes it possible to evaluate chunking as an engineering decision rather than selecting a strategy only through intuition.
