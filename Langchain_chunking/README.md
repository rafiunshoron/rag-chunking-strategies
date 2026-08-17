# LangChain Chunking for RAG

A practical implementation and evaluation of **LangChain text-splitting strategies for Retrieval-Augmented Generation (RAG)**.

This module explores how LangChain handles different types of content, including:

* plain text
* token-based text
* Markdown
* HTML
* JSON
* Python source code
* real PDF documents

The experiments move from basic chunking behavior to a complete retrieval benchmark using embeddings and a vector database.

---

## Project Objective

Chunking directly affects the quality of information retrieved by a RAG system.

This project investigates how different LangChain splitters affect:

* chunk boundaries
* chunk size
* chunk overlap
* token usage
* document structure
* metadata preservation
* structured content
* retrieval performance

The final experiment evaluates chunking as part of a real retrieval pipeline instead of judging chunks only by visual inspection.

---

# Implemented Strategies

| Session | Strategy                   | LangChain Class / Method                                        |
| ------- | -------------------------- | --------------------------------------------------------------- |
| 01      | Character Chunking         | `CharacterTextSplitter`                                         |
| 01      | Recursive Chunking         | `RecursiveCharacterTextSplitter`                                |
| 01      | Token Chunking             | `TokenTextSplitter`                                             |
| 01      | Recursive Token-Aware      | `.from_tiktoken_encoder()`                                      |
| 02      | Markdown Structure-Aware   | `MarkdownHeaderTextSplitter`                                    |
| 02      | Markdown + Recursive       | `MarkdownHeaderTextSplitter` + `RecursiveCharacterTextSplitter` |
| 03      | HTML Header-Aware          | `HTMLHeaderTextSplitter`                                        |
| 03      | HTML Section-Aware         | `HTMLSectionSplitter`                                           |
| 03      | HTML Semantic Preservation | `HTMLSemanticPreservingSplitter`                                |
| 04      | JSON Structure-Aware       | `RecursiveJsonSplitter`                                         |
| 04      | JSON List Handling         | `convert_lists=True`                                            |
| 05      | Generic Code Chunking      | `RecursiveCharacterTextSplitter`                                |
| 05      | Python-Aware Code Chunking | `.from_language(Language.PYTHON)`                               |
| 06      | Real PDF Benchmark         | Recursive Character vs Token-Aware                              |
| 06      | Retrieval Evaluation       | Hit@3 + MRR                                                     |

---

# Project Structure

```text
Langchain_chunking/
│
├── README.md
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

# Session 01 — Basic Text Chunking

Session 01 compares the main general-purpose text splitting approaches.

## Character Chunking

```python
CharacterTextSplitter
```

`CharacterTextSplitter` splits text using a configured separator.

The experiment demonstrated an important limitation.

For example:

```text
chunk_size = 250

Paragraph = 524 characters
```

If the selected separator does not occur inside that paragraph, the splitter may leave the entire 524-character piece intact.

```text
Oversized paragraph
        ↓
No configured separator
        ↓
Cannot split further
        ↓
Chunk exceeds target size
```

---

## Recursive Chunking

```python
RecursiveCharacterTextSplitter
```

Recursive splitting solves this problem by progressively trying smaller boundaries.

Typical fallback order:

```text
Paragraph
   ↓
Newline
   ↓
Space
   ↓
Character
```

This makes it more suitable for general RAG text because it attempts to preserve natural boundaries while still controlling chunk size.

---

## Token Chunking

```python
TokenTextSplitter
```

Instead of measuring chunk size in characters, this splitter works with tokenizer tokens.

This is useful because LLMs and embedding models operate using tokens rather than raw character counts.

---

## Recursive + Token-Aware Chunking

```python
RecursiveCharacterTextSplitter.from_tiktoken_encoder()
```

This combines:

```text
Recursive boundary selection
          +
Token-based size measurement
```

The recursive splitter decides **where to split**, while the tokenizer determines **how chunk size is measured**.

---

# Session 02 — Markdown Structure-Aware Chunking

Markdown already contains useful document hierarchy:

```markdown
# Main Topic
## Section
### Subsection
```

The experiment uses:

```python
MarkdownHeaderTextSplitter
```

Instead of treating Markdown only as plain text, the splitter preserves header information as metadata.

Example:

```python
{
    "Header 1": "RAG Systems",
    "Header 2": "Chunking",
    "Header 3": "Recursive Chunking"
}
```

A second experiment combines:

```text
MarkdownHeaderTextSplitter
            ↓
