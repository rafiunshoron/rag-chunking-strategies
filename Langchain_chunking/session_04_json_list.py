import json

from langchain_text_splitters import RecursiveJsonSplitter


with open("data/session4_products.json", "r", encoding="utf-8") as file:
    json_data = json.load(file)


splitter = RecursiveJsonSplitter(
    max_chunk_size=200
)


chunks = splitter.split_json(
    json_data=json_data,
    convert_lists=True
)


print(f"Number of chunks: {len(chunks)}")


for i, chunk in enumerate(chunks, start=1):

    print("\n" + "=" * 70)
    print(f"CHUNK {i}")
    print("=" * 70)

    print(json.dumps(chunk, indent=2))