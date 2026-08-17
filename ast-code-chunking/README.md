# AST-Aware Code Chunking with Tree-sitter

A structure-aware Python code chunking implementation for Retrieval-Augmented Generation (RAG).

This project uses **Tree-sitter** to parse Python source code into a syntax tree and applies custom hierarchical chunking logic to preserve meaningful structures such as classes, functions, methods, and statements.

> Tree-sitter technically produces a concrete syntax tree (CST), but here it is used in an AST-like way for structural code chunking.

---

## Why Tree-sitter?

LangChain provides language-aware recursive splitting, but it is still mainly **separator-based**.

Tree-sitter actually parses programming-language grammar and identifies real structures such as:

```text
class_definition
function_definition
decorated_definition
```

This allows chunking to follow actual code structure instead of relying only on patterns such as `def`, `class`, or newlines.

---

## Chunking Strategy

The main idea is:

```text
Parse first
   ↓
Understand code structure
   ↓
Keep meaningful units intact
   ↓
Split only when they become too large
```

The chunker follows this hierarchy:

```text
Class
  ↓
Method
  ↓
Statement
  ↓
Line fallback
  ↓
Character fallback
```

If a class or function is already within the configured size limit, it is kept as one chunk.

If it is too large, the chunker recursively moves deeper into the syntax tree.

---

## Architecture

```text
                Python Source File
                        │
                        ▼
              Tree-sitter Parser
                        │
                        ▼
                  Syntax Tree
                        │
                        ▼
              Syntax Validation
                        │
                        ▼
           Detect Structural Nodes
          ┌──────────┬──────────┐
          │          │          │
        Class     Function   Module Code
          │          │          │
          ▼          ▼          ▼
       Size Check  Size Check  Group Context
          │          │
     ┌────┴────┐ ┌───┴────┐
     │         │ │        │
   Small     Large Small  Large
     │         │ │        │
     ▼         ▼ ▼        ▼
 Keep Whole  Methods    Statements
                │           │
                ▼           ▼
             Size Check   Size Check
                            │
                            ▼
                     Oversized Leaf
                            │
                            ▼
                     Line Fallback
                            │
                            ▼
                  Character Fallback
                            │
                            ▼
                    Final Code Chunks
                            │
                            ▼
                     Attach Metadata
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
      Chunk ID          File Path        Parent Scope
      Line Range        Node Type        Chunk Index
      Language          Char Count       Syntax Valid
                            │
                            ▼
                       Ready for RAG
```

---

## Core Processing Flow

```text
chunk_file()
   │
   ├── Validate file
   ├── Parse with Tree-sitter
   ├── Validate syntax
   │
   └── extract_code_chunks()
            │
            └── split_node()
                   │
                   ├── split_large_class()
                   │       └── Methods
                   │
                   └── split_large_function()
                           └── Statements
                                   │
                                   └── split_oversized_node()
```

Tree-sitter handles the **code structure**, while the custom recursive logic controls **how deeply the structure should be split**.

---

## Features

* Tree-sitter-based Python parsing
* structure-aware chunk boundaries
* recursive class-to-method splitting
* function-to-statement splitting
* decorator support
* `async def` support
* nested definition handling
* module-level code preservation
* syntax validation
* configurable maximum chunk size
* parent-scope metadata
* line-number metadata
* deterministic chunk IDs
* automated testing with `pytest`

---

## Project Structure

```text
ast-code-chunking/
│
├── chunker.py
├── sample_code.py
├── demo_chunker.py
├── inspect_tree.py
├── pytest.ini
│
├── tests/
│   └── test_chunker.py
│
└── README.md
```

---

## Installation

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install tree-sitter tree-sitter-python pytest
```

---

## Usage

```python
from chunker import chunk_file

chunks = chunk_file(
    "sample_code.py",
    max_chunk_size=500,
)

for chunk in chunks:
    print(chunk["name"])
    print(chunk["type"])
    print(chunk["parent_scope"])
    print(chunk["content"])
```

---

## Chunk Metadata

Each chunk includes metadata such as:

```text
chunk_id
chunk_index
file_path
file_name
language
type
name
parent_scope
start_line
end_line
char_count
syntax_valid
```

This information can later be used during indexing and retrieval in a code RAG pipeline.

---

## Testing

Run:

```bash
python -m pytest -v
```

The current test suite verifies:

```text
✓ Small functions remain intact
✓ Large classes split into methods
✓ Parent scope is preserved
✓ Decorators are preserved
✓ Async functions are detected
✓ Maximum chunk size is respected
✓ Chunk IDs are deterministic
✓ Invalid Python raises an error
```

Current result:

```text
8 passed
```

---

## Tech Stack

* Python
* Tree-sitter
* tree-sitter-python
* pytest

---

## Design Trade-off

This approach provides more control over code structure than plain separator-based splitting.

The trade-off is additional implementation complexity and maintenance.

For code-oriented RAG systems, the benefit is that chunk boundaries can follow real source-code structures rather than arbitrary text boundaries.
