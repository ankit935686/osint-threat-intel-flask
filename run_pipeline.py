#!/usr/bin/env python3
"""
OSINT Threat Intelligence Pipeline Runner
"""

import sys
import os
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
        
        print("✅ Pipeline completed successfully!")
        print("📊 Check the pipeline/data/reports/ directory for outputs")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()