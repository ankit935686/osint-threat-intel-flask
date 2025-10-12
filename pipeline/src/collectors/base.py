import requests
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseCollector(ABC):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def collect(self, indicators: List[str] = None) -> List[Dict[str, Any]]:
        pass

    def make_request(self, url: str, params: Dict = None, headers: Dict = None) -> Dict:
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {url}: {str(e)}")
            return {}