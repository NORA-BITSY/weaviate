import os
import PyPDF2
import docx
from pathlib import Path
import re
from datetime import datetime
import spacy
from typing import Dict, List, Optional

class LegalDocumentProcessor:
    """
    Processes legal documents to extract text, metadata, and structure
    for ingestion into Weaviate vector database
    """
    
    def __init__(self):
        # Load legal NLP model (install with: python -m spacy download en_core_web_sm)
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
            r'\d+\s+[A-Z][a-z\.]*\s+\d+\s+\(\d{4}\)',  # With year
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
        page_number = 1
        
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
                    "content": current_section.strip(),
                    "pageNumber": page_number,
                    "sectionNumber": section_title
                })
                current_section = ""
                section_title = line
            elif is_header:
                section_title = line
            else:
                current_section += line + " "
                # Rough page estimation
                if len(current_section) > 3000:  # Approximate words per page
                    page_number += 1
        
        # Add final section
        if current_section:
            sections.append({
                "title": section_title,
                "content": current_section.strip(),
                "pageNumber": page_number,
                "sectionNumber": section_title
            })
        
        return sections


class MetadataExtractor:
    """
    Extracts metadata from legal documents including document type,
    practice areas, parties, court information, etc.
    """
    
    def __init__(self):
        self.document_types = {
            'contract': ['agreement', 'contract', 'license', 'nda', 'mou'],
            'motion': ['motion', 'petition', 'application'],
            'brief': ['brief', 'memorandum', 'memo'],
            'pleading': ['complaint', 'answer', 'reply', 'counterclaim'],
            'discovery': ['interrogatory', 'deposition', 'request', 'subpoena'],
            'order': ['order', 'judgment', 'decree', 'ruling'],
            'correspondence': ['letter', 'email', 'correspondence'],
            'opinion': ['opinion', 'decision', 'holding'],
            'statute': ['statute', 'regulation', 'rule', 'code'],
            'filing': ['filing', 'docket', 'notice']
        }
        
        self.practice_areas = {
            'litigation': ['litigation', 'trial', 'court', 'lawsuit', 'dispute'],
            'corporate': ['corporate', 'merger', 'acquisition', 'securities', 'governance'],
            'employment': ['employment', 'labor', 'discrimination', 'harassment', 'wrongful termination'],
            'intellectual_property': ['patent', 'trademark', 'copyright', 'ip', 'trade secret'],
            'real_estate': ['real estate', 'property', 'lease', 'deed', 'mortgage'],
            'family': ['divorce', 'custody', 'family', 'marriage', 'adoption'],
            'criminal': ['criminal', 'prosecution', 'defense', 'plea', 'sentencing'],
            'tax': ['tax', 'irs', 'revenue', 'audit'],
            'bankruptcy': ['bankruptcy', 'insolvency', 'creditor', 'debtor'],
            'immigration': ['immigration', 'visa', 'asylum', 'deportation'],
            'environmental': ['environmental', 'epa', 'pollution', 'cleanup'],
            'healthcare': ['healthcare', 'hipaa', 'medical', 'patient']
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
            r'([A-Z][A-Z\s&,\.]+(?:LLC|INC|CORP|LTD|LP))',
            r'([A-Z][a-z]+\s+(?:Corporation|Company|Inc\.|LLC|Ltd\.))',
        ]
        
        parties = []
        for pattern in party_patterns:
            matches = re.findall(pattern, text[:2000])  # Check first 2000 chars
            parties.extend(matches)
        
        # Clean up party names
        cleaned_parties = []
        for party in parties:
            if isinstance(party, tuple):
                party = party[0]
            party = party.strip().replace(',', '')
            if len(party) > 2 and party not in cleaned_parties:
                cleaned_parties.append(party)
        
        return cleaned_parties
    
    def extract_court_jurisdiction(self, text: str) -> Dict[str, str]:
        """Extract court and jurisdiction information"""
        court_patterns = [
            r'(United States District Court)',
            r'(U\.S\. Court of Appeals)',
            r'(Supreme Court of the United States|U\.S\. Supreme Court)',
            r'([A-Z][a-z]+ (?:District|Superior|Municipal|Circuit) Court)',
            r'(Court of (?:Appeals|Common Pleas))',
        ]
        
        jurisdiction_patterns = [
            r'(?:District of|for the) ([A-Z][a-z]+ District)',
            r'State of ([A-Z][a-z]+)',
            r'Commonwealth of ([A-Z][a-z]+)',
            r'([A-Z][a-z]+) (?:State|County)',
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
    
    def extract_dates(self, text: str) -> List[str]:
        """Extract important dates from legal documents"""
        date_patterns = [
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text[:2000])
            dates.extend(matches)
        
        return list(set(dates))  # Remove duplicates


if __name__ == "__main__":
    # Example usage
    processor = LegalDocumentProcessor()
    extractor = MetadataExtractor()
    
    # Test with a sample document
    sample_text = """
    IN THE UNITED STATES DISTRICT COURT
    FOR THE SOUTHERN DISTRICT OF NEW YORK
    
    Case No. 21-cv-1234
    
    John Smith, Plaintiff,
    v.
    ABC Corporation, Defendant.
    
    MEMORANDUM AND ORDER
    
    This matter comes before the Court on Plaintiff's Motion for Summary Judgment...
    """
    
    # Extract metadata
    doc_type = extractor.extract_document_type(sample_text, "motion_summary_judgment.pdf")
    parties = extractor.extract_parties(sample_text)
    court_info = extractor.extract_court_jurisdiction(sample_text)
    
    print(f"Document Type: {doc_type}")
    print(f"Parties: {parties}")
    print(f"Court: {court_info}")
