from langchain_text_splitters import CharacterTextSplitter


# Load our text file
with open("data/session1_text.txt", "r", encoding="utf-8") as file:
    text = file.read()


# Create the splitter
splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=250,
    chunk_overlap=40,
    length_function=len,
)


# Split the text
chunks = splitter.split_text(text)


# Print the result
print(f"Original document length: {len(text)} characters")
print(f"Number of chunks: {len(chunks)}")


for i, chunk in enumerate(chunks, start=1):
    print("\n" + "=" * 60)
    print(f"CHUNK {i}")
    print(f"Length: {len(chunk)} characters")
    print("=" * 60)
    print(chunk)