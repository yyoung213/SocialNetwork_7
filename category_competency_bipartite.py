import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Load the data
file_path = 'competencies_by_category_eng.xlsx - Sheet1.csv'
df = pd.read_csv(file_path)

# Print data info to confirm columns and types
print("Data Information:")
df.info()

print("\nData Head:")
print(df.head())

# --- Create the bipartite graph ---
B = nx.Graph()

# Get unique nodes for each set
# Drop any potential NaN values first
df_cleaned = df.dropna(subset=['Competency', 'Category'])
competencies = df_cleaned['Competency'].unique()
categories = df_cleaned['Category'].unique()

# Add nodes with the bipartite attribute
B.add_nodes_from(competencies, bipartite=0) # Set 0 for competencies
B.add_nodes_from(categories, bipartite=1)  # Set 1 for categories

# Add edges from the DataFrame
edges = list(zip(df_cleaned['Competency'], df_cleaned['Category']))
B.add_edges_from(edges)

# --- Visualization ---
plt.figure(figsize=(20, 18)) # Increased figure size

# Define node colors
color_map = []
for node in B:
    if node in categories:
        color_map.append('skyblue')
    else:
        color_map.append('lightgreen')

# Get the bipartite layout
# This layout places the two sets of nodes in distinct columns
pos = nx.bipartite_layout(B, categories)

# Draw the network
nx.draw_networkx_nodes(B, pos, node_color=color_map, node_size=1000, alpha=0.9)
nx.draw_networkx_edges(B, pos, alpha=0.4)
# Draw labels, adjust font size
nx.draw_networkx_labels(B, pos, font_size=10, font_weight='bold')

plt.title('Bipartite Network of Competencies and Categories', fontsize=22)
plt.axis('off') # Hide the axes
plt.savefig('competency_network.png', bbox_inches='tight', dpi=150)

print("\nNetwork creation complete. Image 'competency_network.png' saved.")

# --- Basic Analysis ---
# Get the two sets of nodes from the graph properties
category_nodes = {n for n, d in B.nodes(data=True) if d['bipartite']==1}
competency_nodes = {n for n, d in B.nodes(data=True) if d['bipartite']==0}

print(f"\nTotal nodes: {B.number_of_nodes()}")
print(f"Number of competencies: {len(competency_nodes)}")
print(f"Number of categories: {len(category_nodes)}")
print(f"Total edges (relationships): {B.number_of_edges()}")

# Calculate degrees for categories (how many competencies each has)
category_degrees = {node: B.degree(node) for node in category_nodes}
sorted_categories = sorted(category_degrees.items(), key=lambda item: item[1], reverse=True)

print("\n--- Top 5 Categories by Number of Competencies ---")
for i, (category, degree) in enumerate(sorted_categories[:5]):
    print(f"{i+1}. {category}: {degree} competencies")

# Save the full sorted list to a text file
with open('category_degree_ranking.txt', 'w') as f:
    f.write("Categories Ranked by Number of Competencies:\n")
    f.write("==============================================\n")
    for i, (category, degree) in enumerate(sorted_categories):
        f.write(f"{i+1}. {category}: {degree}\n")

print("\nFull ranking of categories saved to 'category_degree_ranking.txt'")
