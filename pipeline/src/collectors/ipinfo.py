import requests
from typing import Dict, Optional, List
import logging

class IPInfoCollector:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "https://ipinfo.io"
        self.logger = logging.getLogger(__name__)
    
    def collect(self, indicators: List[str] = None) -> List[Dict]:
        """IPInfo is primarily used for enrichment, not collection"""
        # This collector is mainly for enrichment purposes
        return []
    
    def get_ip_info(self, ip: str) -> Optional[Dict]:
        """Get IP information for enrichment"""
        url = f"{self.base_url}/{ip}"
        params = {'token': self.api_key} if self.api_key else {}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            self.logger.warning(f"IPInfo lookup failed for {ip}: {str(e)}")
        
        return None