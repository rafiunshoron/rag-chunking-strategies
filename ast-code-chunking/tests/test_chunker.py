import pytest

from chunker import chunk_file


def create_python_file(tmp_path, code: str):
    file_path = tmp_path / "example.py"
    file_path.write_text(
        code,
        encoding="utf-8",
    )

    return file_path


def test_small_function_stays_whole(tmp_path):

    code = """
def add(a, b):
    return a + b
"""

    file_path = create_python_file(
        tmp_path,
        code,
    )

    chunks = chunk_file(
        str(file_path),
        max_chunk_size=500,
    )

    function_chunks = [
        chunk
        for chunk in chunks
        if chunk["name"] == "add"
    ]

    assert len(function_chunks) == 1

    assert "def add" in function_chunks[0]["content"]


def test_large_class_splits_into_methods(tmp_path):

    code = """
class Calculator:

    def add(self, a, b):
        result = a + b
        return result

    def subtract(self, a, b):
        result = a - b
        return result

    def multiply(self, a, b):
        result = a * b
        return result
"""

    file_path = create_python_file(
        tmp_path,
        code,
    )

    chunks = chunk_file(
        str(file_path),
        max_chunk_size=120,
    )

    names = {
        chunk["name"]
        for chunk in chunks
    }

    assert "add" in names
    assert "subtract" in names
    assert "multiply" in names


def test_parent_scope_is_preserved(tmp_path):

    code = """
class UserService:

    def create_user(self):
        return "created"

    def delete_user(self):
        return "deleted"
"""

    file_path = create_python_file(
        tmp_path,
        code,
    )

    chunks = chunk_file(
        str(file_path),
        max_chunk_size=70,
    )

    method_chunks = [
        chunk
        for chunk in chunks
        if chunk["name"] in {
            "create_user",
            "delete_user",
        }
    ]

    assert method_chunks

    for chunk in method_chunks:
        assert chunk["parent_scope"] == "UserService"


def test_decorator_is_preserved(tmp_path):

    code = """
def logger(func):
    return func


@logger
def process():
    return "done"
"""

    file_path = create_python_file(
        tmp_path,
        code,
    )

    chunks = chunk_file(
        str(file_path),
        max_chunk_size=500,
    )

    process_chunk = next(
        chunk
        for chunk in chunks
        if chunk["name"] == "process"
    )

    assert "@logger" in process_chunk["content"]
    assert "def process" in process_chunk["content"]


def test_async_function_is_detected(tmp_path):

    code = """
async def fetch_user():
    return {"status": "active"}
"""

    file_path = create_python_file(
        tmp_path,
        code,
    )

    chunks = chunk_file(
        str(file_path),
        max_chunk_size=500,
    )

    chunk = next(
        chunk
        for chunk in chunks
        if chunk["name"] == "fetch_user"
    )

    assert "async def fetch_user" in chunk["content"]


def test_max_chunk_size_is_respected(tmp_path):

    long_value = "x" * 500

    code = f'''
def huge_function():
    value = "{long_value}"
    return value
'''

    file_path = create_python_file(
        tmp_path,
        code,
    )

    chunks = chunk_file(
        str(file_path),
        max_chunk_size=100,
    )

    assert chunks

    for chunk in chunks:
        assert chunk["char_count"] <= 100


def test_chunk_ids_are_deterministic(tmp_path):

    code = """
def hello():
    return "hello"
"""

    file_path = create_python_file(
        tmp_path,
        code,
    )

    first_run = chunk_file(
        str(file_path)
    )

    second_run = chunk_file(
        str(file_path)
    )

    first_ids = [
        chunk["chunk_id"]
        for chunk in first_run
    ]

    second_ids = [
        chunk["chunk_id"]
        for chunk in second_run
    ]

    assert first_ids == second_ids


def test_invalid_python_raises_error(tmp_path):

    code = """
def broken(:
    return 10
"""

    file_path = create_python_file(
        tmp_path,
        code,
    )

    with pytest.raises(SyntaxError):
        chunk_file(
            str(file_path),
            strict=True,
        )