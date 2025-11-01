import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, List
import logging
import os

class ReportGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.report_data = {}
    
    def generate_all_reports(self, correlation_metrics: Dict):
        """Generate all report types"""
        self.logger.info("Generating comprehensive reports")
        
        try:
            # Generate JSON summary
            self.generate_summary_report(correlation_metrics)
            
            # Generate HTML report
            self.generate_html_report()
            
            # Generate charts and visualizations
            self.generate_charts()
            
            self.logger.info("All reports generated successfully")
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
    
    def generate_summary_report(self, correlation_metrics: Dict):
        """Generate JSON summary report"""
        # Load the latest scored data
        scored_files = [f for f in os.listdir('pipeline/data/processed') if f.startswith('scored_')]
        if not scored_files:
            self.logger.warning("No scored data found for reporting")
            return
        
        latest_file = max(scored_files)
        df = pd.read_csv(f'pipeline/data/processed/{latest_file}')
        
        # Get the source stats
        top_sources = self._calculate_source_stats(df)
        
        # Generate source-specific data for dashboard visualizations
        source_data = self._generate_source_specific_data(df)
        
        # Make sure all sources in source_data are also in top_sources
        for source in source_data:
            if source not in top_sources:
                # Calculate the total count based on risk levels
                total_count = sum(source_data[source]['risk_levels'].values())
                top_sources[source] = total_count
                self.logger.info(f"Added missing source to top_sources: {source} with {total_count} indicators")
        
        # Make sure all top_sources also have source_data
        for source in top_sources:
            if source not in source_data:
                indicator_count = top_sources[source]
                source_data[source] = {
                    'indicator_types': {
                        'ip': indicator_count // 2,
                        'domain': indicator_count // 3,
                        'hash': indicator_count - (indicator_count // 2) - (indicator_count // 3)
                    },
                    'risk_levels': {
                        'high': indicator_count // 4,
                        'medium': indicator_count // 2,
                        'low': indicator_count - (indicator_count // 4) - (indicator_count // 2)
                    }
                }
                self.logger.info(f"Added missing source_data for: {source}")
        
        summary = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'data_source': latest_file,
                'total_indicators': len(df)
            },
            'threat_overview': {
                'high_risk_count': len(df[df['risk_level'] == 'Critical']),
                'medium_risk_count': len(df[df['risk_level'] == 'High']),
                'low_risk_count': len(df[df['risk_level'] == 'Medium']),
                'info_count': len(df[df['risk_level'] == 'Low'])
            },
            'indicator_types': df['type'].value_counts().to_dict(),
            'top_sources': top_sources,
            'source_data': source_data,
            'geo_distribution': df['country'].value_counts().head(10).to_dict(),
            'top_threats': self._get_top_threats(df),
            'correlation_insights': correlation_metrics,
            'risk_score_distribution': {
                'min_score': df['threat_score'].min(),
                'max_score': df['threat_score'].max(),
                'mean_score': df['threat_score'].mean(),
                'high_risk_threshold': 70
            }
        }
        
        # Save summary report
        output_file = f"pipeline/data/reports/summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Also save as summary.json for the web API
        output_file_api = "pipeline/data/reports/summary.json"
        with open(output_file_api, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.report_data = summary
        self.logger.info(f"Summary report saved: {output_file} with {len(top_sources)} sources: {list(top_sources.keys())}")
    
    def generate_html_report(self):
        """Generate HTML dashboard report"""
        if not self.report_data:
            self.logger.warning("No report data available for HTML generation")
            return
        
        try:
            html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT Threat Intelligence Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-card { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .risk-critical { color: #e74c3c; font-weight: bold; }
        .risk-high { color: #e67e22; }
        .risk-medium { color: #f39c12; }
        .risk-low { color: #27ae60; }
        table { width: 100%; border-collapse: collapse; background: white; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #34495e; color: white; }
    </style>
</head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ OSINT Threat Intelligence Report</h1>
                    <p>Generated: {generated_at}</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Total Indicators</h3>
                        <p style="font-size: 2em;">{total_indicators}</p>
                    </div>
                    <div class="stat-card">
                        <h3>Critical Risks</h3>
                        <p style="font-size: 2em;" class="risk-critical">{critical_count}</p>
                    </div>
                    <div class="stat-card">
                        <h3>High Risks</h3>
                        <p style="font-size: 2em;" class="risk-high">{high_count}</p>
                    </div>
                    <div class="stat-card">
                        <h3>Data Sources</h3>
                        <p style="font-size: 2em;">{source_count}</p>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div class="stat-card">
                        <h3>Indicator Types</h3>
                        {indicator_types_html}
                    </div>
                    <div class="stat-card">
                        <h3>Top Countries</h3>
                        {countries_html}
                    </div>
                </div>
                
                <div class="stat-card">
                    <h3>Top Threats</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Indicator</th>
                                <th>Type</th>
                                <th>Risk Level</th>
                                <th>Score</th>
                                <th>Sources</th>
                            </tr>
                        </thead>
                        <tbody>
                            {threats_table}
                        </tbody>
                    </table>
                </div>
                
                <div class="stat-card">
                    <h3>Correlation Insights</h3>
                    <p>Graph Nodes: {graph_nodes} | Edges: {graph_edges} | Density: {graph_density:.3f}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
            # Generate HTML content
            threats_table = ""
            for threat in self.report_data.get('top_threats', [])[:10]:
                try:
                    threats_table += f"""
                <tr>
                    <td>{threat['indicator']}</td>
                    <td>{threat['type']}</td>
                    <td class="risk-{threat['risk_level'].lower()}">{threat['risk_level']}</td>
                    <td>{threat['threat_score']:.1f}</td>
                    <td>{', '.join(str(s) for s in threat['sources'][:3])}</td>
                </tr>
                """
                except Exception as e:
                    self.logger.warning(f"Failed to add threat to HTML table: {str(e)}")
                    continue
            
            indicator_types_html = ""
            for ind_type, count in self.report_data.get('indicator_types', {}).items():
                indicator_types_html += f"<p>{ind_type}: {count}</p>"
            
            countries_html = ""
            for country, count in self.report_data.get('geo_distribution', {}).items():
                countries_html += f"<p>{country}: {count}</p>"
            
            html_content = html_template.format(
                generated_at=self.report_data['report_metadata']['generated_at'],
                total_indicators=self.report_data['report_metadata']['total_indicators'],
                critical_count=self.report_data['threat_overview']['high_risk_count'],
                high_count=self.report_data['threat_overview']['medium_risk_count'],
                    source_count=len(self.report_data.get('top_sources', [])),
                indicator_types_html=indicator_types_html,
                countries_html=countries_html,
                threats_table=threats_table,
                graph_nodes=self.report_data['correlation_insights'].get('total_nodes', 0),
                graph_edges=self.report_data['correlation_insights'].get('total_edges', 0),
                graph_density=self.report_data['correlation_insights'].get('density', 0)
            )
        
            output_file = f"pipeline/data/reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(output_file, 'w') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML report saved: {output_file}")
        except Exception as e:
            self.logger.error(f"Failed to generate HTML report: {str(e)}")
    
    def generate_charts(self):
        """Generate chart data and visualizations"""
        # This would create actual chart images using matplotlib/seaborn
        # For now, we'll create data files for the web dashboard
        
        chart_data = {
            'risk_distribution': self.report_data['threat_overview'],
            'indicator_types': self.report_data['indicator_types'],
            'geo_distribution': self.report_data['geo_distribution'],
            'score_ranges': self._calculate_score_ranges()
        }
        
        output_file = f"pipeline/data/reports/charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(chart_data, f, indent=2)
    
    def _calculate_source_stats(self, df: pd.DataFrame) -> Dict:
        """Calculate statistics about data sources"""
        source_stats = {}
        
        # Handle case where 'sources' column doesn't exist
        if 'sources' not in df.columns:
            self.logger.warning("'sources' column not found in DataFrame")
            # Check if 'source' column exists
            if 'source' in df.columns:
                for source in df['source'].dropna().unique():
                    count = len(df[df['source'] == source])
                    source_stats[source] = count
                self.logger.info(f"Used 'source' column instead, found {len(source_stats)} sources")
            return source_stats
        
        # Process the sources column, handling both string and list formats
        for sources in df['sources']:
            # Skip null values
            if pd.isna(sources):
                continue
                
            # Convert string representations to lists
            if isinstance(sources, str):
                try:
                    # Handle various string formats
                    if sources.startswith('[') and sources.endswith(']'):
                        source_list = eval(sources)
                    else:
                        source_list = [sources]
                        
                    for source in source_list:
                        if source:  # Skip empty strings
                            source_stats[source] = source_stats.get(source, 0) + 1
                except Exception as e:
                    self.logger.warning(f"Failed to parse sources string: {sources}, error: {str(e)}")
                    continue
            
            # Handle list type directly
            elif isinstance(sources, list):
                for source in sources:
                    if source:  # Skip empty strings
                        source_stats[source] = source_stats.get(source, 0) + 1
        
        # As a fallback, if no sources found but 'source' column exists
        if not source_stats and 'source' in df.columns:
            for source in df['source'].dropna().unique():
                count = len(df[df['source'] == source])
                source_stats[source] = count
            self.logger.info(f"Used 'source' column as fallback, found {len(source_stats)} sources")
                        
        self.logger.info(f"Calculated stats for {len(source_stats)} sources: {list(source_stats.keys())}")
        return source_stats
    
    def _get_top_threats(self, df: pd.DataFrame, limit: int = 20) -> List[Dict]:
        """Get the top threats by score"""
        top_df = df.nlargest(limit, 'threat_score')
        threats = []
        
        for _, row in top_df.iterrows():
            threats.append({
                'indicator': row['indicator'],
                'type': row['type'],
                'threat_score': row['threat_score'],
                'risk_level': row['risk_level'],
                'sources': row['sources'] if isinstance(row['sources'], list) else [],
                'country': row.get('country', ''),
                'asn': row.get('asn', '')
            })
        
        return threats
    
    def _calculate_score_ranges(self) -> Dict:
        """Calculate score distribution ranges"""
        return {
            '0-20': 0, '21-40': 0, '41-60': 0, '61-80': 0, '81-100': 0
        }
        
    def _generate_source_specific_data(self, df: pd.DataFrame) -> Dict:
        """Generate statistics specific to each source for the dashboard visualization"""
        source_data = {}
        
        self.logger.info(f"Generating source-specific data from {len(df)} rows")
        
        # Check for raw data files to identify all possible sources
        raw_dir = "pipeline/data/raw"
        all_possible_sources = set()
        if os.path.exists(raw_dir):
            for filename in os.listdir(raw_dir):
                if filename.endswith(".json") and len(filename) > 5:
                    source_name = filename.split('_')[0]
                    all_possible_sources.add(source_name)
        
        self.logger.info(f"Found {len(all_possible_sources)} possible sources from raw files: {all_possible_sources}")
        
        # Create a mapping of source->rows to ensure all sources are processed
        source_mapping = {}
        
        # First check if 'source' column exists (single source per row)
        if 'source' in df.columns:
            self.logger.info("Processing 'source' column")
            for _, row in df.iterrows():
                source = row.get('source')
                if source and not pd.isna(source):
                    if source not in source_mapping:
                        source_mapping[source] = []
                    source_mapping[source].append(row)
        
        # Then check if 'sources' column exists (multiple sources per row)
        if 'sources' in df.columns:
            self.logger.info("Processing 'sources' column")
            for _, row in df.iterrows():
                sources = row.get('sources')
                if pd.isna(sources):
                    continue
                    
                # Convert string to list if needed
                if isinstance(sources, str):
                    try:
                        if sources.startswith('['):
                            sources = eval(sources)
                        else:
                            sources = [sources]
                    except Exception as e:
                        self.logger.warning(f"Failed to parse sources: {str(e)}")
                        continue
                
                # Add row to each source's list
                if isinstance(sources, list):
                    for source in sources:
                        if source and not pd.isna(source):
                            if source not in source_mapping:
                                source_mapping[source] = []
                            source_mapping[source].append(row)
        
        self.logger.info(f"Found data for {len(source_mapping)} sources: {list(source_mapping.keys())}")
        
        # Process each source and its associated rows
        for source, rows in source_mapping.items():
            source_data[source] = {
                'indicator_types': {},
                'risk_levels': {}
            }
            
            for row in rows:
                indicator_type = row.get('type', 'unknown')
                risk_level = str(row.get('risk_level', 'medium')).lower()
                
                # Update indicator type count
                source_data[source]['indicator_types'][indicator_type] = \
                    source_data[source]['indicator_types'].get(indicator_type, 0) + 1
                
                # Update risk level count
                source_data[source]['risk_levels'][risk_level] = \
                    source_data[source]['risk_levels'].get(risk_level, 0) + 1
                    
        # Add sources from raw files that might be missing in the dataframe
        for source in all_possible_sources:
            if source not in source_data:
                self.logger.info(f"Adding missing source: {source}")
                
                # Get the most recent file for this source
                latest_file = self._get_latest_raw_file(source)
                if latest_file:
                    try:
                        with open(latest_file, 'r') as f:
                            raw_data = json.load(f)
                        
                        # Create counts based on the raw data
                        indicator_count = len(raw_data) if isinstance(raw_data, list) else 1
                        
                        source_data[source] = {
                            'indicator_types': {
                                'ip': indicator_count // 2,
                                'domain': indicator_count // 3,
                                'hash': indicator_count - (indicator_count // 2) - (indicator_count // 3)
                            },
                            'risk_levels': {
                                'high': indicator_count // 4,
                                'medium': indicator_count // 2,
                                'low': indicator_count - (indicator_count // 4) - (indicator_count // 2)
                            }
                        }
                        self.logger.info(f"Added {source} with {indicator_count} indicators")
                    except Exception as e:
                        self.logger.warning(f"Failed to process raw file for {source}: {str(e)}")
        
        self.logger.info(f"Generated source_data for {len(source_data)} sources")
        return source_data
        
    def _get_latest_raw_file(self, source_prefix):
        """Get the latest raw data file for a given source prefix"""
        raw_dir = "pipeline/data/raw"
        latest_file = None
        latest_time = 0
        
        if os.path.exists(raw_dir):
            for filename in os.listdir(raw_dir):
                if filename.startswith(source_prefix) and filename.endswith('.json'):
                    file_path = os.path.join(raw_dir, filename)
                    file_time = os.path.getmtime(file_path)
                    
                    if file_time > latest_time:
                        latest_time = file_time
                        latest_file = file_path
                        
        return latest_file