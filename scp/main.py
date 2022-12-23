from dataclasses import dataclass
from enum import Enum
from queue import Queue

SCP_MAP = {
    "WA": ["NT", "SA"],
    "NT": ["WA", "SA", "Q"],
    "SA": ["WA", "NT", "Q", "NSW", "V"],
    "Q": ["NT", "SA", "NSW"],
    "NSW": ["Q", "SA", "V"],
    "V": ["SA", "NSW"],
    "T": [],
}


class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


ALL_COLORS_LIST = [Color.RED, Color.GREEN, Color.BLUE]


class Node:
    def __init__(self, name):
        self.name = name
        self.color = None
        self.neighbors = []
        self.available_colors = ALL_COLORS_LIST.copy()

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self) -> str:
        return f"<{self.name} | {self.color}>"

    def add_neighbor(self, node):
        self.neighbors.append(node)

    def remove_potential_color(self, color: Color):
        self.available_colors.remove(color)

    def check_constraints(self) -> bool:
        # ignore for uncolored node
        if self.color is None:
            return True
        for neighbor in self.neighbors:
            if neighbor.color == self.color:
                return False
        return True

    def do_color(self, color: Color):
        self.color = color
        # self.available_colors = []
        self.available_colors = [color]

    def uncolored_neighbors(self) -> list['Node']:
        return [neighbor for neighbor in self.neighbors if neighbor.color is None]

    def uncolored_neighbors_count(self) -> int:
        return len(self.uncolored_neighbors())

    def is_assigned(self) -> bool:
        return bool(self.color)


class Graph:
    def __init__(self, str_graph: dict[str, list[str]]):
        self.nodes = []
        country_str_to_node = {}

        # create nodes for countries
        for country in SCP_MAP.keys():
            country_node = Node(country)
            country_str_to_node[country] = country_node
            self.nodes.append(country_node)

        # add neighbors to nodes
        for country, neighbors in SCP_MAP.items():
            country_node = country_str_to_node[country]
            for neighbor in neighbors:
                country_node.add_neighbor(country_str_to_node[neighbor])

        # print nodes and their neighbors. for DEBUG
        for country_node in self.nodes:
            print(f"{country_node}: {country_node.neighbors}")

    def __repr__(self) -> str:
        return f"<Graph | {self.nodes}>"

    def check_nodes_constraints(self) -> bool:
        for node in self.nodes:
            if not node.check_constraints():
                return False
        return True

    def is_complete(self) -> bool:
        # ? maybe check if constraints are satisfied ?
        for node in self.nodes:
            if not node.is_assigned():
                return False
        return True

    def get_unassigned_node(self) -> Node | None:
        # TODO maybe pick based on MAX node.uncolored_neighbors_count
        for node in self.nodes:
            if not node.is_assigned():
                return node
        return None

    def get_all_edges(self) -> list[tuple[Node, Node]]:
        edges = []
        for node in self.nodes:
            for neighbor in node.neighbors:
                edges.append((node, neighbor))
        return edges

    # def get_all_unique_edges(self) -> set[set[Node]]:
    #     edges = self.get_all_edges()
    #     unique_edges = set()
    #     for node in self.nodes:
    #         for neighbor in node.neighbors:
    #             unique_edges.add({node, neighbor})
    #     return unique_edges


def chronologic_backtrack(graph: Graph):
    # if complete, return
    if graph.is_complete():
        print("Graph is complete")
        return graph
    unassigned_node = graph.get_unassigned_node()
    print(f"unassigned node: {unassigned_node}")
    # for color in unassigned_node.available_colors:
    for color in ALL_COLORS_LIST:
        unassigned_node.color = color
        print(f"newly assigned node: {unassigned_node}")
        if graph.check_nodes_constraints():
            print(f"constraints satisfied for {unassigned_node}")
            result = chronologic_backtrack(graph)
            if result:
                print("result found")
                return result
            else:
                print("result not found")
        else:
            print(f"constraints NOT satisfied for {unassigned_node}")
        unassigned_node.color = None
    return None


def edge_consistency_backtrack(graph: Graph):
    # if complete, return
    if graph.is_complete():
        print("Graph is complete")
        return graph
    unassigned_node = graph.get_unassigned_node()
    print(f"unassigned node: {unassigned_node}")
    available_colors_backup = unassigned_node.available_colors.copy()
    for color in available_colors_backup:
        # unassigned_node.color = color
        unassigned_node.do_color(color)
        print(f"newly assigned node: {unassigned_node}")
        if graph.check_nodes_constraints():
            print(f"constraints satisfied for {unassigned_node}")
            if ac3(graph):
                print("AC3 consistent")
                # TODO copy graph
                result = edge_consistency_backtrack(graph)
                if result:
                    print("result found")
                    return result
                else:
                    print("result NOT found")
            else:
                print("AC3 INconsistent")
        else:
            print(f"constraints NOT satisfied for {unassigned_node}")
        # revert coloring
        unassigned_node.color = None
        unassigned_node.available_colors = available_colors_backup.copy()
    return None


def ac3(graph: Graph) -> bool:
    all_edges = graph.get_all_edges()

    queue = Queue()
    for edge in all_edges:
        queue.put(edge)

    while not queue.empty():
        node1, node2 = queue.get()
        print(f"edge: {edge}")
        node1_colors_backup = node1.available_colors.copy()
        if revise(graph, node1, node2):
            if len(node1.available_colors) == 0:
                # revert removed potential colors
                node1.available_colors = node1_colors_backup
                return False
            # for neighbor in node1.uncolored_neighbors():
            for neighbor in node1.neighbors:
                if neighbor != node2:
                    queue.put((neighbor, node1))
    return True


def revise(graph, node1: Node, node2: Node) -> bool:
    revised = False
    # copying node1 colors, to avoid delete from a list which is being iterated
    node1_colors_backup = node1.available_colors.copy()
    for node1_color in node1_colors_backup:
        remove_node1_color = True
        for node2_color in node2.available_colors:
            if node1_color != node2_color:
                # return False
                remove_node1_color = False
                break
        if remove_node1_color:
            node1.remove_potential_color(node1_color)
        revised = True
    return revised


def main():
    # country_nodes = create_node_graph(SCP_MAP)
    graph = Graph(SCP_MAP)
    # completed_graph = chronologic_backtrack(graph)
    completed_graph = edge_consistency_backtrack(graph)
    # print(completed_graph)
    # print(graph.get_all_unique_edges())
    # ac3(graph)
    print(graph.get_all_edges())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
