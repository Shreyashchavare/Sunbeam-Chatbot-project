
def manual_chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
):
    start = 0
    length = len(text)

    while start < length:
        end = start + chunk_size
        yield text[start:end]

        start = end - overlap
        if start < 0:
            start = 0
