#!/usr/bin/env python3
"""Visualize the supervisor agent graph structure."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.graph import graph
def show_graph():
    graph.get_graph().draw_mermaid_png(output_file_path="Agent_Graph.png")
if __name__ == "__main__":
    show_graph()