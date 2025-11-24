import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

st.title("Friendship Network")

# --- Build graph ---
G = nx.Graph()

nodes = [
    "Alice","Bob","Charlie","Diana","Eve",
    "Frank","Grace","Hannah","Ian","Jack"
]

edges = [
    ("Alice","Bob"), ("Alice","Charlie"), ("Bob","Charlie"),
    ("Charlie","Diana"), ("Diana","Eve"), ("Bob","Diana"),
    ("Frank","Eve"), ("Eve","Ian"), ("Diana","Ian"),
    ("Ian","Grace"), ("Grace","Hannah"), ("Hannah","Jack"),
    ("Grace","Jack"), ("Charlie","Frank"), ("Alice","Eve"),
    ("Bob","Jack")
]

G.add_nodes_from(nodes)
G.add_edges_from(edges)

# --- Degree ---
degree = dict(G.degree())
degree_df = pd.DataFrame.from_dict(degree, orient="index", columns=["degree"])
st.subheader("Degrees")
st.dataframe(degree_df.sort_values("degree", ascending=False))

# --- Centrality ---
bet = nx.betweenness_centrality(G)
clo = nx.closeness_centrality(G)

central_df = pd.DataFrame({
    "betweenness": bet,
    "closeness": clo,
    "degree": degree
}).sort_values("betweenness", ascending=False)

st.subheader("Centrality Measures")
st.dataframe(central_df)

most_influential = max(bet, key=bet.get)
st.write(f"**Most influential (highest betweenness): {most_influential}**")

# --- Communities ---
from networkx.algorithms.community import greedy_modularity_communities
communities = list(greedy_modularity_communities(G))

st.subheader("Communities")
for i, comm in enumerate(communities, 1):
    st.write(f"Group {i}: {', '.join(comm)}")

# --- Visualization ---
st.subheader("Network Graph")

pos = nx.spring_layout(G, seed=1)

plt.figure(figsize=(7,6))

# Color influential node red, others blue
colors = ["red" if n == most_influential else "skyblue" for n in G.nodes()]

nx.draw(G, pos,
        with_labels=True,
        node_color=colors,
        node_size=600,
        edge_color="gray")

st.pyplot(plt.gcf())

# --- Comments ---
st.subheader("Findings Summary")
st.write("""
- Degree and centrality show who is most connected.
- Betweenness centrality identifies **Bob** as the most influential.
- Communities reveal natural clusters of friends.
- Graph layout visually shows how groups connect through key people.
""")
