import requests
import time
from typing import List, Dict, Optional
import logging

class ShodanCollector:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.shodan.io"
        self.logger = logging.getLogger(__name__)
    
    def collect(self, indicators: List[str] = None) -> List[Dict]:
        """Collect data from Shodan"""
        all_data = []
        
        try:
            # Get trending/malicious IPs from Shodan
            trending_data = self.get_trending_ips()
            all_data.extend(trending_data)
            
            # Query specific indicators if provided
            if indicators:
                for indicator in indicators:
                    data = self.get_ip_data(indicator)
                    if data:
                        all_data.append(data)
                    time.sleep(1)  # Shodan rate limit
                    
        except Exception as e:
            self.logger.error(f"Shodan collection failed: {str(e)}")
        
        return all_data
    
    def get_trending_ips(self) -> List[Dict]:
        """Get trending/malicious IPs from Shodan"""
        # Search for common malicious services
        queries = [
            'category:malware',
            'tag:malware',
            'product:Metasploit',
            'product:Cobalt Strike',
            'tag:honeypot'
        ]
        
        all_results = []
        for query in queries[:2]:  # Limit to avoid rate limits
            try:
                url = f"{self.base_url}/shodan/host/search"
                params = {
                    'key': self.api_key,
                    'query': query,
                    'limit': 10
                }
                
                response = requests.get(url, params=params, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    all_results.extend(data.get('matches', []))
                
                time.sleep(1)
            except Exception as e:
                self.logger.warning(f"Shodan query failed for {query}: {str(e)}")
        
        return all_results
    
    def get_ip_data(self, ip: str) -> Optional[Dict]:
        """Get detailed information for a specific IP"""
        url = f"{self.base_url}/shodan/host/{ip}"
        params = {'key': self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            self.logger.warning(f"Shodan IP lookup failed for {ip}: {str(e)}")
        
        return None