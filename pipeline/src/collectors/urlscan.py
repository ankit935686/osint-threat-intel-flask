import requests
import time
import json
from typing import List, Dict, Optional
import logging

class URLScanCollector:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://urlscan.io/api/v1"
        self.logger = logging.getLogger(__name__)
        self.seen_indicators = set()

    def collect(self, indicators: List[str] = None) -> List[Dict]:
        """Collect data from URLScan for the given indicators."""
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

            # Rate limiting: URLScan free API allows 1 request per second, so we sleep 1 second
            time.sleep(1)

        return all_data

    def get_indicator_data(self, indicator: str) -> Optional[Dict]:
        """Get data for a single indicator (domain or IP)."""
        # URLScan supports domains and IPs
        if self._is_ip(indicator) or self._is_domain(indicator):
            endpoint = f"{self.base_url}/search/"
            params = {
                'q': indicator
            }

            try:
                response = requests.get(endpoint, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                self.logger.error(f"Failed to get data for {indicator} from URLScan: {str(e)}")
                return None
        else:
            self.logger.warning(f"URLScan only supports domains and IPs, skipping {indicator}")
            return None

    def _is_ip(self, indicator: str) -> bool:
        try:
            parts = indicator.split('.')
            if len(parts) == 4 and all(0 <= int(part) < 256 for part in parts):
                return True
        except ValueError:
            pass
        return False

    def _is_domain(self, indicator: str) -> bool:
        # Simple domain check: has a dot and no protocol
        return '.' in indicator and not indicator.startswith(('http://', 'https://'))