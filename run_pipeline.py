#!/usr/bin/env python3
"""
OSINT Threat Intelligence Pipeline Runner
"""

import sys
import os
import json
from pathlib import Path

# Add the pipeline source directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'pipeline/src'))

from main import OSINTPipeline

def main():
    print("🚀 OSINT Threat Intelligence Pipeline")
    print("=" * 50)
    
    try:
        # Initialize and run pipeline
        pipeline = OSINTPipeline()
        
        # You can provide specific indicators or let it collect from subscriptions
        indicators = None
        
        if len(sys.argv) > 1:
            indicators = sys.argv[1:]
            print(f"🔍 Analyzing specific indicators: {indicators}")
        else:
            print("📡 Collecting from subscribed threat feeds...")
        
        pipeline.run_pipeline(indicators)
        
        # Verify the summary.json file was created correctly
        summary_path = os.path.join('pipeline', 'data', 'reports', 'summary.json')
        if os.path.exists(summary_path):
            print(f"✓ Summary file created: {summary_path}")
            
            # Check summary.json content
            with open(summary_path, 'r') as f:
                summary = json.load(f)
                keys = list(summary.keys())
                print(f"✓ Summary contains {len(keys)} keys: {', '.join(keys)}")
                
                # Verify critical data
                if 'source_data' in keys:
                    print(f"✓ Source-specific data found with {len(summary['source_data'])} sources")
                else:
                    print("⚠ Warning: source_data is missing from summary.json")
        else:
            print(f"⚠ Warning: Summary file not found at {summary_path}")
        
        print("✅ Pipeline completed successfully!")
        print("📊 Check the pipeline/data/reports/ directory for outputs")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()