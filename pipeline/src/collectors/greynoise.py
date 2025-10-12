import requests
import time
import json
from typing import List, Dict, Optional
import logging

class GreyNoiseCollector:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.greynoise.io/v3"
        self.logger = logging.getLogger(__name__)
        self.seen_indicators = set()

    def collect(self, indicators: List[str] = None) -> List[Dict]:
        """Collect data from GreyNoise for the given indicators."""
        if indicators is None:
            indicators = []

        all_data = []
        for indicator in indicators:
            if indicator in self.seen_indicators:
                continue
            self.seen_indicators.add(indicator)

            data = self.get_indicator_data(indicator)
            if data:
                all_data.append(data)

            # Rate limiting: GreyNoise community API is 1 request per second, so we sleep 1 second
            time.sleep(1)

        return all_data

    def get_indicator_data(self, indicator: str) -> Optional[Dict]:
        """Get data for a single indicator (IP only)."""
        # GreyNoise only supports IP addresses
        if not self._is_ip(indicator):
            self.logger.warning(f"GreyNoise only supports IP addresses, skipping {indicator}")
            return None

        endpoint = f"{self.base_url}/community/{indicator}"
        headers = {
            'key': self.api_key,
            'User-Agent': 'GreyNoise-API'
        }

        try:
            response = requests.get(endpoint, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Failed to get data for {indicator} from GreyNoise: {str(e)}")
            return None

    def _is_ip(self, indicator: str) -> bool:
        try:
            parts = indicator.split('.')
            if len(parts) == 4 and all(0 <= int(part) < 256 for part in parts):
                return True
        except ValueError:
            pass
        return False