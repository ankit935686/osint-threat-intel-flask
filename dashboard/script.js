// OSINT Threat Intelligence Dashboard
class ThreatDashboard {
    constructor() {
        this.data = {};
        this.init();
    }

    async init() {
        await this.loadData();
        this.updateStats();
        this.renderCharts();
        this.renderThreatTable();
        this.renderSourceSpecificCharts();
    }

    async loadData() {
        try {
            // In a real implementation, this would fetch from your API
            // For now, we'll use mock data or load from generated JSON
            const response = await fetch('/api/summary');
            this.data = await response.json();
        } catch (error) {
            console.error('Failed to load data:', error);
            // Fallback to mock data
            this.data = this.getMockData();
        }
    }

    updateStats() {
        document.getElementById('total-indicators').textContent = 
            this.data.report_metadata?.total_indicators || 0;
        
        document.getElementById('high-risk').textContent = 
            this.data.threat_overview?.high_risk_count || 0;
        
        document.getElementById('total-sources').textContent = 
            Object.keys(this.data.top_sources || {}).length;
        
        document.getElementById('last-updated').textContent = 
            new Date().toLocaleString();
    }

    renderCharts() {
        this.renderScoreChart();
        this.renderTypeChart();
    }

    renderScoreChart() {
        const scoreData = [{
            x: Object.keys(this.data.score_ranges || {}),
            y: Object.values(this.data.score_ranges || {}),
            type: 'bar',
            marker: {
                color: ['#27ae60', '#f39c12', '#e67e22', '#e74c3c', '#c0392b']
            }
        }];

        const layout = {
            title: 'Threat Score Distribution',
            xaxis: { title: 'Score Range' },
            yaxis: { title: 'Count' },
            plot_bgcolor: '#1e293b',
            paper_bgcolor: '#1e293b',
            font: { color: '#e2e8f0' }
        };

        Plotly.newPlot('score-chart', scoreData, layout);
    }

    renderTypeChart() {
        const typeData = [{
            values: Object.values(this.data.indicator_types || {}),
            labels: Object.keys(this.data.indicator_types || {}),
            type: 'pie'
        }];

        const layout = {
            title: 'Indicator Types Distribution',
            plot_bgcolor: '#1e293b',
            paper_bgcolor: '#1e293b',
            font: { color: '#e2e8f0' }
        };

        Plotly.newPlot('type-chart', typeData, layout);
    }

