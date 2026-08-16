import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter


with open("data/session1_text.txt", "r", encoding="utf-8") as file:
    text = file.read()


encoding = tiktoken.get_encoding("cl100k_base")


splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base",
    chunk_size=50,
    chunk_overlap=10,
)


chunks = splitter.split_text(text)


print(f"Original characters: {len(text)}")
print(f"Original tokens: {len(encoding.encode(text))}")
print(f"Number of chunks: {len(chunks)}")


for i, chunk in enumerate(chunks, start=1):

    token_count = len(encoding.encode(chunk))

    print("\n" + "=" * 60)
    print(f"CHUNK {i}")
    print(f"Characters : {len(chunk)}")
    print(f"Tokens     : {token_count}")
    print("=" * 60)

    print(chunk)