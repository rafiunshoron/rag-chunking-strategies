from langchain_text_splitters import HTMLSectionSplitter


with open("data/session3_html.html", "r", encoding="utf-8") as file:
    html_text = file.read()


headers_to_split_on = [
    ("h1", "Header 1"),
    ("h2", "Header 2"),
    ("h3", "Header 3"),
]


splitter = HTMLSectionSplitter(
    headers_to_split_on=headers_to_split_on
)


chunks = splitter.split_text(html_text)


print(f"Number of chunks: {len(chunks)}")


for i, chunk in enumerate(chunks, start=1):

    print("\n" + "=" * 70)
    print(f"CHUNK {i}")
    print("=" * 70)

    print("METADATA:")
    print(chunk.metadata)

    print("\nCONTENT:")
    print(chunk.page_content)