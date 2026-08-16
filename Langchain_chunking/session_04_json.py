import json

from langchain_text_splitters import RecursiveJsonSplitter


# Load JSON
with open("data/session4_users.json", "r", encoding="utf-8") as file:
    json_data = json.load(file)


# Create splitter
splitter = RecursiveJsonSplitter(
    max_chunk_size=200
)


# Split JSON into smaller JSON dictionaries
chunks = splitter.split_json(json_data=json_data)


print(f"Number of chunks: {len(chunks)}")


for i, chunk in enumerate(chunks, start=1):

    chunk_text = json.dumps(chunk)

    print("\n" + "=" * 70)
    print(f"CHUNK {i}")
    print(f"Length: {len(chunk_text)} characters")
    print("=" * 70)

    print(json.dumps(chunk, indent=2))