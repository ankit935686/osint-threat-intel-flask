// OSINT Threat Intelligence Dashboard
class ThreatDashboard {
    constructor() {
        this.data = {};
        this.sourceColors = {
            'alienvault': '#3b82f6',  // blue
            'virustotal': '#8b5cf6',  // purple
            'shodan': '#ec4899',      // pink
            'greynoise': '#10b981',   // green
            'abuseipdb': '#f59e0b',   // amber
            'urlscan': '#06b6d4',     // cyan
            'ipinfo': '#6366f1'       // indigo
        };
        this.init();
        this.startPolling();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Add refresh button event listener
        const refreshButton = document.getElementById('refresh-button');
        if (refreshButton) {
            refreshButton.addEventListener('click', async () => {
                refreshButton.disabled = true;
                refreshButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
                await this.loadData();
                this.updateStats();
                this.renderCharts();
                this.renderThreatTable();
                this.renderSourceSpecificCharts();
                refreshButton.disabled = false;
                refreshButton.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh Now';
            });
        }
    }

    async init() {
        await this.loadData();
        this.updateStats();
        this.renderCharts();
        this.renderThreatTable();
        this.renderSourceSpecificCharts();
    }
    
    startPolling() {
        // Poll every 30 seconds for new data
        this.pollingInterval = setInterval(async () => {
            console.log("Polling for new data...");
            await this.loadData();
            this.updateStats();
            this.renderCharts();
            this.renderThreatTable();
            this.renderSourceSpecificCharts();
        }, 30000); // 30 seconds
    }

    async loadData() {
        // Show loading state
        const statusIndicator = document.getElementById('update-status');
        if (statusIndicator) {
            statusIndicator.innerHTML = `<span class="status-dot loading"></span> Updating data...`;
        }
        
        try {
            // Fetch from the API with cache busting to ensure fresh data
            const timestamp = new Date().getTime();
            console.log(`Fetching data from /api/summary?t=${timestamp}`);
            
            const response = await fetch(`/api/summary?t=${timestamp}`, {
                headers: {
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0'
                }
            });
            
            if (!response.ok) {
                throw new Error(`API returned status: ${response.status}`);
            }
            
            // Get the text response first to handle any possible JSON parsing issues
            const textResponse = await response.text();
            
            let newData;
            try {
                // Try to parse the JSON
                newData = JSON.parse(textResponse);
                console.log("API Response Data:", newData);
            } catch (jsonError) {
                console.error("JSON Parse Error:", jsonError);
                console.log("Raw response:", textResponse.substring(0, 500) + "...");
                throw new Error(`Failed to parse JSON: ${jsonError.message}`);
            }
            
            // Check if response contains an error message
            if (newData.error) {
                throw new Error(newData.error);
            }
            
            // Check if required data fields exist
            if (!newData.report_metadata || !newData.top_sources) {
                console.warn("API data is missing required fields:", newData);
            }
            
            // Check if data has changed before updating
            const hasChanged = JSON.stringify(newData) !== JSON.stringify(this.data);
            this.data = newData;
            
            // Update status indicator
            if (statusIndicator) {
                if (hasChanged) {
                    statusIndicator.innerHTML = `<span class="status-dot updated"></span> Data updated at ${new Date().toLocaleTimeString()}`;
                    console.log("Dashboard data has been updated");
                    // Reset to active state after 3 seconds
                    setTimeout(() => {
                        statusIndicator.innerHTML = `<span class="status-dot active"></span> Live updates enabled`;
                    }, 3000);
                } else {
                    statusIndicator.innerHTML = `<span class="status-dot active"></span> Live updates enabled`;
                    console.log("No changes in dashboard data");
                }
            }
            
            return hasChanged;
        } catch (error) {
            console.error('Failed to load data:', error);
            
            // Update status indicator to show error
            if (statusIndicator) {
                statusIndicator.innerHTML = `<span class="status-dot error"></span> Update failed: ${error.message}`;
            }
            
            // Fallback to mock data ONLY if we don't have data yet
            if (!this.data || Object.keys(this.data).length === 0) {
                console.warn("Using mock data as fallback");
                this.data = this.getMockData();
                return true;
            }
            
            return false;
        }
    }

