from pathlib import Path
import hashlib

from tree_sitter import Language, Parser, Node
import tree_sitter_python as tspython


# ============================================================
# TREE-SITTER SETUP
# ============================================================

PYTHON_LANGUAGE = Language(tspython.language())
parser = Parser(PYTHON_LANGUAGE)


# Definitions that we consider meaningful code structures
DEFINITION_TYPES = {
    "function_definition",
    "class_definition",
    "decorated_definition",
}


# ============================================================
# BASIC NODE UTILITIES
# ============================================================

def get_node_text(
    node: Node,
    source_code: bytes,
) -> str:
    """
    Return the exact source code represented by a Tree-sitter node.
    """

    return source_code[
        node.start_byte:node.end_byte
    ].decode("utf-8")


def unwrap_definition(node: Node) -> Node:
    """
    Decorated Python functions/classes are wrapped inside a
    decorated_definition node.

    Return the actual function_definition or class_definition.
    """

    if node.type != "decorated_definition":
        return node

    definition = node.child_by_field_name("definition")

    if definition is not None:
        return definition

    # Defensive fallback
    for child in node.named_children:

        if child.type in {
            "function_definition",
            "class_definition",
        }:
            return child

    return node


def get_node_name(
    node: Node,
    source_code: bytes,
) -> str | None:
    """
    Extract the function/class name from a definition.
    """

    actual_node = unwrap_definition(node)

    name_node = actual_node.child_by_field_name("name")

    if name_node is None:
        return None

    return get_node_text(
        name_node,
        source_code,
    )


def get_definition_type(node: Node) -> str:
    """
    Return the underlying definition type.

    Example:

    decorated_definition
        ↓
    function_definition
    """

    return unwrap_definition(node).type


# ============================================================
# CHUNK CREATION
# ============================================================

def create_chunk(
    node: Node,
    source_code: bytes,
    parent_scope: str | None = None,
) -> dict:
    """
    Create a chunk directly from one syntax-tree node.
    """

    content = get_node_text(
        node,
        source_code,
    )

    return {
        "type": get_definition_type(node),
        "name": get_node_name(
            node,
            source_code,
        ),
        "parent_scope": parent_scope,
        "start_line": node.start_point.row + 1,
        "end_line": node.end_point.row + 1,
        "char_count": len(content),
        "content": content,
    }


def create_statement_chunk(
    nodes: list[Node],
    source_code: bytes,
    chunk_type: str,
    name: str | None,
    parent_scope: str | None,
) -> dict:
    """
    Combine several consecutive AST/CST statement nodes
    into one chunk.
    """

    first_node = nodes[0]
    last_node = nodes[-1]

    content = source_code[
        first_node.start_byte:last_node.end_byte
    ].decode("utf-8")

    return {
        "type": chunk_type,
        "name": name,
        "parent_scope": parent_scope,
        "start_line": first_node.start_point.row + 1,
        "end_line": last_node.end_point.row + 1,
        "char_count": len(content),
        "content": content,
    }

def split_oversized_node(
    node: Node,
    source_code: bytes,
    max_chunk_size: int,
    chunk_type: str,
    name: str | None,
    parent_scope: str | None,
) -> list[dict]:

    content = get_node_text(node, source_code)

    lines = content.splitlines(keepends=True)

    chunks = []
    buffer = ""
    buffer_start_line = None

    base_line = node.start_point.row + 1

    for offset, line in enumerate(lines):

        line_number = base_line + offset

        # One individual line is itself too large
        if len(line) > max_chunk_size:

            if buffer:
                chunks.append({
                    "type": chunk_type,
                    "name": name,
                    "parent_scope": parent_scope,
                    "start_line": buffer_start_line,
                    "end_line": line_number - 1,
                    "char_count": len(buffer),
                    "content": buffer,
                })

                buffer = ""
                buffer_start_line = None

            # Final fallback: character slices
            for start in range(0, len(line), max_chunk_size):

                piece = line[
                    start:start + max_chunk_size
                ]

                chunks.append({
                    "type": chunk_type,
                    "name": name,
                    "parent_scope": parent_scope,
                    "start_line": line_number,
                    "end_line": line_number,
                    "char_count": len(piece),
                    "content": piece,
                })

            continue

        # Adding this line would exceed the limit
        if buffer and len(buffer) + len(line) > max_chunk_size:

            chunks.append({
                "type": chunk_type,
                "name": name,
                "parent_scope": parent_scope,
                "start_line": buffer_start_line,
                "end_line": line_number - 1,
                "char_count": len(buffer),
                "content": buffer,
            })

            buffer = ""
            buffer_start_line = None

        if not buffer:
            buffer_start_line = line_number

        buffer += line

    if buffer:
        chunks.append({
            "type": chunk_type,
            "name": name,
            "parent_scope": parent_scope,
            "start_line": buffer_start_line,
            "end_line": node.end_point.row + 1,
            "char_count": len(buffer),
            "content": buffer,
        })

    return chunks



