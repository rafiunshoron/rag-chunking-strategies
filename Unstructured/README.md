# Unstructured PDF Chunking

A simple hands-on study of **PDF parsing and chunking with Unstructured**.

## What I Learned

The basic flow is:

```text
PDF
 ↓
Partitioning
 ↓
Structural Elements
 ↓
Chunking
```

Unstructured first identifies elements such as:

```text
Title
NarrativeText
ListItem
Table
Image
FigureCaption
```

Then those elements can be chunked.

## Dataset

I used the official sample PDF:

```text
layout-parser-paper.pdf
```

Source:

```text
https://github.com/Unstructured-IO/unstructured/blob/main/test_unstructured_ingest/example-docs/layout-parser-paper.pdf
```

## Setup

```bash
pip install "unstructured[pdf]"
pip install unstructured-inference
```

Tesseract OCR was also installed for the `hi_res` PDF strategy.

## Partitioning

```python
from unstructured.partition.pdf import partition_pdf

elements = partition_pdf(
    filename="data/layout-parser-paper.pdf",
    strategy="hi_res",
)
```

This PDF produced **174 structural elements** including text, titles, lists, tables, images, and figure captions.

## Basic Chunking

```python
from unstructured.chunking.basic import chunk_elements

chunks = chunk_elements(
    elements,
    max_characters=1000,
    new_after_n_chars=800,
)
```

`new_after_n_chars=800` is the preferred chunk size, while `max_characters=1000` is the hard limit.

The 174 elements became **63 chunks**.

## By-Title Chunking

```python
from unstructured.chunking.title import chunk_by_title

chunks = chunk_by_title(
    elements,
    max_characters=1000,
    new_after_n_chars=800,
)
```

`by_title` also respects detected section titles, making it useful for structured documents such as research papers and books.

## Main Takeaway

Unstructured does not treat a PDF as one large text string.

Instead:

```text
PDF
 ↓
Detect structural elements
 ↓
Basic / By-Title chunking
 ↓
RAG-ready chunks
```

This makes it useful for document-aware chunking of PDFs containing text, headings, lists, tables, and images.
