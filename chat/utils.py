import pypdf
import pdfplumber
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extracts text from a PDF file with multiple fallback methods.
    Returns: string containing the extracted text
    """
    # Try pdfplumber first (more robust with damaged PDFs)
    try:
        return _extract_with_pdfplumber(pdf_path)
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}, trying pypdf...")

    # Fallback to pypdf
    try:
        return _extract_with_pypdf(pdf_path)
    except Exception as e:
        logger.error(f"pypdf also failed: {e}")
        return f"Error: Unable to extract text from PDF - {str(e)}"


def _extract_with_pdfplumber(pdf_path: Path) -> str:
    """Extract text using pdfplumber (more robust)"""
    text_content = []

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        logger.info(f"Processing PDF with {total_pages} pages using pdfplumber")

        for page_num, page in enumerate(pdf.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_content.append(f"--- Page {page_num} ---\n{page_text}")
                else:
                    logger.warning(f"Page {page_num} contains no extractable text")
            except Exception as page_error:
                logger.error(f"Error extracting page {page_num}: {page_error}")
                text_content.append(
                    f"--- Page {page_num} ---\n[Error extracting page content]"
                )

    if not text_content:
        raise Exception("No text could be extracted from this PDF")

    return "\n\n".join(text_content)


def _extract_with_pypdf(pdf_path: Path) -> str:
    """Extract text using pypdf (fallback method)"""
    text_content = []

    with open(pdf_path, "rb") as file:
        # Try with strict=False to handle malformed PDFs
        pdf_reader = pypdf.PdfReader(file, strict=False)

        # Check if PDF is encrypted
        if pdf_reader.is_encrypted:
            try:
                pdf_reader.decrypt("")  # Try empty password
            except Exception:
                raise Exception("PDF is password protected")

        total_pages = len(pdf_reader.pages)
        logger.info(f"Processing PDF with {total_pages} pages using pypdf")

        # Extract from each page with individual error handling
        for page_num, page in enumerate(pdf_reader.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_content.append(f"--- Page {page_num} ---\n{page_text}")
                else:
                    logger.warning(f"Page {page_num} contains no extractable text")
            except Exception as page_error:
                logger.error(f"Error extracting page {page_num}: {page_error}")
                text_content.append(
                    f"--- Page {page_num} ---\n[Error extracting page content]"
                )

    if not text_content:
        raise Exception("No text could be extracted from this PDF")

    return "\n\n".join(text_content)


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