# ============================================================
# STATEMENT GROUPING
# ============================================================

def group_statement_nodes(
    nodes: list[Node],
    source_code: bytes,
    max_chunk_size: int,
    chunk_type: str,
    name: str | None,
    parent_scope: str | None,
) -> list[dict]:

    if not nodes:
        return []

    chunks = []
    current_nodes = []

    for node in nodes:

        node_content = get_node_text(
            node,
            source_code,
        )

        # Single AST node is already too large
        if len(node_content) > max_chunk_size:

            # Flush previous accumulated nodes
            if current_nodes:
                chunks.append(
                    create_statement_chunk(
                        current_nodes,
                        source_code,
                        chunk_type,
                        name,
                        parent_scope,
                    )
                )

                current_nodes = []

            # Split this oversized node further
            chunks.extend(
                split_oversized_node(
                    node=node,
                    source_code=source_code,
                    max_chunk_size=max_chunk_size,
                    chunk_type=chunk_type,
                    name=name,
                    parent_scope=parent_scope,
                )
            )

            continue

        # First normal-sized node
        if not current_nodes:
            current_nodes = [node]
            continue

        candidate = source_code[
            current_nodes[0].start_byte:node.end_byte
        ].decode("utf-8")

        if len(candidate) <= max_chunk_size:
            current_nodes.append(node)

        else:
            chunks.append(
                create_statement_chunk(
                    current_nodes,
                    source_code,
                    chunk_type,
                    name,
                    parent_scope,
                )
            )

            current_nodes = [node]

    # Flush remaining nodes
    if current_nodes:
        chunks.append(
            create_statement_chunk(
                current_nodes,
                source_code,
                chunk_type,
                name,
                parent_scope,
            )
        )

    return chunks


# ============================================================
# LARGE CLASS SPLITTING
# ============================================================

def split_large_class(
    node: Node,
    source_code: bytes,
    max_chunk_size: int,
    parent_scope: str | None,
) -> list[dict]:
    """
    Split an oversized class using its structural children.

    Small methods remain intact.
    Large methods are recursively split.
    """

    actual_node = unwrap_definition(node)

    class_name = get_node_name(
        node,
        source_code,
    )

    body = actual_node.child_by_field_name("body")

    if body is None:

        return [
            create_chunk(
                node,
                source_code,
                parent_scope,
            )
        ]

    chunks = []
    pending_statements = []

    # Example:
    # UserService
    #
    # or:
    #
    # OuterClass.InnerClass

    current_scope = (
        f"{parent_scope}.{class_name}"
        if parent_scope
        else class_name
    )

    for child in body.named_children:

        # Function, nested class, decorated method, etc.
        if child.type in DEFINITION_TYPES:

            # Flush class-level statements first
            if pending_statements:

                chunks.extend(
                    group_statement_nodes(
                        nodes=pending_statements,
                        source_code=source_code,
                        max_chunk_size=max_chunk_size,
                        chunk_type="class_context",
                        name=class_name,
                        parent_scope=parent_scope,
                    )
                )

                pending_statements = []

            chunks.extend(
                split_node(
                    node=child,
                    source_code=source_code,
                    max_chunk_size=max_chunk_size,
                    parent_scope=current_scope,
                )
            )

        else:

            # Class docstring, class variables, assignments, etc.
            pending_statements.append(child)

    # Flush remaining class-level statements
    if pending_statements:

        chunks.extend(
            group_statement_nodes(
                nodes=pending_statements,
                source_code=source_code,
                max_chunk_size=max_chunk_size,
                chunk_type="class_context",
                name=class_name,
                parent_scope=parent_scope,
            )
        )

    # Safety fallback
    if not chunks:

        return [
            create_chunk(
                node,
                source_code,
                parent_scope,
            )
        ]

    return chunks


