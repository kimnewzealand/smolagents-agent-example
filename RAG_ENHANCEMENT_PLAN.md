# Enhanced Compliance Agent: Web Search + RAG Integration Plan

## Overview
Transform the current compliance agent into a hybrid system that combines real-time web searching with knowledge-based retrieval for comprehensive New Zealand startup compliance assistance.

## Current Architecture Analysis

### Existing Strengths
- ✅ Web search capability via `ComplianceWebSearchTool`
- ✅ Structured compliance calendar data
- ✅ Multi-tool orchestration with smolagents
- ✅ Focused on NZ regulatory landscape

### Current Limitations
- ❌ No persistent knowledge base
- ❌ Limited to real-time search results
- ❌ No document storage or citation tracking
- ❌ Cannot access historical regulatory changes

## Proposed Hybrid Architecture

### 1. Knowledge Base Layer
```
knowledge_base/
├── core_documents/
│   ├── tax_legislation/     # Income Tax Act, GST Act
│   ├── company_law/         # Companies Act 1993
│   ├── employment_law/      # Employment Relations Act
│   └── health_safety/       # HSWA 2015
├── regulatory_updates/
│   ├── ird_releases/        # IRD determinations, rulings
│   ├── mbie_updates/        # MBIE policy changes
│   └── companies_office/    # CO announcements
└── practical_guides/
    ├── startup_checklists/  # Step-by-step compliance guides
    ├── form_templates/      # Official forms with instructions
    └── case_studies/        # Common compliance scenarios
```

### 2. Enhanced Tool Suite

#### New RAG Tools
- **`DocumentRetrievalTool`**: Search internal knowledge base
- **`CitationTool`**: Provide specific document references
- **`HistoricalComparisonTool`**: Compare current vs previous regulations
- **`DocumentSummaryTool`**: Summarize long regulatory documents

#### Enhanced Existing Tools
- **`ComplianceWebSearchTool`** → **`HybridSearchTool`**:
  - First check knowledge base for established law
  - Use web search for recent updates and news
  - Cross-reference findings between sources

#### New Specialized Tools
- **`RegulationTrackerTool`**: Monitor specific regulation changes
- **`DeadlineCalculatorTool`**: Calculate compliance dates based on business events
- **`RiskAssessmentTool`**: Evaluate compliance risk levels
- **`FormFinderTool`**: Locate and explain required forms

### 3. Intelligent Routing Strategy

#### Query Classification
```python
def classify_query(query: str) -> QueryType:
    """
    ESTABLISHED_LAW: Use knowledge base (e.g., "What is GST rate?")
    RECENT_CHANGES: Use web search (e.g., "Latest tax changes 2024")
    HYBRID: Use both sources (e.g., "How do new PAYE rules affect startups?")
    PROCEDURAL: Use knowledge base + forms (e.g., "How to register company?")
    """
```

#### Tool Selection Logic
1. **Established Law Queries** → Knowledge Base First
2. **Recent Updates** → Web Search First
3. **Complex Scenarios** → Multi-tool orchestration
4. **Deadline Queries** → Calendar + Calculator tools

### 4. Implementation Phases

#### Phase 1: Foundation (Weeks 1-2)
- Set up vector database (ChromaDB/Pinecone)
- Ingest core tax documents (GST Act, Income Tax Act)
- Create `DocumentRetrievalTool`
- Implement basic RAG pipeline

#### Phase 2: Enhancement (Weeks 3-4)
- Add company law and employment documents
- Develop `HybridSearchTool` combining RAG + web search
- Implement citation tracking
- Add query classification logic

#### Phase 3: Specialization (Weeks 5-6)
- Create specialized tools (deadline calculator, risk assessment)
- Add form templates and procedural guides
- Implement historical comparison capabilities
- Develop confidence scoring system

#### Phase 4: Optimization (Weeks 7-8)
- Fine-tune retrieval algorithms
- Add automated document updates
- Implement user feedback loops
- Performance optimization and testing

