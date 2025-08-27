from smolagents.tools import Tool
from typing import Optional
import requests
from bs4 import BeautifulSoup


class WebSearchTool(Tool):
    name = "web_search"
    description = "Search the internet for recent New Zealand regulatory changes, compliance updates, and government announcements. Use for current information not in the compliance calendar."
    inputs = {
        "query": {
            "type": "string", 
            "description": "Search query for regulatory changes (e.g. 'New Zealand tax changes 2024', 'IRD compliance updates')"
        }
    }
    output_type = "string"
    
    def __init__(self):
        super().__init__()
        self.is_initialized = True

    def forward(self, query: str) -> str:
        """Search for regulatory information using DuckDuckGo."""
        try:
            # Focus search on NZ government and regulatory sites
            focused_query = f"{query} site:ird.govt.nz OR site:companies.govt.nz OR site:mbie.govt.nz OR site:employment.govt.nz"
            
            # Use DuckDuckGo instant answer API (no key required)
            search_url = "https://api.duckduckgo.com/"
            params = {
                'q': focused_query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            data = response.json()
            
            results = []
            
            # Get instant answer if available
            if data.get('Abstract'):
                results.append(f"📋 Summary: {data['Abstract']}")
            
            # Get related topics
            if data.get('RelatedTopics'):
                results.append("\n🔗 Related Information:")
                for topic in data['RelatedTopics'][:3]:
                    if isinstance(topic, dict) and topic.get('Text'):
                        results.append(f"• {topic['Text']}")
            
            # Fallback search results
            if not results:
                results.append(f"🔍 Search completed for: {query}. No results found.")
            
            return "\n".join(results)
            
        except Exception as e:
            return f"❌ Search failed: {str(e)}\n💡 Please check these official sources manually:\n• ird.govt.nz\n• companies.govt.nz\n• mbie.govt.nz"