# ============================================================
# LARGE FUNCTION SPLITTING
# ============================================================

def split_large_function(
    node: Node,
    source_code: bytes,
    max_chunk_size: int,
    parent_scope: str | None,
) -> list[dict]:
    """
    Split an oversized function using its body statements.

    Nested functions/classes are handled recursively.
    """

    actual_node = unwrap_definition(node)

    function_name = get_node_name(
        node,
        source_code,
    )

    body = actual_node.child_by_field_name("body")

    if body is None:

        return [
            create_chunk(
                node,
                source_code,
                parent_scope,
            )
        ]

    chunks = []
    pending_statements = []

    current_scope = (
        f"{parent_scope}.{function_name}"
        if parent_scope
        else function_name
    )

    for child in body.named_children:

        # Nested function / nested class
        if child.type in DEFINITION_TYPES:

            # Flush normal statements before nested definition
            if pending_statements:

                chunks.extend(
                    group_statement_nodes(
                        nodes=pending_statements,
                        source_code=source_code,
                        max_chunk_size=max_chunk_size,
                        chunk_type="function_body",
                        name=function_name,
                        parent_scope=parent_scope,
                    )
                )

                pending_statements = []

            chunks.extend(
                split_node(
                    node=child,
                    source_code=source_code,
                    max_chunk_size=max_chunk_size,
                    parent_scope=current_scope,
                )
            )

        else:

            pending_statements.append(child)

    # Flush remaining function statements
    if pending_statements:

        chunks.extend(
            group_statement_nodes(
                nodes=pending_statements,
                source_code=source_code,
                max_chunk_size=max_chunk_size,
                chunk_type="function_body",
                name=function_name,
                parent_scope=parent_scope,
            )
        )

    return chunks


# ============================================================
# RECURSIVE NODE SPLITTER
# ============================================================

def split_node(
    node: Node,
    source_code: bytes,
    max_chunk_size: int,
    parent_scope: str | None = None,
) -> list[dict]:
    """
    Main recursive structural splitting logic.
    """

    content = get_node_text(
        node,
        source_code,
    )

    # --------------------------------------------------------
    # CASE 1
    # Structural unit already fits
    # --------------------------------------------------------

    if len(content) <= max_chunk_size:

        return [
            create_chunk(
                node,
                source_code,
                parent_scope,
            )
        ]

    definition_type = get_definition_type(node)

    # --------------------------------------------------------
    # CASE 2
    # Large class
    # --------------------------------------------------------

    if definition_type == "class_definition":

        return split_large_class(
            node=node,
            source_code=source_code,
            max_chunk_size=max_chunk_size,
            parent_scope=parent_scope,
        )

    # --------------------------------------------------------
    # CASE 3
    # Large function
    # --------------------------------------------------------

    if definition_type == "function_definition":

        return split_large_function(
            node=node,
            source_code=source_code,
            max_chunk_size=max_chunk_size,
            parent_scope=parent_scope,
        )

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    return [
        create_chunk(
            node,
            source_code,
            parent_scope,
        )
    ]


# ============================================================
# SOURCE-CODE CHUNKING
# ============================================================