    updateStats() {
        document.getElementById('total-indicators').textContent = 
            this.data.report_metadata?.total_indicators || 0;
        
        document.getElementById('high-risk').textContent = 
            this.data.threat_overview?.high_risk_count || 0;
        
        document.getElementById('total-sources').textContent = 
            Object.keys(this.data.top_sources || {}).length;
        
        // Get the timestamp from the API data, or use current time
        let lastUpdated;
        if (this.data.report_metadata?.generated_at) {
            lastUpdated = new Date(this.data.report_metadata.generated_at);
        } else {
            lastUpdated = new Date();
        }
        
        document.getElementById('last-updated').textContent = 
            lastUpdated.toLocaleString();
    }

    renderCharts() {
        this.renderScoreChart();
        this.renderTypeChart();
    }

    renderScoreChart() {
        const scoreRanges = this.data.score_ranges || {};
        // Sort score ranges to ensure they're in ascending order
        const sortedRanges = Object.entries(scoreRanges)
            .sort((a, b) => {
                // Extract the lower bound from range (e.g., "0-20" -> 0)
                const aLower = parseInt(a[0].split('-')[0]);
                const bLower = parseInt(b[0].split('-')[0]);
                return aLower - bLower;
            });
        
        const scoreData = [{
            x: sortedRanges.map(([range]) => range),
            y: sortedRanges.map(([, count]) => count),
            type: 'bar',
            marker: {
                color: [
                    'rgba(39, 174, 96, 0.8)',
                    'rgba(241, 196, 15, 0.8)',
                    'rgba(243, 156, 18, 0.8)',
                    'rgba(231, 76, 60, 0.8)',
                    'rgba(192, 57, 43, 0.8)'
                ]
            },
            hoverinfo: 'y+text',
            text: sortedRanges.map(([range, count]) => `${range}: ${count} indicators`)
        }];

        const layout = {
            margin: { t: 10, b: 50, l: 50, r: 20 },
            xaxis: { 
                title: 'Score Range',
                titlefont: { size: 12, color: '#94a3b8' }
            },
            yaxis: { 
                title: 'Count',
                titlefont: { size: 12, color: '#94a3b8' }
            },
            plot_bgcolor: '#1e293b',
            paper_bgcolor: '#1e293b',
            font: { color: '#e2e8f0' },
            bargap: 0.05,
            showlegend: false,
            autosize: true
        };

        const config = {
            responsive: true,
            displayModeBar: false
        };

        Plotly.newPlot('score-chart', scoreData, layout, config);
    }

    renderTypeChart() {
        const typeData = [{
            values: Object.values(this.data.indicator_types || {}),
            labels: Object.keys(this.data.indicator_types || {}),
            type: 'pie',
            hole: 0.4,
            marker: {
                colors: [
                    'rgba(59, 130, 246, 0.8)',   // blue
                    'rgba(139, 92, 246, 0.8)',   // purple
                    'rgba(16, 185, 129, 0.8)',   // green
                    'rgba(245, 158, 11, 0.8)',   // amber
                    'rgba(236, 72, 153, 0.8)'    // pink
                ]
            },
            textinfo: 'label+percent',
            textposition: 'outside',
            hoverinfo: 'label+value+percent'
        }];

        const layout = {
            margin: { t: 10, b: 10, l: 10, r: 10 },
            showlegend: false,
            plot_bgcolor: '#1e293b',
            paper_bgcolor: '#1e293b',
            font: { color: '#e2e8f0' },
            autosize: true
        };

        const config = {
            responsive: true,
            displayModeBar: false
        };

        Plotly.newPlot('type-chart', typeData, layout, config);
    }

