#!/usr/bin/env python3
"""
Test script to process just the small PDFs first to verify memory improvements.
"""

import sys
import gc
import psutil
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.ingest.pdf_processor import PDFProcessor
from src.ingest.data_processor import process_documents
from src.ingest.chunker import chunk_large_text_streaming
from src.retrieve.vector_store import init_vector_store, add_documents


def get_memory_usage():
    """Get current memory usage information."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return {
        'rss': memory_info.rss / 1024 / 1024,  # MB
        'vms': memory_info.vms / 1024 / 1024,  # MB
        'percent': process.memory_percent()
    }


def log_memory_usage(stage: str):
    """Log memory usage at different stages."""
    memory = get_memory_usage()
    print(f"💾 Memory usage at {stage}: {memory['rss']:.1f}MB RSS, {memory['vms']:.1f}MB VMS")


def cleanup_memory():
    """Force memory cleanup."""
    gc.collect()
    memory = get_memory_usage()
    print(f"🧹 Memory cleanup completed: {memory['rss']:.1f}MB RSS")


def process_small_pdf(pdf_path: Path, processor: PDFProcessor, chunk_size: int = 300, overlap: int = 50):
    """
    Process a smaller PDF file completely using streaming chunking.
    """
    print(f"📄 Processing: {pdf_path.name}")
    log_memory_usage(f"start of {pdf_path.name}")
    
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
        
        print(f"✅ Extracted text: {len(text)} characters")
        print(f"✅ Classified as: {service_type}")
        print(f"✅ Title: {doc_title}")
        
        # Use streaming chunking for all documents to avoid memory issues
        print(f"🔪 Chunking document with streaming approach...")
        
        all_final_records = []
        chunk_count = 0
        
        # Use the streaming chunker for memory efficiency
        for chunk in chunk_large_text_streaming(text, chunk_size=chunk_size, overlap=overlap):
            chunk_count += 1
            
            if chunk_count % 10 == 0:
                print(f"🔪 Processed {chunk_count} chunks...")
                log_memory_usage(f"chunk {chunk_count}")
            
            # Process this single chunk
            try:
                embedded_record = process_documents(
                    [chunk],
                    chunk_size=chunk_size,
                    overlap=overlap
                )
                
                if embedded_record and len(embedded_record) > 0:
                    # Create final record for this chunk
                    final_record = {
                        "text": embedded_record[0]["text"],
                        "embedding": embedded_record[0]["embedding"],
                        "metadata": {
                            **embedded_record[0]["metadata"],
                            "source": str(pdf_path),
                            "service_type": service_type,
                            "doc_title": doc_title,
                            "date": doc_date,
                            "filename": pdf_path.name,
                            "file_size": pdf_path.stat().st_size,
                            "record_id": f"{pdf_path.stem}_chunk_{chunk_count}",
                            "source_type": "pdf_document",
                            "chunk_index": chunk_count,
                            "total_chunks": "unknown"  # We don't know total until done
                        }
                    }
                    all_final_records.append(final_record)
                
                # Clear chunk memory immediately
                del chunk
                if 'embedded_record' in locals():
                    del embedded_record
                
            except Exception as e:
                print(f"⚠️ Error processing chunk {chunk_count}: {e}")
                continue
            
            # Force garbage collection every 20 chunks
            if chunk_count % 20 == 0:
                cleanup_memory()
        
        print(f"✅ Created {len(all_final_records)} final records")
        log_memory_usage(f"end of {pdf_path.name}")
        return all_final_records
        
    except Exception as e:
        print(f"❌ Error processing {pdf_path.name}: {e}")
        return None


def main():
    """
    Process only the small PDFs to test memory improvements.
    """
    print("🚀 NYC Services GPT - Small PDFs Test")
    print("=" * 50)
    
    # Log initial memory usage
    log_memory_usage("start of script")
    
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
    
    # Only process small PDFs for this test
    small_pdfs = []
    
    for pdf_path in pdf_files:
        file_size = pdf_path.stat().st_size
        if file_size <= 500000:  # 500KB threshold
            small_pdfs.append(pdf_path)
    
    print(f"📊 Processing Small PDFs Only:")
    for pdf in small_pdfs:
        size_mb = pdf.stat().st_size / 1024 / 1024
        print(f"    - {pdf.name}: {size_mb:.2f}MB")
    
    # Initialize vector store
    print(f"\n🗄️ Initializing ChromaDB...")
    vector_store = init_vector_store()
    if not vector_store:
        print("❌ Failed to initialize vector store")
        return
    
    # Process small PDFs
    total_added = 0
    
    if small_pdfs:
        print(f"\n📚 Processing Small PDFs")
        print("=" * 40)
        
        for i, pdf_path in enumerate(small_pdfs, 1):
            print(f"\n📚 Small PDF {i}/{len(small_pdfs)}")
            print("-" * 30)
            
            final_records = process_small_pdf(pdf_path, processor, chunk_size=300, overlap=50)
            
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
            cleanup_memory()
            log_memory_usage(f"after processing {pdf_path.name}")
    
    # Final summary
    print(f"\n🎉 Small PDFs Processing Complete!")
    print("=" * 50)
    print(f"✅ Processed: {len(small_pdfs)} PDF files")
    print(f"✅ Added to ChromaDB: {total_added} records")
    print(f"📊 Total in collection: {vector_store.collection.count()}")
    
    # Final memory usage
    log_memory_usage("end of script")


if __name__ == "__main__":
    main()
