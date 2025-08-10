#!/usr/bin/env python3
"""
Simple PDF Text Extraction Script

This script just extracts text from PDFs to see what we're working with.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.ingest.pdf_processor import PDFProcessor


def main():
    """
    Just extract text from PDFs to see what we have.
    """
    print("🔍 NYC Services GPT - PDF Text Extraction")
    print("=" * 50)
    
    # Initialize processor
    processor = PDFProcessor("data/Docs")
    
    if not processor.docs_folder.exists():
        print(f"❌ Docs folder not found: {processor.docs_folder}")
        return
    
    pdf_files = list(processor.docs_folder.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ No PDF files found in {processor.docs_folder}")
        return
    
    print(f"🔍 Found {len(pdf_files)} PDF files")
    
    # Process each PDF individually
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n📄 PDF {i}/{len(pdf_files)}: {pdf_path.name}")
        print("-" * 40)
        
        try:
            # Extract text
            text = processor.extract_text_from_pdf(pdf_path)
            if not text:
                print(f"⚠️ No text extracted")
                continue
            
            # Classify service type
            service_type = processor.classify_service_type(text, pdf_path.name)
            
            # Extract metadata
            doc_title = processor.extract_document_title(text, pdf_path.name)
            doc_date = processor.extract_date(text, pdf_path.name)
            
            print(f"✅ Text length: {len(text)} characters")
            print(f"✅ Service: {service_type}")
            print(f"✅ Title: {doc_title}")
            print(f"✅ Date: {doc_date}")
            print(f"✅ File size: {pdf_path.stat().st_size} bytes")
            
            # Show first 200 characters
            preview = text[:200].replace('\n', ' ').strip()
            print(f"📝 Preview: {preview}...")
            
            # Simple token count
            tokens = text.split()
            print(f"🔢 Approx tokens: {len(tokens)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print(f"✅ PDF {i}/{len(pdf_files)} completed")
    
    print(f"\n🎯 Text extraction complete!")


if __name__ == "__main__":
    main()
