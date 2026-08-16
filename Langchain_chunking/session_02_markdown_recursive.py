from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


# Load Markdown
with open("data/session2_markdown.md", "r", encoding="utf-8") as file:
    markdown_text = file.read()


# Step 1: Split using Markdown structure
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on
)

markdown_chunks = markdown_splitter.split_text(markdown_text)


# Step 2: Split large sections recursively
recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=250,
    chunk_overlap=40,
    length_function=len,
)

final_chunks = recursive_splitter.split_documents(markdown_chunks)


print(f"Markdown sections: {len(markdown_chunks)}")
print(f"Final chunks: {len(final_chunks)}")


for i, chunk in enumerate(final_chunks, start=1):

    print("\n" + "=" * 70)
    print(f"CHUNK {i}")
    print(f"Length: {len(chunk.page_content)} characters")
    print("=" * 70)

    print("METADATA:")
    print(chunk.metadata)

    print("\nCONTENT:")
    print(chunk.page_content)