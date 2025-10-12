import pandas as pd
import numpy as np
from typing import Dict, List
import logging

class MergeDedupeEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process(self, enriched_data: pd.DataFrame) -> pd.DataFrame:
        """Merge and deduplicate indicators from multiple sources"""
        self.logger.info("Merging and deduplicating indicators")
        
        if enriched_data.empty:
            return enriched_data
        
        # Group by indicator and type
        grouped = enriched_data.groupby(['indicator', 'type'])
        
        merged_records = []
        
        for (indicator, ind_type), group in grouped:
            try:
                # Ensure indicator is a string
                indicator = str(indicator)
                merged_record = self._merge_group(group, indicator, ind_type)
                merged_records.append(merged_record)
            except Exception as e:
                self.logger.error(f"Failed to merge indicator {indicator} of type {ind_type}: {str(e)}")
                continue
        
        merged_df = pd.DataFrame(merged_records)
        
        # Save merged data
        output_file = f"pipeline/data/processed/merged_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        merged_df.to_csv(output_file, index=False)
        
        self.logger.info(f"Merged {len(enriched_data)} records into {len(merged_df)} unique indicators")
        return merged_df
    
    def _merge_group(self, group: pd.DataFrame, indicator: str, ind_type: str) -> Dict:
        """Merge a group of duplicate indicators"""
        merged = {
            'indicator': indicator,
            'type': ind_type,
            'sources': list(group['source'].unique()),
            'source_count': len(group['source'].unique()),
            'first_seen': group['first_seen'].min(),
            'last_seen': group['last_seen'].max(),
            'confidence': group['confidence'].max(),
            'severity': self._calculate_merged_severity(group),
            'tags': self._merge_tags(group),
            'descriptions': list(group['description'].unique()),
            'asn': self._get_most_common(group, 'asn'),
            'country': self._get_most_common(group, 'country'),
            'organization': self._get_most_common(group, 'organization'),
            'latitude': group['latitude'].mean() if 'latitude' in group.columns else None,
            'longitude': group['longitude'].mean() if 'longitude' in group.columns else None,
            'ports': self._merge_lists(group, 'ports'),
            'services': self._merge_lists(group, 'services'),
            'malware_families': self._merge_lists(group, 'malware_families'),
            'references': self._merge_lists(group, 'references'),
            'raw_data_sources': {row['source']: row['raw_data'] for _, row in group.iterrows()}
        }
        
        return merged
    
    def _calculate_merged_severity(self, group: pd.DataFrame) -> str:
        """Calculate merged severity based on individual severities"""
        severity_order = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        max_severity = group['severity'].apply(lambda x: severity_order.get(x, 0)).max()
        
        reverse_severity = {v: k for k, v in severity_order.items()}
        return reverse_severity.get(max_severity, 'medium')
    
    def _merge_tags(self, group: pd.DataFrame) -> List[str]:
        """Merge tags from all sources"""
        all_tags = []
        for tags in group['tags']:
            if isinstance(tags, list):
                all_tags.extend(tags)
        return list(set(all_tags))
    
    def _merge_lists(self, group: pd.DataFrame, column: str) -> List:
        """Merge list-type columns"""
        all_items = []
        for items in group[column]:
            if isinstance(items, list):
                all_items.extend(items)
        return list(set(all_items))
    
    def _get_most_common(self, group: pd.DataFrame, column: str):
        """Get the most common non-empty value for a column"""
        values = group[column].dropna()
        if values.empty:
            return None
        return values.mode().iloc[0] if not values.mode().empty else values.iloc[0]