"""
PDF Processor for NYC Services GPT RAG System

This module processes PDF documents from the /data/docs folder, extracts text,
classifies them by service type, adds metadata, and prepares them for chunking
and embedding into ChromaDB.
"""

import os
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime
import PyPDF2
import fitz  # PyMuPDF for better text extraction

from .chunker import chunk_documents
from ..models.rate_limiter import rate_limiter
from ..models.mock_fallback import mock_fallback
from ..config import config


class PDFProcessor:
    """
    Processes PDF documents for NYC Services RAG system.
    
    Extracts text, classifies by service type, adds metadata, and prepares
    documents for chunking and embedding.
    """
    
    def __init__(self, docs_folder: str = "data/Docs"):
        """
        Initialize PDF processor.
        
        Args:
            docs_folder: Path to folder containing PDF documents
        """
        self.docs_folder = Path(docs_folder)
        self.service_keywords = {
            "unemployment": [
                "unemployment", "job loss", "department of labor", "weekly certification",
                "benefit amount", "claim", "appeal", "workers", "employment"
            ],
            "snap": [
                "snap", "food stamps", "ebt", "food assistance", "income limits",
                "household size", "benefits", "nutrition", "food"
            ],
            "medicaid": [
                "medicaid", "health insurance", "healthcare", "medical coverage",
                "provider", "coverage", "health", "medical"
            ],
            "cash_assistance": [
                "cash assistance", "family assistance", "safety net", "financial aid",
                "cash benefits", "temporary assistance", "welfare"
            ],
            "childcare": [
                "childcare", "daycare", "child care", "subsidy", "provider",
                "co-payment", "children", "day care"
            ]
        }
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract text from PDF using PyMuPDF for better quality.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            # Try PyMuPDF first (better text extraction)
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text.strip()
        except Exception as e:
            print(f"⚠️ PyMuPDF failed for {pdf_path.name}, trying PyPDF2: {e}")
            try:
                # Fallback to PyPDF2
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                return text.strip()
            except Exception as e2:
                print(f"❌ Failed to extract text from {pdf_path.name}: {e2}")
                return ""
    
    def classify_service_type(self, text: str, filename: str) -> str:
        """
        Classify document by service type using keyword analysis.
        
        Args:
            text: Extracted text content
            filename: PDF filename for additional context
            
        Returns:
            Classified service type
        """
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        # Score each service based on keyword matches
        service_scores = {}
        
        for service, keywords in self.service_keywords.items():
            score = 0
            
            # Check text content
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            
            # Check filename for additional context
            for keyword in keywords:
                if keyword in filename_lower:
                    score += 2  # Higher weight for filename matches
            
            service_scores[service] = score
        
        # Return service with highest score
        if service_scores:
            best_service = max(service_scores, key=service_scores.get)
            if service_scores[best_service] > 0:
                return best_service
        
        # Default classification based on filename patterns
        if "childcare" in filename_lower or "cs925" in filename_lower:
            return "childcare"
        elif "workers" in filename_lower or "bill" in filename_lower:
            return "unemployment"
        elif "medicaid" in filename_lower:
            return "medicaid"
        elif "dss" in filename_lower:
            return "cash_assistance"
        elif "welcome" in filename_lower:
            return "general"  # General NYC services info
        elif "youth" in filename_lower:
            return "general"  # Youth services info
        
        return "unknown"
    
    def extract_document_title(self, text: str, filename: str) -> str:
        """
        Extract or generate document title.
        
        Args:
            text: Extracted text content
            filename: PDF filename
            
        Returns:
            Document title
        """
        # Try to extract title from first few lines
        lines = text.split('\n')[:10]
        for line in lines:
            line = line.strip()
            if line and len(line) > 10 and len(line) < 200:
                # Clean up the line
                title = re.sub(r'[^\w\s\-\(\)]', '', line)
                if title and not title.isdigit():
                    return title[:100]  # Limit length
        
        # Fallback to filename-based title
        filename_clean = filename.replace('.pdf', '').replace('_', ' ').title()
        return filename_clean
    
    def extract_date(self, text: str, filename: str) -> str:
        """
        Extract document date or use file modification date.
        
        Args:
            text: Extracted text content
            filename: PDF filename
            
        Returns:
            Date string
        """
        # Try to find date patterns in text
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{4}-\d{1,2}-\d{1,2}\b',  # YYYY-MM-DD
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',  # Month YYYY
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        # Fallback to file modification date
        try:
            pdf_path = Path(self.docs_folder) / filename
            if pdf_path.exists():
                mtime = pdf_path.stat().st_mtime
                return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        except:
            pass
        
        return "Unknown"
    
    def process_pdf_documents(self) -> List[Dict]:
        """
        Process all PDF documents in the docs folder.
        
        Returns:
            List of processed document dictionaries with metadata
        """
        if not self.docs_folder.exists():
            print(f"❌ Docs folder not found: {self.docs_folder}")
            return []
        
        pdf_files = list(self.docs_folder.glob("*.pdf"))
        if not pdf_files:
            print(f"❌ No PDF files found in {self.docs_folder}")
            return []
        
        print(f"🔍 Found {len(pdf_files)} PDF files to process")
        
        processed_docs = []
        
        for pdf_path in pdf_files:
            print(f"📄 Processing: {pdf_path.name}")
            
            # Extract text
            text = self.extract_text_from_pdf(pdf_path)
            if not text:
                print(f"⚠️ Skipping {pdf_path.name} - no text extracted")
                continue
            
            # Classify service type
            service_type = self.classify_service_type(text, pdf_path.name)
            
            # Extract metadata
            doc_title = self.extract_document_title(text, pdf_path.name)
            doc_date = self.extract_date(text, pdf_path.name)
            
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
            
            processed_docs.append(doc_record)
            print(f"✅ Processed {pdf_path.name} -> {service_type} service")
        
        print(f"🎯 Successfully processed {len(processed_docs)} documents")
        return processed_docs
    
    def chunk_and_prepare_for_embedding(self, documents: List[Dict], chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
        """
        Chunk documents and prepare them for embedding.
        
        Args:
            documents: List of processed document dictionaries
            chunk_size: Maximum tokens per chunk
            overlap: Overlapping tokens between chunks
            
        Returns:
            List of chunked records ready for embedding
        """
        if not documents:
            return []
        
        print(f"🔪 Chunking {len(documents)} documents...")
        
        chunked_records = []
        
        for doc in documents:
            text = doc["text"]
            metadata = doc["metadata"]
            
            # Chunk the document
            chunks = chunk_documents([text], chunk_size=chunk_size, overlap=overlap)
            
            # Create records for each chunk
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    chunk_record = {
                        "text": chunk,
                        "metadata": {
                            **metadata,  # Include all original metadata
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "chunk_size": chunk_size,
                            "overlap": overlap,
                            "token_count": len(chunk.split())
                        }
                    }
                    chunked_records.append(chunk_record)
        
        print(f"✅ Created {len(chunked_records)} chunks from {len(documents)} documents")
        return chunked_records


def process_pdfs_to_chunks(docs_folder: str = "data/Docs", chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
    """
    Convenience function to process PDFs and return chunked records.
    
    Args:
        docs_folder: Path to folder containing PDF documents
        chunk_size: Maximum tokens per chunk
        overlap: Overlapping tokens between chunks
        
    Returns:
        List of chunked records ready for embedding and storage
    """
    processor = PDFProcessor(docs_folder)
    
    # Process PDFs
    documents = processor.process_pdf_documents()
    if not documents:
        return []
    
    # Chunk documents
    chunked_records = processor.chunk_and_prepare_for_embedding(
        documents, chunk_size=chunk_size, overlap=overlap
    )
    
    return chunked_records


if __name__ == "__main__":
    """
    Demo: Process PDFs and show results
    """
    print("NYC Services GPT - PDF Processor Demo")
    print("=" * 50)
    
    try:
        # Process PDFs
        chunked_records = process_pdfs_to_chunks(chunk_size=500, overlap=100)
        
        if chunked_records:
            print(f"\n📊 Processing Results:")
            print(f"  Total chunks: {len(chunked_records)}")
            
            # Show service distribution
            service_counts = {}
            for record in chunked_records:
                service = record["metadata"]["service_type"]
                service_counts[service] = service_counts.get(service, 0) + 1
            
            print(f"  Service distribution:")
            for service, count in service_counts.items():
                print(f"    {service}: {count} chunks")
            
            # Show sample chunk
            if chunked_records:
                sample = chunked_records[0]
                print(f"\n📝 Sample chunk:")
                print(f"  Service: {sample['metadata']['service_type']}")
                print(f"  Title: {sample['metadata']['doc_title']}")
                print(f"  Text: {sample['text'][:100]}...")
                print(f"  Tokens: {sample['metadata']['token_count']}")
            
            print(f"\n🎯 Ready for embedding and ChromaDB storage!")
            
        else:
            print("❌ No documents processed")
            
    except Exception as e:
        print(f"❌ Error processing PDFs: {e}")
        print("Make sure you have PyMuPDF and PyPDF2 installed:")
        print("pip install PyMuPDF PyPDF2")
