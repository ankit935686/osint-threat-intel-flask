
# OSINT Threat Intelligence Pipeline (Flask)

A comprehensive threat intelligence pipeline that:
1. Collects threat indicators from multiple sources (AlienVault OTX, VirusTotal, GreyNoise, Shodan, etc.)
2. Normalizes data into a common schema
3. Enriches indicators with geo/ASN information
4. Merges and deduplicates across sources
5. Scores threats based on multiple factors
6. Creates correlations between related indicators
7. Generates visual reports via a Flask dashboard

## Quick Start

1. Clone the repository and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the pipeline with specific indicators:
   ```bash
   python run_pipeline.py 8.8.8.8 malicious-domain.com 192.168.1.1
   ```
   
   Or run without arguments to collect from subscribed threat feeds:
   ```bash
   python run_pipeline.py
   ```

3. Start the Flask dashboard:
   ```bash
   python app.py
   ```

4. Open http://127.0.0.1:5000 in your browser to view the dashboard.

## API Keys

The pipeline uses various threat intelligence APIs. Add your API keys to `pipeline/config/api_keys.json`:

```json
{
  "alienvault": "YOUR_ALIENVAULT_API_KEY",
  "virustotal": "YOUR_VIRUSTOTAL_API_KEY",
  "greynoise": "YOUR_GREYNOISE_API_KEY",
  "shodan": "YOUR_SHODAN_API_KEY",
  "abuseipdb": "YOUR_ABUSEIPDB_API_KEY",
  "urlscan": "YOUR_URLSCAN_API_KEY",
  "ipinfo": "YOUR_IPINFO_API_KEY"
}
```

## Pipeline Steps

1. **Collection**: Raw data from APIs
2. **Normalization**: Convert to common schema
3. **Enrichment**: Add geo/ASN context
4. **Merge & Deduplicate**: Combine sources
5. **Scoring**: Calculate threat scores
6. **Correlation**: Build relationship graphs
7. **Reporting**: Generate visual dashboard

## Output

- CSV files in `pipeline/data/processed/`
- JSON reports in `pipeline/data/reports/`
- Interactive web dashboard
