import pypdf
from pathlib import Path


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extracts text from a PDF file.
    Returns: string containing the extracted text
    """
    text_content = []

    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = pypdf.PdfReader(file)

            # Extract from each page
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text.strip():  # Only add non-empty pages
                    text_content.append(f"--- Page {page_num} ---\n{page_text}")

        return "\n\n".join(text_content)

    except Exception as e:
        return f"Error extracting PDF: {str(e)}"


def chunk_text(text: str, chunk_size: int = 4000) -> list[str]:
    """
    Split text into smaller chunks for LLM context.
    Useful for large PDFs that exceed token limits.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_length += len(word) + 1  # +1 for space
        if current_length > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
