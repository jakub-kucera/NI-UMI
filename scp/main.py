from dataclasses import dataclass
from enum import Enum

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


def backtrack():
    # if complete, return
    pass


def main():
    # country_nodes = create_node_graph(SCP_MAP)
    graph = Graph(SCP_MAP)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
