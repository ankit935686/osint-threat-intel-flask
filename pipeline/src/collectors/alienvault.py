import requests
import json
from typing import List, Dict, Optional
import logging
from datetime import datetime

class AlienVaultCollector:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://otx.alienvault.com/api/v1"
        self.headers = {"X-OTX-API-KEY": api_key}
        self.logger = logging.getLogger(__name__)
    
    def collect(self, indicators: List[str] = None) -> List[Dict]:
        """Collect threat data from AlienVault OTX"""
        all_data = []
        
        try:
            # Get subscribed pulses
            pulses = self.get_subscribed_pulses()
            
            for pulse in pulses:
                pulse_data = self.get_pulse_indicators(pulse['id'])
                all_data.extend(pulse_data)
            
            # If specific indicators provided, look them up
            if indicators:
                for indicator in indicators:
                    indicator_data = self.get_indicator_data(indicator)
                    if indicator_data:
                        all_data.append(indicator_data)
            
            self.logger.info(f"Collected {len(all_data)} items from AlienVault")
            
        except Exception as e:
            self.logger.error(f"AlienVault collection failed: {str(e)}")
        
        return all_data
    
    def get_subscribed_pulses(self) -> List[Dict]:
        """Get pulses the API key is subscribed to"""
        url = f"{self.base_url}/pulses/subscribed"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.RequestException as e:
            self.logger.error(f"Failed to get subscribed pulses: {str(e)}")
            return []
    
    def get_pulse_indicators(self, pulse_id: str) -> List[Dict]:
        """Get indicators for a specific pulse"""
        url = f"{self.base_url}/pulses/{pulse_id}/indicators"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            indicators = response.json().get('results', [])
            
            # Add pulse context to each indicator
            for indicator in indicators:
                indicator['pulse_id'] = pulse_id
            
            return indicators
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to get pulse {pulse_id} indicators: {str(e)}")
            return []
    
    def get_indicator_data(self, indicator: str) -> Optional[Dict]:
        """Get detailed information for a specific indicator"""
        url = f"{self.base_url}/indicators/IPv4/{indicator}/general"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.warning(f"Failed to get indicator {indicator}: {str(e)}")
            return None