    renderThreatTable() {
        const tbody = document.getElementById('threat-table-body');
        if (!tbody) return;
        
        tbody.innerHTML = '';

        const threats = this.data.top_threats || [];
        
        if (threats.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = `<td colspan="5" style="text-align: center;">No threat data available</td>`;
            tbody.appendChild(row);
            return;
        }
        
        threats.slice(0, 10).forEach(threat => {
            const row = document.createElement('tr');
            
            // Create source badges
            const sourceBadges = threat.sources.slice(0, 3).map(source => {
                const color = this.sourceColors[source] || '#64748b';
                return `<span class="source-badge" style="background-color: ${color}">${this.formatSourceNameShort(source)}</span>`;
            }).join('');
            
            // Add view details button if there are more sources
            const moreSourcesButton = threat.sources.length > 3 
                ? `<span class="more-sources">+${threat.sources.length - 3}</span>` 
                : '';
            
            row.innerHTML = `
                <td>${this.escapeHtml(threat.indicator)}</td>
                <td><span class="type-badge">${this.escapeHtml(threat.type)}</span></td>
                <td><span class="risk-level risk-${threat.risk_level.toLowerCase()}">${threat.risk_level}</span></td>
                <td>${threat.threat_score.toFixed(1)}</td>
                <td class="sources-cell">${sourceBadges}${moreSourcesButton}</td>
            `;
            
            tbody.appendChild(row);
        });
        
        // Add styles for the new elements
        const style = document.createElement('style');
        style.textContent = `
            .type-badge {
                display: inline-block;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                background-color: rgba(51, 65, 85, 0.7);
                font-size: 0.75rem;
                font-weight: 500;
            }
            .risk-level {
                display: inline-block;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                text-align: center;
                min-width: 70px;
            }
            .sources-cell {
                display: flex;
                align-items: center;
                gap: 0.3rem;
                flex-wrap: wrap;
            }
            .source-badge {
                display: inline-block;
                padding: 0.2rem 0.4rem;
                border-radius: 4px;
                font-size: 0.7rem;
                color: white;
                font-weight: 500;
            }
            .more-sources {
                display: inline-block;
                padding: 0.2rem 0.4rem;
                border-radius: 4px;
                background-color: rgba(51, 65, 85, 0.7);
                font-size: 0.7rem;
                cursor: pointer;
            }
        `;
        document.head.appendChild(style);
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
            
            // Use source-specific color
            const sourceColor = this.sourceColors[source] || '#64748b';
            card.style.borderLeft = `4px solid ${sourceColor}`;
            
            const header = document.createElement('div');
            header.className = 'source-header';
            
            // Set the source circle color
            const sourceName = document.createElement('div');
            sourceName.className = 'source-name';
            sourceName.textContent = this.formatSourceName(source);
            sourceName.style.setProperty('--source-color', sourceColor);
            
            const indicatorCount = document.createElement('div');
            indicatorCount.className = 'source-indicator-count';
            indicatorCount.textContent = `${this.data.top_sources[source] || 0} indicators`;
            
            header.appendChild(sourceName);
            header.appendChild(indicatorCount);
            
            const content = document.createElement('div');
            content.className = 'source-content';
            
            // Create chart divs
            const typeChartDiv = document.createElement('div');
            typeChartDiv.id = `${source}-type-chart`;
            typeChartDiv.className = 'source-chart';
            
            const riskChartDiv = document.createElement('div');
            riskChartDiv.id = `${source}-risk-chart`;
            riskChartDiv.className = 'source-chart';
            
            // Append elements
            content.appendChild(typeChartDiv);
            content.appendChild(riskChartDiv);
            
            card.appendChild(header);
            card.appendChild(content);
            
            sourceContainer.appendChild(card);
            
            // Render charts for this source
            this.renderSourceTypeChart(source, sourceData.indicator_types, sourceColor);
            this.renderSourceRiskChart(source, sourceData.risk_levels);
        });
        
        // Add styles to make source name circles match source colors
        const style = document.createElement('style');
        style.textContent = `
            .source-name::before {
                background: var(--source-color, #3b82f6);
            }
        `;
        document.head.appendChild(style);
    }
    
    renderSourceTypeChart(source, typeData, sourceColor) {
        if (!typeData) {
            console.log(`No type data for source: ${source}`);
            return;
        }
        
        console.log(`Rendering type chart for ${source} with data:`, typeData);
        
        // Generate a gradient of colors based on the source color
        const baseColor = sourceColor || '#3b82f6';
        const colors = this.generateColorShades(baseColor, Object.keys(typeData).length);
        
        const chartData = [{
            values: Object.values(typeData),
            labels: Object.keys(typeData),
            type: 'pie',
            hole: 0.6,
            marker: { colors },
            textinfo: 'label+percent',
            textposition: 'outside',
            hoverinfo: 'label+value+percent'
        }];
        
        const layout = {
            title: {
                text: 'Indicator Types',
                font: { size: 14, color: '#e2e8f0' }
            },
            height: 220,
            margin: { t: 30, b: 10, l: 10, r: 10 },
            showlegend: false,
            plot_bgcolor: '#1e293b',
            paper_bgcolor: '#1e293b',
            font: { color: '#e2e8f0', size: 10 }
        };
        
        const config = {
            responsive: true,
            displayModeBar: false
        };
        
        try {
            const chartElement = document.getElementById(`${source}-type-chart`);
            if (chartElement) {
                Plotly.newPlot(`${source}-type-chart`, chartData, layout, config);
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
                color: sortedEntries.map(([level]) => colors[level] || '#3498db'),
                opacity: 0.8
            },
            hoverinfo: 'y+text',
            text: sortedEntries.map(([level, count]) => `${level}: ${count}`)
        }];
        
        const layout = {
            title: {
                text: 'Risk Distribution',
                font: { size: 14, color: '#e2e8f0' }
            },
            height: 220,
            margin: { t: 30, b: 40, l: 40, r: 10 },
            yaxis: { 
                title: { text: 'Count', font: { size: 10, color: '#94a3b8' } },
                fixedrange: true
            },
            xaxis: {
                fixedrange: true
            },
            plot_bgcolor: '#1e293b',
            paper_bgcolor: '#1e293b',
            font: { color: '#e2e8f0', size: 10 },
            bargap: 0.3,
            showlegend: false
        };
        
        const config = {
            responsive: true,
            displayModeBar: false
        };
        
        try {
            const chartElement = document.getElementById(`${source}-risk-chart`);
            if (chartElement) {
                Plotly.newPlot(`${source}-risk-chart`, chartData, layout, config);
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
    
    formatSourceNameShort(source) {
        // Short version for badges
        const nameMap = {
            'alienvault': 'AlienVault',
            'virustotal': 'VirusTotal',
            'shodan': 'Shodan',
            'greynoise': 'GreyNoise',
            'abuseipdb': 'AbuseIPDB',
            'urlscan': 'URLScan',
            'ipinfo': 'IPInfo'
        };
        
        return nameMap[source] || source.charAt(0).toUpperCase() + source.slice(1);
    }
    
    // Helper to generate color shades for charts
    generateColorShades(baseColor, count) {
        // Parse the base color
        const hexToRGB = (hex) => {
            const r = parseInt(hex.slice(1, 3), 16);
            const g = parseInt(hex.slice(3, 5), 16);
            const b = parseInt(hex.slice(5, 7), 16);
            return [r, g, b];
        };
        
        // Ensure the base color is a valid hex
        if (!/^#[0-9A-F]{6}$/i.test(baseColor)) {
            baseColor = '#3b82f6'; // Default to blue
        }
        
        // Get the RGB values from the hex
        const [r, g, b] = hexToRGB(baseColor);
        
        // Generate variants with different opacities and lightness
        const colors = [];
        for (let i = 0; i < count; i++) {
            // Create a variant with different brightness
            const factor = 0.7 + (i / count) * 0.6;
            const newR = Math.min(255, Math.round(r * factor));
            const newG = Math.min(255, Math.round(g * factor));
            const newB = Math.min(255, Math.round(b * factor));
            
            colors.push(`rgba(${newR}, ${newG}, ${newB}, 0.85)`);
        }
        
        return colors;
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
            score_ranges: {
                "0-20": 26,
                "21-40": 67,
                "41-60": 45,
                "61-80": 12,
                "81-100": 0
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
    window.dashboard = new ThreatDashboard();
    
    // Handle sidebar navigation (only visual, not functional)
    const navItems = document.querySelectorAll('.sidebar-nav li');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
        });
    });
});