### 5. Technical Architecture

#### Vector Database Schema
```python
Document = {
    "id": str,
    "content": str,
    "embedding": List[float],
    "metadata": {
        "source": str,          # "IRD", "Companies Office", etc.
        "document_type": str,   # "legislation", "ruling", "guide"
        "category": str,        # "tax", "employment", "company_law"
        "date_published": datetime,
        "date_effective": datetime,
        "authority": str,       # "IRD", "MBIE", "Parliament"
        "confidence": float,    # Document reliability score
        "page_number": int,     # For citation
        "section": str          # Legal section reference
    }
}
```

#### Enhanced Agent Configuration
```json
{
    "tools": [
        "document_retrieval",
        "hybrid_search", 
        "citation_tracker",
        "deadline_calculator",
        "risk_assessment",
        "form_finder",
        "get_compliance_calendar",
        "final_answer"
    ],
    "retrieval_config": {
        "vector_db": "chromadb",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "chunk_size": 512,
        "chunk_overlap": 50,
        "top_k": 5,
        "similarity_threshold": 0.7
    },
    "search_strategy": {
        "knowledge_base_first": ["established_law", "procedures"],
        "web_search_first": ["recent_changes", "news"],
        "hybrid_approach": ["complex_scenarios", "comparative"]
    }
}
```

### 6. Quality Assurance

#### Source Verification
- Prioritize official government sources
- Timestamp all information with "as of" dates
- Flag potentially outdated information
- Cross-reference between multiple sources

#### Citation Standards
- Always provide document name and section
- Include publication/effective dates
- Link to original source when possible
- Indicate confidence level of information

#### Update Mechanisms
- Weekly automated scraping of IRD/MBIE websites
- Manual review of significant regulatory changes
- Version control for document updates
- Deprecation warnings for superseded information

### 7. User Experience Enhancements

#### Response Format
```
📋 COMPLIANCE ANSWER:
[Direct answer to question]

📚 SOURCES:
• Income Tax Act 2007, Section 15 (as of 1 April 2024)
• IRD Determination DEP-123 (published 15 March 2024)

🔍 RECENT UPDATES:
[Any recent changes found via web search]

⚠️ IMPORTANT NOTES:
[Disclaimers, effective dates, action items]

🔗 USEFUL LINKS:
[Direct links to forms, official pages]
```

#### Smart Suggestions
- Proactive deadline reminders
- Related compliance requirements
- Suggested follow-up questions
- Risk mitigation recommendations

### 8. Success Metrics

#### Accuracy Metrics
- Source attribution rate (target: 95%+)
- Information currency (target: <30 days old)
- Cross-reference validation rate
- User correction feedback

#### Performance Metrics
- Query response time (target: <10 seconds)
- Knowledge base coverage (target: 80% of common queries)
- Web search fallback rate (target: <30%)
- User satisfaction scores

### 9. Risk Mitigation

#### Legal Disclaimers
- Clear "not legal advice" statements
- Recommendation to consult professionals
- Currency warnings on information
- Limitation of liability notices

#### Technical Safeguards
- Fallback to web search if knowledge base fails
- Confidence scoring for all responses
- Human review flags for complex queries
- Regular accuracy audits

### 10. Future Enhancements

#### Advanced Features
- Multi-language support (Māori, Pacific languages)
- Industry-specific compliance modules
- Integration with accounting software APIs
- Automated compliance monitoring dashboards

#### AI Improvements
- Fine-tuned models on NZ legal text
- Improved query understanding
- Predictive compliance alerts
- Natural language form filling

## Conclusion

This hybrid approach leverages the strengths of both knowledge-based retrieval and real-time web search, providing users with comprehensive, accurate, and up-to-date compliance information while maintaining the flexibility to handle novel queries and emerging regulatory changes.

The phased implementation ensures manageable development while delivering value at each stage, ultimately creating a robust compliance assistant that serves as both a reliable knowledge repository and an intelligent research tool.