#!/usr/bin/env python3
"""
Quick fix: Update run_pipeline.py to use test indicators from all sources
"""

import sys
import os

# Add pipeline to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'pipeline/src'))

from main import OSINTPipeline

# Test indicators for all APIs
test_indicators = [
    # IPs for GreyNoise, AbuseIPDB, Shodan
    "1.234.21.73",
    "45.155.205.233",
    "185.220.101.1",
    "91.219.236.218",
    "104.248.144.120",
    
    # Domains for VirusTotal, URLScan
    "freescanonline.com",
    "clicksgear.com",
    "securitydefender.net",
    "malware-traffic-analysis.net",
    "totalav.com",
]

def main():
    print("🚀 OSINT Threat Intelligence Pipeline (Enhanced Multi-Source)")
    print("=" * 60)
    print(f"📊 Using {len(test_indicators)} test indicators to query all APIs")
    print()
    
    try:
        pipeline = OSINTPipeline()
        
        # Run with test indicators to ensure all APIs are queried
        print("🔍 Collecting from ALL sources with test indicators...")
        pipeline.run_pipeline(test_indicators)
        
        print("\n✅ Pipeline completed successfully!")
        print("📊 Data collected from multiple sources")
        print("💡 Start the dashboard to view results:")
        print("   python app.py")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
