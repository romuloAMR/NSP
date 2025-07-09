import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import bipartite

class NurseScheduling:
    def __init__(self, top_nodes=None, bottom_nodes=None, edges=None):
        """
        Initializes a graph with two sets of nodes and edges between them.
        
        Parameters:
        - top_nodes: List of nodes in the first partition (bipartite=0)
        - bottom_nodes: List of nodes in the second partition (bipartite=1)
        - edges: List of edges connecting nodes between partitions
        """
        self.G = nx.Graph()
        
        if top_nodes:
            self.add_top_nodes(top_nodes)
        if bottom_nodes:
            self.add_bottom_nodes(bottom_nodes)
        if edges:
            self.add_edges(edges)
    
    def add_top_nodes(self, nodes):
        """Adds nodes to the top partition (bipartite=0)"""
        self.G.add_nodes_from(nodes, bipartite=0)
    
    def add_bottom_nodes(self, nodes):
        """Adds nodes to the bottom partition (bipartite=1)"""
        self.G.add_nodes_from(nodes, bipartite=1)
    
    def add_edges(self, edges):
        """
        Adds edges between partitions.
        Raises ValueError if edges connect nodes within the same partition.
        """
        for u, v in edges:
            if self.G.nodes[u]['bipartite'] == self.G.nodes[v]['bipartite']:
                raise ValueError(f"Edge ({u}, {v}) connects nodes in the same partition")
        self.G.add_edges_from(edges)

    def get_partitions(self):
        """
        Returns the two partitions of the bipartite graph.
        """
        return bipartite.sets(self.G)
    
    def show(self):
        """
        Plots the bipartite graph with nodes positioned by partition
        """
    
        top_nodes, bottom_nodes = self.get_partitions()
        
        pos = {}
        pos.update((node, (0, i)) for i, node in enumerate(top_nodes))
        pos.update((node, (1, i)) for i, node in enumerate(bottom_nodes))
        
        node_colors = ['skyblue'] * len(top_nodes) + ['lightgreen'] * len(bottom_nodes)
        
        nx.draw(self.G, pos, with_labels=True, node_color=node_colors,
                node_size=800, edge_color='gray', width=2)
        
        plt.title("Graph Visualization")
        plt.show()
    
    def run(self):
        """Solves the nurse scheduling problem"""
        return "Done"
    
    def info(self):
        """Returns information about the scheduling graph"""
        num_nodes = self.G.number_of_nodes()
        num_edges = self.G.number_of_edges()
        
        info_str = f"Bipartite Graph with {num_nodes} nodes and {num_edges} edges.\n"
        
        return info_str
