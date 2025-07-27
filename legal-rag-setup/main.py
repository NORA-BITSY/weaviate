#!/usr/bin/env python3
"""
Legal Document RAG System - Complete Example
Demonstrates the full pipeline from document ingestion to retrieval and generation
"""

import os
import sys
from pathlib import Path
from typing import Dict, List

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from weaviate_client import LegalWeaviateClient
from ingestion_pipeline import LegalDocumentPipeline
from search_engine import LegalRAGSystem


class LegalRAGDemo:
    """
    Demonstration of the complete Legal Document RAG system
    """
    
    def __init__(self):
        # Initialize Weaviate client
        self.weaviate_client = LegalWeaviateClient(
            weaviate_url=os.getenv("WEAVIATE_URL", "http://localhost:8080"),
            api_key=os.getenv("WEAVIATE_API_KEY")
        )
        
        # Initialize pipeline and RAG system
        self.pipeline = LegalDocumentPipeline(self.weaviate_client)
        self.rag_system = LegalRAGSystem(self.weaviate_client)
    
    def setup_system(self):
        """Setup the system and check connectivity"""
        print("🏛️  Legal Document RAG System")
        print("=" * 50)
        
        # Check Weaviate connectivity
        try:
            schema_info = self.weaviate_client.get_schema_info()
            print("✅ Connected to Weaviate successfully")
            print(f"📊 Schema classes: {len(schema_info.get('classes', []))}")
        except Exception as e:
            print(f"❌ Failed to connect to Weaviate: {e}")
            return False
        
        return True
    
    def ingest_documents(self, document_path: str):
        """Ingest documents from a directory or file"""
        print(f"\n📁 Ingesting documents from: {document_path}")
        
        if not os.path.exists(document_path):
            print(f"❌ Path not found: {document_path}")
            return
        
        if os.path.isfile(document_path):
            # Single file
            document_id = self.pipeline.process_document(document_path)
            if document_id:
                print(f"✅ Successfully processed file: {os.path.basename(document_path)}")
            else:
                print(f"❌ Failed to process file: {document_path}")
        else:
            # Directory
            stats = self.pipeline.get_processing_stats(document_path)
            print(f"📊 Directory stats:")
            print(f"   Total files: {stats['total_files']}")
            print(f"   Supported files: {stats['supported_files']}")
            print(f"   Total size: {stats['total_size_mb']} MB")
            
            if stats['supported_files'] > 0:
                processed_docs = self.pipeline.process_directory(document_path)
                print(f"✅ Successfully processed {len(processed_docs)} documents")
            else:
                print("❌ No supported documents found")
    
    def demonstrate_search(self):
        """Demonstrate various search capabilities"""
        print(f"\n🔍 Search Demonstrations")
        print("-" * 30)
        
        # Example searches
        search_examples = [
            {
                "name": "Semantic Search",
                "query": "What are the obligations of employers regarding workplace safety?",
                "search_type": "semantic",
                "filters": {"practice_area": ["employment"]}
            },
            {
                "name": "Keyword Search",
                "query": "non-compete clause",
                "search_type": "keyword",
                "filters": {"document_type": "contract"}
            },
            {
                "name": "Hybrid Search",
                "query": "intellectual property licensing terms",
                "search_type": "hybrid",
                "filters": {"practice_area": ["intellectual_property"]}
            }
        ]
        
        for example in search_examples:
            print(f"\n🔎 {example['name']}")
            print(f"Query: '{example['query']}'")
            
            try:
                result = self.rag_system.query(
                    question=example['query'],
                    search_type=example['search_type'],
                    filters=example.get('filters'),
                    limit=3
                )
                
                print(f"📄 Found {len(result['source_documents'])} relevant documents")
                
                if result['source_documents']:
                    for i, doc in enumerate(result['source_documents'][:2], 1):
                        title = doc.get('title', 'Unknown')[:50]
                        doc_type = doc.get('documentType', 'unknown')
                        score = doc.get('_additional', {}).get('score', 'N/A')
                        print(f"   {i}. {title}... ({doc_type}, score: {score})")
                
                # Show generated answer (truncated)
                answer = result['answer'][:200] + "..." if len(result['answer']) > 200 else result['answer']
                print(f"🤖 Answer: {answer}")
                
            except Exception as e:
                print(f"❌ Search failed: {e}")
    
    def demonstrate_legal_research(self):
        """Demonstrate legal research capabilities"""
        print(f"\n📚 Legal Research Demonstration")
        print("-" * 35)
        
        research_topics = [
            {
                "topic": "employment termination procedures",
                "practice_area": "employment"
            },
            {
                "topic": "merger and acquisition due diligence",
                "practice_area": "corporate"
            }
        ]
        
        for research in research_topics:
            print(f"\n📖 Researching: {research['topic']}")
            
            try:
                result = self.rag_system.legal_research(
                    topic=research['topic'],
                    practice_area=research['practice_area']
                )
                
                print(f"📄 Found {len(result['documents'])} relevant documents")
                print(f"📑 Found {len(result['sections'])} relevant sections")
                
                # Show summary (truncated)
                summary = result['research_summary'][:300] + "..." if len(result['research_summary']) > 300 else result['research_summary']
                print(f"📝 Summary: {summary}")
                
            except Exception as e:
                print(f"❌ Research failed: {e}")
    
    def demonstrate_case_analysis(self):
        """Demonstrate case analysis if case documents exist"""
        print(f"\n⚖️  Case Analysis Demonstration")
        print("-" * 32)
        
        # Try to find any case numbers in the system
        try:
            # Simple search to find documents with case numbers
            sample_docs = self.rag_system.search_engine.semantic_search("case", limit=5)
            
            case_numbers = []
            for doc in sample_docs:
                case_num = doc.get('caseNumber')
                if case_num and case_num != 'Unknown':
                    case_numbers.append(case_num)
            
            if case_numbers:
                case_number = case_numbers[0]
                print(f"📋 Analyzing case: {case_number}")
                
                result = self.rag_system.case_analysis(case_number)
                
                print(f"📄 Total documents: {result.get('total_documents', 0)}")
                print(f"👥 Parties: {', '.join(result.get('parties', [])[:3])}")
                print(f"🏛️  Courts: {', '.join(result.get('courts', []))}")
                print(f"⚖️  Practice areas: {', '.join(result.get('practice_areas', []))}")
                
            else:
                print("📋 No case numbers found in current documents")
                
        except Exception as e:
            print(f"❌ Case analysis failed: {e}")
    
    def interactive_mode(self):
        """Interactive query mode"""
        print(f"\n💬 Interactive Mode")
        print("-" * 18)
        print("Ask questions about your legal documents. Type 'exit' to quit.")
        
        while True:
            try:
                question = input("\n❓ Your question: ").strip()
                
                if question.lower() in ['exit', 'quit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not question:
                    continue
                
                print("🔍 Searching...")
                
                result = self.rag_system.query(
                    question=question,
                    search_type="hybrid",
                    limit=3
                )
                
                print(f"\n🤖 Answer: {result['answer']}")
                print(f"\n📚 Based on {len(result['source_documents'])} source documents:")
                
                for i, doc in enumerate(result['source_documents'], 1):
                    title = doc.get('title', 'Unknown')
                    doc_type = doc.get('documentType', 'unknown')
                    print(f"   {i}. {title} ({doc_type})")
                
                if result['citations']:
                    print(f"\n📖 Related citations: {', '.join(result['citations'][:3])}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def run_demo(self, document_path: str = None):
        """Run the complete demonstration"""
        if not self.setup_system():
            return
        
        # Ingest documents if path provided
        if document_path:
            self.ingest_documents(document_path)
        
        # Run demonstrations
        self.demonstrate_search()
        self.demonstrate_legal_research()
        self.demonstrate_case_analysis()
        
        # Interactive mode
        self.interactive_mode()


def main():
    """Main function to run the demo"""
    print("🏛️  Legal Document RAG System - Demo")
    print("=====================================")
    
    # Check environment variables
    required_env_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables and try again.")
        return
    
    # Get document path from command line or use default
    document_path = None
    if len(sys.argv) > 1:
        document_path = sys.argv[1]
    else:
        # Check for default paths
        default_paths = [
            "./legal-docs",
            "./documents",
            "/legal-docs"
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                document_path = path
                break
    
    if document_path:
        print(f"📁 Will process documents from: {document_path}")
    else:
        print("📁 No document path provided. Demo will use existing data.")
        print("   Usage: python main.py /path/to/legal/documents")
    
    # Create and run demo
    demo = LegalRAGDemo()
    demo.run_demo(document_path)


if __name__ == "__main__":
    main()