    renderThreatTable() {
        const tbody = document.getElementById('threat-table-body');
        tbody.innerHTML = '';

        const threats = this.data.top_threats || [];
        
        threats.slice(0, 10).forEach(threat => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${this.escapeHtml(threat.indicator)}</td>
                <td>${this.escapeHtml(threat.type)}</td>
                <td class="risk-${threat.risk_level.toLowerCase()}">${threat.risk_level}</td>
                <td>${threat.threat_score.toFixed(1)}</td>
                <td>${threat.sources.slice(0, 3).join(', ')}</td>
            `;
            
            tbody.appendChild(row);
        });
    }

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
    
    renderSourceSpecificCharts() {
        const sourceContainer = document.getElementById('source-metrics-container');
        if (!sourceContainer) {
            console.error('Source container element not found');
            return;
        }
        
        sourceContainer.innerHTML = ''; // Clear existing content
        
        // Get list of sources from the data
        const sources = Object.keys(this.data.top_sources || {});
        
        if (!sources.length) {
            console.log('No source data available');
            sourceContainer.innerHTML = '<div class="no-data">No source data available</div>';
            return;
        }
        
        console.log('Rendering charts for sources:', sources);
        console.log('Source data:', this.data.source_data);
        
        // Create a card for each source
        sources.forEach(source => {
            // Check if we have source-specific data
            const sourceData = this.data.source_data?.[source];
            if (!sourceData) {
                console.log(`No specific data for source: ${source}`);
                return;
            }
            
            // Create card elements
            const card = document.createElement('div');
            card.className = 'source-card';
            
            const header = document.createElement('div');
            header.className = 'source-header';
            header.innerHTML = `
                <div class="source-name">${this.formatSourceName(source)}</div>
                <div class="source-indicator-count">${this.data.top_sources[source] || 0} indicators</div>
            `;
            
            const content = document.createElement('div');
            content.className = 'source-content';
            
            // Create chart divs
            const typeChartDiv = document.createElement('div');
            typeChartDiv.id = `${source}-type-chart`;
            typeChartDiv.className = 'source-chart';
            typeChartDiv.style.height = '220px';
            
            const riskChartDiv = document.createElement('div');
            riskChartDiv.id = `${source}-risk-chart`;
            riskChartDiv.className = 'source-chart';
            riskChartDiv.style.height = '220px';
            
            // Append elements
            content.appendChild(typeChartDiv);
            content.appendChild(riskChartDiv);
            
            card.appendChild(header);
            card.appendChild(content);
            
            sourceContainer.appendChild(card);
            
            // Render charts for this source
            this.renderSourceTypeChart(source, sourceData.indicator_types);
            this.renderSourceRiskChart(source, sourceData.risk_levels);
        });
    }
    
    renderSourceTypeChart(source, typeData) {
        if (!typeData) {
            console.log(`No type data for source: ${source}`);
            return;
        }
        
        console.log(`Rendering type chart for ${source} with data:`, typeData);
        
        const chartData = [{
            values: Object.values(typeData),
            labels: Object.keys(typeData),
            type: 'pie',
            hole: 0.4
        }];
        
        const layout = {
            title: 'Indicator Types',
            height: 220,
            margin: { t: 30, b: 10, l: 10, r: 10 },
            showlegend: true,
            legend: { orientation: 'h', y: -0.2 },
            plot_bgcolor: '#1e293b',
            paper_bgcolor: '#1e293b',
            font: { color: '#e2e8f0' }
        };
        
        try {
            const chartElement = document.getElementById(`${source}-type-chart`);
            if (chartElement) {
                Plotly.newPlot(`${source}-type-chart`, chartData, layout, {responsive: true});
            } else {
                console.error(`Chart element not found for ${source}-type-chart`);
            }
        } catch (error) {
            console.error(`Error rendering type chart for ${source}:`, error);
        }
    }
    
    renderSourceRiskChart(source, riskData) {
        if (!riskData) {
            console.log(`No risk data for source: ${source}`);
            return;
        }
        
        console.log(`Rendering risk chart for ${source} with data:`, riskData);
        
        // Sort risk levels in order of severity
        const riskOrder = ['critical', 'high', 'medium', 'low', 'info'];
        const sortedEntries = Object.entries(riskData)
            .sort((a, b) => riskOrder.indexOf(a[0]) - riskOrder.indexOf(b[0]));
            
        const colors = {
            'critical': '#c0392b',
            'high': '#e74c3c',
            'medium': '#e67e22',
            'low': '#f39c12',
            'info': '#27ae60'
        };
        
        const chartData = [{
            x: sortedEntries.map(([level]) => level.charAt(0).toUpperCase() + level.slice(1)),
            y: sortedEntries.map(([, count]) => count),
            type: 'bar',
            marker: {
                color: sortedEntries.map(([level]) => colors[level] || '#3498db')
            }
        }];
        
        const layout = {
            title: 'Risk Distribution',
            height: 220,
            margin: { t: 30, b: 40, l: 35, r: 10 },
            yaxis: { title: 'Count' },
            plot_bgcolor: '#1e293b',
            paper_bgcolor: '#1e293b',
            font: { color: '#e2e8f0' }
        };
        
        try {
            const chartElement = document.getElementById(`${source}-risk-chart`);
            if (chartElement) {
                Plotly.newPlot(`${source}-risk-chart`, chartData, layout, {responsive: true});
            } else {
                console.error(`Chart element not found for ${source}-risk-chart`);
            }
        } catch (error) {
            console.error(`Error rendering risk chart for ${source}:`, error);
        }
    }
    
    formatSourceName(source) {
        // Format the source name for display (capitalize, replace hyphens with spaces, etc.)
        const nameMap = {
            'alienvault': 'AlienVault OTX',
            'virustotal': 'VirusTotal',
            'shodan': 'Shodan',
            'greynoise': 'GreyNoise',
            'abuseipdb': 'AbuseIPDB',
            'urlscan': 'URLScan.io',
            'ipinfo': 'IPInfo'
        };
        
        return nameMap[source] || source.charAt(0).toUpperCase() + source.slice(1);
    }

    getMockData() {
        return {
            report_metadata: {
                total_indicators: 150,
                generated_at: new Date().toISOString()
            },
            threat_overview: {
                high_risk_count: 12,
                medium_risk_count: 45,
                low_risk_count: 67,
                info_count: 26
            },
            indicator_types: {
                ip: 89,
                domain: 42,
                hash: 19
            },
            top_sources: {
                alienvault: 45,
                virustotal: 38,
                shodan: 32,
                greynoise: 25,
                abuseipdb: 10
            },
            source_data: {
                alienvault: {
                    indicator_types: { ip: 30, domain: 15 },
                    risk_levels: { high: 10, medium: 20, low: 15 }
                },
                virustotal: {
                    indicator_types: { ip: 20, domain: 10, hash: 8 },
                    risk_levels: { critical: 5, high: 8, medium: 15, low: 10 }
                },
                shodan: {
                    indicator_types: { ip: 25, domain: 7 },
                    risk_levels: { high: 6, medium: 18, low: 8 }
                },
                greynoise: {
                    indicator_types: { ip: 20, domain: 5 },
                    risk_levels: { high: 4, medium: 12, low: 9 }
                },
                abuseipdb: {
                    indicator_types: { ip: 8, domain: 2 },
                    risk_levels: { high: 3, medium: 4, low: 3 }
                }
            },
            top_threats: [
                {
                    indicator: "192.168.1.100",
                    type: "ip",
                    threat_score: 95.5,
                    risk_level: "Critical",
                    sources: ["alienvault", "virustotal", "greynoise"]
                },
                {
                    indicator: "malicious-domain.com",
                    type: "domain", 
                    threat_score: 87.2,
                    risk_level: "High",
                    sources: ["virustotal", "alienvault"]
                }
            ]
        };
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ThreatDashboard();
    
    // Auto-refresh every 5 minutes
    setInterval(() => {
        location.reload();
    }, 300000);
});