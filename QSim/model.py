#######################################################
##########         Notes for later        #############
#######################################################





#######################################################
##############         Imports        #################
#######################################################
import networkx as nx
import numpy as np
from collections import defaultdict, deque
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
from viewer import *



#########################################################
##############         Functions        #################
#########################################################
def is_power_of_two(n: int) -> bool:
    '''
    Checks if a given integer is a power of 2.
    
    :param n: The integer to be checked.
    :type n: int

    :return: Returns :literal:`True` if the integer is a power of 2, otherwise returns :literal:`False`.
    :rtype: bool
    '''
    assert isinstance(n, int), f"Expected an integer, got {type(n)}"
    return n > 0 and (n & (n - 1)) == 0





#########################################################
################         Classes        #################
#########################################################

class State():
    '''
    
    '''
    def __init__(self, state_vector: np.array, **kwargs) -> None:
        
        self.state_vector = state_vector


    def get_dimension(self) -> int:

        return len(self.state_vector)


    def get_state_vector(self) -> np.array:

        return self.state_vector


    def __str__(self):
        return f"State({self.state_vector})"


    @classmethod
    def from_state_vector(cls, state_vector):
        return cls(state_vector)


    @classmethod
    def from_path_modes(cls, dimension):
        
        state_vector = np.zeros(dimension)
        state_vector[0] = 1
        return cls(state_vector, dimension=dimension)
        


class Operation():

    def __init__(self, dimension):
        
        self.matrix = np.identity(dimension, dtype=complex)
        self.dimension = dimension


    def apply_operation_on_state(self, in_state: State) -> State:

        in_state_vector = in_state.get_state_vector()

        out_state_vector = np.dot(self.matrix, in_state_vector)

        return State.from_state_vector(out_state_vector)

    def cascade_operation(self, other_operation) -> None:

        self.matrix = np.dot(self.matrix, other_operation.matrix)


    def modify_to_beam_splitter(self, in1, in2, out1, out2) -> None:

        assert (in1 < self.dimension) and (in2 < self.dimension) and \
            (out1 < self.dimension) and (out2 < self.dimension), "locations must be within the dimension limits"

        # replace target columns with zero column
        self.matrix[:, in1] = 0
        self.matrix[:, in2] = 0

        # enter the values of beam splitter operation
        self.matrix[out1, in1] = 1/np.sqrt(2)
        self.matrix[out1, in2] = 1j/np.sqrt(2)
        self.matrix[out2, in1] = 1j/np.sqrt(2)
        self.matrix[out2, in2] = 1/np.sqrt(2)


    def __str__(self):
        return f"Operation(\n{self.matrix}\n)"

        


class Graph(nx.MultiDiGraph):

    def __init__(self,):
        super().__init__()

        # default dictionary for counting elements for each type
        self.counts = defaultdict(int)

        # default dictionary to store elements of each type
        self.elements = defaultdict(list)

        # initialize variables
        self.path_modes_count = 0



    def add_element(self, element: GridItem) -> str:

        # assign an ID to the element
        id = element.__class__.__name__ + f"({element.row},{element.col})"
        
        # increase the counts of elements of this class
        self.counts[element.__class__] += 1

        # append the element to the list
        self.elements[element.__class__].append({
            'element':element,
            'id': id
        })

        # add node with the id of the element
        self.add_node(id,
                      pos=(element.col, element.row),
                      element=element)

        # return the element's id
        return id



    def add_connection(self, from_element: GridItem, to_element: GridItem) -> None:

        # add the two elements to the graph and get their ids
        from_id = self.add_element(from_element)
        to_id   = self.add_element(to_element)

        # Calculate the distance between both elements
        weight = abs(from_element.row - to_element.row) + abs(from_element.col - to_element.col)

        # add an edge between the two ids
        self.add_edge(from_id, to_id,
                      weight=weight,
                      label="",
                      state = None)



    def __visualize_graph(self) -> None:

        # extract positioning of nodes
        pos = {
            node:self.nodes[node]['pos'] for node in self.nodes
        }

        # labeling edges
        edge_labels = {(u, v): f'{data["weight"]}, |{data["label"]}>' for u, v, data in self.edges(data=True)}

        # draw the graph
        nx.draw(self, pos, with_labels=True, arrows=True)
        nx.draw_networkx_edge_labels(self, pos, edge_labels=edge_labels, font_color='red', font_size=12)
        plt.show()


    def __label_paths_temp(self):

        # HACK: Assuming a single laser device
        start_id = self.elements[Laser][0]['id']
        
        # get a list of edges using bfs
        bfs_edges = list(nx.edge_bfs(self, source=start_id))

        # dictionary to hold the in_labels of all nodes
        in_labels = {start_id:[0]}


        last_id = start_id
        for i in range(len(bfs_edges)):

            # terminal nodes of the current edge
            start_id = bfs_edges[i][0]
            end_id   = bfs_edges[i][1]

            # case 1: a node with two labeled inputs
            





    def __label_paths(self):

        # HACK: Assumming single laser device
        start_id = self.elements[Laser][0]['id']

        # get the DFS edges
        # HACK: Loops are not completely labeled
        # TODO: change the way you get the edges
        dfs_edges = list(nx.dfs_edges(self, source=start_id))

        # assign a label to every DFS edge
        label = 0
        for i in range(len(dfs_edges)):
            
            if (i == 0) or (dfs_edges[i-1][1] == dfs_edges[i][0]):
                pass
            else:
                label+=1
            self[dfs_edges[i][0]][dfs_edges[i][1]][0]['label'] = label
        
        # store the number of path modes
        self.path_modes_count = label + 1

    

    def calculate_results(self, visualize=False) -> np.array:

        # set labels for paths before starting
        self.__label_paths()

        # HACK: start with an initial state for the path qubit only
        state = State.from_path_modes(self.path_modes_count)

        # Optional: Visualize Graph
        if visualize:
            self.__visualize_graph()

        # start with a node group of all lasers
        node_group = []
        for laser in self.elements[Laser]:
            node_group.append(laser['id'])


        while node_group:

            # start an empty new node group
            next_node_group = []

            # operation
            operation = Operation(self.path_modes_count)

            # iterate over each node
            for node in node_group:
                
                # HACK: only considering the beam splitter for now
                if self.nodes[node]['element'].__class__ == BeamSplitter:

                    # get the input labels
                    in_edges = self.in_edges(node, data=True)
                    in_labels = [data['label'] for source, target, data in in_edges]

                    # get the output labels
                    out_edges = self.out_edges(node, data=True)
                    out_labels = [data['label'] for source, target, data in out_edges]

                    # apply the operation of the beam splitter
                    # HACK: Working on a special case were the input labels are the same as the output labels
                    beam_splitter_operation = Operation(self.path_modes_count)
                    beam_splitter_operation.modify_to_beam_splitter(
                            in1=out_labels[0], 
                            in2=out_labels[1], 
                            out1=out_labels[0], 
                            out2=out_labels[1], 
                            )
                    operation.cascade_operation(beam_splitter_operation)

                # create the next node group
                for _, next_node, edge_data in self.out_edges(node, data=True):
                    next_node_group.append(next_node)

            state = operation.apply_operation_on_state(state)


            node_group = next_node_group
        
        
        return state.get_state_vector()
        
        
        