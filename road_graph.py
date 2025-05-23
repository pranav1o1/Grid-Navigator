import osmnx as ox
import networkx as nx

def load_graph(place_name="Chalisgaon, Maharashtra, India"):
    # Load road network from OpenStreetMap
    G = ox.graph_from_place(place_name, network_type="drive")
    G_proj = ox.project_graph(G)
    return G_proj

def graph_to_grid_nodes(G_proj, grid_size):
    """
    Maps real-world road graph nodes to grid positions (row, col) in Pygame grid.
    """
    nodes = list(G_proj.nodes(data=True))
    
    # Step 1: Get bounds of coordinates
    xs = [data['x'] for _, data in nodes]
    ys = [data['y'] for _, data in nodes]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    def to_grid(x, y):
        col = int((x - min_x) / (max_x - min_x) * (grid_size - 1))
        row = int((y - min_y) / (max_y - min_y) * (grid_size - 1))
        return row, col

    grid_positions = {}
    for node, data in nodes:
        grid_positions[node] = to_grid(data['x'], data['y'])

    return grid_positions
