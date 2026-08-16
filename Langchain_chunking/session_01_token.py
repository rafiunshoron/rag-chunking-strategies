from langchain_text_splitters import TokenTextSplitter


# Load the same text
with open("data/session1_text.txt", "r", encoding="utf-8") as file:
    text = file.read()


# Create token splitter
splitter = TokenTextSplitter(
    encoding_name="cl100k_base",
    chunk_size=50,
    chunk_overlap=10,
)


# Split
chunks = splitter.split_text(text)


# Print results
print(f"Number of chunks: {len(chunks)}")


for i, chunk in enumerate(chunks, start=1):
    print("\n" + "=" * 60)
    print(f"CHUNK {i}")
    print(f"Characters: {len(chunk)}")
    print("=" * 60)
    print(chunk)