import weaviate
import json
import os
from typing import Dict, List, Optional
from datetime import datetime

# Legal Document Schema
legal_document_schema = {
    "class": "LegalDocument",
    "description": "Legal documents with full text and metadata for RAG functionality",
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
        },
        {
            "name": "createdAt",
            "dataType": ["date"],
            "description": "When document was added to system"
        },
        {
            "name": "lastModified",
            "dataType": ["date"],
            "description": "Last modification date"
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


class LegalWeaviateClient:
    """
    Weaviate client specifically configured for legal document management
    with proper schemas, security, and legal-specific functionality
    """
    
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
            # Add timestamps
            current_time = datetime.now().isoformat()
            document_data["createdAt"] = current_time
            document_data["lastModified"] = current_time
            
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
    
    def update_document(self, document_id: str, updates: Dict):
        """Update an existing legal document"""
        try:
            updates["lastModified"] = datetime.now().isoformat()
            
            self.client.data_object.update(
                uuid=document_id,
                class_name="LegalDocument",
                data_object=updates
            )
            print(f"Updated document {document_id}")
        except Exception as e:
            print(f"Error updating document {document_id}: {e}")
    
    def delete_document(self, document_id: str):
        """Delete a legal document and its associated sections"""
        try:
            # First delete associated sections
            sections_result = (
                self.client.query
                .get("DocumentSection", ["_additional {id}"])
                .with_where({
                    "path": ["parentDocument", "LegalDocument", "id"],
                    "operator": "Equal",
                    "valueText": document_id
                })
                .do()
            )
            
            sections = sections_result.get("data", {}).get("Get", {}).get("DocumentSection", [])
            for section in sections:
                section_id = section["_additional"]["id"]
                self.client.data_object.delete(uuid=section_id)
                print(f"Deleted section {section_id}")
            
            # Delete the main document
            self.client.data_object.delete(uuid=document_id)
            print(f"Deleted document {document_id}")
            
        except Exception as e:
            print(f"Error deleting document {document_id}: {e}")
    
    def get_document_by_id(self, document_id: str) -> Optional[Dict]:
        """Retrieve a specific document by ID"""
        try:
            result = self.client.data_object.get_by_id(
                uuid=document_id,
                class_name="LegalDocument"
            )
            return result
        except Exception as e:
            print(f"Error retrieving document {document_id}: {e}")
            return None
    
    def get_schema_info(self) -> Dict:
        """Get information about current schemas"""
        try:
            schema = self.client.schema.get()
            return schema
        except Exception as e:
            print(f"Error retrieving schema: {e}")
            return {}
    
    def backup_data(self, backup_id: str) -> bool:
        """Create a backup of legal documents"""
        try:
            backup_config = {
                "id": backup_id,
                "include": ["LegalDocument", "Citation", "DocumentSection"]
            }
            
            response = self.client.backup.create(
                backup_id=backup_id,
                backend="s3",
                include_classes=backup_config["include"]
            )
            
            print(f"Backup created with ID: {backup_id}")
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def restore_data(self, backup_id: str) -> bool:
        """Restore data from backup"""
        try:
            response = self.client.backup.restore(
                backup_id=backup_id,
                backend="s3"
            )
            
            print(f"Data restored from backup: {backup_id}")
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    client = LegalWeaviateClient(
        weaviate_url="http://localhost:8080",
        api_key=os.getenv("WEAVIATE_API_KEY")
    )
    
    # Example document data
    sample_document = {
        "title": "Employment Agreement - John Doe",
        "content": "This Employment Agreement is entered into between...",
        "summary": "Standard employment agreement with non-compete clauses...",
        "documentType": "contract",
        "caseNumber": "EMP-2024-001",
        "court": None,
        "parties": ["John Doe", "ABC Corporation"],
        "date": "2024-01-15T00:00:00Z",
        "filePath": "/legal-docs/employment/john_doe_agreement.pdf",
        "pageCount": 15,
        "practiceArea": ["employment"],
        "jurisdiction": "California",
        "citations": [],
        "confidentialityLevel": "confidential"
    }
    
    # Add document
    doc_id = client.add_legal_document(sample_document)
    
    if doc_id:
        print(f"Successfully added document with ID: {doc_id}")
        
        # Example of updating the document
        updates = {
            "confidentialityLevel": "standard"
        }
        client.update_document(doc_id, updates)