RecursiveCharacterTextSplitter
```

This provides both:

* structural metadata preservation
* chunk-size control for oversized sections

---

# Session 03 — HTML Structure-Aware Chunking

Three HTML-specific approaches were implemented.

## HTML Header Splitting

```python
HTMLHeaderTextSplitter
```

Uses HTML heading elements such as:

```html
<h1>
<h2>
<h3>
```

to identify logical document boundaries.

---

## HTML Section Splitting

```python
HTMLSectionSplitter
```

Groups content into larger logical HTML sections instead of treating the document as ordinary text.

---

## HTML Semantic Preservation

```python
HTMLSemanticPreservingSplitter
```

This splitter can preserve important HTML structures such as:

```html
<table>
<ul>
```

even when they exceed the configured chunk-size target.

For example:

```text
max_chunk_size = 50

Normal text     → approximately ≤ 50 characters
Preserved table → may exceed 50 characters
Preserved list  → may exceed 50 characters
```

This behavior prevents useful structured information from being broken into meaningless fragments.

The experiment also demonstrated the importance of fine fallback separators:

```python
["\n\n", "\n", ". ", "! ", "? ", " ", ""]
```

Without smaller fallbacks such as spaces and individual characters, ordinary text can also remain larger than the requested chunk size.

---

# Session 04 — JSON Structure-Aware Chunking

JSON contains nested key-value relationships that should not always be treated as raw text.

The project uses:

```python
RecursiveJsonSplitter
```

Example structure:

```text
user
├── name
├── email
├── address
│   ├── city
│   └── geo
└── company
```

The splitter recursively follows this structure while creating smaller JSON chunks.

---

## JSON List Handling

The project also tests:

```python
convert_lists=True
```

This is useful for list-heavy JSON structures such as:

```text
users[]
products[]
articles[]
transactions[]
```

It gives the splitter more structural units to work with when dividing large JSON arrays.

---

# Session 05 — Code-Aware Chunking

Source code has different logical boundaries from normal prose.

The experiment compares:

```python
RecursiveCharacterTextSplitter
```

against:

```python
RecursiveCharacterTextSplitter.from_language(
    Language.PYTHON
)
```

The Python-aware configuration uses language-specific separators that give priority to constructs such as:

```python
class
def
```

This generally creates more meaningful boundaries for source-code retrieval.

---

## Observed Limitation

Python-aware recursive splitting is still **separator-based**.

It is not a Python AST parser.

Therefore, if a function or class exceeds the configured chunk size, the splitter may still divide that code block.

The experiment demonstrated this when a standalone:

```python
return documents
```

became a separate chunk.

This shows that language-aware splitting improves code boundaries but does not guarantee complete syntactic units.

---

# Session 06 — Real-World RAG Chunking Benchmark

The final experiment evaluates chunking using the **Nike 2023 10-K annual report**.

The PDF contains:

```text
107 pages
```

Two chunking strategies are compared under the same retrieval pipeline.

---

## Benchmark Architecture

```text
Nike 2023 10-K PDF
        ↓
PDF Text Extraction
        ↓
Chunking Strategy
        ↓
SentenceTransformer Embeddings
        ↓
Chroma Vector Database
        ↓
Top-3 Similarity Search
        ↓
Retrieval Evaluation
```

The embedding model, vector database, retrieval configuration, and test questions remain the same.

The main experimental variable is the **chunking configuration**.

---

# Strategy A — Recursive Character

```python
RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
```

# Strategy B — Recursive Token-Aware

```python
RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base",
    chunk_size=250,
    chunk_overlap=50
)
```

---

# Chunk Statistics

| Metric             | Recursive Character | Recursive Token-Aware |
| ------------------ | ------------------: | --------------------: |
| Number of chunks   |                 516 |                   438 |
| Average characters |               847.2 |                 974.8 |
| Average tokens     |               180.7 |                 208.1 |
| Maximum characters |                 999 |                  1494 |
| Maximum tokens     |                 417 |                   249 |

The comparison demonstrates an important difference between characters and tokens.

```text
Recursive Character
Maximum tokens = 417

Recursive Token-Aware
Maximum tokens = 249
```

The token-aware strategy produced some chunks with more characters but maintained a much more predictable token ceiling.

This demonstrates that:

```text
Character count ≠ Token count
```

---

# Retrieval Benchmark

The benchmark uses manually verified questions from the Nike annual report.

Example queries:

* How many significant distribution centers does Nike have in the United States?
* When was Nike incorporated?
* What was Nike's revenue in fiscal 2023?
* How was Nike's gross margin impacted in fiscal 2023?

For each query:

```text
Query
  ↓
