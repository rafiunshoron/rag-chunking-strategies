# RAG Systems

Retrieval-Augmented Generation combines retrieval with language generation.

## Chunking

Chunking divides large documents into smaller units that can be retrieved independently.

### Recursive Chunking

Recursive chunking tries large natural boundaries first, such as paragraphs. If a piece is still too large, it tries smaller boundaries.

This strategy is useful because documents naturally contain different levels of structure. A document may contain paragraphs, sentences, words, and characters. Instead of immediately cutting text at an arbitrary character position, recursive splitting tries to preserve the largest meaningful unit possible.

For example, a paragraph may contain an explanation of how embeddings are generated and stored inside a vector database. If the paragraph is too large for the configured chunk size, the splitter can move to smaller separators such as newlines or spaces. This allows the system to create smaller chunks while still trying to preserve meaningful textual boundaries.

### Token-Aware Chunking

Token-aware chunking measures chunk size using tokenizer tokens instead of raw characters.

## Retrieval

Retrieval searches the indexed chunks and selects information relevant to the user's query.

### Dense Retrieval

Dense retrieval converts queries and documents into embedding vectors and compares them using vector similarity.

