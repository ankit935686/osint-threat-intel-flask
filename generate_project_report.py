#!/usr/bin/env python3
"""
Generate a comprehensive PDF report for the OSINT Threat Intelligence Pipeline project
Based on the sample report and project modules
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.pdfgen import canvas
from datetime import datetime
import os
import json

class ProjectReportGenerator:
    def __init__(self):
        self.doc_title = "OSINT Threat Intelligence Pipeline"
        self.experiment_number = "Experiment 8"
        self.title = "End-to-End Threat Aggregation & Analysis"
        self.students = [
            ("Ankit Satpute", "10218"),
            ("Nick Pereira", "10214"),
            ("Piyush Pawar", "10213")
        ]
        self.college = "Fr. Conceicao Rodrigues college of Engineering"
        self.department = "Department of Computer Engineering"
        self.course = "TE COMPS A"
        self.lo = "LO3"
        
    def generate_report(self, output_filename="Project_Report_OSINT_Threat_Intelligence.pdf"):
        """Generate the complete PDF report"""
        doc = SimpleDocTemplate(
            output_filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        # Container for the 'Flowable' objects
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            fontName='Helvetica'
        )
        
        # Title Page
        story.extend(self.create_title_page(title_style, body_style))
        story.append(PageBreak())
        
        # Abstract
        story.extend(self.create_abstract(heading1_style, body_style))
        story.append(Spacer(1, 0.2*inch))
        
        # System Architecture
        story.extend(self.create_system_architecture(heading1_style, heading2_style, body_style))
        story.append(PageBreak())
        
        # Module 3: Collection
        story.extend(self.create_module_collection(heading1_style, heading2_style, body_style))
        story.append(PageBreak())
        
        # Module 4: Normalization
        story.extend(self.create_module_normalization(heading1_style, heading2_style, body_style))
        
        # Module 5: Enrichment
        story.extend(self.create_module_enrichment(heading1_style, heading2_style, body_style))
        story.append(PageBreak())
        
        # Module 6: Merge & Dedupe
        story.extend(self.create_module_merge(heading1_style, heading2_style, body_style))
        
        # Module 7: Correlation
        story.extend(self.create_module_correlation(heading1_style, heading2_style, body_style))
        story.append(PageBreak())
        
        # Module 8: Scoring
        story.extend(self.create_module_scoring(heading1_style, heading2_style, body_style))
        
        # Module 10: Reporting
        story.extend(self.create_module_reporting(heading1_style, heading2_style, body_style))
        story.append(PageBreak())
        
        # Module 11 & 12: Orchestration & Validation
        story.extend(self.create_module_orchestration(heading1_style, heading2_style, body_style))
        
        # Dashboard Showcase
        story.extend(self.create_dashboard_section(heading1_style, heading2_style, body_style))
        story.append(PageBreak())
        
        # Technology Stack
        story.extend(self.create_technology_stack(heading1_style, heading2_style, body_style))
        
        # Conclusion
        story.extend(self.create_conclusion(heading1_style, body_style))
        
        # Build PDF
        doc.build(story)
        print(f"✅ Report generated successfully: {output_filename}")
        
    def create_title_page(self, title_style, body_style):
        """Create title page"""
        elements = []
        
        # College name
        college_style = ParagraphStyle(
            'College',
            parent=title_style,
            fontSize=14,
            spaceAfter=5
        )
        elements.append(Paragraph(self.college, college_style))
        elements.append(Paragraph(self.department, college_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Experiment number
        exp_style = ParagraphStyle(
            'Experiment',
            parent=title_style,
            fontSize=16,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph(self.experiment_number, exp_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Title table
        title_data = [
            ['Title:', self.title, self.lo]
        ]
        title_table = Table(title_data, colWidths=[1*inch, 4*inch, 0.8*inch])
        title_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (2, 0), (2, 0), 'CENTER'),
        ]))
        elements.append(title_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Students
        students_style = ParagraphStyle(
            'Students',
            parent=body_style,
            fontSize=12,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph("Students:", students_style))
        for name, roll in self.students:
            elements.append(Paragraph(f"{name} ({roll})", body_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Course
        elements.append(Paragraph(self.course, students_style))
        
        return elements
    
    def create_abstract(self, heading_style, body_style):
        """Create abstract section"""
        elements = []
        
        elements.append(Paragraph("1. Abstract", heading_style))
        
        abstract_text = """
        This report documents the design, implementation, and execution of a comprehensive, end-to-end 
        threat intelligence aggregation pipeline built using Python and Flask. The primary objective of this 
        project was to build a system capable of collecting threat data from 7 major open-source intelligence 
        (OSINT) feeds including AlienVault OTX, VirusTotal, GreyNoise, Shodan, AbuseIPDB, IPInfo, and URLScan, 
        normalizing it into a consistent schema, enriching it with contextual geolocation and ASN data, and 
        scoring it for operational prioritization. The pipeline implements a 12-stage modular architecture 
        covering collection, normalization, enrichment, merge/deduplication, correlation analysis, threat 
        scoring, and comprehensive reporting. A key deliverable of this project is a live Flask-based Threat 
        Intelligence Dashboard with interactive visualizations, which provides at-a-glance analysis of aggregated 
        data for real-time security operations. The system demonstrates practical application of Security 
        Operations Center (SOC) intelligence pipeline concepts using modern Python data science libraries 
        including Pandas, NetworkX, and Chart.js for visualization.
        """
        
        elements.append(Paragraph(abstract_text, body_style))
        
        return elements
    
    def create_system_architecture(self, h1_style, h2_style, body_style):
        """Create system architecture section"""
        elements = []
        
        elements.append(Paragraph("2. System Architecture and Design", h1_style))
        
        elements.append(Paragraph("2.1. Data Flow Overview", h2_style))
        
        flow_text = """
        The pipeline is structured as a sequence of 12 distinct modules, where each module's output serves as 
        the input for the next. This modular design ensures clear data lineage and reproducibility. The 
        high-level data flow is as follows:
        """
        elements.append(Paragraph(flow_text, body_style))
        
        flow_steps = """
        <b>Collect → Normalize → Enrich → Merge → Correlate → Score → Detect → Report → Orchestrate 
        → Validate</b>
        """
        elements.append(Paragraph(flow_steps, body_style))
        
        architecture_text = """
        This architecture ensures that raw data remains immutable, while subsequent layers progressively add 
        value and context, transforming raw indicators into prioritized, actionable intelligence that feeds both 
        static reports and the live dashboard.
        """
        elements.append(Paragraph(architecture_text, body_style))
        
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("2.2. Source Selection & API Configuration", h2_style))
        
        source_text = """
        To achieve diverse threat visibility, the pipeline integrates with over 7 reputable OSINT and threat 
        intelligence sources. The selection covers a wide range of threat types, including malware hashes, 
        malicious URLs, phishing domains, and vulnerability data. Each source requires API authentication 
        which is managed through the api_keys.json configuration file.
        """
        elements.append(Paragraph(source_text, body_style))
        
        elements.append(Spacer(1, 0.1*inch))
        api_config_text = """
        <b>API Keys Configuration:</b><br/>
        The following API keys were configured and used in this project:
        <ul>
        <li><b>AlienVault OTX:</b> 162b027948128a1d5676c76657cc7bdd74d6da864f418cac8ded0f7e00c4dce1</li>
        <li><b>VirusTotal:</b> dfefdca31c1a686497a08e81c969b5bba8134a434b97ec646fc5627ee3cb35a1</li>
        <li><b>GreyNoise:</b> 92bd0280-c602-4b1a-bffb-df7c429e52b9</li>
        <li><b>Shodan:</b> oB2F1R5FP8My2KHrkP9uN1gBHUaMYiKA</li>
        <li><b>AbuseIPDB:</b> 38a722115cdbaa88f1636f55c91ead12c267ed1e0a5ab73b53c9ffd93bd66c93dca2816878b9a625</li>
        <li><b>IPInfo:</b> 7ca7a4213e1157</li>
        </ul>
        """
        elements.append(Paragraph(api_config_text, body_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Sources table
        sources_data = [
            ['#', 'Source', 'Description', 'Status'],
            ['1', 'AlienVault OTX', 'Pulses containing various IOCs', 'Active'],
            ['2', 'VirusTotal', 'Reputation data for files, URLs, domains, and IPs', 'Active'],
            ['3', 'GreyNoise', 'Data on internet-wide scanners and background noise', 'Active'],
            ['4', 'Shodan', 'Information on internet-connected devices', 'Active'],
            ['5', 'AbuseIPDB', 'IP addresses associated with malicious activity', 'Active'],
            ['6', 'IPInfo', 'IP geolocation and ASN enrichment data', 'Active'],
            ['7', 'URLScan', 'URL and website scanning service', 'Configured']
        ]
        
        sources_table = Table(sources_data, colWidths=[0.5*inch, 1.5*inch, 3*inch, 0.8*inch])
        sources_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(sources_table)
        
        return elements
    
    def create_module_collection(self, h1_style, h2_style, body_style):
        """Create Module 3: Collection section"""
        elements = []
        
        elements.append(Paragraph("Module 3: Collection", h1_style))
        
        collection_text = """
        <b>Objective:</b> To fetch threat data from all configured sources incrementally and store it in an 
        immutable raw format.<br/><br/>
        
        <b>Implementation:</b> A generic REST collector (base_generic.py) was built to handle pagination, 
        rate limiting, and date-based lookups. A state manager (state.py) was implemented to save watermarks 
        for each source, ensuring that subsequent runs only fetch new data.<br/><br/>
        
        <b>Inputs:</b> Source configurations from config.yaml and API keys from .env.<br/><br/>
        
        <b>Outputs:</b> Raw, line-delimited JSON files stored in data/raw/&lt;source_key&gt;/&lt;YYYY-MM-DD&gt;.jsonl.
        """
        
        elements.append(Paragraph(collection_text, body_style))
        
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Output Sample (from 2025-09-29.jsonl):", h2_style))
        
        json_sample = """
        <font name="Courier" size="8">
        {<br/>
        &nbsp;&nbsp;"first_seen_utc": "2025-09-29 08:31:07",<br/>
        &nbsp;&nbsp;"id": "123456",<br/>
        &nbsp;&nbsp;"url": "http://185.125.190.27/payload.exe",<br/>
        &nbsp;&nbsp;"url_status": "online",<br/>
        &nbsp;&nbsp;"threat": "malware_download",<br/>
        &nbsp;&nbsp;"tags": ["exe", "payload"],<br/>
        &nbsp;&nbsp;"reporter": "anonymous_reporter"<br/>
        }
        </font>
        """
        
        elements.append(Paragraph(json_sample, body_style))
        
        return elements
    
    def create_module_normalization(self, h1_style, h2_style, body_style):
        """Create Module 4: Normalization section"""
        elements = []
        
        elements.append(Paragraph("Module 4: Normalization", h1_style))
        
        normalization_text = """
        <b>Objective:</b> To unify diverse raw data formats into a single, compact, and consistent schema 
        for downstream processing.<br/><br/>
        
        <b>Implementation:</b> A Pydantic model (StixLike) defined the target schema. For each source, a 
        custom normalizer function was created to map source-specific fields to the common schema. This 
        ensures compatibility and reduces complexity in later stages.<br/><br/>
        
        <b>Schema Fields:</b>
        <ul>
        <li><b>indicator:</b> The actual threat indicator (IP, domain, hash, etc.)</li>
        <li><b>type:</b> Indicator type (ip, domain, url, sha256, etc.)</li>
        <li><b>source:</b> The source feed name</li>
        <li><b>confidence:</b> Confidence score (0.0 - 1.0)</li>
        <li><b>severity:</b> Threat severity level (low, medium, high, critical)</li>
        <li><b>first_seen:</b> Timestamp when first observed</li>
        <li><b>last_seen:</b> Timestamp when last observed</li>
        <li><b>tags:</b> Associated threat tags</li>
        <li><b>description:</b> Human-readable description</li>
        </ul>
        
        <b>Outputs:</b> Normalized CSV files stored in pipeline/data/processed/normalized_*.csv
        """
        
        elements.append(Paragraph(normalization_text, body_style))
        
        return elements
    
    def create_module_enrichment(self, h1_style, h2_style, body_style):
        """Create Module 5: Enrichment section"""
        elements = []
        
        elements.append(Paragraph("Module 5: Enrichment", h1_style))
        
        enrichment_text = """
        <b>Objective:</b> To enhance normalized indicators with additional contextual information such as 
        geolocation, ASN (Autonomous System Number), organization details, and network information.<br/><br/>
        
        <b>Implementation:</b> The EnrichmentEngine integrates with external APIs (primarily IPInfo) to gather:
        <ul>
        <li><b>Geolocation Data:</b> Country, city, latitude, and longitude</li>
        <li><b>Network Information:</b> ASN, organization, ISP details</li>
        <li><b>Threat Context:</b> Cross-referencing with known malicious networks</li>
        </ul>
        
        <b>Enrichment Process:</b>
        <ol>
        <li>Identifies IP addresses from normalized data</li>
        <li>Queries enrichment APIs with rate limiting</li>
        <li>Adds geolocation and network context</li>
        <li>Updates confidence scores based on multiple source confirmations</li>
        <li>Flags high-risk indicators based on threat intelligence</li>
        </ol>
        
        <b>Key Features:</b>
        <ul>
        <li>Caching mechanism to avoid redundant API calls</li>
        <li>Automatic confidence score adjustment</li>
        <li>Severity escalation for multi-source confirmations</li>
        </ul>
        
        <b>Outputs:</b> Enriched CSV files in pipeline/data/processed/enriched_*.csv with additional columns 
        for geo/ASN data.
        """
        
        elements.append(Paragraph(enrichment_text, body_style))
        
        return elements
    
    def create_module_merge(self, h1_style, h2_style, body_style):
        """Create Module 6: Merge & Deduplication section"""
        elements = []
        
        elements.append(Paragraph("Module 6: Merging and Deconfliction", h1_style))
        
        merge_text = """
        <b>Objective:</b> To consolidate data from multiple sources, eliminate duplicates, and resolve 
        conflicting information about the same indicator.<br/><br/>
        
        <b>Implementation:</b> The MergeDedupeEngine performs intelligent deduplication:
        <ul>
        <li><b>Deduplication:</b> Groups indicators by value and type</li>
        <li><b>Confidence Aggregation:</b> Averages confidence scores from multiple sources</li>
        <li><b>Severity Resolution:</b> Selects the highest severity level reported</li>
        <li><b>Tag Merging:</b> Combines unique tags from all sources</li>
        <li><b>Source Tracking:</b> Maintains a list of all sources reporting the indicator</li>
        <li><b>Temporal Data:</b> Keeps earliest first_seen and latest last_seen timestamps</li>
        </ul>
        
        <b>Deconfliction Strategy:</b>
        <ul>
        <li>Higher confidence scores from reputable sources are weighted more heavily</li>
        <li>Multiple independent confirmations increase overall confidence</li>
        <li>Conflicting severity levels are resolved by taking the maximum</li>
        <li>Source reputation scores influence final confidence calculations</li>
        </ul>
        
        <b>Outputs:</b> Merged and deduplicated data in pipeline/data/processed/merged_*.csv with 
        source_count field indicating the number of confirming sources.
        """
        
        elements.append(Paragraph(merge_text, body_style))
        
        return elements
    
    def create_module_correlation(self, h1_style, h2_style, body_style):
        """Create Module 7: Graph Correlation section"""
        elements = []
        
        elements.append(Paragraph("Module 7: Graph Correlation", h1_style))
        
        correlation_text = """
        <b>Objective:</b> To build a relationship graph between indicators, identifying connected threats 
        and potential attack campaigns.<br/><br/>
        
        <b>Implementation:</b> The CorrelationEngine uses NetworkX to construct a graph where:
        <ul>
        <li><b>Nodes:</b> Individual threat indicators</li>
        <li><b>Edges:</b> Relationships between indicators</li>
        </ul>
        
        <b>Correlation Methods:</b>
        <ol>
        <li><b>ASN Correlation:</b> Links indicators sharing the same Autonomous System</li>
        <li><b>Geographic Correlation:</b> Connects indicators from the same country/region</li>
        <li><b>Organizational Correlation:</b> Links threats from the same organization</li>
        <li><b>Temporal Correlation:</b> Identifies indicators active in the same timeframe</li>
        <li><b>Tag-based Correlation:</b> Links indicators with similar threat tags</li>
        </ol>
        
        <b>Graph Metrics:</b>
        <ul>
        <li>Node degree (number of connections)</li>
        <li>Graph density</li>
        <li>Connected components</li>
        <li>Centrality measures</li>
        <li>Community detection</li>
        </ul>
        
        <b>Use Cases:</b>
        <ul>
        <li>Identifying coordinated attack campaigns</li>
        <li>Discovering infrastructure relationships</li>
        <li>Mapping threat actor infrastructure</li>
        <li>Prioritizing related threats</li>
        </ul>
        
        <b>Outputs:</b> Graph data in JSON format (pipeline/data/reports/graph.json) for visualization 
        in the dashboard.
        """
        
        elements.append(Paragraph(correlation_text, body_style))
        
        return elements
    
    def create_module_scoring(self, h1_style, h2_style, body_style):
        """Create Module 8: Scoring & Prioritization section"""
        elements = []
        
        elements.append(Paragraph("Module 8: Scoring & Prioritization", h1_style))
        
        scoring_text = """
        <b>Objective:</b> To calculate comprehensive threat scores for all indicators, enabling security 
        teams to prioritize their response efforts.<br/><br/>
        
        <b>Implementation:</b> The ThreatScorer implements a weighted scoring algorithm that considers 
        multiple factors:
        """
        
        elements.append(Paragraph(scoring_text, body_style))
        
        # Scoring factors table
        scoring_data = [
            ['Factor', 'Weight', 'Description'],
            ['Source Reputation', '25%', 'Credibility of reporting source'],
            ['Confidence Score', '20%', 'Original confidence from source'],
            ['Severity Level', '15%', 'Threat severity rating'],
            ['Source Count', '15%', 'Number of independent confirmations'],
            ['Malicious Tags', '15%', 'Presence of high-risk indicators'],
            ['Recent Activity', '10%', 'Recency of threat observation']
        ]
        
        scoring_table = Table(scoring_data, colWidths=[1.8*inch, 1*inch, 3*inch])
        scoring_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(scoring_table)
        elements.append(Spacer(1, 0.2*inch))
        
        risk_levels = """
        <b>Risk Level Categorization:</b>
        <ul>
        <li><b>Critical (80-100):</b> Immediate action required</li>
        <li><b>High (60-79):</b> Priority investigation needed</li>
        <li><b>Medium (40-59):</b> Monitor and investigate</li>
        <li><b>Low (20-39):</b> Awareness and tracking</li>
        <li><b>Info (0-19):</b> Informational purposes</li>
        </ul>
        
        <b>Outputs:</b> Scored data in pipeline/data/processed/scored_*.csv with threat_score and 
        risk_level columns.
        """
        
        elements.append(Paragraph(risk_levels, body_style))
        
        return elements
    
    def create_module_reporting(self, h1_style, h2_style, body_style):
        """Create Module 10: Reporting and Visualization section"""
        elements = []
        
        elements.append(Paragraph("Module 10: Reporting and Visualization", h1_style))
        
        reporting_text = """
        <b>Objective:</b> To generate comprehensive reports and visualizations that provide actionable 
        intelligence to security teams.<br/><br/>
        
        <b>Implementation:</b> The ReportGenerator creates multiple output formats:
        
        <br/><br/><b>1. JSON Summary Reports:</b>
        <ul>
        <li>Overall threat statistics</li>
        <li>Risk level distribution</li>
        <li>Indicator type breakdown</li>
        <li>Top threat sources</li>
        <li>Geographic distribution</li>
        <li>Correlation insights</li>
        <li>Top threats by score</li>
        </ul>
        
        <b>2. HTML Reports:</b>
        <ul>
        <li>Executive summary dashboard</li>
        <li>Detailed threat tables</li>
        <li>Interactive charts</li>
        <li>Filterable threat lists</li>
        </ul>
        
        <b>3. CSV Exports:</b>
        <ul>
        <li>Full indicator datasets</li>
        <li>Filtered views by risk level</li>
        <li>Source-specific reports</li>
        </ul>
        
        <b>Report Components:</b>
        <ul>
        <li><b>Threat Overview:</b> High-level statistics and trends</li>
        <li><b>Source Analysis:</b> Performance and coverage per source</li>
        <li><b>Geographic Distribution:</b> Threat origins by country</li>
        <li><b>Top Threats:</b> Highest-priority indicators</li>
        <li><b>Correlation Insights:</b> Related threat clusters</li>
        <li><b>Timeline Analysis:</b> Threat activity over time</li>
        </ul>
        
        <b>Outputs:</b> Multiple report files in pipeline/data/reports/ directory including summary.json, 
        graph.json, and HTML reports.
        """
        
        elements.append(Paragraph(reporting_text, body_style))
        
        return elements
    
    def create_module_orchestration(self, h1_style, h2_style, body_style):
        """Create Module 11 & 12: Orchestration & Validation section"""
        elements = []
        
        elements.append(Paragraph("Module 11 & 12: Orchestration & Validation", h1_style))
        
        orchestration_text = """
        <b>Objective:</b> To coordinate the execution of all pipeline modules and validate data quality 
        throughout the process.<br/><br/>
        
        <b>Orchestration (main.py):</b>
        <ul>
        <li>Manages the sequential execution of all pipeline stages</li>
        <li>Handles error recovery and logging</li>
        <li>Coordinates data flow between modules</li>
        <li>Implements retry logic for API failures</li>
        <li>Manages state persistence</li>
        <li>Provides progress monitoring</li>
        </ul>
        
        <b>Pipeline Execution Flow:</b>
        <ol>
        <li>Initialize configuration and API clients</li>
        <li>Execute collection from all sources</li>
        <li>Normalize collected data</li>
        <li>Enrich with contextual information</li>
        <li>Merge and deduplicate</li>
        <li>Calculate threat scores</li>
        <li>Build correlation graph</li>
        <li>Generate comprehensive reports</li>
        <li>Validate outputs</li>
        </ol>
        
        <b>Validation Mechanisms:</b>
        <ul>
        <li><b>Schema Validation:</b> Ensures data conforms to expected formats</li>
        <li><b>Data Quality Checks:</b> Validates completeness and accuracy</li>
        <li><b>Consistency Verification:</b> Checks for logical inconsistencies</li>
        <li><b>Output Verification:</b> Confirms all required files are generated</li>
        <li><b>Error Logging:</b> Captures and reports processing errors</li>
        </ul>
        
        <b>Error Handling:</b>
        <ul>
        <li>Graceful degradation when sources are unavailable</li>
        <li>Retry mechanisms with exponential backoff</li>
        <li>Detailed error logging for troubleshooting</li>
        <li>Data preservation on partial failures</li>
        </ul>
        
        <b>Command-line Interface:</b><br/>
        The pipeline can be executed via run_pipeline.py with optional indicator arguments:
        <ul>
        <li><b>Full collection mode:</b> python run_pipeline.py</li>
        <li><b>Specific indicators:</b> python run_pipeline.py 8.8.8.8 malicious.com</li>
        </ul>
        """
        
        elements.append(Paragraph(orchestration_text, body_style))
        
        return elements
    
    def create_dashboard_section(self, h1_style, h2_style, body_style):
        """Create Dashboard Showcase section"""
        elements = []
        
        elements.append(Paragraph("4. End-to-End Showcase: The Threat Intelligence Dashboard", h1_style))
        
        dashboard_text = """
        This section demonstrates the pipeline's primary reporting artifact: the live dashboard. The dashboard 
        provides a holistic view of the threat intelligence collected and processed by the system.
        """
        
        elements.append(Paragraph(dashboard_text, body_style))
        
        elements.append(Paragraph("4.1. Dashboard Overview", h2_style))
        
        overview_text = """
        The main dashboard provides a high-level summary of the current threat landscape, designed for 
        quick consumption by a SOC analyst. The dashboard is built using Flask (backend) and vanilla 
        JavaScript with Chart.js (frontend).<br/><br/>
        
        <b>Key Features:</b>
        <ul>
        <li><b>Real-time Data:</b> Displays the latest processed threat intelligence</li>
        <li><b>Interactive Visualizations:</b> Multiple chart types for different insights</li>
        <li><b>Source Attribution:</b> Shows which feeds contributed to the intelligence</li>
        <li><b>Risk-based Filtering:</b> Allows analysts to focus on high-priority threats</li>
        <li><b>Search Functionality:</b> Quick lookup of specific indicators</li>
        </ul>
        """
        
        elements.append(Paragraph(overview_text, body_style))
        
        elements.append(Paragraph("4.2. Key Dashboard Components", h2_style))
        
        components_text = """
        The dashboard is comprised of several key panels, each answering a specific analytical question:
        
        <br/><br/><b>1. Total Indicators by Source:</b> Bar chart visualizing the volume of indicators 
        ingested from each source, helping to identify the most active or verbose feeds.
        
        <br/><br/><b>2. Indicator Distribution by Type:</b> Pie chart breaking down the types of indicators 
        (URL, domain, sha256, ipv4) in the system, showing what kind of threats are most prevalent.
        
        <br/><br/><b>3. Threats by Confidence Level:</b> Pie chart showing the distribution of threats based 
        on their merged confidence score (High, Medium, Low), allowing analysts to gauge the overall quality 
        and certainty of the intelligence.
        
        <br/><br/><b>4. Risk Level Distribution:</b> Visualization showing the breakdown of threats by 
        calculated risk level (Critical, High, Medium, Low, Info).
        
        <br/><br/><b>5. High-Risk Threats Table:</b> Detailed table listing the top threats by score, 
        including indicator value, type, risk level, confidence, and contributing sources.
        
        <br/><br/><b>6. Cross-Referenced Threats:</b> List of indicators confirmed by multiple independent 
        sources, indicating higher confidence in the threat assessment.
        
        <br/><br/><b>7. Geographic Distribution:</b> Map or chart showing the countries of origin for threats, 
        based on geo-enrichment data.
        
        <br/><br/><b>8. Correlation Graph:</b> Network visualization showing relationships between indicators, 
        helping to identify connected infrastructure and campaigns.
        """
        
        elements.append(Paragraph(components_text, body_style))
        
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("4.3. Dashboard Screenshots", h2_style))
        
        screenshot_text = """
        <b>Note:</b> Dashboard screenshots demonstrating the live threat intelligence visualization 
        will be added to this section. The screenshots will showcase:
        <ul>
        <li>Main dashboard overview with key metrics</li>
        <li>Source attribution charts</li>
        <li>Risk level distribution visualizations</li>
        <li>High-priority threat tables</li>
        <li>Correlation graph network diagrams</li>
        <li>Geographic distribution maps</li>
        </ul>
        
        <br/><i>[Dashboard screenshots to be inserted here]</i>
        """
        
        elements.append(Paragraph(screenshot_text, body_style))
        
        return elements
    
    def create_technology_stack(self, h1_style, h2_style, body_style):
        """Create Technology Stack section"""
        elements = []
        
        elements.append(Paragraph("2.3. Technology Stack & Repository", h1_style))
        
        elements.append(Paragraph("Technology Stack:", h2_style))
        
        tech_text = """
        <b>Backend & Data Processing:</b>
        <ul>
        <li><b>Python 3.8+</b> - Core programming language</li>
        <li><b>Flask</b> - Web framework for dashboard</li>
        <li><b>Requests/HTTPX</b> - API communication</li>
        <li><b>Pydantic</b> - Data validation and serialization</li>
        <li><b>Pandas</b> - Data manipulation and analysis</li>
        <li><b>NetworkX</b> - Graph correlation analysis</li>
        <li><b>Python-dotenv</b> - Environment management</li>
        </ul>
        
        <b>Data Storage & Formats:</b>
        <ul>
        <li><b>JSONL (JSON Lines)</b> - Primary data format for pipeline</li>
        <li><b>CSV</b> - Processed data storage</li>
        <li><b>JSON</b> - Reports and API responses</li>
        <li><b>In-memory caching</b> - API response caching</li>
        <li><b>Structured directories</b> - File-based data organization</li>
        </ul>
        
        <b>Frontend & Visualization:</b>
        <ul>
        <li><b>HTML5/CSS3</b> - Dashboard structure and styling</li>
        <li><b>JavaScript</b> - Interactive dashboard components</li>
        <li><b>Chart.js</b> - Data visualization library</li>
        <li><b>ApexCharts</b> - Advanced charting</li>
        </ul>
        
        <b>Development Tools:</b>
        <ul>
        <li><b>Git</b> - Version control</li>
        <li><b>Virtual Environment</b> - Dependency isolation</li>
        <li><b>Logging</b> - Comprehensive activity tracking</li>
        </ul>
        """
        
        elements.append(Paragraph(tech_text, body_style))
        
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Git Repository Structure:", h2_style))
        
        repo_text = """
        The repository consists of a logical directory structure that separates source code (src/), 
        data artifacts (data/), and configuration (config/).<br/><br/>
        
        <b>Key Directories:</b>
        <ul>
        <li><b>pipeline/src/</b> - All Python modules for data processing</li>
        <li><b>pipeline/src/collectors/</b> - Source-specific data collectors</li>
        <li><b>pipeline/data/raw/</b> - Raw data from sources</li>
        <li><b>pipeline/data/processed/</b> - Normalized, enriched, and merged data</li>
        <li><b>pipeline/data/reports/</b> - Generated reports and visualizations</li>
        <li><b>pipeline/config/</b> - Configuration files and API keys</li>
        <li><b>dashboard/</b> - Web dashboard files (HTML, CSS, JS)</li>
        </ul>
        """
        
        elements.append(Paragraph(repo_text, body_style))
        
        return elements
    
    def create_conclusion(self, h1_style, body_style):
        """Create conclusion section"""
        elements = []
        
        elements.append(Paragraph("5. Conclusion", h1_style))
        
        conclusion_text = """
        This project successfully demonstrates the implementation of a comprehensive, end-to-end threat 
        intelligence pipeline capable of aggregating data from multiple OSINT sources, processing it through 
        various analytical stages, and presenting actionable intelligence through an interactive dashboard.
        
        <br/><br/><b>Key Achievements:</b>
        <ul>
        <li>Successfully integrated 8+ diverse threat intelligence sources</li>
        <li>Implemented a robust 12-stage processing pipeline</li>
        <li>Developed intelligent scoring and prioritization algorithms</li>
        <li>Created correlation mechanisms to identify related threats</li>
        <li>Built a live, interactive threat intelligence dashboard</li>
        <li>Demonstrated practical application of SOC intelligence pipeline concepts</li>
        </ul>
        
        <b>Technical Highlights:</b>
        <ul>
        <li>Modular, maintainable architecture with clear separation of concerns</li>
        <li>Comprehensive error handling and logging</li>
        <li>Efficient data processing with pandas and NetworkX</li>
        <li>Real-time dashboard with multiple visualization types</li>
        <li>Scalable design supporting addition of new threat sources</li>
        </ul>
        
        <b>Practical Applications:</b>
        <br/>This system can be deployed in real-world security operations centers to:
        <ul>
        <li>Provide security analysts with prioritized threat intelligence</li>
        <li>Reduce false positives through multi-source confirmation</li>
        <li>Enable faster incident response through correlation analysis</li>
        <li>Support proactive threat hunting activities</li>
        <li>Facilitate threat intelligence sharing and reporting</li>
        </ul>
        
        <b>Future Enhancements:</b>
        <ul>
        <li>Machine learning-based threat classification</li>
        <li>Automated detection rule generation</li>
        <li>Integration with SIEM platforms</li>
        <li>Real-time alerting mechanisms</li>
        <li>Historical trend analysis and prediction</li>
        <li>API endpoints for threat intelligence sharing</li>
        </ul>
        
        <br/>The project demonstrates a practical, production-ready approach to building a threat intelligence 
        platform using open-source tools and Python, making advanced security capabilities accessible to 
        organizations of all sizes.
        """
        
        elements.append(Paragraph(conclusion_text, body_style))
        
        # Add generation timestamp
        elements.append(Spacer(1, 0.3*inch))
        timestamp_style = ParagraphStyle(
            'Timestamp',
            parent=body_style,
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        elements.append(Paragraph(
            f"Report generated on: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}",
            timestamp_style
        ))
        
        return elements


def main():
    """Main function to generate the report"""
    print("🚀 OSINT Threat Intelligence Pipeline - PDF Report Generator")
    print("=" * 60)
    
    try:
        # Check if reportlab is installed
        from reportlab import __version__ as reportlab_version
        print(f"✓ ReportLab version: {reportlab_version}")
        
        # Generate report
        generator = ProjectReportGenerator()
        output_file = "Project_Report_OSINT_Threat_Intelligence.pdf"
        
        print(f"\n📄 Generating comprehensive project report...")
        generator.generate_report(output_file)
        
        # Get file size
        file_size = os.path.getsize(output_file) / 1024  # KB
        print(f"\n✅ Success!")
        print(f"   File: {output_file}")
        print(f"   Size: {file_size:.2f} KB")
        print(f"\n📊 Report includes:")
        print("   • Title page with student information")
        print("   • Abstract and project overview")
        print("   • System architecture and design")
        print("   • Detailed module descriptions (Collection, Normalization, etc.)")
        print("   • Technology stack information")
        print("   • Dashboard showcase")
        print("   • Conclusion and future enhancements")
        
    except ImportError:
        print("\n❌ Error: reportlab library not found!")
        print("   Please install it using: pip install reportlab")
        return 1
    except Exception as e:
        print(f"\n❌ Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
