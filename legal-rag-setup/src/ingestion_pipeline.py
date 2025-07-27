import os
from typing import Dict, List, Optional
from datetime import datetime
from document_processor import LegalDocumentProcessor, MetadataExtractor
from weaviate_client import LegalWeaviateClient


class LegalDocumentPipeline:
    """
    Complete processing pipeline for legal documents:
    1. Extract text and metadata
    2. Process and clean content
    3. Vectorize and store in Weaviate
    4. Enable search and retrieval
    """
    
    def __init__(self, weaviate_client: LegalWeaviateClient):
        self.weaviate = weaviate_client
        self.processor = LegalDocumentProcessor()
        self.metadata_extractor = MetadataExtractor()
        
        # Configuration
        self.max_file_size_mb = int(os.getenv("MAX_DOCUMENT_SIZE_MB", "50"))
        self.supported_formats = os.getenv("SUPPORTED_FORMATS", "pdf,docx,txt,html").split(",")
        self.default_practice_area = os.getenv("DEFAULT_PRACTICE_AREA", "general")
        self.confidentiality_levels = os.getenv("CONFIDENTIALITY_LEVELS", "public,standard,confidential,highly_confidential").split(",")
    
    def validate_file(self, file_path: str) -> bool:
        """Validate file before processing"""
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            print(f"File too large: {file_size_mb:.2f}MB > {self.max_file_size_mb}MB")
            return False
        
        # Check file format
        file_extension = os.path.splitext(file_path)[1].lower().replace('.', '')
        if file_extension not in self.supported_formats:
            print(f"Unsupported format: {file_extension}")
            return False
        
        return True
    
    def extract_text_by_format(self, file_path: str) -> str:
        """Extract text based on file format"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self.processor.extract_text_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return self.processor.extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
        elif file_extension in ['.html', '.htm']:
            try:
                from bs4 import BeautifulSoup
                with open(file_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                    return soup.get_text()
            except ImportError:
                print("BeautifulSoup not installed. Install with: pip install beautifulsoup4")
                return ""
        else:
            print(f"Unsupported file type: {file_extension}")
            return ""
    
    def determine_confidentiality(self, text: str, filename: str) -> str:
        """Determine confidentiality level based on content"""
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        # High confidentiality indicators
        high_conf_indicators = [
            'confidential', 'privileged', 'attorney-client', 'work product',
            'trade secret', 'proprietary', 'classified'
        ]
        
        # Standard confidentiality indicators
        std_conf_indicators = [
            'internal', 'restricted', 'sensitive', 'private'
        ]
        
        for indicator in high_conf_indicators:
            if indicator in text_lower or indicator in filename_lower:
                return "highly_confidential"
        
        for indicator in std_conf_indicators:
            if indicator in text_lower or indicator in filename_lower:
                return "confidential"
        
        # Check if it's clearly public
        public_indicators = ['public', 'filing', 'published', 'press release']
        for indicator in public_indicators:
            if indicator in text_lower or indicator in filename_lower:
                return "public"
        
        return "standard"  # Default level
    
    def process_document(self, file_path: str, custom_metadata: Dict = None) -> Optional[str]:
        """Process a single legal document through the full pipeline"""
        print(f"Processing: {file_path}")
        
        # Validate file
        if not self.validate_file(file_path):
            return None
        
        # Extract text
        text = self.extract_text_by_format(file_path)
        
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
        dates = self.metadata_extractor.extract_dates(text)
        
        # Determine confidentiality
        confidentiality = self.determine_confidentiality(text, filename)
        
        # Generate summary (first 500 words or use custom logic)
        words = text.split()
        if len(words) > 500:
            summary = ' '.join(words[:500]) + "..."
        else:
            summary = text
        
        # Estimate page count (rough approximation)
        page_count = max(1, len(text) // 3000)
        
        # Get document date (try to extract from content, fall back to file mtime)
        document_date = None
        if dates:
            try:
                # Try to parse the first date found
                from dateutil import parser
                document_date = parser.parse(dates[0]).isoformat()
            except:
                pass
        
        if not document_date:
            # Use file modification time
            mtime = os.path.getmtime(file_path)
            document_date = datetime.fromtimestamp(mtime).isoformat()
        
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
            "pageCount": page_count,
            "practiceArea": practice_areas if practice_areas else [self.default_practice_area],
            "citations": citations,
            "confidentialityLevel": confidentiality,
            "date": document_date
        }
        
        # Merge with custom metadata if provided
        if custom_metadata:
            document_data.update(custom_metadata)
        
        # Add to Weaviate
        document_id = self.weaviate.add_legal_document(document_data)
        
        if document_id:
            # Process sections
            sections = self.processor.split_into_sections(text)
            if sections:
                self.weaviate.add_document_sections(sections, document_id)
            
            # Add citations as separate objects
            if citations:
                self.weaviate.add_citations(citations, document_id)
            
            print(f"Successfully processed {filename} -> Document ID: {document_id}")
        
        return document_id
    
    def process_directory(self, directory_path: str, recursive: bool = True, 
                         custom_metadata: Dict = None) -> List[str]:
        """Process all legal documents in a directory"""
        if not os.path.exists(directory_path):
            print(f"Directory not found: {directory_path}")
            return []
        
        processed_documents = []
        
        # Get all files to process
        files_to_process = []
        
        if recursive:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    files_to_process.append(file_path)
        else:
            files_to_process = [
                os.path.join(directory_path, f) 
                for f in os.listdir(directory_path) 
                if os.path.isfile(os.path.join(directory_path, f))
            ]
        
        # Filter by supported extensions
        supported_extensions = [f".{fmt}" for fmt in self.supported_formats]
        files_to_process = [
            f for f in files_to_process 
            if any(f.lower().endswith(ext) for ext in supported_extensions)
        ]
        
        print(f"Found {len(files_to_process)} files to process")
        
        # Process each file
        for i, file_path in enumerate(files_to_process, 1):
            try:
                print(f"\nProcessing {i}/{len(files_to_process)}: {os.path.basename(file_path)}")
                document_id = self.process_document(file_path, custom_metadata)
                if document_id:
                    processed_documents.append(document_id)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        print(f"\nProcessing complete. Successfully processed {len(processed_documents)} documents.")
        return processed_documents
    
    def reprocess_document(self, document_id: str, file_path: str) -> bool:
        """Reprocess an existing document (update)"""
        try:
            # Process the document again
            new_doc_id = self.process_document(file_path)
            
            if new_doc_id:
                # Delete the old document
                self.weaviate.delete_document(document_id)
                print(f"Updated document {document_id} -> {new_doc_id}")
                return True
            
        except Exception as e:
            print(f"Error reprocessing document {document_id}: {e}")
        
        return False
    
    def get_processing_stats(self, directory_path: str) -> Dict:
        """Get statistics about documents in a directory"""
        if not os.path.exists(directory_path):
            return {"error": "Directory not found"}
        
        stats = {
            "total_files": 0,
            "supported_files": 0,
            "file_types": {},
            "total_size_mb": 0,
            "largest_file": None,
            "largest_size_mb": 0
        }
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                file_ext = os.path.splitext(file)[1].lower()
                
                stats["total_files"] += 1
                stats["total_size_mb"] += file_size_mb
                
                if file_size_mb > stats["largest_size_mb"]:
                    stats["largest_size_mb"] = file_size_mb
                    stats["largest_file"] = file_path
                
                if file_ext.replace('.', '') in self.supported_formats:
                    stats["supported_files"] += 1
                
                if file_ext in stats["file_types"]:
                    stats["file_types"][file_ext] += 1
                else:
                    stats["file_types"][file_ext] = 1
        
        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        stats["largest_size_mb"] = round(stats["largest_size_mb"], 2)
        
        return stats


if __name__ == "__main__":
    # Example usage
    
    # Initialize the pipeline
    weaviate_client = LegalWeaviateClient(
        weaviate_url="http://localhost:8080",
        api_key=os.getenv("WEAVIATE_API_KEY")
    )
    
    pipeline = LegalDocumentPipeline(weaviate_client)
    
    # Get processing statistics
    directory_path = "/path/to/legal/documents"
    if os.path.exists(directory_path):
        stats = pipeline.get_processing_stats(directory_path)
        print("Processing Statistics:")
        print(f"Total files: {stats['total_files']}")
        print(f"Supported files: {stats['supported_files']}")
        print(f"Total size: {stats['total_size_mb']} MB")
        print(f"File types: {stats['file_types']}")
        
        # Process the directory
        processed_docs = pipeline.process_directory(directory_path)
        print(f"Processed {len(processed_docs)} documents")
    
    # Process a single document with custom metadata
    custom_meta = {
        "practiceArea": ["litigation", "corporate"],
        "confidentialityLevel": "highly_confidential"
    }
    
    # doc_id = pipeline.process_document("/path/to/document.pdf", custom_meta)
