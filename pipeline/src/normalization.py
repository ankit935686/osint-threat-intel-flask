import json
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import ipaddress
import hashlib
import re

class IndicatorNormalizer:
    def __init__(self):
        self.common_fields = [
            'indicator', 'type', 'source', 'first_seen', 'last_seen',
            'confidence', 'severity', 'tags', 'description', 'raw_data',
            'asn', 'country', 'organization', 'latitude', 'longitude',
            'ports', 'services', 'malware_families', 'references'
        ]
    
    def detect_indicator_type(self, indicator: str) -> str:
        """Auto-detect the type of indicator"""
        # IP Address
        try:
            ipaddress.ip_address(indicator)
            return 'ip'
        except ValueError:
            pass
        
        # URL
        if re.match(r'^https?://', indicator, re.IGNORECASE):
            return 'url'
        
        # Domain
        if re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$', indicator):
            return 'domain'
        
        # Hash types
        if re.match(r'^[a-fA-F0-9]{32}$', indicator):
            return 'hash_md5'
        elif re.match(r'^[a-fA-F0-9]{40}$', indicator):
            return 'hash_sha1'
        elif re.match(r'^[a-fA-F0-9]{64}$', indicator):
            return 'hash_sha256'
        
        return 'unknown'
    
    def normalize(self, raw_item: Dict, source: str) -> Optional[Dict]:
        """Normalize raw data from any source to common schema"""
        try:
            if source == 'alienvault':
                return self._normalize_alienvault(raw_item)
            elif source == 'virustotal':
                return self._normalize_virustotal(raw_item)
            elif source == 'greynoise':
                return self._normalize_greynoise(raw_item)
            elif source == 'shodan':
                return self._normalize_shodan(raw_item)
            elif source == 'abuseipdb':
                return self._normalize_abuseipdb(raw_item)
            else:
                return self._normalize_generic(raw_item, source)
        except Exception as e:
            print(f"Normalization error for {source}: {str(e)}")
            return None
    
    def _normalize_alienvault(self, item: Dict) -> Dict:
        """Normalize AlienVault OTX data"""
        normalized = {
            'indicator': item.get('indicator', ''),
            'type': self.detect_indicator_type(item.get('indicator', '')),
            'source': 'alienvault',
            'first_seen': item.get('created', ''),
            'last_seen': item.get('updated', ''),
            'confidence': 0.7,  # Default for AlienVault
            'severity': 'medium',
            'tags': [],
            'description': '',
            'raw_data': item,
            'asn': '',
            'country': '',
            'organization': '',
            'ports': [],
            'services': [],
            'malware_families': [],
            'references': []
        }
        
        # Extract from pulse info
        pulse_info = item.get('pulse_info', {})
        pulses = pulse_info.get('pulses', [])
        
        if pulses:
            pulse = pulses[0]
            normalized['description'] = pulse.get('description', '')
            normalized['tags'] = pulse.get('tags', [])
            normalized['references'] = pulse.get('references', [])
        
        return normalized
    
    def _normalize_virustotal(self, item: Dict) -> Dict:
        """Normalize VirusTotal data"""
        # Implementation for VirusTotal
        normalized = {
            'indicator': item.get('id', ''),
            'type': self.detect_indicator_type(item.get('id', '')),
            'source': 'virustotal',
            'first_seen': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'confidence': 0.8,
            'severity': 'high',
            'tags': ['virustotal'],
            'description': 'VirusTotal detection',
            'raw_data': item
        }
        
        # Add VirusTotal specific fields
        attributes = item.get('attributes', {})
        last_analysis_stats = attributes.get('last_analysis_stats', {})
        
        malicious_count = last_analysis_stats.get('malicious', 0)
        if malicious_count > 10:
            normalized['severity'] = 'critical'
        elif malicious_count > 5:
            normalized['severity'] = 'high'
        
        return {**{field: '' for field in self.common_fields}, **normalized}
    
    def _normalize_greynoise(self, item: Dict) -> Dict:
        """Normalize GreyNoise data"""
        normalized = {
            'indicator': item.get('ip', ''),
            'type': 'ip',
            'source': 'greynoise',
            'first_seen': item.get('first_seen', ''),
            'last_seen': item.get('last_seen', ''),
            'confidence': 0.9 if item.get('classification') == 'malicious' else 0.3,
            'severity': 'critical' if item.get('classification') == 'malicious' else 'low',
            'tags': [item.get('classification', 'unknown')],
            'description': item.get('actor', ''),
            'raw_data': item,
            'organization': item.get('organization', ''),
            'asn': item.get('asn', ''),
            'country': item.get('country', ''),
            'ports': list(set([item.get('port', 0)])),
            'services': [item.get('protocol', '')]
        }
        
        return {**{field: '' for field in self.common_fields}, **normalized}
    
    def _normalize_shodan(self, item: Dict) -> Dict:
        """Normalize Shodan data"""
        normalized = {
            'indicator': item.get('ip_str', ''),
            'type': 'ip',
            'source': 'shodan',
            'first_seen': item.get('timestamp', ''),
            'last_seen': datetime.now().isoformat(),
            'confidence': 0.6,
            'severity': 'medium',
            'tags': [],
            'description': f"Open ports: {', '.join([str(p) for p in item.get('ports', [])])}",
            'raw_data': item,
            'asn': item.get('asn', ''),
            'country': item.get('country_code', ''),
            'organization': item.get('org', ''),
            'ports': item.get('ports', []),
            'services': list(set([str(port) for port in item.get('ports', [])]))
        }
        
        # Add services from port data
        services = []
        for port in item.get('ports', []):
            services.append(f"port_{port}")
        normalized['services'] = services
        
        return {**{field: '' for field in self.common_fields}, **normalized}
    
    def _normalize_abuseipdb(self, item: Dict) -> Dict:
        """Normalize AbuseIPDB data"""
        # AbuseIPDB returns data wrapped in 'data' key
        data = item.get('data', item)
        
        normalized = {
            'indicator': data.get('ipAddress', ''),
            'type': 'ip',
            'source': 'abuseipdb',
            'first_seen': data.get('lastReportedAt', datetime.now().isoformat()),
            'last_seen': datetime.now().isoformat(),
            'confidence': min(data.get('abuseConfidenceScore', 0) / 100, 1.0),
            'severity': 'critical' if data.get('abuseConfidenceScore', 0) > 80 else 'high',
            'tags': [data.get('usageType', 'unknown')] if data.get('usageType') else [],
            'description': f"Abuse confidence: {data.get('abuseConfidenceScore', 0)}%, Reports: {data.get('totalReports', 0)}",
            'raw_data': item,
            'country': data.get('countryCode', ''),
            'asn': '',
            'organization': data.get('isp', ''),
            'latitude': '',
            'longitude': '',
            'ports': [],
            'services': [],
            'malware_families': [],
            'references': []
        }
        
        return normalized
    
    def _normalize_generic(self, item: Dict, source: str) -> Dict:
        """Generic normalization for unknown sources"""
        return {
            'indicator': item.get('indicator', item.get('ip', item.get('domain', ''))),
            'type': self.detect_indicator_type(item.get('indicator', '')),
            'source': source,
            'first_seen': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'confidence': 0.5,
            'severity': 'medium',
            'tags': [],
            'description': '',
            'raw_data': item
        }