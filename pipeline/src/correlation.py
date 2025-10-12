import pandas as pd
import networkx as nx
import json
from typing import Dict, List, Set, Tuple
import logging
from datetime import datetime

class CorrelationEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.graph = nx.Graph()
    
    def build_graph(self, scored_data: pd.DataFrame) -> Dict:
        """Build correlation graph between indicators"""
        self.logger.info("Building correlation graph")
        
        self.graph.clear()
        
        # Add nodes for all indicators
        for _, row in scored_data.iterrows():
            self._add_indicator_node(row)
        
        # Build relationships
        self._build_relationships(scored_data)
        
        # Calculate graph metrics
        metrics = self._calculate_graph_metrics()
        
        # Save graph data
        self._save_graph_data(scored_data)
        
        self.logger.info(f"Graph built with {len(self.graph.nodes())} nodes and {len(self.graph.edges())} edges")
        return metrics
    
    def _add_indicator_node(self, row: pd.Series):
        """Add an indicator as a node to the graph"""
        node_id = f"{row['type']}_{row['indicator']}"
        
        self.graph.add_node(node_id, **{
            'indicator': row['indicator'],
            'type': row['type'],
            'threat_score': row.get('threat_score', 0),
            'risk_level': row.get('risk_level', 'Unknown'),
            'sources': row.get('sources', []),
            'asn': row.get('asn', ''),
            'country': row.get('country', ''),
            'organization': row.get('organization', '')
        })
    
    def _build_relationships(self, scored_data: pd.DataFrame):
        """Build relationships between indicators"""
        
        # Group by common attributes to find relationships
        self._link_by_asn(scored_data)
        self._link_by_country(scored_data)
        self._link_by_organization(scored_data)
        self._link_by_services(scored_data)
        self._link_ips_and_domains(scored_data)
    
    def _link_by_asn(self, scored_data: pd.DataFrame):
        """Link indicators sharing the same ASN"""
        asn_groups = scored_data.groupby('asn')
        for asn, group in asn_groups:
            if asn and len(group) > 1:
                indicators = group['indicator'].tolist()
                self._create_edges(indicators, 'same_asn', asn)
    
    def _link_by_country(self, scored_data: pd.DataFrame):
        """Link indicators from the same country"""
        country_groups = scored_data.groupby('country')
        for country, group in country_groups:
            if country and len(group) > 1:
                indicators = group['indicator'].tolist()
                self._create_edges(indicators, 'same_country', country)
    
    def _link_by_organization(self, scored_data: pd.DataFrame):
        """Link indicators from the same organization"""
        org_groups = scored_data.groupby('organization')
        for org, group in org_groups:
            if org and len(group) > 1:
                indicators = group['indicator'].tolist()
                self._create_edges(indicators, 'same_org', org)
    
    def _link_by_services(self, scored_data: pd.DataFrame):
        """Link indicators sharing common services"""
        # This would require service/port data from Shodan/etc.
        pass
    
    def _link_ips_and_domains(self, scored_data: pd.DataFrame):
        """Link IPs and domains that resolve to each other"""
        # This would require DNS resolution data
        # For now, we can look for patterns in the data
        pass
    
    def _create_edges(self, indicators: List[str], relationship: str, value: str):
        """Create edges between indicators with the given relationship"""
        from itertools import combinations
        
        for ind1, ind2 in combinations(indicators, 2):
            node1 = f"ip_{ind1}" if '.' in ind1 else f"domain_{ind1}"
            node2 = f"ip_{ind2}" if '.' in ind2 else f"domain_{ind2}"
            
            if self.graph.has_node(node1) and self.graph.has_node(node2):
                if self.graph.has_edge(node1, node2):
                    # Update existing edge
                    self.graph[node1][node2]['relationships'].append((relationship, value))
                else:
                    # Create new edge
                    self.graph.add_edge(node1, node2, relationships=[(relationship, value)])
    
    def _calculate_graph_metrics(self) -> Dict:
        """Calculate graph metrics and insights"""
        if len(self.graph.nodes()) == 0:
            return {}
        
        metrics = {
            'total_nodes': len(self.graph.nodes()),
            'total_edges': len(self.graph.edges()),
            'density': nx.density(self.graph),
            'connected_components': nx.number_connected_components(self.graph),
            'average_degree': sum(dict(self.graph.degree()).values()) / len(self.graph.nodes()),
            'node_degrees': dict(self.graph.degree()),
            'centrality': nx.degree_centrality(self.graph)
        }
        
        # Find clusters/communities
        try:
            from networkx.algorithms import community
            communities = list(community.greedy_modularity_communities(self.graph))
            metrics['communities'] = len(communities)
            metrics['community_sizes'] = [len(c) for c in communities]
        except:
            metrics['communities'] = 0
        
        return metrics
    
    def _save_graph_data(self, scored_data: pd.DataFrame):
        """Save graph data for visualization"""
        # Save graph in JSON format for web visualization
        graph_data = {
            'nodes': [],
            'edges': [],
            'metrics': self._calculate_graph_metrics()
        }
        
        # Add nodes
        for node_id, node_data in self.graph.nodes(data=True):
            graph_data['nodes'].append({
                'id': node_id,
                'label': node_data.get('indicator', ''),
                'type': node_data.get('type', ''),
                'threat_score': node_data.get('threat_score', 0),
                'risk_level': node_data.get('risk_level', 'Unknown'),
                'group': node_data.get('country', 'unknown')
            })
        
        # Add edges
        for edge in self.graph.edges(data=True):
            graph_data['edges'].append({
                'from': edge[0],
                'to': edge[1],
                'relationships': edge[2].get('relationships', [])
            })
        
        # Save to file
        output_file = f"pipeline/data/reports/correlation_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        # Also save as graph.json for the web API
        output_file_api = "pipeline/data/reports/graph.json"
        with open(output_file_api, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        self.logger.info(f"Graph data saved to {output_file}")
    
    def find_related_indicators(self, indicator: str, max_depth: int = 2) -> List:
        """Find indicators related to the given indicator"""
        node_id = f"ip_{indicator}" if '.' in indicator else f"domain_{indicator}"
        
        if node_id not in self.graph:
            return []
        
        related = []
        visited = set()
        
        def dfs(current_node, depth):
            if depth > max_depth or current_node in visited:
                return
            
            visited.add(current_node)
            related.append(current_node)
            
            for neighbor in self.graph.neighbors(current_node):
                dfs(neighbor, depth + 1)
        
        dfs(node_id, 0)
        return [node for node in related if node != node_id]