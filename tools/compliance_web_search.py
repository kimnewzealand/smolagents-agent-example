from smolagents.tools import Tool
import requests
from bs4 import BeautifulSoup


class ComplianceWebSearchTool(Tool):
    name = "compliance_web_search"
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
        """Search for regulatory information using multiple methods."""
        try:
            # Method 1: Try DuckDuckGo HTML search (more reliable than API)
            results = self._search_duckduckgo_html(query)
            if results:
                return results
            
            # Method 2: Try direct government site search
            results = self._search_government_sites(query)
            if results:
                return results
            
            # Method 3: Fallback with helpful guidance
            return self._fallback_response(query)
            
        except Exception as e:
            return f"❌ Search failed: {str(e)}\n💡 Please check these official sources manually:\n• ird.govt.nz\n• companies.govt.nz\n• mbie.govt.nz"

    def _search_duckduckgo_html(self, query: str) -> str:
        """Search using DuckDuckGo HTML interface."""
        try:
            # Focus search on NZ government sites
            focused_query = f"{query} site:ird.govt.nz OR site:companies.govt.nz OR site:mbie.govt.nz"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            search_url = "https://html.duckduckgo.com/html/"
            params = {'q': focused_query}
            
            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                
                # Extract search results
                for result in soup.find_all('div', class_='result')[:3]:
                    title_elem = result.find('a', class_='result__a')
                    snippet_elem = result.find('a', class_='result__snippet')
                    
                    if title_elem and snippet_elem:
                        title = title_elem.get_text().strip()
                        snippet = snippet_elem.get_text().strip()
                        url = title_elem.get('href', '')
                        
                        results.append(f"📄 {title}\n   {snippet}\n   🔗 {url}")
                
                if results:
                    return f"🔍 Recent search results for: {query}\n\n" + "\n\n".join(results)
            
            return None
            
        except Exception:
            return None

    def _search_government_sites(self, query: str) -> str:
        """Search specific government sites directly."""
        try:
            sites_to_check = [
                ("IRD", "https://www.ird.govt.nz"),
                ("Companies Office", "https://www.companies.govt.nz"),
                ("MBIE", "https://www.mbie.govt.nz")
            ]
            
            results = []
            for site_name, base_url in sites_to_check:
                try:
                    # Simple check if site is accessible
                    response = requests.get(base_url, timeout=5)
                    if response.status_code == 200:
                        results.append(f"✅ {site_name}: {base_url} (accessible)")
                    else:
                        results.append(f"⚠️ {site_name}: {base_url} (check manually)")
                except:
                    results.append(f"⚠️ {site_name}: {base_url} (check manually)")
            
            if results:
                return f"🏛️ Government sites to check for '{query}':\n\n" + "\n".join(results)
            
            return None
            
        except Exception:
            return None

    def _fallback_response(self, query: str) -> str:
        """Provide helpful fallback when search fails."""
        return f"""🔍 Search for '{query}' completed but no specific results found.

📋 **Recommended Actions:**
• Visit ird.govt.nz directly for latest tax updates
• Check companies.govt.nz for business compliance changes  
• Review mbie.govt.nz for employment law updates
• Subscribe to IRD email updates for real-time notifications

🔗 **Direct Links:**
• IRD News: https://www.ird.govt.nz/about-us/news-updates
• Companies Office Updates: https://www.companies.govt.nz/news-and-updates/
• MBIE Updates: https://www.mbie.govt.nz/about/news/"""
