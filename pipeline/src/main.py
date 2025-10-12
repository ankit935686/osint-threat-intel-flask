import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging

from collectors.alienvault import AlienVaultCollector
from collectors.virustotal import VirusTotalCollector
from collectors.greynoise import GreyNoiseCollector
from collectors.shodan import ShodanCollector
from collectors.abuseipdb import AbuseIPDBCollector
from collectors.urlscan import URLScanCollector
from collectors.ipinfo import IPInfoCollector
from normalization import IndicatorNormalizer
from enrichment import EnrichmentEngine
from merge_dedupe import MergeDedupeEngine
from scoring import ThreatScorer
from correlation import CorrelationEngine
from report_generator import ReportGenerator

class OSINTPipeline:
    def __init__(self, config_path: str = "pipeline/config/api_keys.json"):
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.setup_directories()
        
        # Initialize components
        self.collectors = self.initialize_collectors()
        self.normalizer = IndicatorNormalizer()
        self.enricher = EnrichmentEngine(self.config)
        self.merger = MergeDedupeEngine()
        self.scorer = ThreatScorer()
        self.correlator = CorrelationEngine()
        self.reporter = ReportGenerator()
        
    def load_config(self, config_path: str) -> Dict:
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_directories(self):
        """Create necessary directories"""
        directories = [
            'pipeline/data/raw',
            'pipeline/data/processed', 
            'pipeline/data/reports',
            'pipeline/data/processed/normalized',
            'pipeline/data/processed/enriched'
        ]
        
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def initialize_collectors(self) -> Dict:
        """Initialize all data collectors"""
        return {
            'alienvault': AlienVaultCollector(self.config.get('alienvault')),
            'virustotal': VirusTotalCollector(self.config.get('virustotal')),
            'greynoise': GreyNoiseCollector(self.config.get('greynoise')),
            'shodan': ShodanCollector(self.config.get('shodan')),
            'abuseipdb': AbuseIPDBCollector(self.config.get('abuseipdb')),
            'urlscan': URLScanCollector(self.config.get('urlscan')),
            'ipinfo': IPInfoCollector(self.config.get('ipinfo'))
        }
    
    def run_pipeline(self, indicators: List[str] = None):
        """Execute the complete OSINT pipeline"""
        self.logger.info("Starting OSINT Threat Intelligence Pipeline")
        
        try:
            # Step 1: Collection
            raw_data = self.collect_data(indicators)
            
            # Step 2: Normalization
            normalized_data = self.normalize_data(raw_data)
            
            # Step 3: Enrichment
            enriched_data = self.enrich_data(normalized_data)
            
            # Step 4: Merge & Deduplicate
            merged_data = self.merge_deduplicate_data(enriched_data)
            
            # Step 5: Scoring
            scored_data = self.score_data(merged_data)
            
            # Step 6: Correlation
            correlated_data = self.correlate_data(scored_data)
            
            # Step 7: Reporting
            self.generate_reports(correlated_data)
            
            self.logger.info("Pipeline execution completed successfully")
            
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {str(e)}")
            raise
    
    def collect_data(self, indicators: List[str] = None) -> Dict[str, List]:
        """Collect data from all sources"""
        self.logger.info("Starting data collection from all sources")
        
        all_data = {}
        
        for source_name, collector in self.collectors.items():
            try:
                self.logger.info(f"Collecting from {source_name}")
                data = collector.collect(indicators)
                all_data[source_name] = data
                
                # Save raw data
                output_file = f"pipeline/data/raw/{source_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=2)
                    
                self.logger.info(f"Collected {len(data)} indicators from {source_name}")
                
            except Exception as e:
                self.logger.error(f"Failed to collect from {source_name}: {str(e)}")
                continue
        
        return all_data
    
    def normalize_data(self, raw_data: Dict[str, List]) -> pd.DataFrame:
        """Normalize all collected data to common schema"""
        self.logger.info("Normalizing data to common schema")
        
        all_normalized = []
        
        for source_name, data_list in raw_data.items():
            for item in data_list:
                try:
                    normalized = self.normalizer.normalize(item, source_name)
                    if normalized:
                        all_normalized.append(normalized)
                except Exception as e:
                    self.logger.warning(f"Failed to normalize item from {source_name}: {str(e)}")
                    continue
        
        df = pd.DataFrame(all_normalized)
        
        # Save normalized data
        output_file = f"pipeline/data/processed/normalized_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(output_file, index=False)
        
        self.logger.info(f"Normalized {len(df)} indicators")
        return df
    
    def enrich_data(self, normalized_data: pd.DataFrame) -> pd.DataFrame:
        """Enrich indicators with additional context"""
        return self.enricher.enrich(normalized_data)
    
    def merge_deduplicate_data(self, enriched_data: pd.DataFrame) -> pd.DataFrame:
        """Merge and deduplicate indicators from multiple sources"""
        try:
            return self.merger.process(enriched_data)
        except Exception as e:
            self.logger.error(f"Merge/dedupe failed: {str(e)}")
            # Dump sample data for debugging
            with open("debug_enriched_data.txt", "w") as f:
                f.write(str(enriched_data.head()))
            raise
    
    def score_data(self, merged_data: pd.DataFrame) -> pd.DataFrame:
        """Calculate threat scores for indicators"""
        try:
            return self.scorer.calculate_scores(merged_data)
        except Exception as e:
            self.logger.error(f"Scoring failed: {str(e)}")
            # Dump sample data for debugging
            with open("debug_merged_data.txt", "w") as f:
                f.write(str(merged_data.head()))
            raise
    
    def correlate_data(self, scored_data: pd.DataFrame):
        """Build correlation graph between indicators"""
        return self.correlator.build_graph(scored_data)
    
    def generate_reports(self, correlated_data):
        """Generate comprehensive reports"""
        return self.reporter.generate_all_reports(correlated_data)

def main():
    """Main entry point for the pipeline"""
    pipeline = OSINTPipeline()
    
    # Example: Run with specific indicators
    test_indicators = [
        "8.8.8.8",
        "google.com", 
        "malicious-domain.com"
    ]
    
    pipeline.run_pipeline(test_indicators)

if __name__ == "__main__":
    main()