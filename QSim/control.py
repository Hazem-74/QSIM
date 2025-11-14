###############################################
##########         Imports        #############
###############################################

import sys
import os
from PyQt6.QtWidgets import (
     QApplication, QMainWindow
    )
from viewer import *
from model import *
from collections import deque



###############################################
##########         Classes        #############
###############################################

class MainWindow(QMainWindow):
    '''
    The main controller class of the application. Orchestrates the working of backend and frontend together.

    Inherits from :class:`QMainWindow`

    :ivar ui: The ui part of the application, containing all elements that are viewed to the user.
    :vartype ui: Ui_MainWindow

    :ivar graph: The graph of the system that is used for backend calculations
    :vartype graph: Graph
    '''
    # Constructor
    def __init__(self) -> None:
        '''
        Initializes a :class:`MainWindow` instance.

        :return: This method does not return anything.
        :rtype: None
        '''
        # call parent constructor
        super(MainWindow, self).__init__()

        # attatch UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # start with no graph
        self.graph = Graph()

        # connect control buttons
        self.ui.connect_play_button(self.simulate)
        self.ui.connect_exit_button(self.exit)

        # get the limits of the grid
        self.grid_rows, self.grid_cols = self.ui.get_grid_size()


    # called when play button is clicked
    def simulate(self) -> None:
        '''
        Puts the application in simulation mode to simulate the optical setup currently presented on the grid.

        This method is called when the ``playButton`` is clicked.

        It applies the following:
        1- Builds the steup graph.
        2- Calculates the final state vector of the system.
        3- Visualizes the graph and the vector.

        :return: This method does not return anything.
        :rtype: None
        '''
        # build the new graph
        self.graph = self.build_graph()

        # TODO: Complete this function
        final_quantum_state = self.graph.calculate_results(visualize=True)
        

        # Visualize the state vector
        self.ui.visualize_vector(final_quantum_state)


        
        ## OBSELETE & TO BE DELETED ##

        # # step 1: get all lasers and grid size
        # lasers = self.ui.get_lasers()
        # rows, cols = self.ui.get_grid_size()

        # # HACK: enforce the number of lasers to be only 1
        # assert len(lasers) <= 1, "Only one laser allowed (for now)"


        # # step 2: apply operations for each laser
        # for laser in lasers:

        #     mirror = self.get_next_element(laser.row, laser.col, laser.orientation)

        #     if mirror:
        #         self.ui.move_photon((laser.row, laser.col), (mirror.row, mirror.col), laser.orientation)

        #     if mirror.__class__ == Mirror:
        #          element = self.get_next_element(mirror.row, mirror.col, mirror.orientation+1)
        #          if element:
        #             self.ui.move_photon((mirror.row, mirror.col), (element.row, element.col), mirror.orientation+1)


    def build_graph(self) -> Graph:
        '''
        Builds the graph of the optical setup (elements and their relative positioning) presented on the grid.

        :return: Returns the constructed graph object.
        :rtype: Graph 
        '''
        # create a new graph
        graph = Graph()

        # get a list of all lasers
        lasers = self.ui.get_lasers()

        # create a set to keep track of visited elements
        visited = set()

        # queue of the BFS traversal algorithm
        queue = deque()

        # start from each laser to create a graph
        for laser in lasers:


            queue.append((laser, laser.orientation))
            visited.add(laser)
            

            while queue:
                
                # get the element on the front of the queue
                element, orient = queue.popleft()

                successors = self.__get_successors(element, orient)

                for next_element, next_orient in successors:
                    
                    # Add a wall to the graph
                    if next_element is None:
                        continue

                    # Append an edge to the graph here
                    graph.add_connection(element, next_element)

                    # add the element to the queue, if not previously added
                    if next_element not in visited:
                        queue.append((next_element, next_orient))
                        visited.add(next_element)

        # HACK: Assert that the graph is acyclic
        # HACK: If you remove this line, you must modify graph creation to allow multiple edges between the same two nodes
        assert nx.is_directed_acyclic_graph(graph), "The graph is acyclic"

        return graph

                    


    def __get_successors(self, element: GridItem, orentation: int) -> list:
        '''
        This is an auxiliary function and is inteded for internal use only.

        Given and element and the orientation in which the light enters the element, returns the next element(s) in the light travel direction (if any).
        For example, if a light enters a mirror in a given direction, returns the next element after reflection by the mirror.
        For the case of a beamsplitter, two elements will be returned.

        :param element: The element at which the traversal should start.
        :type element: GridItem

        :param orientation: The direction of traversal starting from the given element.
        :type orientation: int

        :return: Returns a list of successors. The list would contain two elements for a beamsplitter and one element for the test of element types.
        :rtype: list
        '''
        # list of next successors
        successors = []

        # list of orientations or traversal
        orientations = element.get_next_orient(orentation)

        # append each successor element for each orientation
        for orient in orientations:

            successors.append((self.__get_next_element_in_dir(element, orient), orient))

        # return a list of succesors
        return successors
        
        
    def __get_next_element_in_dir(self, element: GridItem, orientation: int) -> Union[GridItem,None]:
        '''
        This is an auxiliary method and is inteded for internal use only.

        This method is used as part of the traversal algorithm. Given an element and a next orientation, gets the next element in that specific direction.

        :param element: The element at which the traversal should start.
        :type element: GridItem

        :param orientation: The direction of traversal starting from the given element.
        :type orientation: int

        :return:
        :rtype: GridItem | None
        '''
        # get the row and col of the element
        x, y = element.row, element.col


        # get the direction of increment/decrement based on orientation of movement
        dx, dy = self.__get_dx_dy_from_orientation(orientation)

    
        # traverse till you find next element
        while self.__check_valid_position(x, y) :
            x += dx
            y += dy

            element = self.ui.get_item_at(x, y)

            # if an element is found, return it
            if element:
                return element
            
        # return none if no elements are found
        return GridWall(x, y)
    

    
    def __get_dx_dy_from_orientation(self, orientation: int) -> tuple[int, int]:
        '''
        This is an method function and is inteded for internal use only.

        Calculates the next increase/decrease in position to get the next step in the grid, given an orientation.

        :param orientation:The direction of traversal.
        :type orientation: int

        :return: Returns a tuple of the step (dx, dy)
        :rtype: tuple[int, int]
        '''
        if orientation == 0:
            dx, dy = (0, +1)
        elif orientation == 1:
            dx, dy = (+1, 0)
        elif orientation == 2:
            dx, dy = (0, -1)
        else:
            dx, dy = (-1, 0)

        return dx, dy
    
    
    def __check_valid_position(self, x:int, y:int) -> bool:
        '''
        This is an auxiliary method and is inteded for internal use only.

        Checks if a given position is within the grid's bounds or not.

        :param x: The row number.
        :type x: int

        :param x: The column number.
        :type y: int

        :return: Returns :literal:`True` if the position is within the grid's bounds, otherwise returns :literal:`False`.
        :rtype: bool
        '''
        if (x >= 0) and (x < self.grid_rows) and (y < self.grid_cols) and (y >= 0):
            return True
        else:
            return False
        

    def exit(self) -> None:
        '''
        Terminates the application.

        :return: This method does not return anything.
        :rtype: None
        '''
        sys.exit()





###############################################
############         Main        ##############
###############################################
if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())