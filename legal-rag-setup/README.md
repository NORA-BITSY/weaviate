# Legal Document RAG System with Weaviate

This guide provides comprehensive instructions for setting up Weaviate to process, vectorize, and store legal documents for Retrieval-Augmented Generation (RAG) functionality with both semantic and keyword search capabilities.

## Table of Contents

1. [System Overview](#system-overview)
2. [Prerequisites](#prerequisites)
3. [Weaviate Configuration for Legal Documents](#weaviate-configuration-for-legal-documents)
4. [Document Schema Design](#document-schema-design)
5. [Document Preprocessing Pipeline](#document-preprocessing-pipeline)
6. [Vectorization and Embedding](#vectorization-and-embedding)
7. [Ingestion Pipeline](#ingestion-pipeline)
8. [Search and Retrieval](#search-and-retrieval)
9. [Legal-Specific Considerations](#legal-specific-considerations)
10. [Production Deployment](#production-deployment)

## System Overview

This setup creates a comprehensive legal document processing and retrieval system with:

- **Document Preprocessing**: Extract text, metadata, and structure from legal documents
- **Multi-Modal Vectorization**: Support for text and document images
- **Hybrid Search**: Combine semantic vector search with keyword/BM25 search
- **Legal Metadata**: Store case information, dates, parties, document types
- **Citation Tracking**: Reference tracking and link analysis
- **Security**: Authentication and access control for sensitive legal data

## Prerequisites

### System Requirements
- **Memory**: 16GB+ RAM (32GB+ recommended for large corpora)
- **Storage**: SSD with 500GB+ available space
- **CPU**: 8+ cores recommended
- **Docker**: Version 20.10+ with Docker Compose v2.0+

### Legal Document Formats Supported
- PDF documents
- Word documents (.docx, .doc)
- Plain text files
- HTML/XML legal databases
- Scanned documents (with OCR)

## Weaviate Configuration for Legal Documents

### 1. Docker Compose Configuration

Create a production-ready Weaviate setup optimized for legal documents:

```yaml
version: '3.4'
services:
  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8080:8080"
      - "50051:50051"
    environment:
      # Core Configuration
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_APIKEY_ENABLED: 'true'
      AUTHENTICATION_APIKEY_ALLOWED_KEYS: 'legal-system-key'
      AUTHENTICATION_APIKEY_USERS: 'legal-user@firm.com'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      
      # Modules Configuration
      ENABLE_MODULES: 'text2vec-openai,text2vec-transformers,generative-openai,backup-s3'
      DEFAULT_VECTORIZER_MODULE: 'text2vec-openai'
      
      # Performance Optimization
      GOMAXPROCS: '8'
      PERSISTENCE_MEMTABLES_MAX_SIZE: '500'
      PERSISTENCE_MEMTABLES_FLUSH_IDLE_AFTER_SECONDS: '30'
      
      # Legal-specific
      CLUSTER_HOSTNAME: 'legal-weaviate-node'
      LOG_LEVEL: 'info'
      LOG_FORMAT: 'json'
      
      # External API Keys
      OPENAI_APIKEY: '${OPENAI_API_KEY}'
      TRANSFORMERS_INFERENCE_API: 'http://t2v-transformers:8080'
      
      # Backup Configuration
      BACKUP_S3_BUCKET: '${S3_BACKUP_BUCKET}'
      AWS_ACCESS_KEY_ID: '${AWS_ACCESS_KEY_ID}'
      AWS_SECRET_ACCESS_KEY: '${AWS_SECRET_ACCESS_KEY}'
      AWS_REGION: '${AWS_REGION}'
    volumes:
      - weaviate_data:/var/lib/weaviate
      - ./legal-docs:/legal-docs:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/v1/.well-known/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  # Local transformers for sensitive legal data
  t2v-transformers:
    image: semitechnologies/transformers-inference:sentence-transformers-all-MiniLM-L6-v2
    environment:
      ENABLE_CUDA: '0'  # Set to '1' if GPU available
    ports:
      - "8081:8080"

  # Optional: Local embedding model for highly sensitive documents
  legal-embeddings:
    image: semitechnologies/transformers-inference:sentence-transformers-legal-bert-base
    environment:
      ENABLE_CUDA: '0'
    ports:
      - "8082:8080"

volumes:
  weaviate_data:
```

### 2. Environment Variables

Create a `.env` file:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# AWS Configuration for Backups
S3_BACKUP_BUCKET=legal-documents-backup
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# Security
WEAVIATE_API_KEY=legal-system-key
```

## Document Schema Design

### Legal Document Class Schema

```python
legal_document_schema = {
    "class": "LegalDocument",
    "description": "Legal documents with full text and metadata",
    "vectorizer": "text2vec-openai",
    "moduleConfig": {
        "text2vec-openai": {
            "model": "text-embedding-3-large",
            "dimensions": 3072,
            "type": "text"
        },
        "generative-openai": {
            "model": "gpt-4"
        }
    },
    "vectorIndexConfig": {
        "distance": "cosine",
        "pq": {
            "enabled": True,
            "segments": 32,
            "centroids": 256
        }
    },
    "properties": [
        {
            "name": "title",
            "dataType": ["text"],
            "description": "Document title or case name",
            "tokenization": "word"
        },
        {
            "name": "content",
            "dataType": ["text"],
            "description": "Full document text content",
            "tokenization": "word"
        },
        {
            "name": "summary",
            "dataType": ["text"],
            "description": "Executive summary or abstract",
            "tokenization": "word"
        },
        {
            "name": "documentType",
            "dataType": ["text"],
            "description": "Type of legal document (contract, motion, brief, etc.)",
            "tokenization": "keyword"
        },
        {
            "name": "caseNumber",
            "dataType": ["text"],
            "description": "Case or matter number",
            "tokenization": "keyword"
        },
        {
            "name": "court",
            "dataType": ["text"],
            "description": "Court or jurisdiction",
            "tokenization": "keyword"
        },
        {
            "name": "parties",
            "dataType": ["text[]"],
            "description": "Parties involved in the case",
            "tokenization": "keyword"
        },
        {
            "name": "date",
            "dataType": ["date"],
            "description": "Document date"
        },
        {
            "name": "filePath",
            "dataType": ["text"],
            "description": "Original file path",
            "tokenization": "keyword"
        },
        {
            "name": "pageCount",
            "dataType": ["int"],
            "description": "Number of pages"
        },
        {
            "name": "practiceArea",
            "dataType": ["text[]"],
            "description": "Practice areas (litigation, corporate, etc.)",
            "tokenization": "keyword"
        },
        {
            "name": "jurisdiction",
            "dataType": ["text"],
            "description": "Legal jurisdiction",
            "tokenization": "keyword"
        },
        {
            "name": "citations",
            "dataType": ["text[]"],
            "description": "Legal citations referenced",
            "tokenization": "keyword"
        },
        {
            "name": "confidentialityLevel",
            "dataType": ["text"],
            "description": "Confidentiality classification",
            "tokenization": "keyword"
        }
    ]
}

# Citation/Case Law Schema
citation_schema = {
    "class": "Citation",
    "description": "Legal citations and case law references",
    "vectorizer": "text2vec-openai",
    "properties": [
        {
            "name": "citation",
            "dataType": ["text"],
            "description": "Full legal citation",
            "tokenization": "keyword"
        },
        {
            "name": "caseName",
            "dataType": ["text"],
            "description": "Case name",
            "tokenization": "word"
        },
        {
            "name": "court",
            "dataType": ["text"],
            "description": "Court name",
            "tokenization": "keyword"
        },
        {
            "name": "year",
            "dataType": ["int"],
            "description": "Year decided"
        },
        {
            "name": "holding",
            "dataType": ["text"],
            "description": "Case holding or principle",
            "tokenization": "word"
        },
        {
            "name": "referencedBy",
            "dataType": ["LegalDocument"],
            "description": "Documents that cite this case"
        }
    ]
}

# Document Sections Schema
section_schema = {
    "class": "DocumentSection",
    "description": "Individual sections or paragraphs of legal documents",
    "vectorizer": "text2vec-openai",
    "properties": [
        {
            "name": "content",
            "dataType": ["text"],
            "description": "Section content",
            "tokenization": "word"
        },
        {
            "name": "sectionTitle",
            "dataType": ["text"],
            "description": "Section heading",
            "tokenization": "word"
        },
        {
            "name": "pageNumber",
            "dataType": ["int"],
            "description": "Page number in original document"
        },
        {
            "name": "sectionNumber",
            "dataType": ["text"],
            "description": "Section numbering (e.g., 1.a.i)",
            "tokenization": "keyword"
        },
        {
            "name": "parentDocument",
            "dataType": ["LegalDocument"],
            "description": "Reference to parent document"
        }
    ]
}
```

## Document Preprocessing Pipeline

### 1. Text Extraction and Preprocessing

```python
import os
import PyPDF2
import docx
from pathlib import Path
import re
from datetime import datetime
import spacy
from typing import Dict, List, Optional

class LegalDocumentProcessor:
    def __init__(self):
        # Load legal NLP model (install with: python -m spacy download en_legal_ner)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF files"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting PDF {file_path}: {e}")
        return text
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from Word documents"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            print(f"Error extracting DOCX {file_path}: {e}")
            return ""
    
    def extract_legal_entities(self, text: str) -> Dict:
        """Extract legal entities using NLP"""
        if not self.nlp:
            return {}
        
        doc = self.nlp(text)
        entities = {
            "persons": [],
            "organizations": [],
            "dates": [],
            "money": [],
            "locations": []
        }
        
        for ent in doc.ents:
            if ent.label_ in ["PERSON"]:
                entities["persons"].append(ent.text)
            elif ent.label_ in ["ORG"]:
                entities["organizations"].append(ent.text)
            elif ent.label_ in ["DATE"]:
                entities["dates"].append(ent.text)
            elif ent.label_ in ["MONEY"]:
                entities["money"].append(ent.text)
            elif ent.label_ in ["GPE", "LOC"]:
                entities["locations"].append(ent.text)
        
        return entities
    
    def extract_citations(self, text: str) -> List[str]:
        """Extract legal citations from text"""
        # Regex patterns for common citation formats
        citation_patterns = [
            r'\d+\s+[A-Z][a-z\.]+\s+\d+',  # Basic citation pattern
            r'\d+\s+U\.S\.\s+\d+',  # US Supreme Court
            r'\d+\s+F\.\d+d\s+\d+',  # Federal courts
            r'\d+\s+S\.Ct\.\s+\d+',  # Supreme Court Reporter
        ]
        
        citations = []
        for pattern in citation_patterns:
            matches = re.findall(pattern, text)
            citations.extend(matches)
        
        return list(set(citations))  # Remove duplicates
    
    def extract_case_number(self, text: str, filename: str) -> Optional[str]:
        """Extract case number from text or filename"""
        # Try filename first
        case_patterns = [
            r'[Cc]ase\s*[Nn]o\.?\s*(\d{1,2}:\d{2}-\w{2}-\d{4,5})',
            r'[Nn]o\.?\s*(\d{1,2}:\d{2}-\w{2}-\d{4,5})',
            r'(\d{4,5})',  # Simple number pattern
        ]
        
        for pattern in case_patterns:
            match = re.search(pattern, filename)
            if match:
                return match.group(1)
        
        # Try text content
        for pattern in case_patterns:
            match = re.search(pattern, text[:1000])  # Check first 1000 chars
            if match:
                return match.group(1)
        
        return None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove page numbers and headers/footers
        text = re.sub(r'Page \d+ of \d+', '', text)
        # Remove line breaks within sentences
        text = re.sub(r'(?<=[a-z])\n(?=[a-z])', ' ', text)
        return text.strip()
    
    def split_into_sections(self, text: str) -> List[Dict]:
        """Split document into logical sections"""
        # Split by common legal section patterns
        section_patterns = [
            r'^[IVX]+\.\s+',  # Roman numerals
            r'^\d+\.\s+',  # Numbers
            r'^[A-Z]+\.\s+',  # Capital letters
            r'^WHEREAS',  # Whereas clauses
            r'^NOW THEREFORE',  # Therefore clauses
        ]
        
        sections = []
        current_section = ""
        section_title = ""
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            is_header = any(re.match(pattern, line) for pattern in section_patterns)
            
            if is_header and current_section:
                sections.append({
                    "title": section_title,
                    "content": current_section.strip()
                })
                current_section = ""
                section_title = line
            elif is_header:
                section_title = line
            else:
                current_section += line + " "
        
        # Add final section
        if current_section:
            sections.append({
                "title": section_title,
                "content": current_section.strip()
            })
        
        return sections
```

### 2. Metadata Extraction

```python
class MetadataExtractor:
    def __init__(self):
        self.document_types = {
            'contract': ['agreement', 'contract', 'license', 'nda'],
            'motion': ['motion', 'petition', 'application'],
            'brief': ['brief', 'memorandum', 'memo'],
            'pleading': ['complaint', 'answer', 'reply'],
            'discovery': ['interrogatory', 'deposition', 'request'],
            'order': ['order', 'judgment', 'decree'],
            'correspondence': ['letter', 'email', 'correspondence']
        }
        
        self.practice_areas = {
            'litigation': ['litigation', 'trial', 'court', 'lawsuit'],
            'corporate': ['corporate', 'merger', 'acquisition', 'securities'],
            'employment': ['employment', 'labor', 'discrimination', 'harassment'],
            'intellectual_property': ['patent', 'trademark', 'copyright', 'ip'],
            'real_estate': ['real estate', 'property', 'lease', 'deed'],
            'family': ['divorce', 'custody', 'family', 'marriage'],
            'criminal': ['criminal', 'prosecution', 'defense', 'plea']
        }
    
    def extract_document_type(self, text: str, filename: str) -> str:
        """Determine document type from content and filename"""
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        for doc_type, keywords in self.document_types.items():
            for keyword in keywords:
                if keyword in text_lower or keyword in filename_lower:
                    return doc_type
        
        return 'other'
    
    def extract_practice_areas(self, text: str) -> List[str]:
        """Identify practice areas from content"""
        text_lower = text.lower()
        areas = []
        
        for area, keywords in self.practice_areas.items():
            for keyword in keywords:
                if keyword in text_lower:
                    areas.append(area)
                    break
        
        return areas or ['general']
    
    def extract_parties(self, text: str) -> List[str]:
        """Extract party names from legal documents"""
        # Common patterns for party identification
        party_patterns = [
            r'([A-Z][a-z]+ [A-Z][a-z]+),?\s+(?:Plaintiff|Defendant|Petitioner|Respondent)',
            r'(?:Plaintiff|Defendant|Petitioner|Respondent):?\s+([A-Z][a-z]+ [A-Z][a-z]+)',
            r'([A-Z][A-Z\s&,\.]+(?:LLC|INC|CORP|LTD))',
        ]
        
        parties = []
        for pattern in party_patterns:
            matches = re.findall(pattern, text[:2000])  # Check first 2000 chars
            parties.extend(matches)
        
        return list(set(parties))  # Remove duplicates
    
    def extract_court_jurisdiction(self, text: str) -> Dict[str, str]:
        """Extract court and jurisdiction information"""
        court_patterns = [
            r'(United States District Court)',
            r'(U\.S\. Court of Appeals)',
            r'(Supreme Court)',
            r'([A-Z][a-z]+ (?:District|Superior|Municipal) Court)',
        ]
        
        jurisdiction_patterns = [
            r'(?:District of|for the) ([A-Z][a-z]+ District)',
            r'State of ([A-Z][a-z]+)',
            r'Commonwealth of ([A-Z][a-z]+)',
        ]
        
        court = None
        jurisdiction = None
        
        for pattern in court_patterns:
            match = re.search(pattern, text[:1000])
            if match:
                court = match.group(1)
                break
        
        for pattern in jurisdiction_patterns:
            match = re.search(pattern, text[:1000])
            if match:
                jurisdiction = match.group(1)
                break
        
        return {"court": court, "jurisdiction": jurisdiction}
```

## Vectorization and Embedding

### 1. Weaviate Client Setup

```python
import weaviate
import json
from typing import Dict, List, Optional
import openai

class LegalWeaviateClient:
    def __init__(self, weaviate_url: str = "http://localhost:8080", api_key: str = None):
        auth_config = weaviate.AuthApiKey(api_key=api_key) if api_key else None
        
        self.client = weaviate.Client(
            url=weaviate_url,
            auth_client_secret=auth_config,
            additional_headers={
                "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
            }
        )
        
        # Initialize schemas
        self.setup_schemas()
    
    def setup_schemas(self):
        """Create Weaviate schemas for legal documents"""
        schemas = [legal_document_schema, citation_schema, section_schema]
        
        for schema in schemas:
            try:
                if not self.client.schema.exists(schema["class"]):
                    self.client.schema.create_class(schema)
                    print(f"Created schema for {schema['class']}")
                else:
                    print(f"Schema for {schema['class']} already exists")
            except Exception as e:
                print(f"Error creating schema for {schema['class']}: {e}")
    
    def add_legal_document(self, document_data: Dict) -> str:
        """Add a legal document to Weaviate"""
        try:
            # Add main document
            result = self.client.data_object.create(
                data_object=document_data,
                class_name="LegalDocument"
            )
            
            document_id = result
            print(f"Added document with ID: {document_id}")
            
            return document_id
        except Exception as e:
            print(f"Error adding document: {e}")
            return None
    
    def add_document_sections(self, sections: List[Dict], document_id: str):
        """Add document sections with reference to parent document"""
        for i, section in enumerate(sections):
            try:
                section_data = {
                    **section,
                    "parentDocument": [{
                        "beacon": f"weaviate://localhost/LegalDocument/{document_id}"
                    }]
                }
                
                section_id = self.client.data_object.create(
                    data_object=section_data,
                    class_name="DocumentSection"
                )
                print(f"Added section {i+1} with ID: {section_id}")
            except Exception as e:
                print(f"Error adding section {i+1}: {e}")
    
    def add_citations(self, citations: List[str], document_id: str):
        """Add citations with reference to source document"""
        for citation in citations:
            try:
                citation_data = {
                    "citation": citation,
                    "referencedBy": [{
                        "beacon": f"weaviate://localhost/LegalDocument/{document_id}"
                    }]
                }
                
                citation_id = self.client.data_object.create(
                    data_object=citation_data,
                    class_name="Citation"
                )
                print(f"Added citation: {citation}")
            except Exception as e:
                print(f"Error adding citation {citation}: {e}")
```

### 2. Batch Processing Pipeline

```python
class LegalDocumentPipeline:
    def __init__(self, weaviate_client: LegalWeaviateClient):
        self.weaviate = weaviate_client
        self.processor = LegalDocumentProcessor()
        self.metadata_extractor = MetadataExtractor()
    
    def process_document(self, file_path: str) -> Optional[str]:
        """Process a single legal document through the full pipeline"""
        print(f"Processing: {file_path}")
        
        # Extract text based on file type
        if file_path.endswith('.pdf'):
            text = self.processor.extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            text = self.processor.extract_text_from_docx(file_path)
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            print(f"Unsupported file type: {file_path}")
            return None
        
        if not text.strip():
            print(f"No text extracted from {file_path}")
            return None
        
        # Clean text
        text = self.processor.clean_text(text)
        
        # Extract metadata
        filename = os.path.basename(file_path)
        document_type = self.metadata_extractor.extract_document_type(text, filename)
        practice_areas = self.metadata_extractor.extract_practice_areas(text)
        parties = self.metadata_extractor.extract_parties(text)
        court_info = self.metadata_extractor.extract_court_jurisdiction(text)
        citations = self.processor.extract_citations(text)
        case_number = self.processor.extract_case_number(text, filename)
        
        # Generate summary (first 500 words)
        words = text.split()
        summary = ' '.join(words[:500]) if len(words) > 500 else text
        
        # Create document data
        document_data = {
            "title": filename.replace('.pdf', '').replace('.docx', '').replace('_', ' '),
            "content": text,
            "summary": summary,
            "documentType": document_type,
            "caseNumber": case_number or "Unknown",
            "court": court_info.get("court"),
            "jurisdiction": court_info.get("jurisdiction"),
            "parties": parties,
            "filePath": file_path,
            "pageCount": len(text) // 3000,  # Rough estimate
            "practiceArea": practice_areas,
            "citations": citations,
            "confidentialityLevel": "standard",  # Default
            "date": datetime.now().isoformat()
        }
        
        # Add to Weaviate
        document_id = self.weaviate.add_legal_document(document_data)
        
        if document_id:
            # Process sections
            sections = self.processor.split_into_sections(text)
            if sections:
                self.weaviate.add_document_sections(sections, document_id)
            
            # Add citations
            if citations:
                self.weaviate.add_citations(citations, document_id)
        
        return document_id
    
    def process_directory(self, directory_path: str):
        """Process all legal documents in a directory"""
        supported_extensions = ['.pdf', '.docx', '.txt']
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if any(file.endswith(ext) for ext in supported_extensions):
                    file_path = os.path.join(root, file)
                    try:
                        self.process_document(file_path)
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
                        continue
```

## Search and Retrieval

### 1. Hybrid Search Implementation

```python
class LegalSearchEngine:
    def __init__(self, weaviate_client: LegalWeaviateClient):
        self.weaviate = weaviate_client
    
    def semantic_search(self, query: str, limit: int = 10, filters: Dict = None) -> List[Dict]:
        """Perform semantic vector search"""
        where_filter = self._build_where_filter(filters) if filters else None
        
        result = (
            self.weaviate.client.query
            .get("LegalDocument", [
                "title", "content", "summary", "documentType", 
                "caseNumber", "court", "parties", "practiceArea", 
                "citations", "date", "_additional {score}"
            ])
            .with_near_text({"concepts": [query]})
            .with_limit(limit)
            .with_where(where_filter)
            .do()
        )
        
        return result.get("data", {}).get("Get", {}).get("LegalDocument", [])
    
    def keyword_search(self, query: str, limit: int = 10, filters: Dict = None) -> List[Dict]:
        """Perform BM25 keyword search"""
        where_filter = self._build_where_filter(filters) if filters else None
        
        result = (
            self.weaviate.client.query
            .get("LegalDocument", [
                "title", "content", "summary", "documentType", 
                "caseNumber", "court", "parties", "practiceArea", 
                "citations", "date", "_additional {score}"
            ])
            .with_bm25(query=query)
            .with_limit(limit)
            .with_where(where_filter)
            .do()
        )
        
        return result.get("data", {}).get("Get", {}).get("LegalDocument", [])
    
    def hybrid_search(self, query: str, alpha: float = 0.5, limit: int = 10, filters: Dict = None) -> List[Dict]:
        """Perform hybrid search combining semantic and keyword search"""
        where_filter = self._build_where_filter(filters) if filters else None
        
        result = (
            self.weaviate.client.query
            .get("LegalDocument", [
                "title", "content", "summary", "documentType", 
                "caseNumber", "court", "parties", "practiceArea", 
                "citations", "date", "_additional {score}"
            ])
            .with_hybrid(query=query, alpha=alpha)
            .with_limit(limit)
            .with_where(where_filter)
            .do()
        )
        
        return result.get("data", {}).get("Get", {}).get("LegalDocument", [])
    
    def search_citations(self, citation: str) -> List[Dict]:
        """Search for specific legal citations"""
        result = (
            self.weaviate.client.query
            .get("Citation", ["citation", "caseName", "court", "year", "holding"])
            .with_where({
                "path": ["citation"],
                "operator": "Like",
                "valueText": f"*{citation}*"
            })
            .do()
        )
        
        return result.get("data", {}).get("Get", {}).get("Citation", [])
    
    def search_by_case_number(self, case_number: str) -> List[Dict]:
        """Search documents by case number"""
        result = (
            self.weaviate.client.query
            .get("LegalDocument", [
                "title", "content", "summary", "documentType", 
                "caseNumber", "court", "parties", "practiceArea", "date"
            ])
            .with_where({
                "path": ["caseNumber"],
                "operator": "Equal",
                "valueText": case_number
            })
            .do()
        )
        
        return result.get("data", {}).get("Get", {}).get("LegalDocument", [])
    
    def _build_where_filter(self, filters: Dict) -> Dict:
        """Build where filter for Weaviate queries"""
        conditions = []
        
        if filters.get("document_type"):
            conditions.append({
                "path": ["documentType"],
                "operator": "Equal",
                "valueText": filters["document_type"]
            })
        
        if filters.get("practice_area"):
            conditions.append({
                "path": ["practiceArea"],
                "operator": "ContainsAny",
                "valueText": filters["practice_area"]
            })
        
        if filters.get("court"):
            conditions.append({
                "path": ["court"],
                "operator": "Like",
                "valueText": f"*{filters['court']}*"
            })
        
        if filters.get("date_after"):
            conditions.append({
                "path": ["date"],
                "operator": "GreaterThan",
                "valueDate": filters["date_after"]
            })
        
        if len(conditions) == 1:
            return conditions[0]
        elif len(conditions) > 1:
            return {
                "operator": "And",
                "operands": conditions
            }
        
        return {}
    
    def generate_answer(self, query: str, context_docs: List[Dict]) -> str:
        """Generate answer using retrieved documents as context"""
        context = "\n\n".join([
            f"Document: {doc['title']}\nContent: {doc['summary'][:500]}..."
            for doc in context_docs[:3]
        ])
        
        result = (
            self.weaviate.client.query
            .get("LegalDocument", ["title"])
            .with_generate(
                single_prompt=f"Based on the following legal documents, answer this question: {query}\n\nContext:\n{context}\n\nAnswer:"
            )
            .with_limit(1)
            .do()
        )
        
        generated = result.get("data", {}).get("Get", {}).get("LegalDocument", [])
        if generated and generated[0].get("_additional", {}).get("generate", {}).get("singleResult"):
            return generated[0]["_additional"]["generate"]["singleResult"]
        
        return "Unable to generate answer based on available documents."
```

### 2. RAG Query Interface

```python
class LegalRAGSystem:
    def __init__(self, weaviate_client: LegalWeaviateClient):
        self.search_engine = LegalSearchEngine(weaviate_client)
    
    def query(self, question: str, search_type: str = "hybrid", filters: Dict = None, limit: int = 5) -> Dict:
        """Main query interface for the legal RAG system"""
        
        # Retrieve relevant documents
        if search_type == "semantic":
            documents = self.search_engine.semantic_search(question, limit=limit, filters=filters)
        elif search_type == "keyword":
            documents = self.search_engine.keyword_search(question, limit=limit, filters=filters)
        else:  # hybrid
            documents = self.search_engine.hybrid_search(question, limit=limit, filters=filters)
        
        # Generate answer
        answer = self.search_engine.generate_answer(question, documents)
        
        # Extract citations from retrieved documents
        citations = []
        for doc in documents:
            if doc.get("citations"):
                citations.extend(doc["citations"])
        
        return {
            "question": question,
            "answer": answer,
            "source_documents": documents,
            "citations": list(set(citations)),  # Remove duplicates
            "search_type": search_type
        }
    
    def legal_research(self, topic: str, practice_area: str = None) -> Dict:
        """Specialized legal research query"""
        filters = {"practice_area": [practice_area]} if practice_area else None
        
        # Perform multiple searches with different strategies
        semantic_results = self.search_engine.semantic_search(topic, limit=3, filters=filters)
        keyword_results = self.search_engine.keyword_search(topic, limit=3, filters=filters)
        
        # Combine and deduplicate results
        all_results = semantic_results + keyword_results
        unique_results = []
        seen_titles = set()
        
        for doc in all_results:
            if doc["title"] not in seen_titles:
                unique_results.append(doc)
                seen_titles.add(doc["title"])
        
        return {
            "topic": topic,
            "practice_area": practice_area,
            "documents": unique_results[:5],
            "research_summary": self._generate_research_summary(unique_results[:3])
        }
    
    def _generate_research_summary(self, documents: List[Dict]) -> str:
        """Generate a research summary from multiple documents"""
        if not documents:
            return "No relevant documents found."
        
        context = "\n\n".join([
            f"Document: {doc['title']}\nSummary: {doc['summary'][:300]}..."
            for doc in documents
        ])
        
        # This would typically use the generative module
        return f"Based on {len(documents)} documents, the research indicates..."
```

## Usage Examples

### 1. Setting Up the System

```python
# Initialize the system
weaviate_client = LegalWeaviateClient(
    weaviate_url="http://localhost:8080",
    api_key="legal-system-key"
)

# Create processing pipeline
pipeline = LegalDocumentPipeline(weaviate_client)

# Process documents
pipeline.process_directory("/path/to/legal/documents")

# Initialize RAG system
rag_system = LegalRAGSystem(weaviate_client)
```

### 2. Querying the System

```python
# Basic question answering
result = rag_system.query(
    question="What are the key provisions in employment contracts regarding non-compete clauses?",
    search_type="hybrid",
    filters={"practice_area": ["employment"]},
    limit=5
)

print(f"Answer: {result['answer']}")
print(f"Based on {len(result['source_documents'])} documents")

# Legal research
research_result = rag_system.legal_research(
    topic="intellectual property licensing agreements",
    practice_area="intellectual_property"
)

print(f"Research Summary: {research_result['research_summary']}")

# Case-specific search
case_docs = rag_system.search_engine.search_by_case_number("21-cv-1234")
print(f"Found {len(case_docs)} documents for case 21-cv-1234")

# Citation search
citations = rag_system.search_engine.search_citations("Brown v. Board")
print(f"Found {len(citations)} citations matching 'Brown v. Board'")
```

## Legal-Specific Considerations

### 1. Privacy and Security

```python
# Implement document-level security
def add_security_filters(self, user_role: str, user_id: str) -> Dict:
    """Add security filters based on user permissions"""
    if user_role == "partner":
        return {}  # Partners can see everything
    elif user_role == "associate":
        return {
            "path": ["confidentialityLevel"],
            "operator": "NotEqual",
            "valueText": "highly_confidential"
        }
    elif user_role == "paralegal":
        return {
            "path": ["confidentialityLevel"],
            "operator": "Equal",
            "valueText": "standard"
        }
    else:
        return {
            "path": ["confidentialityLevel"],
            "operator": "Equal",
            "valueText": "public"
        }
```

### 2. Audit Logging

```python
class AuditLogger:
    def __init__(self):
        self.log_file = "/var/log/legal-rag-audit.log"
    
    def log_query(self, user_id: str, query: str, results_count: int):
        """Log search queries for compliance"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "user_id": user_id,
            "action": "search",
            "query": query,
            "results_count": results_count
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def log_document_access(self, user_id: str, document_id: str):
        """Log document access for compliance"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "user_id": user_id,
            "action": "document_access",
            "document_id": document_id
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
```

### 3. Data Retention and Deletion

```python
class DataRetentionManager:
    def __init__(self, weaviate_client):
        self.client = weaviate_client
    
    def mark_for_deletion(self, document_id: str, retention_date: str):
        """Mark documents for deletion based on retention policies"""
        self.client.client.data_object.update(
            uuid=document_id,
            class_name="LegalDocument",
            data_object={"retentionDate": retention_date}
        )
    
    def purge_expired_documents(self):
        """Remove documents past their retention date"""
        today = datetime.now().isoformat()
        
        # Query for expired documents
        result = (
            self.client.client.query
            .get("LegalDocument", ["title"])
            .with_where({
                "path": ["retentionDate"],
                "operator": "LessThan",
                "valueDate": today
            })
            .with_additional(["id"])
            .do()
        )
        
        expired_docs = result.get("data", {}).get("Get", {}).get("LegalDocument", [])
        
        for doc in expired_docs:
            doc_id = doc["_additional"]["id"]
            self.client.client.data_object.delete(uuid=doc_id)
            print(f"Deleted expired document: {doc_id}")
```

## Production Deployment

### 1. Docker Compose for Production

```yaml
version: '3.4'
services:
  weaviate:
    image: semitechnologies/weaviate:latest
    restart: unless-stopped
    ports:
      - "8080:8080"
      - "50051:50051"
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_APIKEY_ENABLED: 'true'
      AUTHENTICATION_APIKEY_ALLOWED_KEYS: '${WEAVIATE_API_KEY}'
      AUTHENTICATION_APIKEY_USERS: 'legal-system@firm.com'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      ENABLE_MODULES: 'text2vec-openai,generative-openai,backup-s3'
      DEFAULT_VECTORIZER_MODULE: 'text2vec-openai'
      OPENAI_APIKEY: '${OPENAI_API_KEY}'
      BACKUP_S3_BUCKET: '${S3_BACKUP_BUCKET}'
      AWS_ACCESS_KEY_ID: '${AWS_ACCESS_KEY_ID}'
      AWS_SECRET_ACCESS_KEY: '${AWS_SECRET_ACCESS_KEY}'
      AWS_REGION: '${AWS_REGION}'
      LOG_LEVEL: 'info'
      PROMETHEUS_MONITORING_ENABLED: 'true'
    volumes:
      - weaviate_data:/var/lib/weaviate
      - ./backup:/backup
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/v1/.well-known/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          memory: 16G
          cpus: '8'
        reservations:
          memory: 8G
          cpus: '4'

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - weaviate

volumes:
  weaviate_data:
```

### 2. Backup Strategy

```bash
#!/bin/bash
# backup-legal-docs.sh

# Create backup
curl -X POST \
  http://localhost:8080/v1/backups/s3 \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer legal-system-key' \
  -d '{
    "id": "legal-docs-backup-'$(date +%Y%m%d)'",
    "include": ["LegalDocument", "Citation", "DocumentSection"]
  }'

# Verify backup status
curl -X GET \
  http://localhost:8080/v1/backups/s3/legal-docs-backup-$(date +%Y%m%d) \
  -H 'Authorization: Bearer legal-system-key'
```

### 3. Monitoring and Alerting

```python
import requests
import time
from prometheus_client import start_http_server, Counter, Histogram, Gauge

class LegalRAGMonitoring:
    def __init__(self):
        self.query_counter = Counter('legal_rag_queries_total', 'Total queries')
        self.query_duration = Histogram('legal_rag_query_duration_seconds', 'Query duration')
        self.active_users = Gauge('legal_rag_active_users', 'Active users')
        
        # Start Prometheus metrics server
        start_http_server(8000)
    
    def check_weaviate_health(self):
        """Monitor Weaviate health"""
        try:
            response = requests.get("http://localhost:8080/v1/.well-known/ready")
            return response.status_code == 200
        except:
            return False
    
    def monitor_performance(self):
        """Monitor system performance metrics"""
        while True:
            try:
                # Check Weaviate health
                if not self.check_weaviate_health():
                    print("ALERT: Weaviate is not healthy")
                
                # Check memory usage
                memory_response = requests.get("http://localhost:2112/metrics")
                if memory_response.status_code == 200:
                    # Parse memory metrics and alert if high
                    pass
                
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(60)
```

This comprehensive setup provides a robust foundation for processing legal documents with Weaviate, including preprocessing, vectorization, storage, and retrieval capabilities specifically designed for legal use cases.
