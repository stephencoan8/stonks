"""
PDF processing module for extracting instructions from PDF files.
"""

from pathlib import Path
from typing import Optional
import PyPDF2
import pdfplumber


def extract_text_pypdf2(pdf_path: str) -> str:
    """
    Extract text from a PDF file using PyPDF2.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a string
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: If there's an error reading the PDF
    """
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    text_content = []
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            print(f"Processing {num_pages} pages...")
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                if text:
                    text_content.append(f"--- Page {page_num} ---\n{text}\n")
                    
        return "\n".join(text_content)
    
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")


def extract_text_pdfplumber(pdf_path: str) -> str:
    """
    Extract text from a PDF file using pdfplumber (better for complex layouts).
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a string
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: If there's an error reading the PDF
    """
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    text_content = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            num_pages = len(pdf.pages)
            print(f"Processing {num_pages} pages...")
            
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    text_content.append(f"--- Page {page_num} ---\n{text}\n")
                    
        return "\n".join(text_content)
    
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")


def process_pdf_instructions(pdf_path: str, method: str = 'pdfplumber') -> dict:
    """
    Process a PDF file containing instructions and return structured data.
    
    Args:
        pdf_path: Path to the PDF file
        method: Extraction method ('pypdf2' or 'pdfplumber')
        
    Returns:
        Dictionary containing extracted text and metadata
    """
    pdf_file = Path(pdf_path)
    
    # Extract text using specified method
    if method == 'pypdf2':
        text = extract_text_pypdf2(pdf_path)
    else:
        text = extract_text_pdfplumber(pdf_path)
    
    # Return structured result
    result = {
        'filename': pdf_file.name,
        'path': str(pdf_file.absolute()),
        'text': text,
        'word_count': len(text.split()),
        'char_count': len(text)
    }
    
    return result


def save_extracted_text(pdf_path: str, output_path: Optional[str] = None) -> str:
    """
    Extract text from PDF and save to a text file.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Optional path for output file (defaults to same name with .txt)
        
    Returns:
        Path to the saved text file
    """
    # Extract text
    result = process_pdf_instructions(pdf_path)
    
    # Determine output path
    if output_path is None:
        pdf_file = Path(pdf_path)
        output_path = pdf_file.with_suffix('.txt')
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Extracted from: {result['filename']}\n")
        f.write(f"Word count: {result['word_count']}\n")
        f.write(f"Character count: {result['char_count']}\n")
        f.write("=" * 80 + "\n\n")
        f.write(result['text'])
    
    print(f"Text saved to: {output_path}")
    return str(output_path)