Top-3 Similarity Search
  ↓
Retrieved Pages
  ↓
Evaluation
```

---

## Evaluation Metrics

### Hit@3

Measures whether expected relevant evidence appears somewhere in the top three retrieved results.

```text
Relevant result in Top 3 → HIT
No relevant result        → MISS
```

### Mean Reciprocal Rank — MRR

Measures how highly the expected result is ranked.

```text
Rank 1 → 1.00
Rank 2 → 0.50
Rank 3 → 0.33
```

---

# Benchmark Results

| Strategy              |    Hit@3 |      MRR |
| --------------------- | -------: | -------: |
| Recursive Character   | **1.00** | **1.00** |
| Recursive Token-Aware | **1.00** | **0.88** |

Both strategies retrieved expected evidence within the top three results for every benchmark question.

Under the initial page-level ground-truth labels, the Recursive Character configuration achieved the higher MRR.

However, the experiment also revealed an important evaluation limitation.

For the fiscal 2023 revenue question:

```text
Expected page → 35

Token-aware rank 1 → page 30
Token-aware rank 2 → page 35
```

Page 30 already contained the correct fiscal 2023 revenue information.

Therefore, the lower MRR does not necessarily mean that the token-aware retriever returned worse evidence.

Instead, it shows that a question can have **multiple valid evidence locations**.

---

# Key Findings

The project produced several practical observations.

### 1. Chunk size alone is not sufficient

Good chunking also depends on meaningful boundaries and context preservation.

### 2. Recursive splitting is more flexible than single-separator splitting

It can progressively fall back to smaller boundaries when necessary.

### 3. Character count and token count behave differently

Token-aware chunking provides more predictable model-facing chunk sizes.

### 4. Existing document structure should be used when possible

Useful boundaries already exist in:

```text
Markdown → headings
HTML     → sections, tables, lists
JSON     → nested objects
Code     → classes and functions
```

### 5. Semantic structure can be more important than strict size limits

For example, splitting a table only to enforce a chunk-size target may destroy useful relationships between its values.

### 6. Chunking should be evaluated through retrieval

```text
Chunking
   ↓
Embedding
   ↓
Retrieval
   ↓
Evaluation
```

Visual inspection alone cannot determine whether a chunking configuration improves a RAG system.

### 7. Evaluation ground truth also matters

A query may have more than one relevant passage or page.

Therefore, retrieval metrics should be interpreted together with the quality of the relevance labels.

---

# Setup

Clone the repository:

```bash
git clone https://github.com/rafiunshoron/rag-chunking-strategies.git
```

Enter this module:

```bash
cd rag-chunking-strategies/Langchain_chunking
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

---

# Running the Experiments

Character splitting:

```bash
python session_01_character.py
```

Recursive splitting:

```bash
python session_01_recursive.py
```

Token-aware recursive splitting:

```bash
python session_01_recursive_token.py
```

Markdown:

```bash
python session_02_markdown_recursive.py
```

HTML semantic preservation:

```bash
python session_03_html_semantic.py
```

JSON:

```bash
python session_04_json.py
```

Python-aware code splitting:

```bash
python session_05_python_aware.py
```

Final retrieval benchmark:

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

Official LangChain documentation used throughout the project:

* [Text Splitters Overview](https://docs.langchain.com/oss/python/integrations/splitters)
* [Recursive Character Text Splitter](https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter)
* [Character Text Splitter](https://docs.langchain.com/oss/python/integrations/splitters/character_text_splitter)
* [Token-Based Splitting](https://docs.langchain.com/oss/python/integrations/splitters/split_by_token)
* [Markdown Header Splitting](https://docs.langchain.com/oss/python/integrations/splitters/markdown_header_metadata_splitter)
* [HTML Splitting](https://docs.langchain.com/oss/python/integrations/splitters/split_html)
* [Recursive JSON Splitting](https://docs.langchain.com/oss/python/integrations/splitters/recursive_json_splitter)
* [Code Splitting](https://docs.langchain.com/oss/python/integrations/splitters/code_splitter)

---

## Summary

This module implements LangChain chunking strategies across several document types and connects those experiments to a real retrieval benchmark.

The complete workflow is:

```text
Document
   ↓
LangChain Chunking
   ↓
Embedding
   ↓
Vector Database
   ↓
Similarity Search
   ↓
Retrieval Evaluation
```

The project demonstrates that chunking is not simply a preprocessing operation. It is an engineering decision that directly influences the information made available to the retrieval and generation stages of a RAG system.
