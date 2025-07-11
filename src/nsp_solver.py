import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms import bipartite
import numpy as np

class NurseScheduling:
    def __init__(
            self,
            nurses=None,
            shifts=None,
            edges=None,
            nurse_limits=None,
            shift_limits=None
        ):
        self.G = nx.DiGraph()
        self.source = "source"
        self.sink = "sink"
        
        if nurses:
            self.add_nurses(nurses)
        if shifts:
            self.add_shifts(shifts)
        if edges:
            self.add_edges(edges)
        
        self.G.add_node(self.source, bipartite=-1)
        self.G.add_node(self.sink, bipartite=-1)
        
        if nurses and nurse_limits:
            if len(nurses) != len(nurse_limits):
                raise ValueError("Mismatch between nurses and nurse_limits")
            for i, nurse in enumerate(nurses):
                min_shifts, max_shifts = nurse_limits[i]
                self.G.add_edge(self.source, nurse, lb=min_shifts, capacity=max_shifts)
        
        if shifts and shift_limits:
            if len(shifts) != len(shift_limits):
                raise ValueError("Mismatch between shifts and shift_limits")
            for i, shift in enumerate(shifts):
                min_nurses, max_nurses = shift_limits[i]
                self.G.add_edge(shift, self.sink, lb=min_nurses, capacity=max_nurses)
                
    
    def add_nurses(self, nodes):
        self.G.add_nodes_from(nodes, bipartite=0)
    
    def add_shifts(self, nodes):
        self.G.add_nodes_from(nodes, bipartite=1)
    
    def add_edges(self, edges):
        for (u, v) in edges:
            if self.G.nodes[u]['bipartite'] == self.G.nodes[v]['bipartite']:
                raise ValueError(f"Edge ({u}, {v}) connects nodes from the same partition")
            self.G.add_edge(u, v, lb=0, capacity=1)
    
    def get_partitions(self):
        nurses = {n for n, d in self.G.nodes(data=True) if d.get('bipartite') == 0}
        shifts = {n for n, d in self.G.nodes(data=True) if d.get('bipartite') == 1}
        return nurses, shifts
    
    def info(self):
        nurses, shifts = self.get_partitions()
        info_str = (
            f"Flow Network for Nurse Scheduling:\n"
            f"- Source: {self.source}\n"
            f"- Sink: {self.sink}\n"
            f"- Nurses: {len(nurses)} ({nurses})\n"
            f"- Shifts: {len(shifts)} ({shifts})\n"
            f"- Total edges: {self.G.number_of_edges()}\n"
            f"\nEdge Details (source -> target: [lb, capacity]):\n"
        )
        for u, v, data in self.G.edges(data=True):
            info_str += f"{u} -> {v}: [{data['lb']}, {data['capacity']}]\n"
        return info_str
    
    def show(self):
        nurses, shifts = self.get_partitions()

        pos = {}
        column_spacing = 1.0
        vertical_spacing = 0.5

        max_count = max(len(nurses), len(shifts), 1)
        total_height = (max_count - 1) * vertical_spacing

        def get_y_positions(count):
            start = -total_height / 2
            return [start + i * vertical_spacing for i in range(count)]

        pos[self.source] = (0, 0)

        nurse_ys = get_y_positions(len(nurses))
        for i, nurse in enumerate(sorted(nurses)):
            pos[nurse] = (column_spacing, nurse_ys[i])

        shift_ys = get_y_positions(len(shifts))
        for i, shift in enumerate(sorted(shifts)):
            pos[shift] = (2 * column_spacing, shift_ys[i])

        pos[self.sink] = (3 * column_spacing, 0)

        node_colors = []
        for node in self.G.nodes():
            if node == self.source:
                node_colors.append('red')
            elif node == self.sink:
                node_colors.append('orange')
            elif node in nurses:
                node_colors.append('skyblue')
            else:
                node_colors.append('lightgreen')

        plt.figure(figsize=(12, 8 + max_count * 0.2))

        nx.draw_networkx_nodes(
            self.G, pos, 
            node_color=node_colors, 
            node_size=1500,
            edgecolors='black',
            linewidths=1
        )

        nx.draw_networkx_labels(
            self.G, pos, 
            font_size=10, 
            font_weight='bold'
        )

        nx.draw_networkx_edges(
            self.G, pos, 
            edge_color='gray', 
            width=1.5,
            arrows=True, 
            arrowstyle='->', 
            arrowsize=20
        )

        edge_labels = {
            (u, v): f"{d['lb']}/{d['capacity']}" 
            for u, v, d in self.G.edges(data=True)
        }
        nx.draw_networkx_edge_labels(
            self.G, pos, 
            edge_labels=edge_labels, 
            font_color='black',
            font_size=9,
            bbox=dict(alpha=0.7)
        )

        plt.title("Nurse Scheduling Flow Network\n(Edges: Min_Flow/Max_Flow)", pad=20)
        plt.axis('off')
        plt.tight_layout()
        plt.show()

    def run(self):
        """Solve the problem using maximum flow with demands (if there are minimum limits)."""
        pass
