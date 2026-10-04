from typing import Any, Dict, List

import networkx as nx

from app.graph.models import GraphEdge, GraphNode
from app.ingest.normalize import Transfer


class GraphBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_transfers(self, transfers: List[Transfer]):
        for t in transfers:
            # Update/add source node
            if not self.graph.has_node(t.from_addr):
                self.graph.add_node(t.from_addr, data=GraphNode(chain=t.chain, address=t.from_addr, first_seen=t.ts, last_seen=t.ts))
            else:
                node_data: GraphNode = self.graph.nodes[t.from_addr]["data"]
                node_data.first_seen = min(node_data.first_seen, t.ts) if node_data.first_seen else t.ts
                node_data.last_seen = max(node_data.last_seen, t.ts) if node_data.last_seen else t.ts

            # Update/add dest node
            if not self.graph.has_node(t.to_addr):
                self.graph.add_node(t.to_addr, data=GraphNode(chain=t.chain, address=t.to_addr, first_seen=t.ts, last_seen=t.ts))
            else:
                node_data: GraphNode = self.graph.nodes[t.to_addr]["data"]
                node_data.first_seen = min(node_data.first_seen, t.ts) if node_data.first_seen else t.ts
                node_data.last_seen = max(node_data.last_seen, t.ts) if node_data.last_seen else t.ts

            # Update/add edge

            # networkx multi-edge by manual aggregate or MultiDiGraph? The prompt says "NetworkX DiGraph" with edges aggregated by src, dst, asset.
            # But DiGraph only has one edge between u, v. We can use u, v and store a dict of assets inside the edge, OR use MultiDiGraph.
            # Let's use DiGraph and store a dictionary of assets, or use a MultiDiGraph where key=asset.
            # The simplest is DiGraph, with an edge holding a dict of `GraphEdge` keyed by asset.
            # Let's just do that.
            if not self.graph.has_edge(t.from_addr, t.to_addr):
                self.graph.add_edge(t.from_addr, t.to_addr, assets={})

            edge_data = self.graph.edges[t.from_addr, t.to_addr]["assets"]
            if t.asset not in edge_data:
                edge_data[t.asset] = GraphEdge(
                    src=t.from_addr,
                    dst=t.to_addr,
                    asset=t.asset,
                    total_amount=t.amount,
                    tx_count=1,
                    first_ts=t.ts,
                    last_ts=t.ts,
                    tx_refs=[t.tx_hash]
                )
            else:
                e: GraphEdge = edge_data[t.asset]
                e.total_amount += t.amount
                e.tx_count += 1
                e.first_ts = min(e.first_ts, t.ts)
                e.last_ts = max(e.last_ts, t.ts)
                if t.tx_hash not in e.tx_refs:
                    e.tx_refs.append(t.tx_hash)

    def get_graph(self) -> nx.DiGraph:
        return self.graph

    def get_node(self, address: str) -> GraphNode | None:
        if self.graph.has_node(address):
            return self.graph.nodes[address]["data"]
        return None

    def get_neighbors(self, address: str) -> List[str]:
        if self.graph.has_node(address):
            return list(self.graph.successors(address))
        return []

    def export_json(self) -> Dict[str, Any]:
        nodes = []
        for n, d in self.graph.nodes(data=True):
            node_data: GraphNode = d["data"]
            nodes.append(node_data.model_dump(mode='json'))

        edges = []
        for u, v, d in self.graph.edges(data=True):
            for asset, edge_data in d["assets"].items():
                edges.append(edge_data.model_dump(mode='json'))

        return {"nodes": nodes, "edges": edges}
