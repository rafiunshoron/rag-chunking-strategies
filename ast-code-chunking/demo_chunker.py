from chunker import chunk_file


chunks = chunk_file(
    "sample_code.py",
    max_chunk_size=500,
)

for index, chunk in enumerate(chunks, start=1):

    print("\n" + "=" * 70)
    print(f"CHUNK {index}")
    print("=" * 70)

    print(f"Type         : {chunk['type']}")
    print(f"Name         : {chunk['name']}")
    print(f"Parent Scope : {chunk['parent_scope']}")
    print(f"Lines        : {chunk['start_line']} - {chunk['end_line']}")
    print(f"Characters   : {chunk['char_count']}")

    print("\nCONTENT:\n")

    print(chunk["content"])



    #              AST node
    #                 │
    #          check its size
    #                 │
    #       ┌─────────┴─────────┐
    #       │                   │
    #    <= limit            > limit
    #       │                   │
    #  keep intact        inspect type
    #                           │
    #               ┌───────────┴───────────┐
    #               │                       │
    #             class                  function
    #               │                       │
    #          split into              split body
    #           methods               statements