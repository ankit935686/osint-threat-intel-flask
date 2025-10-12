import pandas as pd
import numpy as np
from typing import Dict, List
import logging

class ThreatScorer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.weights = {
            'source_reputation': 0.25,
            'confidence': 0.20,
            'severity': 0.15,
            'source_count': 0.15,
            'malicious_tags': 0.15,
            'recent_activity': 0.10
        }
    
    def calculate_scores(self, merged_data: pd.DataFrame) -> pd.DataFrame:
        """Calculate threat scores for all indicators"""
        self.logger.info("Calculating threat scores")
        
        scored_data = merged_data.copy()
        
        # Calculate individual component scores
        scored_data['source_reputation_score'] = scored_data.apply(self._calculate_source_reputation, axis=1)
        scored_data['confidence_score'] = scored_data['confidence'] * 100
        scored_data['severity_score'] = scored_data['severity'].apply(self._severity_to_score)
        scored_data['source_count_score'] = scored_data['source_count'] * 10
        scored_data['malicious_tags_score'] = scored_data['tags'].apply(self._calculate_malicious_tags_score)
        scored_data['recent_activity_score'] = scored_data.apply(self._calculate_recency_score, axis=1)
        
        # Calculate overall threat score
        scored_data['threat_score'] = (
            scored_data['source_reputation_score'] * self.weights['source_reputation'] +
            scored_data['confidence_score'] * self.weights['confidence'] +
            scored_data['severity_score'] * self.weights['severity'] +
            scored_data['source_count_score'] * self.weights['source_count'] +
            scored_data['malicious_tags_score'] * self.weights['malicious_tags'] +
            scored_data['recent_activity_score'] * self.weights['recent_activity']
        )
        
        # Clip scores to 0-100 range
        scored_data['threat_score'] = scored_data['threat_score'].clip(0, 100)
        
        # Add risk level categorization
        scored_data['risk_level'] = scored_data['threat_score'].apply(self._score_to_risk_level)
        
        # Save scored data
        output_file = f"pipeline/data/processed/scored_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
        scored_data.to_csv(output_file, index=False)
        
        self.logger.info(f"Calculated scores for {len(scored_data)} indicators")
        return scored_data
    
    def _calculate_source_reputation(self, row) -> float:
        """Calculate score based on source reputation"""
        source_scores = {
            'virustotal': 90,
            'greynoise': 85,
            'alienvault': 80,
            'abuseipdb': 75,
            'shodan': 60,
            'urlscan': 70
        }
        
        sources = row.get('sources', [])
        if not sources:
            return 0
        
        avg_score = np.mean([source_scores.get(source, 50) for source in sources])
        return min(avg_score, 100)
    
    def _severity_to_score(self, severity: str) -> float:
        """Convert severity to numerical score"""
        severity_scores = {
            'low': 25,
            'medium': 50,
            'high': 75,
            'critical': 100
        }
        return severity_scores.get(severity, 50)
    
    def _calculate_malicious_tags_score(self, tags: List[str]) -> float:
        """Calculate score based on malicious tags"""
        if not isinstance(tags, list):
            return 0
        
        malicious_terms = {
            'malware': 20,
            'botnet': 25,
            'phishing': 20,
            'c2': 30,
            'ransomware': 25,
            'exploit': 15,
            'brute-force': 15,
            'scanning': 10
        }
        
        score = 0
        for tag in tags:
            if tag in malicious_terms:
                score += malicious_terms[tag]
        
        return min(score, 100)
    
    def _calculate_recency_score(self, row) -> float:
        """Calculate score based on recent activity"""
        # Placeholder - implement based on first_seen/last_seen timestamps
        # More recent activity = higher score
        return 50  # Default medium score
    
    def _score_to_risk_level(self, score: float) -> str:
        """Convert numerical score to risk level"""
        if score >= 80:
            return 'Critical'
        elif score >= 60:
            return 'High'
        elif score >= 40:
            return 'Medium'
        elif score >= 20:
            return 'Low'
        else:
            return 'Info'