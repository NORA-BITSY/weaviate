# Quick Start Guide - Legal Document RAG System

## Overview
This system provides a complete solution for preprocessing, vectorizing, and storing legal documents in a Weaviate vector database for Retrieval-Augmented Generation (RAG) functionality.

## Quick Setup

### 1. Prerequisites
- Docker and Docker Compose
- Python 3.8+
- OpenAI API key

### 2. Installation
```bash
# Clone or navigate to the setup directory
cd legal-rag-setup

# Run the automated setup
./setup.sh

# Edit environment variables (required)
nano .env  # Add your OpenAI API key
```

### 3. Start the System
```bash
# Start Weaviate services
./setup.sh start

# Activate Python environment
source venv/bin/activate

# Run the demo with sample documents
python main.py ./legal-docs
```

## Basic Usage

### Document Ingestion
```python
from src.weaviate_client import LegalWeaviateClient
from src.ingestion_pipeline import LegalDocumentPipeline

# Initialize
client = LegalWeaviateClient()
pipeline = LegalDocumentPipeline(client)

# Process documents
pipeline.process_directory("/path/to/legal/documents")
```

### Search and Query
```python
from src.search_engine import LegalRAGSystem

# Initialize RAG system
rag = LegalRAGSystem(client)

# Ask questions
result = rag.query(
    question="What are the key provisions in employment contracts?",
    search_type="hybrid",
    filters={"practice_area": ["employment"]}
)

print(result['answer'])
```

### Legal Research
```python
# Comprehensive legal research
research = rag.legal_research(
    topic="intellectual property licensing",
    practice_area="intellectual_property"
)

print(research['research_summary'])
```

## Key Features

✅ **Document Processing**: PDF, DOCX, TXT, HTML support  
✅ **Metadata Extraction**: Parties, courts, case numbers, citations  
✅ **Hybrid Search**: Semantic + keyword search  
✅ **Legal-Specific Schema**: Optimized for legal documents  
✅ **RAG Generation**: AI-powered question answering  
✅ **Security**: Confidentiality levels and access control  
✅ **Backup & Recovery**: S3-based backup system  

## Architecture

```
Legal Documents → Preprocessing → Vectorization → Weaviate → RAG System
     ↓                ↓              ↓            ↓          ↓
   Extract Text    Clean & Parse   OpenAI      Vector DB   Q&A + Search
   Metadata        Structure       Embeddings   Storage     Generation
```

## File Structure
```
legal-rag-setup/
├── src/
│   ├── document_processor.py    # Text extraction & preprocessing
│   ├── weaviate_client.py      # Weaviate integration
│   ├── ingestion_pipeline.py   # Document processing pipeline
│   └── search_engine.py        # Search & RAG functionality
├── docker-compose.yml          # Weaviate services
├── requirements.txt            # Python dependencies
├── setup.sh                   # Automated setup script
├── main.py                    # Demo application
└── README.md                  # Complete documentation
```

## Configuration

### Environment Variables (.env)
```bash
OPENAI_API_KEY=your_openai_api_key_here
WEAVIATE_API_KEY=legal-system-key
S3_BACKUP_BUCKET=legal-documents-backup
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

### Supported Document Types
- PDF documents
- Word documents (.docx, .doc)
- Plain text files (.txt)
- HTML files (.html, .htm)

### Legal Document Schema
- **LegalDocument**: Main document class with full text and metadata
- **Citation**: Legal citations and case references
- **DocumentSection**: Individual sections for granular search

## Common Use Cases

### 1. Contract Analysis
```python
# Search employment contracts
results = rag.search_engine.advanced_search({
    'query': 'non-compete clause',
    'document_type': 'contract',
    'practice_area': ['employment'],
    'search_type': 'hybrid'
})
```

### 2. Case Research
```python
# Analyze a specific case
case_analysis = rag.case_analysis("21-cv-1234")
print(f"Found {case_analysis['total_documents']} documents")
```

### 3. Citation Tracking
```python
# Find how a citation is used
citation_analysis = rag.citation_analysis("Brown v. Board")
```

## Troubleshooting

### Common Issues

1. **Weaviate Connection Failed**
   ```bash
   # Check if services are running
   docker-compose ps
   
   # View logs
   docker-compose logs weaviate
   ```

2. **OpenAI API Errors**
   - Verify your API key in `.env`
   - Check API quota and billing

3. **Document Processing Errors**
   - Ensure supported file formats
   - Check file permissions
   - Verify file sizes (default limit: 50MB)

### Performance Optimization

1. **Memory Settings**
   - Increase Docker memory allocation
   - Adjust `PERSISTENCE_MEMTABLES_MAX_SIZE`

2. **Vector Index Tuning**
   - Modify PQ settings for large datasets
   - Adjust `ef` and `efConstruction` parameters

3. **Batch Processing**
   - Process documents in smaller batches
   - Use background processing for large volumes

## Commands Reference

```bash
# Setup and management
./setup.sh setup    # Complete setup
./setup.sh start    # Start services
./setup.sh stop     # Stop services
./setup.sh restart  # Restart services
./setup.sh test     # Test connectivity
./setup.sh clean    # Clean up everything

# Python environment
source venv/bin/activate  # Activate environment
deactivate               # Deactivate environment

# Docker commands
docker-compose up -d        # Start in background
docker-compose down         # Stop and remove
docker-compose logs         # View logs
docker-compose ps          # List services
```

## Next Steps

1. **Production Deployment**: See README.md for production configuration
2. **Custom Models**: Configure local embedding models for sensitive data
3. **Advanced Security**: Implement user authentication and document-level permissions
4. **Monitoring**: Set up Prometheus/Grafana monitoring
5. **Backup Strategy**: Configure automated S3 backups

## Support

For issues and questions:
- Check the full README.md for detailed documentation
- Review Docker Compose logs for service issues
- Verify environment variables and API keys
- Ensure proper file permissions and formats

## Legal Considerations

⚠️ **Important**: This system is designed to handle legal documents which may contain sensitive information:

- Configure appropriate confidentiality levels
- Implement proper access controls
- Follow data retention policies
- Ensure compliance with applicable regulations
- Consider data residency requirements for cloud services
