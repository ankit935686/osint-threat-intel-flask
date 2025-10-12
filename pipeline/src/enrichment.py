import pandas as pd
import requests
import time
from typing import Dict, List
import logging
from collectors.ipinfo import IPInfoCollector

class EnrichmentEngine:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.ipinfo_collector = IPInfoCollector(config.get('ipinfo', ''))
        
    def enrich(self, normalized_data: pd.DataFrame) -> pd.DataFrame:
        """Enrich normalized indicators with additional context"""
        self.logger.info("Starting data enrichment")
        
        enriched_data = normalized_data.copy()
        
        # Enrich IP addresses
        ip_indicators = enriched_data[enriched_data['type'] == 'ip']
        if not ip_indicators.empty:
            enriched_data = self._enrich_ip_addresses(enriched_data)
        
        # Enrich domains
        domain_indicators = enriched_data[enriched_data['type'] == 'domain']
        if not domain_indicators.empty:
            enriched_data = self._enrich_domains(enriched_data)
        
        # Add threat intelligence context
        enriched_data = self._add_threat_context(enriched_data)
        
        # Save enriched data
        output_file = f"pipeline/data/processed/enriched_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        enriched_data.to_csv(output_file, index=False)
        
        self.logger.info(f"Enriched {len(enriched_data)} indicators")
        return enriched_data
    
    def _enrich_ip_addresses(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich IP addresses with geo and network data"""
        self.logger.info("Enriching IP addresses with geo data")
        
        for idx, row in df[df['type'] == 'ip'].iterrows():
            try:
                ip = row['indicator']
                
                # Get IP information
                ip_info = self.ipinfo_collector.get_ip_info(ip)
                
                if ip_info:
                    # Update dataframe with enrichment data
                    df.at[idx, 'asn'] = ip_info.get('asn', '')
                    df.at[idx, 'country'] = ip_info.get('country', '')
                    df.at[idx, 'organization'] = ip_info.get('org', '')
                    
                    # Handle location data
                    loc = ip_info.get('loc', '').split(',')
                    if len(loc) == 2:
                        df.at[idx, 'latitude'] = float(loc[0])
                        df.at[idx, 'longitude'] = float(loc[1])
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.warning(f"Failed to enrich IP {row['indicator']}: {str(e)}")
                continue
        
        return df
    
    def _enrich_domains(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich domain indicators"""
        # Placeholder for domain enrichment (WHOIS, DNS records, etc.)
        # You can integrate with domain tools like SecurityTrails, Whois, etc.
        return df
    
    def _add_threat_context(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add threat intelligence context based on existing data"""
        
        # Calculate confidence based on multiple sources
        source_counts = df.groupby('indicator')['source'].nunique()
        
        for indicator, count in source_counts.items():
            mask = df['indicator'] == indicator
            if count > 1:
                # Increase confidence for indicators seen in multiple sources
                df.loc[mask, 'confidence'] = df.loc[mask, 'confidence'] * 1.2
                df.loc[mask, 'confidence'] = df.loc[mask, 'confidence'].clip(upper=1.0)
                
                # Update severity if multiple sources agree
                if count >= 3:
                    df.loc[mask, 'severity'] = 'high'
        
        # Add context based on tags
        malicious_tags = ['malware', 'botnet', 'phishing', 'c2', 'ransomware']
        for tag in malicious_tags:
            mask = df['tags'].apply(lambda x: tag in x if isinstance(x, list) else False)
            df.loc[mask, 'severity'] = 'critical'
            df.loc[mask, 'confidence'] = 0.9
        
        return df