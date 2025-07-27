from typing import Dict, List, Optional
from weaviate_client import LegalWeaviateClient


class LegalSearchEngine:
    """
    Advanced search engine for legal documents with semantic, keyword,
    and hybrid search capabilities optimized for legal use cases
    """
    
    def __init__(self, weaviate_client: LegalWeaviateClient):
        self.weaviate = weaviate_client
    
    def semantic_search(self, query: str, limit: int = 10, filters: Dict = None) -> List[Dict]:
        """Perform semantic vector search using embeddings"""
        where_filter = self._build_where_filter(filters) if filters else None
        
        try:
            result = (
                self.weaviate.client.query
                .get("LegalDocument", [
                    "title", "content", "summary", "documentType", 
                    "caseNumber", "court", "parties", "practiceArea", 
                    "citations", "date", "confidentialityLevel",
                    "_additional {score id}"
                ])
                .with_near_text({"concepts": [query]})
                .with_limit(limit)
            )
            
            if where_filter:
                result = result.with_where(where_filter)
            
            response = result.do()
            return response.get("data", {}).get("Get", {}).get("LegalDocument", [])
            
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    def keyword_search(self, query: str, limit: int = 10, filters: Dict = None) -> List[Dict]:
        """Perform BM25 keyword search for exact term matching"""
        where_filter = self._build_where_filter(filters) if filters else None
        
        try:
            result = (
                self.weaviate.client.query
                .get("LegalDocument", [
                    "title", "content", "summary", "documentType", 
                    "caseNumber", "court", "parties", "practiceArea", 
                    "citations", "date", "confidentialityLevel",
                    "_additional {score id}"
                ])
                .with_bm25(query=query)
                .with_limit(limit)
            )
            
            if where_filter:
                result = result.with_where(where_filter)
            
            response = result.do()
            return response.get("data", {}).get("Get", {}).get("LegalDocument", [])
            
        except Exception as e:
            print(f"Error in keyword search: {e}")
            return []
    
    def hybrid_search(self, query: str, alpha: float = 0.5, limit: int = 10, 
                     filters: Dict = None) -> List[Dict]:
        """
        Perform hybrid search combining semantic and keyword search
        alpha: 0.0 = pure keyword, 1.0 = pure semantic, 0.5 = balanced
        """
        where_filter = self._build_where_filter(filters) if filters else None
        
        try:
            result = (
                self.weaviate.client.query
                .get("LegalDocument", [
                    "title", "content", "summary", "documentType", 
                    "caseNumber", "court", "parties", "practiceArea", 
                    "citations", "date", "confidentialityLevel",
                    "_additional {score id}"
                ])
                .with_hybrid(query=query, alpha=alpha)
                .with_limit(limit)
            )
            
            if where_filter:
                result = result.with_where(where_filter)
            
            response = result.do()
            return response.get("data", {}).get("Get", {}).get("LegalDocument", [])
            
        except Exception as e:
            print(f"Error in hybrid search: {e}")
            return []
    
    def search_citations(self, citation: str) -> List[Dict]:
        """Search for specific legal citations"""
        try:
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
            
        except Exception as e:
            print(f"Error searching citations: {e}")
            return []
    
    def search_by_case_number(self, case_number: str) -> List[Dict]:
        """Search documents by case number"""
        try:
            result = (
                self.weaviate.client.query
                .get("LegalDocument", [
                    "title", "content", "summary", "documentType", 
                    "caseNumber", "court", "parties", "practiceArea", 
                    "date", "confidentialityLevel"
                ])
                .with_where({
                    "path": ["caseNumber"],
                    "operator": "Equal",
                    "valueText": case_number
                })
                .do()
            )
            
            return result.get("data", {}).get("Get", {}).get("LegalDocument", [])
            
        except Exception as e:
            print(f"Error searching by case number: {e}")
            return []
    
    def search_by_parties(self, party_name: str) -> List[Dict]:
        """Search documents by party name"""
        try:
            result = (
                self.weaviate.client.query
                .get("LegalDocument", [
                    "title", "content", "summary", "documentType", 
                    "caseNumber", "court", "parties", "practiceArea", 
                    "date", "confidentialityLevel"
                ])
                .with_where({
                    "path": ["parties"],
                    "operator": "ContainsAny",
                    "valueText": [party_name]
                })
                .do()
            )
            
            return result.get("data", {}).get("Get", {}).get("LegalDocument", [])
            
        except Exception as e:
            print(f"Error searching by parties: {e}")
            return []
    
    def advanced_search(self, criteria: Dict) -> List[Dict]:
        """
        Advanced search with multiple criteria
        criteria = {
            'query': 'contract terms',
            'document_type': 'contract',
            'practice_area': ['corporate', 'employment'],
            'court': 'District Court',
            'date_after': '2023-01-01',
            'date_before': '2024-01-01',
            'parties': ['ABC Corp'],
            'confidentiality': 'standard',
            'search_type': 'hybrid',  # 'semantic', 'keyword', 'hybrid'
            'limit': 20
        }
        """
        query = criteria.get('query', '')
        search_type = criteria.get('search_type', 'hybrid')
        limit = criteria.get('limit', 10)
        
        # Build filters from criteria
        filters = {}
        
        if criteria.get('document_type'):
            filters['document_type'] = criteria['document_type']
        
        if criteria.get('practice_area'):
            filters['practice_area'] = criteria['practice_area']
        
        if criteria.get('court'):
            filters['court'] = criteria['court']
        
        if criteria.get('date_after'):
            filters['date_after'] = criteria['date_after']
        
        if criteria.get('date_before'):
            filters['date_before'] = criteria['date_before']
        
        if criteria.get('parties'):
            filters['parties'] = criteria['parties']
        
        if criteria.get('confidentiality'):
            filters['confidentiality'] = criteria['confidentiality']
        
        # Perform search based on type
        if search_type == 'semantic':
            return self.semantic_search(query, limit=limit, filters=filters)
        elif search_type == 'keyword':
            return self.keyword_search(query, limit=limit, filters=filters)
        else:  # hybrid
            alpha = criteria.get('alpha', 0.5)
            return self.hybrid_search(query, alpha=alpha, limit=limit, filters=filters)
    
    def search_sections(self, query: str, limit: int = 10) -> List[Dict]:
        """Search within document sections for more granular results"""
        try:
            result = (
                self.weaviate.client.query
                .get("DocumentSection", [
                    "content", "sectionTitle", "pageNumber", "sectionNumber",
                    "parentDocument {... on LegalDocument {title caseNumber documentType}}",
                    "_additional {score id}"
                ])
                .with_hybrid(query=query)
                .with_limit(limit)
                .do()
            )
            
            return result.get("data", {}).get("Get", {}).get("DocumentSection", [])
            
        except Exception as e:
            print(f"Error searching sections: {e}")
            return []
    
    def generate_answer(self, query: str, context_docs: List[Dict]) -> str:
        """Generate answer using retrieved documents as context"""
        if not context_docs:
            return "No relevant documents found to answer the question."
        
        # Prepare context from top documents
        context_parts = []
        for i, doc in enumerate(context_docs[:3], 1):
            title = doc.get('title', 'Unknown Document')
            summary = doc.get('summary', '')[:500]  # Limit summary length
            context_parts.append(f"Document {i}: {title}\nContent: {summary}")
        
        context = "\n\n".join(context_parts)
        
        try:
            result = (
                self.weaviate.client.query
                .get("LegalDocument", ["title"])
                .with_generate(
                    single_prompt=f"""Based on the following legal documents, provide a comprehensive answer to this question: {query}

Context Documents:
{context}

Please provide a detailed answer based on the legal documents provided. Include relevant legal principles, cite specific documents when appropriate, and note any limitations or caveats.

Answer:"""
                )
                .with_limit(1)
                .do()
            )
            
            generated = result.get("data", {}).get("Get", {}).get("LegalDocument", [])
            if generated and generated[0].get("_additional", {}).get("generate", {}).get("singleResult"):
                return generated[0]["_additional"]["generate"]["singleResult"]
            
        except Exception as e:
            print(f"Error generating answer: {e}")
        
        return "Unable to generate answer based on available documents."
    
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
            practice_areas = filters["practice_area"]
            if isinstance(practice_areas, str):
                practice_areas = [practice_areas]
            conditions.append({
                "path": ["practiceArea"],
                "operator": "ContainsAny",
                "valueText": practice_areas
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
        
        if filters.get("date_before"):
            conditions.append({
                "path": ["date"],
                "operator": "LessThan",
                "valueDate": filters["date_before"]
            })
        
        if filters.get("parties"):
            parties = filters["parties"]
            if isinstance(parties, str):
                parties = [parties]
            conditions.append({
                "path": ["parties"],
                "operator": "ContainsAny",
                "valueText": parties
            })
        
        if filters.get("confidentiality"):
            conditions.append({
                "path": ["confidentialityLevel"],
                "operator": "Equal",
                "valueText": filters["confidentiality"]
            })
        
        # Combine conditions
        if len(conditions) == 0:
            return {}
        elif len(conditions) == 1:
            return conditions[0]
        else:
            return {
                "operator": "And",
                "operands": conditions
            }


class LegalRAGSystem:
    """
    Complete Retrieval-Augmented Generation system for legal documents
    combining search capabilities with AI-powered question answering
    """
    
    def __init__(self, weaviate_client: LegalWeaviateClient):
        self.search_engine = LegalSearchEngine(weaviate_client)
    
    def query(self, question: str, search_type: str = "hybrid", 
              filters: Dict = None, limit: int = 5) -> Dict:
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
            "search_type": search_type,
            "filters_applied": filters
        }
    
    def legal_research(self, topic: str, practice_area: str = None, 
                      document_types: List[str] = None) -> Dict:
        """Specialized legal research query for comprehensive topic analysis"""
        
        # Build filters
        filters = {}
        if practice_area:
            filters["practice_area"] = [practice_area]
        if document_types:
            # Need to do separate searches for multiple document types
            pass
        
        # Perform multiple searches with different strategies
        semantic_results = self.search_engine.semantic_search(topic, limit=5, filters=filters)
        keyword_results = self.search_engine.keyword_search(topic, limit=5, filters=filters)
        
        # Also search sections for more detailed information
        section_results = self.search_engine.search_sections(topic, limit=3)
        
        # Combine and deduplicate results
        all_results = semantic_results + keyword_results
        unique_results = []
        seen_ids = set()
        
        for doc in all_results:
            doc_id = doc.get("_additional", {}).get("id")
            if doc_id and doc_id not in seen_ids:
                unique_results.append(doc)
                seen_ids.add(doc_id)
        
        # Sort by relevance score if available
        unique_results.sort(key=lambda x: x.get("_additional", {}).get("score", 0), reverse=True)
        
        return {
            "topic": topic,
            "practice_area": practice_area,
            "documents": unique_results[:10],
            "sections": section_results,
            "research_summary": self._generate_research_summary(unique_results[:3], topic)
        }
    
    def case_analysis(self, case_number: str) -> Dict:
        """Comprehensive analysis of a specific case"""
        
        # Search for all documents related to the case
        case_documents = self.search_engine.search_by_case_number(case_number)
        
        if not case_documents:
            return {
                "case_number": case_number,
                "error": "No documents found for this case number"
            }
        
        # Analyze document types
        doc_types = {}
        parties = set()
        courts = set()
        practice_areas = set()
        
        for doc in case_documents:
            # Document types
            doc_type = doc.get("documentType", "unknown")
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            # Parties
            if doc.get("parties"):
                parties.update(doc["parties"])
            
            # Courts
            if doc.get("court"):
                courts.add(doc["court"])
            
            # Practice areas
            if doc.get("practiceArea"):
                practice_areas.update(doc["practiceArea"])
        
        return {
            "case_number": case_number,
            "total_documents": len(case_documents),
            "document_types": doc_types,
            "parties": list(parties),
            "courts": list(courts),
            "practice_areas": list(practice_areas),
            "documents": case_documents,
            "case_summary": self._generate_case_summary(case_documents)
        }
    
    def citation_analysis(self, citation: str) -> Dict:
        """Analyze how a specific citation is used across documents"""
        
        # Search for the citation
        citation_results = self.search_engine.search_citations(citation)
        
        # Search for documents that mention this citation
        doc_results = self.search_engine.keyword_search(citation, limit=20)
        
        return {
            "citation": citation,
            "citation_details": citation_results,
            "citing_documents": doc_results,
            "usage_analysis": self._analyze_citation_usage(citation, doc_results)
        }
    
    def _generate_research_summary(self, documents: List[Dict], topic: str) -> str:
        """Generate a research summary from multiple documents"""
        if not documents:
            return "No relevant documents found for this research topic."
        
        context = f"Research Topic: {topic}\n\n"
        for i, doc in enumerate(documents, 1):
            title = doc.get('title', 'Unknown Document')
            summary = doc.get('summary', '')[:200]
            context += f"Document {i}: {title}\nSummary: {summary}\n\n"
        
        # Generate summary using the context
        prompt = f"""Based on the following legal documents related to "{topic}", provide a comprehensive research summary that includes:

1. Key legal principles and concepts
2. Relevant case law or statutory provisions
3. Current trends or developments
4. Practical implications
5. Areas for further research

{context}

Research Summary:"""
        
        try:
            result = (
                self.search_engine.weaviate.client.query
                .get("LegalDocument", ["title"])
                .with_generate(single_prompt=prompt)
                .with_limit(1)
                .do()
            )
            
            generated = result.get("data", {}).get("Get", {}).get("LegalDocument", [])
            if generated and generated[0].get("_additional", {}).get("generate", {}).get("singleResult"):
                return generated[0]["_additional"]["generate"]["singleResult"]
                
        except Exception as e:
            print(f"Error generating research summary: {e}")
        
        return f"Based on {len(documents)} documents, research indicates relevant information about {topic}. Manual review of source documents recommended for detailed analysis."
    
    def _generate_case_summary(self, case_documents: List[Dict]) -> str:
        """Generate a summary of a case based on its documents"""
        if not case_documents:
            return "No documents available for case summary."
        
        # Create a timeline and summary based on document types
        doc_types = set(doc.get("documentType", "unknown") for doc in case_documents)
        
        summary_parts = []
        summary_parts.append(f"Case involves {len(case_documents)} documents of types: {', '.join(doc_types)}")
        
        # Add party information
        all_parties = set()
        for doc in case_documents:
            if doc.get("parties"):
                all_parties.update(doc["parties"])
        
        if all_parties:
            summary_parts.append(f"Parties involved: {', '.join(list(all_parties)[:5])}")
        
        return ". ".join(summary_parts)
    
    def _analyze_citation_usage(self, citation: str, documents: List[Dict]) -> Dict:
        """Analyze how a citation is used across documents"""
        analysis = {
            "total_references": len(documents),
            "document_types": {},
            "practice_areas": {},
            "usage_contexts": []
        }
        
        for doc in documents:
            # Document types
            doc_type = doc.get("documentType", "unknown")
            analysis["document_types"][doc_type] = analysis["document_types"].get(doc_type, 0) + 1
            
            # Practice areas
            if doc.get("practiceArea"):
                for area in doc["practiceArea"]:
                    analysis["practice_areas"][area] = analysis["practice_areas"].get(area, 0) + 1
        
        return analysis


if __name__ == "__main__":
    # Example usage
    from weaviate_client import LegalWeaviateClient
    import os
    
    # Initialize the system
    weaviate_client = LegalWeaviateClient(
        weaviate_url="http://localhost:8080",
        api_key=os.getenv("WEAVIATE_API_KEY")
    )
    
    # Create RAG system
    rag_system = LegalRAGSystem(weaviate_client)
    
    # Example queries
    
    # 1. Basic question answering
    result = rag_system.query(
        question="What are the key provisions in employment contracts regarding non-compete clauses?",
        search_type="hybrid",
        filters={"practice_area": ["employment"]},
        limit=5
    )
    
    print("Question:", result['question'])
    print("Answer:", result['answer'])
    print(f"Based on {len(result['source_documents'])} documents")
    
    # 2. Legal research
    research_result = rag_system.legal_research(
        topic="intellectual property licensing agreements",
        practice_area="intellectual_property"
    )
    
    print("\nResearch Topic:", research_result['topic'])
    print("Summary:", research_result['research_summary'])
    
    # 3. Case analysis
    case_analysis = rag_system.case_analysis("21-cv-1234")
    print("\nCase Analysis:", case_analysis)
    
    # 4. Advanced search
    search_engine = LegalSearchEngine(weaviate_client)
    advanced_results = search_engine.advanced_search({
        'query': 'contract breach damages',
        'document_type': 'contract',
        'practice_area': ['corporate'],
        'date_after': '2023-01-01',
        'search_type': 'hybrid',
        'limit': 10
    })
    
    print(f"\nAdvanced search found {len(advanced_results)} documents")
