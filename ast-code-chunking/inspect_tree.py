from tree_sitter import Language, Parser
import tree_sitter_python as tspython


# Load Python grammar
PYTHON_LANGUAGE = Language(tspython.language())


# Create parser
parser = Parser(PYTHON_LANGUAGE)


# Read source code as bytes
with open("sample_code.py", "rb") as file:
    source_code = file.read()


# Parse source code
tree = parser.parse(source_code)


# Get root node
root = tree.root_node


print(root)

print("\nROOT TYPE:")
print(root.type)

print("\nTOP-LEVEL CHILDREN:")

for child in root.children:
    print(
        child.type,
        child.start_point,
        child.end_point
    )