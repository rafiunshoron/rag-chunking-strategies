from pathlib import Path
from llama_index.core import SimpleDirectoryReader


# --------------------------------------------------
# 1. Build the PDF path
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

pdf_path = PROJECT_ROOT / "data" / "nist_ai_rmf.pdf"


# --------------------------------------------------
# 2. Load the PDF
# --------------------------------------------------

reader = SimpleDirectoryReader(
    input_files=[str(pdf_path)]
)

documents = reader.load_data()


# --------------------------------------------------
# 3. Inspect what was loaded
# --------------------------------------------------

print("Number of documents loaded:", len(documents))


for i, document in enumerate(documents[:3], start=1):

    print("\n" + "=" * 70)
    print(f"DOCUMENT {i}")
    print("=" * 70)

    print("\nMETADATA:")
    print(document.metadata)

    print("\nTEXT:")
    print(document.text[:1000])