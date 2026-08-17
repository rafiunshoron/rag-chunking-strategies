# AST-Aware Code Chunking with Tree-sitter

A structure-aware Python code chunking implementation for Retrieval-Augmented Generation (RAG).

Instead of treating source code as plain text, this project uses **Tree-sitter** to parse Python source code into a syntax tree and then applies a custom hierarchical chunking strategy that preserves logical structures such as classes, functions, methods, and statements.

> Tree-sitter technically produces a concrete syntax tree (CST). In this project, it is used in an AST-like manner for structural code chunking.

---

## Why Structure-Aware Code Chunking?

Traditional text splitters usually work with:

* characters
* newlines
* separators
* token limits

This works well for normal text, but source code contains additional structure.

For example:

```python
class UserService:

    def create_user(self):
        ...

    def delete_user(self):
        ...
```

A plain text splitter may break this code based mainly on size or separators.

This project first parses the code structure and then chunks according to actual syntax nodes.

```text
Source Code
     ↓
Tree-sitter Parser
     ↓
Syntax Tree
     ↓
Class / Function / Method
     ↓
Size Check
     ↓
Recursive Structural Splitting
     ↓
Final Code Chunks
```

---

## Why Tree-sitter Instead of Only LangChain's Code Splitter?

LangChain provides language-aware recursive splitting through:

```python
RecursiveCharacterTextSplitter.from_language(...)
```

It improves code splitting by using language-specific separators.

However, it is still primarily **separator-based**.

Tree-sitter actually parses the programming language grammar and identifies real syntax structures such as:

```text
class_definition
function_definition
decorated_definition
```

This allows the chunking strategy to work directly with the source-code hierarchy rather than relying only on textual patterns.

---

## Chunking Strategy

The chunker follows a hierarchical approach.

```text
Python File
   ↓
Parse with Tree-sitter
   ↓
Top-level structural unit
   ↓
Is it within max_chunk_size?
   │
   ├── Yes → Keep intact
   │
   └── No
        ↓
   Inspect structure
        ↓
   Class → Methods
        ↓
   Function → Statements
        ↓
   Oversized statement → Lines
        ↓
   Oversized line → Character fallback
```

The important principle is:

> Preserve the largest meaningful code structure possible before splitting into smaller units.

---

## Features

* Tree-sitter-based Python parsing
* structure-aware chunk boundaries
* recursive class-to-method splitting
* oversized function splitting by statements
* decorated function support
* `async def` support
* nested definition handling
* module-level code and import preservation
* parent-scope metadata
* source line tracking
* deterministic chunk IDs
* configurable maximum chunk size
* syntax-error validation
* fallback splitting for oversized leaf nodes
* automated test coverage with `pytest`

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

### `chunker.py`

Contains the main Tree-sitter parsing and chunking implementation.

### `sample_code.py`

Example Python source file used to inspect chunking behavior.

### `inspect_tree.py`

Displays the Tree-sitter syntax tree and top-level syntax nodes.

### `demo_chunker.py`

Runs the chunker on the sample source file and prints generated chunks and metadata.

### `tests/test_chunker.py`

Automated tests for the core chunking behavior.

---

## Installation

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate it

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install tree-sitter tree-sitter-python pytest
```

---

## Basic Usage

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

## Example Chunk Metadata

Each generated chunk contains metadata similar to:

```python
{
    "chunk_id": "21e84fe91c036d46bb8a846a",
    "chunk_index": 3,
    "file_path": "sample_code.py",
    "file_name": "sample_code.py",
    "language": "python",
    "type": "function_definition",
    "name": "create_user",
    "parent_scope": "UserService",
    "start_line": 20,
    "end_line": 35,
    "char_count": 420,
    "syntax_valid": True,
    "content": "def create_user(...): ..."
}
```

This metadata can later be useful during indexing and retrieval in a code RAG system.

---

## Recursive Structural Splitting

The main difference between this implementation and normal recursive text splitting is **what is being recursively traversed**.

A regular recursive text splitter might do:

```text
paragraph
   ↓
newline
   ↓
space
   ↓
character
```

This implementation primarily follows the parsed code hierarchy:

```text
class
   ↓
method
   ↓
statement
```

For example:

```text
UserService
│
├── create_user()
├── get_user()
└── delete_user()
```

If the entire `UserService` class fits within the configured chunk size, it can remain one chunk.

If it is too large, the chunker descends into its methods and processes those independently.

---

## Syntax Validation

Before chunking, the source file is parsed with Tree-sitter.

With:

```python
strict=True
```

files containing parser errors raise a `SyntaxError`.

Example:

```python
chunks = chunk_file(
    "sample_code.py",
    max_chunk_size=500,
    strict=True,
)
```

Malformed source code can also be processed with:

```python
strict=False
```

In that case:

```python
chunk["syntax_valid"]
```

indicates whether Tree-sitter detected syntax errors.

---

## Testing

Run the full test suite from the project root:

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

## Design Trade-off

This approach provides more structural control than a simple text-based splitter, but that control comes with additional implementation complexity.

```text
Tree-sitter + custom structural recursion

Advantages
├── real syntax boundaries
├── hierarchical splitting
├── richer metadata
└── fine-grained control

Trade-offs
├── more implementation code
├── language grammar dependency
├── more edge cases
└── more testing and maintenance
```

For code-oriented RAG systems, this trade-off can be useful when preserving source-code structure is more important than using a simple generic text-splitting pipeline.

---

## Technologies

* Python
* Tree-sitter
* tree-sitter-python
* pytest

---

## License

This project can be used as a learning and experimentation implementation for structure-aware code chunking.
