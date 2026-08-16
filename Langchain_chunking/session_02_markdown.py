from langchain_text_splitters import MarkdownHeaderTextSplitter


# Load markdown document
with open("data/session2_markdown.md", "r", encoding="utf-8") as file:
    markdown_text = file.read()


# Define the Markdown hierarchy we care about
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]


# Create splitter
splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on
)


# Split document
chunks = splitter.split_text(markdown_text)


print(f"Number of chunks: {len(chunks)}")


for i, chunk in enumerate(chunks, start=1):

    print("\n" + "=" * 70)
    print(f"CHUNK {i}")
    print("=" * 70)

    print("METADATA:")
    print(chunk.metadata)

    print("\nCONTENT:")
    print(chunk.page_content)