import osmnx as ox
import networkx as nx
from math import sqrt
import matplotlib.pyplot as plt

# Step 1: Load drivable road graph of Chalisgaon
place = "Chalisgaon, Maharashtra, India"
G = ox.graph_from_place(place, network_type="drive")

# Step 2: Plot and collect clicks
fig, ax = ox.plot_graph(G, show=False, close=False)
clicked_coords = []

def onclick(event):
    if event.xdata and event.ydata:
        clicked_coords.append((event.ydata, event.xdata))  # (lat, lon)
        print(f"Selected: lat={event.ydata}, lon={event.xdata}")
        if len(clicked_coords) == 2:
            fig.canvas.mpl_disconnect(cid)
            plt.close()

cid = fig.canvas.mpl_connect('button_press_event', onclick)
plt.title("Click origin and then destination")
plt.show()

# Step 3: Ensure two points were clicked
if len(clicked_coords) != 2:
    raise ValueError("You must click exactly two points!")

# Step 4: Find nearest graph nodes to clicked points
(orig_lat, orig_lon), (dest_lat, dest_lon) = clicked_coords
orig_node = ox.distance.nearest_nodes(G, orig_lon, orig_lat)
dest_node = ox.distance.nearest_nodes(G, dest_lon, dest_lat)

# Step 5: Define heuristic function
def euclidean_heuristic(u, v):
    x1, y1 = G.nodes[u]['x'], G.nodes[u]['y']
    x2, y2 = G.nodes[v]['x'], G.nodes[v]['y']
    return sqrt((x1 - x2)**2 + (y1 - y2)**2)

# Step 6: Run A* to find route
route = nx.astar_path(G, orig_node, dest_node, heuristic=euclidean_heuristic, weight='length')

# Step 7: Plot the route
fig, ax = ox.plot_graph_route(G, route, route_linewidth=4, node_size=0, bgcolor="white")
