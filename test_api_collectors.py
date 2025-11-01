#!/usr/bin/env python3
"""
Test script to verify all API collectors are working
"""

import sys
import os
import json
from pathlib import Path

# Add the pipeline source directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'pipeline/src'))

from collectors.alienvault import AlienVaultCollector
from collectors.virustotal import VirusTotalCollector
from collectors.greynoise import GreyNoiseCollector
from collectors.shodan import ShodanCollector
from collectors.abuseipdb import AbuseIPDBCollector
from collectors.urlscan import URLScanCollector
from collectors.ipinfo import IPInfoCollector
from collectors.threat_feeds import get_all_indicators

def load_api_keys():
    """Load API keys from config file"""
    config_path = "pipeline/config/api_keys.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def test_collector(name, collector, test_indicators):
    """Test a single collector"""
    print(f"\n{'='*60}")
    print(f"Testing {name}...")
    print(f"{'='*60}")
    
    try:
        # For AlienVault, don't pass indicators (use subscribed pulses)
        if name == "AlienVault":
            data = collector.collect(None)
        else:
            data = collector.collect(test_indicators)
        
        print(f"✓ {name}: Collected {len(data)} items")
        
        if data:
            print(f"  Sample data: {json.dumps(data[0], indent=2)[:200]}...")
        else:
            print(f"  ⚠ No data returned (this might be normal if no matches found)")
        
        return len(data)
        
    except Exception as e:
        print(f"✗ {name}: Failed - {str(e)}")
        import traceback
        traceback.print_exc()
        return 0

def main():
    print("🔍 OSINT API Collector Test Suite")
    print("="*60)
    
    # Load API keys
    try:
        api_keys = load_api_keys()
        print("✓ Loaded API keys")
    except Exception as e:
        print(f"✗ Failed to load API keys: {str(e)}")
        return 1
    
    # Get test indicators
    test_indicators = get_all_indicators()
    print(f"✓ Using {len(test_indicators)} test indicators")
    print(f"  IPs: {test_indicators[:3]}")
    print(f"  Domains: {test_indicators[5:8]}")
    
    # Initialize collectors
    collectors = {
        'AlienVault': AlienVaultCollector(api_keys.get('alienvault', '')),
        'VirusTotal': VirusTotalCollector(api_keys.get('virustotal', '')),
        'GreyNoise': GreyNoiseCollector(api_keys.get('greynoise', '')),
        'Shodan': ShodanCollector(api_keys.get('shodan', '')),
        'AbuseIPDB': AbuseIPDBCollector(api_keys.get('abuseipdb', '')),
        'URLScan': URLScanCollector(api_keys.get('urlscan', '')),
        'IPInfo': IPInfoCollector(api_keys.get('ipinfo', '')),
    }
    
    # Test each collector
    results = {}
    for name, collector in collectors.items():
        count = test_collector(name, collector, test_indicators)
        results[name] = count
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    
    total = 0
    working = 0
    
    for name, count in results.items():
        status = "✓ Working" if count > 0 else "⚠ No data"
        print(f"  {name:15s}: {count:4d} items - {status}")
        total += count
        if count > 0:
            working += 1
    
    print(f"\n  Total items: {total}")
    print(f"  Working APIs: {working}/{len(collectors)}")
    
    if working < len(collectors):
        print("\n⚠ Some APIs returned no data. This could be due to:")
        print("  - Rate limits")
        print("  - Invalid/inactive API keys")
        print("  - No matching data for test indicators")
        print("  - Network/connectivity issues")
    
    if total > 0:
        print("\n✅ At least some APIs are working! Run the full pipeline:")
        print("   python run_pipeline.py")
    else:
        print("\n❌ No APIs returned data. Check your API keys and network connection.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
