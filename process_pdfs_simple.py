#!/usr/bin/env python3
"""
Simple PDF Processing Script for NYC Services GPT RAG System

This script processes PDFs one at a time to avoid memory issues.
"""

import os
import sys
import gc
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.ingest.pdf_processor import PDFProcessor
from src.ingest.data_processor import process_documents
from src.retrieve.vector_store import init_vector_store, add_documents


def process_single_pdf(pdf_path: Path, processor: PDFProcessor, chunk_size: int = 300, overlap: int = 50):
    """
    Process a single PDF file completely.
    """
    print(f"📄 Processing: {pdf_path.name}")
    
    try:
        # Extract text
        text = processor.extract_text_from_pdf(pdf_path)
        if not text:
            print(f"⚠️ No text extracted from {pdf_path.name}")
            return None
        
        # Classify service type
        service_type = processor.classify_service_type(text, pdf_path.name)
        
        # Extract metadata
        doc_title = processor.extract_document_title(text, pdf_path.name)
        doc_date = processor.extract_date(text, pdf_path.name)
        
        # Create document record
        doc_record = {
            "text": text,
            "metadata": {
                "source": str(pdf_path),
                "service_type": service_type,
                "doc_title": doc_title,
                "date": doc_date,
                "filename": pdf_path.name,
                "file_size": pdf_path.stat().st_size,
                "processing_date": datetime.now().isoformat()
            }
        }
        
        print(f"✅ Extracted text: {len(text)} characters")
        print(f"✅ Classified as: {service_type}")
        print(f"✅ Title: {doc_title}")
        
        # Chunk the document
        print(f"🔪 Chunking document...")
        chunks = processor.chunk_and_prepare_for_embedding([doc_record], chunk_size, overlap)
        
        if not chunks:
            print(f"⚠️ No chunks created for {pdf_path.name}")
            return None
        
        print(f"✅ Created {len(chunks)} chunks")
        
        # Generate embeddings for chunks
        print(f"🧮 Generating embeddings...")
        chunk_texts = [chunk["text"] for chunk in chunks]
        
        embedded_records = process_documents(
            chunk_texts,
            chunk_size=chunk_size,
            overlap=overlap
        )
        
        if not embedded_records:
            print(f"⚠️ No embeddings generated for {pdf_path.name}")
            return None
        
        print(f"✅ Generated {len(embedded_records)} embeddings")
        
        # Merge metadata
        final_records = []
        for i, (embedded_record, chunked_record) in enumerate(zip(embedded_records, chunks)):
            final_record = {
                "text": embedded_record["text"],
                "embedding": embedded_record["embedding"],
                "metadata": {
                    **chunked_record["metadata"],
                    **embedded_record["metadata"],
                    "record_id": f"{pdf_path.stem}_chunk_{i}",
                    "source_type": "pdf_document"
                }
            }
            final_records.append(final_record)
        
        print(f"✅ Merged metadata for {len(final_records)} records")
        return final_records
        
    except Exception as e:
        print(f"❌ Error processing {pdf_path.name}: {e}")
        return None


def main():
    """
    Process PDFs one at a time to avoid memory issues.
    """
    print("🚀 NYC Services GPT - Simple PDF Processing Pipeline")
    print("=" * 60)
    
    # Initialize processor
    processor = PDFProcessor("data/Docs")
    
    if not processor.docs_folder.exists():
        print(f"❌ Docs folder not found: {processor.docs_folder}")
        return
    
    pdf_files = list(processor.docs_folder.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ No PDF files found in {processor.docs_folder}")
        return
    
    print(f"🔍 Found {len(pdf_files)} PDF files to process")
    
    # Initialize vector store
    print(f"\n🗄️ Initializing ChromaDB...")
    vector_store = init_vector_store()
    if not vector_store:
        print("❌ Failed to initialize vector store")
        return
    
    # Process each PDF individually
    total_added = 0
    
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n📚 Processing PDF {i}/{len(pdf_files)}")
        print("-" * 40)
        
        # Process this PDF
        final_records = process_single_pdf(pdf_path, processor, chunk_size=300, overlap=50)
        
        if final_records:
            # Add to ChromaDB
            print(f"📚 Adding {len(final_records)} records to ChromaDB...")
            
            success = add_documents(vector_store, final_records)
            if success:
                total_added += len(final_records)
                print(f"✅ Successfully added {len(final_records)} records from {pdf_path.name}")
            else:
                print(f"❌ Failed to add records from {pdf_path.name}")
        else:
            print(f"⚠️ Skipping {pdf_path.name} - processing failed")
        
        # Clear memory
        if 'final_records' in locals():
            del final_records
        gc.collect()
        
        print(f"✅ PDF {i}/{len(pdf_files)} completed")
    
    # Final summary
    print(f"\n🎉 PDF Processing Complete!")
    print("=" * 60)
    print(f"✅ Processed: {len(pdf_files)} PDF files")
    print(f"✅ Added to ChromaDB: {total_added} records")
    print(f"📊 Total in collection: {vector_store.collection.count()}")
    
    # Show service distribution
    try:
        results = vector_store.collection.get(limit=1000)
        if results and 'metadatas' in results:
            service_counts = {}
            for metadata in results['metadatas']:
                if metadata and 'service_type' in metadata:
                    service = metadata['service_type']
                    service_counts[service] = service_counts.get(service, 0) + 1
            
            print(f"\n📊 Service Distribution:")
            for service, count in service_counts.items():
                print(f"  {service}: {count} records")
    except Exception as e:
        print(f"⚠️ Could not retrieve service distribution: {e}")


if __name__ == "__main__":
    main()
