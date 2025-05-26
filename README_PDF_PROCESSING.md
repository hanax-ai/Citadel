# PDF Processing for Project Citadel

This document describes the PDF processing capabilities implemented for Project Citadel.

## Overview

The PDF processing module provides comprehensive capabilities for extracting and processing information from PDF documents. It includes:

1. Text extraction
2. Metadata extraction
3. Image handling with OCR (when enabled)
4. Document structure preservation
5. Content chunking for LLM integration

Additionally, a specialized PDFCrawler class has been implemented that extends the BaseCrawler class and uses the PDF processing module to crawl and process PDF documents from URLs.

## Components

### PDF Processing Module

The PDF processing module (`citadel_core/pdf_processing.py`) provides the following functionality:

- **PDFProcessor class**: A comprehensive class for processing PDF documents
  - Text extraction
  - Metadata extraction
  - Document structure identification (headings, paragraphs, tables)
  - Image processing with OCR (when enabled)
  - Content chunking for LLM integration

- **Utility functions**:
  - `extract_text_from_pdf`: Extract text from a PDF
  - `extract_metadata_from_pdf`: Extract metadata from a PDF
  - `chunk_pdf_content`: Extract and chunk text from a PDF

### PDFCrawler Class

The PDFCrawler class (`citadel_core/crawlers/pdf_crawler.py`) extends the BaseCrawler class and provides specialized functionality for crawling and processing PDF documents:

- Download PDFs from URLs
- Process PDFs using the PDFProcessor class
- Save PDFs to disk
- Process local PDF files

## Usage

### Basic Text Extraction

```python
from citadel_core.pdf_processing import extract_text_from_pdf

# Extract text from a PDF
text = extract_text_from_pdf('path/to/document.pdf')
print(text)
```

### Metadata Extraction

```python
from citadel_core.pdf_processing import extract_metadata_from_pdf

# Extract metadata from a PDF
metadata = extract_metadata_from_pdf('path/to/document.pdf')
print(metadata)
```

### Content Chunking for LLM Integration

```python
from citadel_core.pdf_processing import chunk_pdf_content

# Extract and chunk text from a PDF
chunks = chunk_pdf_content('path/to/document.pdf', chunk_size=1000, overlap=100)
for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1}: {chunk[:100]}...")
```

### Using the PDFProcessor Class

```python
from citadel_core.pdf_processing import PDFProcessor

# Create a PDF processor
processor = PDFProcessor(ocr_enabled=True, language='eng')

# Process a PDF
result = processor.process_pdf('path/to/document.pdf')

# Access the extracted information
print(f"Text: {result['text'][:100]}...")
print(f"Metadata: {result['metadata']}")
print(f"Number of pages: {len(result['pages'])}")
print(f"Number of headings: {len(result['structure']['headings'])}")
print(f"Number of paragraphs: {len(result['structure']['paragraphs'])}")
print(f"Number of chunks: {len(result['chunks'])}")
```

### Using the PDFCrawler Class

```python
from citadel_core.crawlers.pdf_crawler import PDFCrawler

# Create a PDF crawler
crawler = PDFCrawler(
    base_url="https://example.com",
    ocr_enabled=True,
    language='eng',
    chunk_size=1000,
    chunk_overlap=100
)

# Crawl PDFs from URLs
results = crawler.crawl([
    "https://example.com/document1.pdf",
    "https://example.com/document2.pdf"
])

# Process a local PDF
result = crawler.process_local_pdf('path/to/document.pdf')

# Save a PDF to disk
crawler.save_pdf("https://example.com/document.pdf", "path/to/save/document.pdf")
```

## Dependencies

The PDF processing module depends on the following packages:

- PyPDF2: For PDF parsing and text extraction
- pytesseract: For OCR (optional)
- Pillow: For image processing (required for OCR)

These dependencies have been added to the project's `setup.py` file.

## OCR Support

OCR (Optical Character Recognition) is supported for extracting text from images within PDFs. This functionality requires:

1. The pytesseract Python package
2. The Tesseract OCR engine installed on the system

OCR can be enabled or disabled when creating a PDFProcessor or PDFCrawler instance:

```python
# Enable OCR
processor = PDFProcessor(ocr_enabled=True, language='eng')

# Disable OCR
processor = PDFProcessor(ocr_enabled=False)
```

## Testing

The PDF processing functionality can be tested using:

1. The test scripts in the `tests` directory:
   - `test_pdf_processing.py`: Tests for the PDF processing module
   - `test_pdf_crawler.py`: Tests for the PDFCrawler class

2. The demo script in the `scripts` directory:
   - `pdf_demo.py`: Demonstrates the PDF processing capabilities

Example:

```bash
# Run the demo script
python scripts/pdf_demo.py --pdf path/to/document.pdf --ocr

# Run the tests
python -m unittest tests/test_pdf_processing.py
python -m unittest tests/test_pdf_crawler.py
```