def extract_code_chunks(
    source_code: bytes,
    max_chunk_size: int = 500,
    tree=None,
) -> list[dict]:
    """
    Chunk Python source code using Tree-sitter structure.

    Handles:
    - functions
    - classes
    - decorators
    - async functions
    - nested definitions
    - imports
    - module-level code
    """

    if tree is None:
        tree = parser.parse(source_code)

    root = tree.root_node

    chunks = []

    # Module-level statements such as:
    #
    # imports
    # constants
    # module docstrings
    # assignments
    module_nodes = []

    for node in root.named_children:

        if node.type in DEFINITION_TYPES:

            # Flush module context before definition
            if module_nodes:

                chunks.extend(
                    group_statement_nodes(
                        nodes=module_nodes,
                        source_code=source_code,
                        max_chunk_size=max_chunk_size,
                        chunk_type="module_context",
                        name=None,
                        parent_scope=None,
                    )
                )

                module_nodes = []

            chunks.extend(
                split_node(
                    node=node,
                    source_code=source_code,
                    max_chunk_size=max_chunk_size,
                )
            )

        else:

            module_nodes.append(node)

    # Flush remaining module-level statements
    if module_nodes:

        chunks.extend(
            group_statement_nodes(
                nodes=module_nodes,
                source_code=source_code,
                max_chunk_size=max_chunk_size,
                chunk_type="module_context",
                name=None,
                parent_scope=None,
            )
        )

    return chunks


# ============================================================
# STABLE CHUNK ID
# ============================================================

def generate_chunk_id(
    file_path: str,
    chunk: dict,
) -> str:
    """
    Generate a deterministic ID for a chunk.

    Same file + same location + same content
    produces the same ID.
    """

    identity = "|".join([
        file_path,
        chunk.get("type") or "",
        chunk.get("name") or "",
        chunk.get("parent_scope") or "",
        str(chunk.get("start_line")),
        chunk.get("content") or "",
    ])

    return hashlib.sha256(
        identity.encode("utf-8")
    ).hexdigest()[:24]


# ============================================================
# PRODUCTION ENTRY POINT
# ============================================================

def chunk_file(
    file_path: str,
    max_chunk_size: int = 500,
    strict: bool = True,
) -> list[dict]:
    """
    Parse and chunk one Python source file.

    Parameters
    ----------
    file_path:
        Path to the Python source file.

    max_chunk_size:
        Maximum desired chunk size in characters.

    strict:
        If True, reject source files containing syntax errors.

        If False, Tree-sitter will still attempt to produce
        chunks and syntax_valid will be False.

    Returns
    -------
    list[dict]
        Structured code chunks with metadata.
    """

    path = Path(file_path)

    # --------------------------------------------------------
    # 1. VALIDATE INPUT
    # --------------------------------------------------------

    if max_chunk_size <= 0:

        raise ValueError(
            "max_chunk_size must be greater than 0."
        )

    if not path.exists():

        raise FileNotFoundError(
            f"File does not exist: {file_path}"
        )

    if not path.is_file():

        raise ValueError(
            f"Path is not a file: {file_path}"
        )

    if path.suffix.lower() != ".py":

        raise ValueError(
            f"Expected a Python file, got: {path.suffix}"
        )

    # --------------------------------------------------------
    # 2. READ SOURCE CODE
    # --------------------------------------------------------

    source_code = path.read_bytes()

    # Empty file
    if not source_code.strip():
        return []

    # --------------------------------------------------------
    # 3. PARSE ONCE
    # --------------------------------------------------------

    tree = parser.parse(source_code)

    root = tree.root_node

    # --------------------------------------------------------
    # 4. SYNTAX VALIDATION
    # --------------------------------------------------------

    if root.has_error and strict:

        raise SyntaxError(
            f"Tree-sitter found syntax errors in: {file_path}"
        )

    # --------------------------------------------------------
    # 5. STRUCTURAL CHUNKING
    # --------------------------------------------------------

    chunks = extract_code_chunks(
        source_code=source_code,
        max_chunk_size=max_chunk_size,
        tree=tree,
    )

    # --------------------------------------------------------
    # 6. ATTACH PRODUCTION METADATA
    # --------------------------------------------------------

    normalized_path = path.as_posix()

    for index, chunk in enumerate(chunks):

        chunk["chunk_index"] = index

        chunk["file_path"] = normalized_path

        chunk["file_name"] = path.name

        chunk["language"] = "python"

        chunk["syntax_valid"] = not root.has_error

        chunk["chunk_id"] = generate_chunk_id(
            normalized_path,
            chunk,
        )

    return chunks