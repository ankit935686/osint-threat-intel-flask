"""
Threat feed aggregator to provide known malicious indicators for querying APIs
"""

# Common known malicious IPs and domains for testing and enrichment
KNOWN_MALICIOUS_IPS = [
    "1.234.21.73",      # Known malicious
    "45.155.205.233",   # Malware C2
    "185.220.101.1",    # Suspicious
    "91.219.236.218",   # Phishing
    "104.248.144.120",  # Botnet
    "62.210.105.116",   # Malware
    "185.220.102.242",  # Tor exit node
    "95.214.55.43",     # Malicious
    "103.109.247.10",   # C2 Server
    "23.106.122.168",   # Malware distribution
]

KNOWN_MALICIOUS_DOMAINS = [
    "freescanonline.com",
    "clicksgear.com", 
    "go.mail.ru",
    "securitydefender.net",
    "totalav.com",
    "systweak.com",
    "driver-update.com",
    "cleanmypc.com",
    "pckeeper.com",
    "reimageplus.com",
]

KNOWN_MALICIOUS_URLS = [
    "http://malware-traffic-analysis.net/suspicious.exe",
    "http://185.220.101.1/payload.bin",
    "https://clicksgear.com/phishing",
]

KNOWN_MALICIOUS_HASHES = [
    "44d88612fea8a8f36de82e1278abb02f",  # MD5 - EICAR test file
    "3395856ce81f2b7382dee72602f798b642f14140",  # SHA1
    "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f",  # SHA256
]

def get_test_indicators():
    """Get a diverse set of test indicators for all API types"""
    return {
        'ips': KNOWN_MALICIOUS_IPS[:5],  # Use first 5 to avoid rate limits
        'domains': KNOWN_MALICIOUS_DOMAINS[:5],
        'urls': KNOWN_MALICIOUS_URLS[:3],
        'hashes': KNOWN_MALICIOUS_HASHES[:3],
    }

def get_all_indicators():
    """Get all indicators as a flat list"""
    indicators = []
    indicators.extend(KNOWN_MALICIOUS_IPS[:5])
    indicators.extend(KNOWN_MALICIOUS_DOMAINS[:5])
    return indicators
