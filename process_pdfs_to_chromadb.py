#!/usr/bin/env python3
"""
Complete PDF Processing Pipeline for NYC Services GPT RAG System

This script processes PDF documents from /data/docs, extracts text, classifies them,
chunks them, generates embeddings, and adds them to ChromaDB vector store.

Usage:
    python process_pdfs_to_chromadb.py
"""

import os
import sys
import gc
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.ingest.pdf_processor import process_pdfs_to_chunks
from src.ingest.data_processor import process_documents
from src.retrieve.vector_store import init_vector_store, add_documents
from src.config import config


def process_in_batches(chunked_records, batch_size=50):
    """
    Process documents in smaller batches to manage memory.
    """
    total_batches = (len(chunked_records) + batch_size - 1) // batch_size
    
    for i in range(0, len(chunked_records), batch_size):
        batch = chunked_records[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        print(f"🔄 Processing batch {batch_num}/{total_batches} ({len(batch)} records)")
        
        # Process this batch
        yield batch
        
        # Clear memory
        del batch
        gc.collect()


def main():
    """
    Main pipeline: Process PDFs → Chunk → Embed → Store in ChromaDB
    """
    print("🚀 NYC Services GPT - PDF Processing Pipeline")
    print("=" * 60)
    
    # Step 1: Process PDFs and chunk them
    print("\n📄 Step 1: Processing PDF Documents")
    print("-" * 40)
    
    try:
        # Use smaller chunks and overlap for memory efficiency
        chunked_records = process_pdfs_to_chunks(
            docs_folder="data/Docs",
            chunk_size=300,  # Smaller chunks for memory efficiency
            overlap=50        # Smaller overlap
        )
        
        if not chunked_records:
            print("❌ No PDF documents processed. Check your /data/docs folder.")
            return
        
        print(f"✅ Successfully processed {len(chunked_records)} chunks")
        
        # Show service distribution
        service_counts = {}
        for record in chunked_records:
            service = record["metadata"]["service_type"]
            service_counts[service] = service_counts.get(service, 0) + 1
        
        print(f"\n📊 Service Distribution:")
        for service, count in service_counts.items():
            print(f"  {service}: {count} chunks")
        
    except Exception as e:
        print(f"❌ Error processing PDFs: {e}")
        print("Make sure you have PyMuPDF and PyPDF2 installed:")
        print("pip install PyMuPDF PyPDF2")
        return
    
    # Step 2: Generate embeddings for chunks in batches
    print(f"\n🧮 Step 2: Generating Embeddings (Batch Processing)")
    print("-" * 40)
    
    try:
        all_embedded_records = []
        batch_size = 30  # Process 30 chunks at a time
        
        for batch_num, batch in enumerate(process_in_batches(chunked_records, batch_size)):
            print(f"🔧 Processing batch {batch_num + 1}...")
            
            # Extract text from this batch
            batch_texts = [record["text"] for record in batch]
            
            # Generate embeddings for this batch
            embedded_batch = process_documents(
                batch_texts,
                chunk_size=300,  # Match our chunking
                overlap=50
            )
            
            if embedded_batch:
                all_embedded_records.extend(embedded_batch)
                print(f"✅ Batch {batch_num + 1} completed: {len(embedded_batch)} embeddings")
            else:
                print(f"⚠️ Batch {batch_num + 1} failed to generate embeddings")
            
            # Clear batch memory
            del batch_texts, embedded_batch
            gc.collect()
        
        if not all_embedded_records:
            print("❌ No embeddings generated")
            return
        
        print(f"✅ Generated {len(all_embedded_records)} total embeddings")
        
    except Exception as e:
        print(f"❌ Error generating embeddings: {e}")
        return
    
    # Step 3: Merge metadata from chunked records with embeddings
    print(f"\n🔗 Step 3: Merging Metadata")
    print("-" * 40)
    
    try:
        # Ensure we have the same number of records
        if len(all_embedded_records) != len(chunked_records):
            print(f"⚠️ Mismatch: {len(all_embedded_records)} embeddings vs {len(chunked_records)} chunks")
            # Use the smaller number to avoid index errors
            min_count = min(len(all_embedded_records), len(chunked_records))
            all_embedded_records = all_embedded_records[:min_count]
            chunked_records = chunked_records[:min_count]
        
        # Merge metadata from chunked records into embedded records
        final_records = []
        for i, (embedded_record, chunked_record) in enumerate(zip(all_embedded_records, chunked_records)):
            # Create final record with embedding + rich metadata
            final_record = {
                "text": embedded_record["text"],
                "embedding": embedded_record["embedding"],
                "metadata": {
                    **chunked_record["metadata"],  # All PDF metadata
                    **embedded_record["metadata"],  # Embedding metadata
                    "record_id": f"pdf_chunk_{i}",
                    "source_type": "pdf_document"
                }
            }
            final_records.append(final_record)
        
        print(f"✅ Merged metadata for {len(final_records)} records")
        
        # Show sample record
        if final_records:
            sample = final_records[0]
            print(f"\n📝 Sample Record:")
            print(f"  Service: {sample['metadata']['service_type']}")
            print(f"  Title: {sample['metadata']['doc_title']}")
            print(f"  Source: {sample['metadata']['filename']}")
            print(f"  Tokens: {sample['metadata']['token_count']}")
            print(f"  Embedding: {len(sample['embedding'])} dimensions")
        
    except Exception as e:
        print(f"❌ Error merging metadata: {e}")
        return
    
    # Step 4: Initialize ChromaDB and store documents
    print(f"\n🗄️ Step 4: Storing in ChromaDB")
    print("-" * 40)
    
    try:
        # Initialize vector store
        print("🔧 Initializing ChromaDB vector store...")
        vector_store = init_vector_store()
        
        if not vector_store:
            print("❌ Failed to initialize vector store")
            return
        
        # Add documents to vector store in batches
        print(f"📚 Adding {len(final_records)} records to ChromaDB...")
        
        # Process in smaller batches for ChromaDB
        chroma_batch_size = 20
        total_added = 0
        
        for i in range(0, len(final_records), chroma_batch_size):
            batch = final_records[i:i + chroma_batch_size]
            batch_num = (i // chroma_batch_size) + 1
            total_batches = (len(final_records) + chroma_batch_size - 1) // chroma_batch_size
            
            print(f"📚 Adding batch {batch_num}/{total_batches} ({len(batch)} records)...")
            
            success = add_documents(vector_store, batch)
            if success:
                total_added += len(batch)
                print(f"✅ Batch {batch_num} added successfully")
            else:
                print(f"❌ Failed to add batch {batch_num}")
                break
            
            # Clear batch memory
            del batch
            gc.collect()
        
        if total_added > 0:
            print(f"✅ Successfully added {total_added} records to ChromaDB")
            print(f"📊 Total documents in collection: {vector_store.collection.count()}")
            
            # Show final service distribution in ChromaDB
            print(f"\n🎯 Final ChromaDB Contents:")
            print(f"  Total records: {vector_store.collection.count()}")
            
            # Query to get service distribution
            try:
                # Get a sample of records to show service distribution
                results = vector_store.collection.get(limit=1000)
                if results and 'metadatas' in results:
                    service_counts = {}
                    for metadata in results['metadatas']:
                        if metadata and 'service_type' in metadata:
                            service = metadata['service_type']
                            service_counts[service] = service_counts.get(service, 0) + 1
                    
                    print(f"  Service Distribution:")
                    for service, count in service_counts.items():
                        print(f"    {service}: {count} records")
            except Exception as e:
                print(f"  ⚠️ Could not retrieve service distribution: {e}")
            
        else:
            print("❌ Failed to add any documents to vector store")
            return
        
    except Exception as e:
        print(f"❌ Error storing in ChromaDB: {e}")
        return
    
    # Success!
    print(f"\n🎉 PDF Processing Pipeline Complete!")
    print("=" * 60)
    print(f"✅ Processed PDFs: {len(chunked_records)} chunks")
    print(f"✅ Generated embeddings: {len(all_embedded_records)}")
    print(f"✅ Stored in ChromaDB: {total_added} records")
    print(f"🎯 Your PDF documents are now searchable in the vector store!")
    
    # Show next steps
    print(f"\n📋 Next Steps:")
    print(f"  1. Test retrieval with: python -c \"from src.retrieve.vector_store import *; vs = init_vector_store(); print('ChromaDB ready!')\"")
    print(f"  2. Run evaluation: python src/tests/baseline_evaluation.py")
    print(f"  3. Query your documents through the RAG pipeline")


if __name__ == "__main__":
    main()
