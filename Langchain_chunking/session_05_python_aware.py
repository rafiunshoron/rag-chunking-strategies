from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    Language,
)


with open("data/session5_code.py", "r", encoding="utf-8") as file:
    code = file.read()


splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=300,
    chunk_overlap=0,
)


chunks = splitter.split_text(code)


print(f"Number of chunks: {len(chunks)}")


for i, chunk in enumerate(chunks, start=1):

    print("\n" + "=" * 70)
    print(f"CHUNK {i}")
    print(f"Length: {len(chunk)} characters")
    print("=" * 70)

    print(chunk)