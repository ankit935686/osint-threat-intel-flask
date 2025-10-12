import requests
import time
from typing import List, Dict, Optional
import logging

class VirusTotalCollector:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.virustotal.com/api/v3"
        self.headers = {"x-apikey": api_key}
        self.logger = logging.getLogger(__name__)
    
    def collect(self, indicators: List[str] = None) -> List[Dict]:
        """Collect threat data from VirusTotal"""
        all_data = []
        
        if not indicators:
            # Get recent comments which often contain IOCs
            all_data.extend(self.get_recent_comments())
        else:
            for indicator in indicators:
                try:
                    data = self.get_indicator_data(indicator)
                    if data:
                        all_data.append(data)
                    time.sleep(15)  # VT rate limit
                except Exception as e:
                    self.logger.error(f"Failed to get VT data for {indicator}: {str(e)}")
        
        return all_data
    
    def get_indicator_data(self, indicator: str) -> Optional[Dict]:
        """Get data for a specific indicator"""
        indicator_type = self.detect_type(indicator)
        
        if indicator_type == 'ip':
            url = f"{self.base_url}/ip_addresses/{indicator}"
        elif indicator_type == 'domain':
            url = f"{self.base_url}/domains/{indicator}"
        elif indicator_type == 'hash':
            url = f"{self.base_url}/files/{indicator}"
        else:
            return None
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            self.logger.warning(f"VirusTotal API error for {indicator}: {str(e)}")
        
        return None
    
    def get_recent_comments(self) -> List[Dict]:
        """Get recent comments containing IOCs"""
        # This is a placeholder - you'd need VT enterprise for full access
        # For now, return empty or use public endpoints if available
        return []
    
    def detect_type(self, indicator: str) -> str:
        """Detect indicator type for VirusTotal"""
        import ipaddress
        try:
            ipaddress.ip_address(indicator)
            return 'ip'
        except:
            pass
        
        if len(indicator) in [32, 40, 64] and all(c in '0123456789abcdefABCDEF' for c in indicator):
            return 'hash'
        elif '.' in indicator and ' ' not in indicator:
            return 'domain'
        
        return 'unknown'