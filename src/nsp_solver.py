import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms import bipartite
import numpy as np
import graph_algorithms as ga

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
        self.s = "s"
        self.t = "t"
        
        if nurses:
            self.add_nurses(nurses)
        if shifts:
            self.add_shifts(shifts)
        if edges:
            self.add_edges(edges)
        
        self.G.add_node(self.s, bipartite=-1)
        self.G.add_node(self.t, bipartite=-1)
        
        if nurses and nurse_limits:
            if len(nurses) != len(nurse_limits):
                raise ValueError("Different number between nurses and nurse_limits")
            for i, nurse in enumerate(nurses):
                min_shifts, max_shifts = nurse_limits[i]
                self.G.add_edge(self.s, nurse, lb=min_shifts, capacity=max_shifts)
        
        if shifts and shift_limits:
            if len(shifts) != len(shift_limits):
                raise ValueError("Different number between shifts and shift_limits")
            for i, shift in enumerate(shifts):
                min_nurses, max_nurses = shift_limits[i]
                self.G.add_edge(shift, self.t, lb=min_nurses, capacity=max_nurses)
                
    
    def add_nurses(self, nodes):
        self.G.add_nodes_from(nodes, bipartite=0)
    
    def add_shifts(self, nodes):
        self.G.add_nodes_from(nodes, bipartite=1)
    
    def add_edges(self, edges):
        for (u, v) in edges:
            if self.G.nodes[u]['bipartite'] == self.G.nodes[v]['bipartite']:
                raise ValueError(f"Forbidden edge: {u}, {v} in the same partition")
            self.G.add_edge(u, v, lb=0, capacity=1)
    
    def get_partitions(self):
        nurses = {n for n, d in self.G.nodes(data=True) if d.get('bipartite') == 0}
        shifts = {n for n, d in self.G.nodes(data=True) if d.get('bipartite') == 1}
        return nurses, shifts
    
    def info(self):
        nurses, shifts = self.get_partitions()
        info_str = (
            f"Info:\n"
            f"- Source: {self.s}\n"
            f"- Sink: {self.t}\n"
            f"- Nurses: {len(nurses)} ({nurses})\n"
            f"- Shifts: {len(shifts)} ({shifts})\n"
            f"- Edges: {self.G.number_of_edges()}\n"
            f"\nEdge Details (source -> target: Min/Max):\n"
        )
        for u, v, data in self.G.edges(data=True):
            info_str += f"{u} -> {v}: {data['lb']}/{data['capacity']}\n"
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

        pos[self.s] = (0, 0)

        nurse_ys = get_y_positions(len(nurses))
        for i, nurse in enumerate(sorted(nurses)):
            pos[nurse] = (column_spacing, nurse_ys[i])

        shift_ys = get_y_positions(len(shifts))
        for i, shift in enumerate(sorted(shifts)):
            pos[shift] = (2 * column_spacing, shift_ys[i])

        pos[self.t] = (3 * column_spacing, 0)

        node_colors = []
        for node in self.G.nodes():
            if node == self.s:
                node_colors.append('red')
            elif node == self.t:
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

        self.H = self.G.copy()

        # Looking for a viable circulation
        # Make H
        H = nx.DiGraph()
        H.add_nodes_from(self.G.nodes())
        
        demands = {node: 0 for node in self.G.nodes()}
        
        for u, v, data in self.G.edges(data=True):
            lb = data.get('lb', 0)
            if lb > 0:
                demands[u] -= lb
                demands[v] += lb
            H.add_edge(u, v, capacity=data['capacity'] - lb)

        H.add_edge(self.t, self.s, capacity=float('inf'))

        s2, t2 = "s2", "t2"
        H.add_node(s2, bipartite = -1)
        H.add_node(t2, bipartite = -1)

        total_demand = 0
        for node, demand_value in demands.items():
            if demand_value > 0:
                H.add_edge(s2, node, capacity=demand_value)
                total_demand += demand_value
            elif demand_value < 0:
                H.add_edge(node, t2, capacity=-demand_value)

        # Calc flow in H
        circ_flow_value, circ_flow_dict = ga.max_flow(H, s2, t2, method="edmonds-karp")

        # Viable flow test
        if round(total_demand, 0) != round(circ_flow_value, 0):
            print("Unable to satisfy all constraints:\n" \
            "- All nurses must work their minimum shifts\n" \
            "- All shifts must have minimum staffing")
            return None
        
        # Viable flow
        flow_viable = {u: {v: 0 for v in self.G.neighbors(u)} for u in self.G.nodes()}
        for u, v, data in self.G.edges(data=True):
            lb = data.get('lb', 0)
            circ_flow = circ_flow_dict.get(u, {}).get(v, 0)
            flow_viable[u][v] = lb + circ_flow

        # Max Flow
        # Make residual graph
        G_residual = nx.DiGraph()
        for u, v, data in self.G.edges(data=True):
            forward_capacity = data['capacity'] - flow_viable[u][v]
            if forward_capacity > 0:
                G_residual.add_edge(u, v, capacity=forward_capacity)
            
            backward_capacity = flow_viable[u][v] - data.get('lb', 0)
            if backward_capacity > 0:
                G_residual.add_edge(v, u, capacity=backward_capacity)

        # Calc aug
        _, aug_flow_dict = ga.max_flow(G_residual, self.s, self.t, method="edmonds-karp")
        
        # Calc max flow
        final_flow_dict = {u: {v: 0 for v in self.G.neighbors(u)} for u in self.G.nodes()}
        for u, v in self.G.edges():
            aug_flow = aug_flow_dict.get(u, {}).get(v, 0)
            rev_aug_flow = aug_flow_dict.get(v, {}).get(u, 0)
            final_flow_dict[u][v] = flow_viable[u][v] + aug_flow - rev_aug_flow
            
        # Show Results
        nurses, shifts = self.get_partitions()
        total_shifts_assigned = sum(final_flow_dict[n][s] for n in nurses for s in shifts if s in final_flow_dict[n])
        
        print(f"\n--- Scheduling Results ---")
        print(f"Total shifts assigned: {int(total_shifts_assigned)}")
        
        print("\nNurse Assignments:")
        for nurse in sorted(nurses):
            assigned_shifts = [shift for shift, flow in final_flow_dict[nurse].items() if flow > 0.5]
            if assigned_shifts:
                print(f"- {nurse}: {', '.join(sorted(assigned_shifts))}")
            else:
                 print(f"- {nurse}: No shifts")
        final_result = {
            'total_alocated': total_shifts_assigned,
            'assignments': final_flow_dict
        }
        return final_result