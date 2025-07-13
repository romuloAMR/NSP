import networkx as nx

def bfs_augmenting_path(G_residual, s, t):
    parent = {s: None}
    queue = [s]

    head = 0
    while head < len(queue):
        u = queue[head]
        head += 1
        
        if u == t:
            # Reconstructs the path from t back to s
            path = []
            curr = t
            while curr is not None:
                path.append(curr)
                curr = parent.get(curr)
            path.reverse()
            return path

        for v, data in G_residual[u].items():
            if v not in parent and data.get('capacity', 0) > 0:
                parent[v] = u
                queue.append(v)

    return None # No path

def edmonds_karp_max_flow(G, s, t):
    G_residual = nx.DiGraph()
    for u, v, data in G.edges(data=True):
        capacity = data.get('capacity', 0)
        G_residual.add_edge(u, v, capacity=capacity)
        if not G_residual.has_edge(v, u):
            G_residual.add_edge(v, u, capacity=0)

    flow = {u: {v: 0 for v in G.neighbors(u)} for u in G.nodes()}
    max_flow = 0
    while True:
        # Find an augmenting path in the residual graph
        path = bfs_augmenting_path(G_residual, s, t)
        if not path:
            break

        # Find minimum residual capacity along the path
        path_flow = min(G_residual[u][v]['capacity'] for u, v in zip(path, path[1:]))

        # Update residual capacities and flow
        for u, v in zip(path, path[1:]):
            if G_residual.has_edge(u, v):
                G_residual[u][v]['capacity'] -= path_flow
                G_residual[v][u]['capacity'] += path_flow
                
                if G.has_edge(u, v):
                    flow[u][v] += path_flow
                else:
                    flow[v][u] -= path_flow

        max_flow += path_flow

    return max_flow, flow

def build_layered_network(G_residual, s, t):
    level = {s: 0}
    queue = [s]
    found_t = False
    
    while queue and not found_t:
        u = queue.pop(0)
        for v in G_residual.neighbors(u):
            if v not in level and G_residual[u][v]['capacity'] > 0:
                level[v] = level[u] + 1
                if v == t:
                    found_t = True
                queue.append(v)
    
    if t not in level:
        return None, None
    
    # Build the layer network
    H = nx.DiGraph()
    
    for u in level:
        H.add_node(u, level=level[u])
        for v in G_residual.neighbors(u):
            if level.get(v, -1) == level[u] + 1 and G_residual[u][v]['capacity'] > 0:
                H.add_edge(u, v, capacity=G_residual[u][v]['capacity'])
    
    return H, level


def layered_dfs(G_residual, level, flow, u, target, pushed, visited):
    if u == target:
        return pushed
    visited.add(u)
    
    for _, v, data in G_residual.out_edges(u, data=True):
        cap = data['capacity']
        if cap > 0 and v in level and level[v] == level[u] + 1 and v not in visited:
            to_send = min(pushed, cap)
            sent = layered_dfs(G_residual, level, flow, v, target, to_send, visited)
            if sent > 0:
                # Updates the flow
                flow[u][v] = flow[u].get(v, 0) + sent
                G_residual[u][v]['capacity'] -= sent
                if G_residual[u][v]['capacity'] == 0:
                    G_residual.remove_edge(u, v)

                # Reverse edge
                if not G_residual.has_edge(v, u):
                    G_residual.add_edge(v, u, capacity=0)
                G_residual[v][u]['capacity'] += sent
                return sent
    return 0

def push(G_residual, level, flow, v, t, g):
    visited = set()
    return layered_dfs(G_residual, level, flow, v, t, g, visited)

def pull(G_residual, level, flow, s, v, g):
    visited = set()
    return layered_dfs(G_residual, level, flow, s, v, g, visited)

def build_residual(G, flow):
    G_residual = nx.DiGraph()
    for u, v, data in G.edges(data=True):
        residual = data['capacity'] - flow[u][v]
        if residual > 0:
            G_residual.add_edge(u, v, capacity=residual)
        if flow[u][v] > 0:
            G_residual.add_edge(v, u, capacity=flow[u][v])
    return G_residual

# MPM max flow algorithm implementation.
# Note: This version is not fully working yet. Use for testing only.
def mpm_maximum_flow(G, s, t):
    flow = {u: {v: 0 for v in G.neighbors(u)} for u in G.nodes()}
    
    
    G_residual = build_residual(G, flow)
    H, level = build_layered_network(G_residual, s, t)

    while H is not None:
        while True:
            min_potential = float('inf')
            min_node = None
            
            for v in H.nodes():
                if v == s or v == t:
                    continue
                in_potential = sum(data['capacity'] for _, _, data in H.in_edges(v, data=True))
                out_potential = sum(data['capacity'] for _, _, data in H.out_edges(v, data=True))
                node_potential = min(in_potential, out_potential)
                if 0 < node_potential < min_potential:
                    min_potential = node_potential
                    min_node = v

            if min_node is None:
                break

            g = min_potential
            push(G_residual, level, flow, min_node, t, g)
            pull(G_residual, level, flow, s, min_node, g)

            G_residual = build_residual(G, flow)
            H, level = build_layered_network(G_residual, s, t)
            if H is None:
                break

        G_residual = build_residual(G, flow)
        H, level = build_layered_network(G_residual, s, t)

    flow_value = sum(flow[s][v] for v in G.neighbors(s))
    return flow_value, flow

def max_flow(G, s, t, method='edmonds-karp'):
    if method not in ('edmonds-karp', 'mpm'):
        raise ValueError("Method must be 'edmonds-karp' or 'mpm'")
    if method == 'edmonds-karp':
        return edmonds_karp_max_flow(G, s, t)
    elif method == 'mpm':
        return mpm_maximum_flow(G, s, t)