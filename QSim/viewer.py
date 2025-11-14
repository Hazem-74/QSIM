#######################################################
##########         Notes for later        #############
#######################################################




#######################################################
##############         Imports        #################
#######################################################
from PyQt6.QtWidgets import *
from PyQt6.QtGui     import *
from PyQt6.QtCore    import *
from typing import Union
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
)
from matplotlib.figure import Figure
import numpy as np
from typing import Union, Callable






#######################################################
#############         Constants        ################
#######################################################
LEFT_MENU_WIDTH     = 230
BACKGROUND_COLOR    = 'white'
TEXT_COLOR          = 'black'
SIMULATION_AREA_MARGINS = 15
SIMULATION_AREA_BG_COLOR = 'grey'
GRID_AREA_BG_COLOR = 'white'
GRID_ROWS = 20
GRID_COLS = 50
GRID_CELL_SIZE = 50
PHOTON_RADIUS = 10


# icons
LASER_ICON = "images/laser.png"
DETECTOR_ICON = "images/detector.png"
BEAM_SPLITTER_ICON = "images/beam_splitter.png"
MIRROR_ICON = "images/mirror.png"
POLAR_BEAM_SPLITTER_ICON = "images/polarizing_beam_splitter.png"
MIRROR_ICON = "images/mirror.png"


# display text
LASER_TEXT = "Laser"
DETECTOR_TEXT = "Detector"
BEAM_SPLITTER_TEXT = "Beam Splitter"
MIRROR_TEXT = "Mirror"
POLAR_BEAM_SPLITTER_TEXT = "Polarizing Beam Splitter"
MIRROR_TEXT = "Mirror"




#######################################################
###############         Enums        ##################
#######################################################






#######################################################
##############         Globals        #################
#######################################################
icons = {}
components = {}
texts = {}
dragged_item = None




#######################################################
#############  user-defined functions  ################
#######################################################

def rotate_icon(icon: QIcon, angle: int) -> QIcon:
    '''Rtotates an icon with a given angle

    Args:
        icon (QIcon): The icon intended to be rotated.
        angle (int): The amount of rotation in degrees. Takes an integer value from 0 to 360 degrees. 

    Returns:
        The icon after applying rotation.
    
    '''

    # Convert the QIcon to QPixmap
    pixmap = icon.pixmap(64, 64)  # Set the size as needed
    
    # Create a transformation to rotate
    transform = QTransform().rotate(angle)
    
    # Apply the transformation to the pixmap
    rotated_pixmap = pixmap.transformed(transform)
    
    # return the new QIcon
    return QIcon(rotated_pixmap)




#######################################################
##############         Classes        #################
#######################################################


class VLine(QFrame):
    '''
    A line that spans the entire window vertically, regardless of the window's size.
    
    This class inherits from ``QFrame`` and modifies the properties to produce a line.
    It adds to extra attributes or methods to those originally inherited from `QFrame`.

    '''

    def __init__(self, **kwargs) -> None:
        '''
        Initializes a ``VLine`` instance
        '''
        super().__init__(**kwargs)

        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)


class HLine(QFrame):
    '''
    A line that spans the entire window horizontally, regardless of the window's size.
    
    This class inherits from `QFrame` and modifies the properties to produce a line.
    It adds to extra attributes or methods to those originally inherited from `QFrame`.

    '''


    def __init__(self, **kwargs) -> None:
        '''
        Initializes an ``HLine`` instance
        '''
        super().__init__(**kwargs)

        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)


class VSpacer(QSpacerItem):
    '''
    A vertical spacer that extends maximally within a widget.

    It takes up a maximal vertical space, aligning items above it at the top of the container and items beneath it at the bottom of the container.
    It inherits from ``QSpacerItem`` and adds no extra attributes or methods to it.
    '''

    def __init__(self, **kwargs) -> None:
        '''
        Initializes a ``VSpacer`` instance.
        '''
        super().__init__(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding, **kwargs)


class HSpacer(QSpacerItem):
    '''
    A horizontal spacer that extends maximally within a widget.

    It takes up a maximal horizontal space, aligning items before it to the leftmost of the container and items after it to the rightmost of the container.
    It inherits from ``QSpacerItem`` and adds no extra attributes or methods to it.
    '''

    def __init__(self, **kwargs) -> None:
        '''
        Initializes an ``HSpacer`` instance.
        '''
        super().__init__(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum, **kwargs)


class Photon(QWidget):
    '''
    Appears as a red dot on the screen to indicate a photon.

    Inherits from ``QWidget`` and overrides its properties to achieve the desired appearance.
    '''

    def __init__(self, parent=None) -> None:
        '''
        Initializes a ``Photon`` instance.
        '''
        super().__init__(parent)

        # always start in a hidden state
        self.hide()

        # Set a fixed size for the photon
        self.setFixedSize(PHOTON_RADIUS, PHOTON_RADIUS)



    def paintEvent(self, event:QPaintEvent) -> None:
        '''
        Changes the ``paintEvent`` of ``Photon`` so it appears as a red dot on the screen.

        Args:
            event (QPaintEvent): Provides information about the repainting request.

        Returns:
            None
        '''
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # Enable anti-aliasing for smoother edges
        brush = QBrush(QColor(255, 0, 0))  # Red color
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)  # Remove border
        # Draw a circle centered in the widget
        radius = min(self.width(), self.height()) // 2
        painter.drawEllipse(self.rect().center(), radius, radius)




    def move_to_position(self, start_pos:tuple[int, int], end_pos:tuple[int, int], duration:int=1000) -> None:
        '''
        Simulates movement of a photon between two positions on the grid.
        The starting and ending positions are given in the form of the row and column within the grid.

        Args:
            start_pos (tuple[int, int]): the position that the photon path should start at. this is a tuple of two integers representing the row and column of the position.
            end_pos (tuple[int, int]): the position that the photon's path should end at.
            duration (int): The duration of the movement event in milliseconds.

        Returns:
            None
        '''

        # Set the starting position of the photon
        self.setGeometry(start_pos[0], start_pos[1], PHOTON_RADIUS, PHOTON_RADIUS)
        
        # show the photon on the ui
        self.show()

        # Create an animation to move the photon
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(duration)  # Animation duration (in milliseconds)
        
        # Starting and ending positions (QRect objects)
        start_rect = QRect(start_pos[0], start_pos[1], PHOTON_RADIUS, PHOTON_RADIUS)
        end_rect = QRect(end_pos[0], end_pos[1], PHOTON_RADIUS, PHOTON_RADIUS)

        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)


        # Connect the animation finished signal to delete the widget
        self.animation.finished.connect(self.deleteLater)

        # Start the animation
        self.animation.start()


class tool(QPushButton):
    '''
    A generic tool element of the left toolbar.

    Inherits from ``QPushButton`` to achieve the clickable appearance, but provides no action on clicking.

    Attributes:
        compType (): The type of the component the tool represents (e.g. LASER, BEAMSPLITTER, etc.).
    '''

    def __init__(self, type, **kwargs) -> None:
        '''
        Initializes a ``tool`` instance.

        Args:
            type (): The type of the component.

        Returns:
            None: This function does not return anything
        '''
        super().__init__(texts[type], **kwargs)

        self.compType = type

        # set palette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Button, QColor("white"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("black"))  # RGB for blue
        self.setPalette(palette)

        # set component icon
        self.setIcon(icons[type][0])


    def mouseMoveEvent(self, event: QMouseEvent):
        '''
        Overrides the mouse movement event inherited from ``QPushButton`` to achieve the drag and drop functionality for ``tool``.

        Args:
            event (QMouseEvent): Provides information about a mouse movement event, such as the position of the mouse pointer, button states, and modifiers (e.g., Shift or Ctrl keys).

        Returns:
            None: This method does not return anything.
        '''

        if event.buttons() == Qt.MouseButton.LeftButton:
            
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.compType)
            drag.setMimeData(mime)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            # TODO: uncomment this line and fix the position of the icon
            #pixmap = self.icon().pixmap(QSize(GRID_CELL_SIZE, GRID_CELL_SIZE))
            drag.setPixmap(pixmap)
            
            drag.setHotSpot(event.position().toPoint())

            drag.exec(Qt.DropAction.CopyAction)
            self.show() # Show this widget again, if it's dropped outside.


class ToolsListHeader(QLabel):
    '''
    The header title of the tools list.

    Inherits from ``QLabel`` and modifies attributes to achieve desired appearance properties.
    '''
    def __init__(self, headerText: str, **kwargs) -> None:
        '''
        Initializes a ``ToolsListHeader`` instance.

        Args:
            headerText (str): The text that shall be written on the title.
        
        Returns:
            None: This function does not return anything.

        '''
        super().__init__(text=headerText, **kwargs)

        # set ToolsListHeader attributes
        self.setObjectName("ToolsListHeader")
        self.setFrameShape(QFrame.Shape.Box)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(2*self.fontMetrics().height())


class ToolsListContents(QWidget):
    '''
    A container that carries tools in a sidebar's list of tools.

    Inherits from the generic ``QWidget``.
    '''

    def __init__(self, **kwargs) -> None:
        '''
        Initializes a ``ToolsListContents`` instance.

        Returns:
            None: This function does not return anything.
        '''
        super().__init__(**kwargs)

        # HACK: Add buttons to the list
        self.myLayout = QVBoxLayout(self)
        self.myLayout.setSpacing(0)
        self.setLayout(self.myLayout)

    
    def addTool(self, compType:str) -> None:
        '''
        Adds a tool to the tools list.
    
        Args:
            compType (str): The type of the component the tool represents.

        Returns:
            None: This function does not return anything.
        '''
        self.myLayout.addWidget(tool(compType))


class ToolsList(QFrame):
    '''
    A tools list that contains a group of tools along with a header title for the group.

    Inherits from ``QFrame``.

    Attributes:
        myHeader (ToolsListHeader): The header of the tools list. Displays the title.
        myContents (ToolsListContents): The actual contents of the list with is a list of ``tool`` objects.
    '''

    def __init__(self, headerText: str, **kwargs) -> None:
        '''
        Initializes a ``ToolsList`` instance.

        Args:
            headerText (str): The string appearing at the title of the list.

        Returns:
            None: This function does not return anything.
        '''
        super().__init__(**kwargs)

        # set ToolsList attributes
        self.setFrameShape(QFrame.Shape.Box)

        
        # Create a header for the list
        self.myHeader = ToolsListHeader(headerText)

        # Create list contents
        self.myContents = ToolsListContents()

        # Set ToolsList layout to vertical
        self.myLayout = QVBoxLayout(self)
        self.myLayout.addWidget(self.myHeader)
        self.myLayout.addWidget(self.myContents)
        self.myLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.myLayout)


    def addTool(self, type: str) -> None:
        '''
        Adds a tool to the list.

        Args:
            type (str): A string indicatin the type of the tool to be added.

        Returns:
            This function does not return anything.
        '''
        self.myContents.addTool(type)

        
class ToolsListsArea(QScrollArea):
    '''
    This is the entire area of tools lists within the sidebar.

    Contains several lists of tools (``ToolsList``), each with a specific header to give a title to the group of tools within the list.

    Attributes:
        myToolsLists (list): A list of all ``ToolsList`` objects included within the tools list area.
    '''

    def __init__(self, name=None, **kwargs) -> None:
        '''
        Initializes a ``ToolsListsArea`` instance.

        Args:
            name (str): The intenral name that shall be given to this instance.
        
        Returns:
            None: This function does not return anything.
        '''
        super().__init__(**kwargs)

        # set ToolsListArea attributes
        if name:
            self.setObjectName(name)
        self.setWidgetResizable(True)

        # start with an empty list of ToolsLists
        self.myToolsLists = [] 

        # Create the container widget
        self.containerWidget = QWidget()
        self.setWidget(self.containerWidget)
        

        # Set ToolsList layout to vertical
        self.containerWidgetLayout = QVBoxLayout(self.containerWidget)
        self.containerWidget.setLayout(self.containerWidgetLayout)
        self.containerWidgetLayout.setContentsMargins(0, 0, 0, 0)

        
        

    def addToolsList(self, newToolsList: ToolsList) -> None:

        self.myToolsLists.append(newToolsList)
        self.containerWidgetLayout.addWidget(newToolsList)


class GridItem(QPushButton):
    '''
    A generic parent class for all items that could be included in the grid (e.g. Laser, Beamsplitter, Mirror, etc.).

    Inherits from ``QPushButton`` to obtain button behavior.

    Attributes:
        type (): The type of this grid item (e.g. Laser, Beamsplitter, Mirror, etc.).
    '''

    def __init__(self, type, **kwargs) -> None:
        '''
        Initializes a ``GridItem`` instance.

        Args:
            type (TODO): The type of item being initialized.
        
        Returns:
            None: This method does not return anything.
        '''
        super().__init__(**kwargs)

        self.orientation = 0
        self.type = type

        # set icon
        self.setText("")
        self.setIconSize(self.size())
        self.setIcon(icons[self.type][self.orientation])

        # color palette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Button, QColor("white"))
        self.setPalette(palette)

        # set GridItem attributes
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # connect signals
        self.clicked.connect(self.rotate)


    def rotate(self) -> None:
        '''
        Rotates the item by 45 degrees on the screen.

        Returns:
            None: This method does not return anything.
        '''

        # calculate the new orientation indes
        self.orientation = (self.orientation + 1) % len(icons[self.type])

        # update to the new orientation
        self.setIcon(icons[self.type][self.orientation])


    def mouseMoveEvent(self, event: QMouseEvent):
        '''
        Overrides the mouse movement event inherited from ``QPushButton`` to achieve drag and drop functionality.
        
        Args:
            event (QMouseEvent): Provides information about a mouse movement event, such as the position of the mouse pointer, button states, and modifiers (e.g., Shift or Ctrl keys).

        Returns:
            None: This method does not return anything.
        '''
        if event.buttons() == Qt.MouseButton.LeftButton:


            # detach this item from its containing cell
            self.setParent(None)

            # register this object as being currently dragged
            global dragged_item
            dragged_item = self

            # create MimeData and Drag
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText("GridItem")
            drag.setMimeData(mime)

            # set visible pixmap of the drag object
            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.position().toPoint())


            drag.exec(Qt.DropAction.MoveAction)

    def get_next_orient(self, orientation: int) -> list:
        '''
        DEPRECATED
        '''
        return []
    

class GridWall(GridItem):
    '''
    Represents an item that is out of bounds of the grid.

    Although not an intuitive ``GridItem``, it helps in the backend logic.

    Attributes:
        row (int): The row number of ``GridWall`` within the grid.
        col (int): The column number of ``GridWall`` within the grid.
    '''
    def __init__(self, row: int, col: int) -> None:
        '''
        Initializes a ``GridWall`` instance.

        Args:
            row (int): the row number of the instance.
            col (int): the column number of the instance.

        Returns:
            None: This method does not return anything.
        '''

        self.row = row
        self.col = col


class Laser(GridItem):
    '''
    Represents a laser item within the grid.

    Inherits from ``GridItem`` and extends functionality to achieve the appearance and behavior of a laser.
    '''
    def __init__(self, **kwargs) -> None:
        '''
        Initializes a ``Laser`` instance.

        Returns:
            None: This method does not return anything.
        '''
        super().__init__(Laser.__name__, **kwargs)


    def get_next_orient(self, orientation: int) -> list:
        '''
        DEPRECATED
        '''
        if self.orientation == orientation:
            return [orientation]
        else:
            return []


class Detector(GridItem):
    '''
    Represents a detector item within the grid.

    Inherits from ``GridItem`` and extends functionality to achieve the appearance and behavior of a detector.
    '''
    def __init__(self, **kwargs) -> None:
        '''
        Initializes a ``Detector`` instance.
        '''
        super().__init__(Detector.__name__, **kwargs)


class BeamSplitter(GridItem):
    '''
    Represents a beamsplitter item within the grid.

    Inherits from ``GridItem`` and extends functionality to achieve the appearance and behavior of a beamsplitter.
    '''
    def __init__(self, **kwargs) -> None:
        '''
        Initializes a ``BeamSplitter`` instance.
        '''
        super().__init__(BeamSplitter.__name__, **kwargs)

    def get_next_orient(self, orientation: int):
        '''
        DEPRECATED
        '''
        reflected_orientation = (orientation + pow(-1, (self.orientation&1)+(orientation&1)) + 4) % 4
        return [orientation, reflected_orientation]


class PolarBeamSplitter(BeamSplitter):
    '''
    Represents a polarizing beamsplitter item within the grid.

    Inherits from ``GridItem`` and extends functionality to achieve the appearance and behavior of a polarizing beamsplitter.
    '''
    def __init__(self, **kwargs):
        '''
        Initializes a ``PolarBeamSplitter`` instance.
        '''
        GridItem.__init__(self, PolarBeamSplitter.__name__, **kwargs)


class Mirror(GridItem):
    '''
    Represents a mirror item within the grid.

    Inherits from ``GridItem`` and extends functionality to achieve the appearance and behavior of a mirror.
    '''
    def __init__(self, **kwargs):
        super().__init__(Mirror.__name__, **kwargs)
        '''
        Initializes a ``BeamSplitter`` instance.
        '''
    def get_next_orient(self, orientation: int):
        '''
        DEPRECATED
        '''
        reflected_orientation = (orientation + pow(-1, (self.orientation&1)+(orientation&1)) + 4) % 4
        return [reflected_orientation]

class GridCell(QFrame):
    '''
    A single cell within the simulation grid. Holds items that inherit from ``GridItem`` (e.g. Laser, Beamsplitter, etc.).

    Inherits from ``QFrame``.

    Attributes:
        row (int): stores the row of the cell within the grid.
        col (int): stores the col of the cell within the grid.
    '''
    def __init__(self, row, col, **kwargs) -> None:
        '''
        Initializes a ``GridCell`` instance.

        Args:
            row (int): the row number of the cell instance.
            col (int): the col number of the cell instance.

        Returns:
            None: This method does not return anything.
        '''
        super().__init__(**kwargs)

        # set the location of the cell within the grid
        self.row = row
        self.col = col

        # set GridCell attributes
        self.setAcceptDrops(True)
        self.setFixedSize(GRID_CELL_SIZE, GRID_CELL_SIZE)

        # set GridCell style sheets
        self.setStyleSheet("""GridCell{
                                border: 1px dashed black;
                           }
                           """)

        # set GridCell layout
        self.myLayout = QVBoxLayout(self)
        self.myLayout.setContentsMargins(0, 0, 2, 1)


    def dragEnterEvent(self, event:  QDragEnterEvent) -> None:
        '''
        Overrides the drag event handling of the parent class ``QFrame`` to enable dragging and dropping tools on the cell.

        Args:
            event (QDragEnterEvent): Contains information about the drag event.

        Returns:
            None: This method does not return anything.
        '''
        if event.mimeData().hasText():
            event.acceptProposedAction()


    def dropEvent(self, event: QDropEvent) -> None:
        '''
        Adds or replaces a new item (e.g. Laser, beamsplitter, etc.) to the current instance of ``GridCell``.

        Args:
            event (QDropEvent): Holds information about the type of componented to be added.

        Returns:
            None: This method does not return anything.
        '''
        
        # extract MimeData from event
        mime = event.mimeData()

        # check if it is a new tool or a dragged one
        global dragged_item
        if mime.text() == "GridItem":
            newItem = dragged_item
        else:
            newItem = components[mime.text()]()
        dragged_item = None


        # Remove any existing widgets from the cell
        while self.myLayout.count():
            self.remove_item()


        # add the new element 
        self.add_item(newItem)


        # no idea what this does, but all people use it
        event.acceptProposedAction()


    def get_item(self) -> Union[None, GridItem]:
        '''
        A getter method for the grid item that is currently held by the cell.

        :return: A ``GridItem`` (or one of its children) if the cell holds one, otherwise returns ``None``.
        :rtype: GridItem | None
            
        '''
        item = self.myLayout.itemAt(0)
        if item:
            return item.widget()
        else:
            return None
        
    def remove_item(self) -> None:
        '''
        Removes the current ``GridItem`` held by the cell, if any.

        :return: This method does not return anything.
        :rtype: None
        '''
        while self.myLayout.count():
            currentItem = self.myLayout.takeAt(0)
            currentItem.widget().deleteLater()

    def add_item(self, item:GridItem) -> None:
        '''
        Adds a ``GridItem`` (or one of its children) to the cell.

        :param item: The item to be added to the cell.
        :type item: GridItem

        :return: This method does not return anything.
        :rtype: None
        '''
        item.row = self.row
        item.col = self.col
        self.myLayout.addWidget(item)


class GridArea(QWidget):
    '''
    The entire grid area that holds all instances of :class:`GridCell` objects.

    Inherits from the generic class :class:`QWidget`.

    :ivar rows: The total number of rows of cells.
    :vartype rows: int

    :ivar cols: The total number of columns of cells.
    :vartype cols: int

    :ivar photon: A photon that is used for visualizing simulations.
    :vartype photon: Photon
    '''
    def __init__(self, **kwargs) -> None:
        '''
        Initializes a :class:`GridArea` instance.

        :return: This function does not return anything.
        :rtype: None
        '''
        super().__init__(**kwargs)

        # create photon
        self.photon = Photon(parent=self)
        self.photon.raise_()

        # set GridArea size
        self.rows = GRID_ROWS
        self.cols = GRID_COLS

        # set GridArea attributes
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(GRID_AREA_BG_COLOR))
        self.setPalette(palette)

        # allowed item types
        self.allowedItemTypes= (GridItem,
                                Laser,
                                Detector,
                                BeamSplitter,
                                PolarBeamSplitter,
                                Mirror)


        # set the grid layout
        self.myLayout = QGridLayout(self)
        self.myLayout.setSpacing(0)
        self.create_grid(self.rows, self.cols)


    def create_grid(self, rows:int, cols:int) -> None:
        '''
        Fills :class:`GridArea` with :class:`GridCell` instances.

        :param rows: The total number of rows, which is the number of cells per column.
        :type rows: int

        :param cols: The total number of columns, which is the number of cells per row.
        :type cols: int

        :return: This method does not return anything.
        :rtype: None
        '''
        for row in range(rows):
            for col in range(cols):
                self.myLayout.addWidget(GridCell(row, col), row, col)


    def get_item_at(self, row: int, col: int) -> Union[GridItem,None]: 
        '''
        Returns the item stored in the cell at the location (row, col) within the grid.

        :param row: The row number of the target cell.
        :type row: int

        :param col: The column number of the target cell.
        :type col: int

        :return: Returns the item held by the cell if it exists, otherwise returns None.
        :rtype: GridItem | None
        '''
        if row >= self.rows or row < 0 or col >= self.cols or col < 0:
            return None
        
        grid_cell: GridCell = self.myLayout.itemAtPosition(row, col).widget()
        item: GridItem = grid_cell.get_item()

        return item

    def get_items_by_type(self, type:type) -> list:
        '''
        Returns a list of all items within the grid of a given type.

        :param type: The type of items needed to be returned, given in the form of class names (e.g. Laser, Mirror, etc.)
        :type type: type

        :return: Returns a list of items of the given type. If no items of such type exist, returns an empty list.
        :rtype: list
        '''
        # check the validity of the item type
        assert type in self.allowedItemTypes, "Not an allowed item type"

        items = []
        for r in range(self.rows):
            for c in range(self.cols):
            
                grid_cell = self.myLayout.itemAtPosition(r, c).widget()
                item = grid_cell.get_item()

                if isinstance(item, type):
                    items.append(item)
        
        return items
            

    def get_lasers(self) -> list:
        '''
        Returns a list of all instances of :class:`Laser` objects within the grid.

        :return: Returns a list of laser objects. In case no lasers exist, returns an empty list.
        :rtype: list
        '''
        return self.get_items_by_type(Laser)

        
    def get_grid_size(self) -> tuple[int, int]:
        '''
        Getter method for the size of the grid.

        :return: Returns a tuple of grid size in the form (number of rows, number of columns).
        :rtype: tuple[int, int]
        '''
        return self.rows, self.cols
    

    def show_photon(self) -> None:
        '''
        Shows the photon on the screen.

        :return: This method does not return anything.
        :rtype: None
        '''
        self.photon.show()
        self.photon.raise_()

    def hide_photon(self) -> None:
        '''
        Hides the photon.

        :return: This function does not return anything.
        :rtype: None
        '''
        self.photon.hide()

    def move_photon(self, start_cell:tuple[int, int], end_cell:tuple[int, int], orientation=None) -> None:
        '''
        Shows animation of a photon moving from a starting grid cell to another grid cell then hides it again.

        :param start_cell: The cell position that the photon should start at, given in the form of (row, column). 
        :type start_cell: tuple[int, int]

        :param end_cell: The cell position that the photon should end at, given in the form of (row, column). 
        :type end_cell: tuple[int, int]

        :param orientation: The orientation of the photon's movement (right, left, up, down). Used to make the photon's start and end positions appear at the edge of the cell rather than at its center.
        :type orientation: int

        :return: This function does not return anything.
        :rtype: None
        '''

        # create a photon (starts hidden by default)
        photon = Photon(parent=self)

        # raise the photon above all other widgets
        photon.raise_()
        photon.show()

        # calculate starting and ending positions of the photon
        start_pos = [start_cell[1]*GRID_CELL_SIZE, start_cell[0]*GRID_CELL_SIZE]
        end_pos   = [end_cell[1]*GRID_CELL_SIZE,   end_cell[0]*GRID_CELL_SIZE]

        # account for starting positions based on orientation
        if orientation == 0:
            start_pos[0] += GRID_CELL_SIZE
            start_pos[1] += (GRID_CELL_SIZE//2)
            end_pos[1] += (GRID_CELL_SIZE//2)

        elif orientation == 1:
            start_pos[0] += (GRID_CELL_SIZE//2)
            start_pos[1] += GRID_CELL_SIZE
            end_pos[0] += (GRID_CELL_SIZE//2)

        elif orientation == 2:
            start_pos[1] += (GRID_CELL_SIZE//2)
            end_pos[0] += GRID_CELL_SIZE
            end_pos[1] += (GRID_CELL_SIZE//2)

        elif orientation == 3:
            start_pos[0] += (GRID_CELL_SIZE//2)
            end_pos[0] += (GRID_CELL_SIZE//2)
            end_pos[1] += GRID_CELL_SIZE


        # move the photon from starting position to ending position
        photon.move_to_position(start_pos, end_pos)

        # delete the photon
        #photon.deleteLater()
     

class SimulationArea(QScrollArea):
    '''
    The entire simulation area, including :class:`GridArea` and a margin around it.

    Inherits from :class:`QScrollArea`.

    :ivar gridArea: The entire grid area within the simulation area. 
    :vartype gridArea: GridArea
    '''
    def __init__(self, **kwargs) -> None:
        '''
        Initializes a :class:`SimulationArea` instance.

        :return: This method does not return anything.
        :rtype: None
        '''
        super().__init__(**kwargs)

        # set SimulationArea attributes
        self.setWidgetResizable(True)
        self.setContentsMargins(0, 0, 0, 0)
        
        # containerWidget
        self.containerWidget = QWidget()
        self.containerWidget.setAutoFillBackground(True)
        palette = self.containerWidget.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(SIMULATION_AREA_BG_COLOR))
        self.containerWidget.setPalette(palette)
        self.setWidget(self.containerWidget)

        # Grid Area
        self.gridArea = GridArea()

        # layout of the container widget
        self.containerWidgetLayout = QVBoxLayout()
        self.containerWidgetLayout.addWidget(self.gridArea)
        self.containerWidgetLayout.setContentsMargins(SIMULATION_AREA_MARGINS,
                                                      SIMULATION_AREA_MARGINS,
                                                      SIMULATION_AREA_MARGINS,
                                                      SIMULATION_AREA_MARGINS)
        self.containerWidget.setLayout(self.containerWidgetLayout)

    def get_item_at(self, row: int, col: int) -> Union[GridItem,None]:
        '''
        Returns the item stored in the cell at the location (row, col) within the simulation area's grid.

        :param row: The row number of the target cell.
        :type row: int

        :param col: The column number of the target cell.
        :type col: int

        :return: Returns the item held by the cell if it exists, otherwise returns None.
        :rtype: GridItem | None
        '''
        return self.gridArea.get_item_at(row, col)

    def get_grid_size(self) -> None:
        '''
        Getter method for the size of the grid.

        :return: Returns a tuple of grid size in the form (number of rows, number of columns).
        :rtype: tuple[int, int]
        '''
        return self.gridArea.get_grid_size()

    def get_lasers(self) -> None:
        '''
        Returns a list of all instances of :class:`Laser` objects within the grid.

        :return: Returns a list of laser objects. In case no lasers exist, returns an empty list.
        :rtype: list
        '''
        return self.gridArea.get_lasers()        

    def show_photon(self) -> None:
        '''
        Shows the photon on the screen.

        :return: This method does not return anything.
        :rtype: None
        '''
        self.gridArea.show_photon()

    def hide_photon(self) -> None:
        '''
        Hides the photon.

        :return: This function does not return anything.
        :rtype: None
        '''
        self.gridArea.hide_photon()

    def move_photon(self, start_cell:tuple[int, int], end_cell:tuple[int, int], orientation=None) -> None:
        '''
        Shows animation of a photon moving from a starting grid cell to another grid cell then hides it again.

        :param start_cell: The cell position that the photon should start at, given in the form of (row, column). 
        :type start_cell: tuple[int, int]

        :param end_cell: The cell position that the photon should end at, given in the form of (row, column). 
        :type end_cell: tuple[int, int]

        :param orientation: The orientation of the photon's movement (right, left, up, down). Used to make the photon's start and end positions appear at the edge of the cell rather than at its center.
        :type orientation: int

        :return: This function does not return anything.
        :rtype: None
        '''
        self.gridArea.move_photon(start_cell, end_cell, orientation)



class LeftMenu(QWidget):
    '''
    The left menu area of the application window.

    :ivar playButton: A button to start the simulation.
    :vartype playButton: QPushButton

    :ivar stopButton:A button to stop the simulation.
    :vartype stopButton: QPushButton

    :ivar exitButton: A button to exit the application.
    :vartype exitButton: QPushButton

    :ivar toolsArea: A tools area to hold the draggable tools.
    :vartype toolsArea: ToolsListsArea
    '''
    def __init__(self, **kwargs) -> None:
        '''
        Initializes a :class:`LeftMenu` instance.

        :return: This method does not return anything.
        :rtype: None
        '''
        super().__init__(**kwargs)

        # set LeftMenu attributes
        if "name" in kwargs:
            self.setObjectName(kwargs["name"])

        #self.setMinimumWidth(LEFT_MENU_WIDTH)
        self.setMaximumWidth(LEFT_MENU_WIDTH)

        # Create LeftMenu Buttons
        self.playButton = QPushButton('Play')
        self.stopButton = QPushButton('Stop')
        self.exitButton = QPushButton('Exit')

        # create all lists of tools
        self.componentsList = ToolsList("Components")
        for _, comp in components.items():
            self.componentsList.addTool(comp.__name__)


        # Create scroll area for tools lists
        self.toolsArea = ToolsListsArea()
        self.toolsArea.addToolsList(self.componentsList)

        # set LeftMenu layout to vertical
        self.myLayout = QVBoxLayout(self)
        self.myLayout.addWidget(self.playButton)
        self.myLayout.addWidget(self.stopButton)
        self.myLayout.addWidget(self.toolsArea)
        self.myLayout.addItem(VSpacer())
        self.myLayout.addWidget(self.exitButton)
        self.setLayout(self.myLayout)

    def connect_play_button(self, func:Callable) -> None:
        '''
        Connects a function to :attr:`playButton` to be called when the button is clicked.

        :param func: A function to be called when the button is clicked.
        :type func: Callable

        :return: This function does not return anything.
        :rtype: None
        '''
        self.playButton.clicked.connect(func)
    
    def connect_stop_button(self, func: Callable) -> None:
        '''
        Connects a function to :attr:`stopButton` to be called when the button is clicked.

        :param func: A function to be called when the button is clicked.
        :type func: Callable
        
        :return: This function does not return anything.
        :rtype: None
        '''
        self.stopButton.clicked.connect(func)

    def connect_exit_button(self, func: Callable) -> None:
        '''
        Connects a function to :attr:`exitButton` to be called when the button is clicked.

        :param func: A function to be called when the button is clicked.
        :type func: Callable
        
        :return: This function does not return anything.
        :rtype: None
        '''
        self.exitButton.clicked.connect(func)



class CentralWidget(QWidget):
    '''
    A class for the central widget of the application's window. Holds the :class:`LeftMenu`, :class:`SimulationArea` and all of their contents.

    :ivar leftMenu: The left menu of the application, containing control buttons and tools lists. 
    :vartype leftMenu: LeftMenu

    :ivar simulationArea: The simulation area containing the grid and all grid items.
    :vartype simulationArea: SimulationArea
    '''
    def __init__(self, **kwargs) -> None:
        '''
        Initializes a :class:`CentralWidget` instance.

        :return: This method does not return anything.
        :rtype: None
        '''
        super().__init__(**kwargs)
        
        # set CentralWidget attributes

        # Create LeftMenu
        self.leftMenu = LeftMenu()
        self.leftMenu.playButton

        # Create Simulation area
        self.simulationArea = SimulationArea()

        # set CentralWidget layout to horizontal
        self.myLayout = QHBoxLayout(self)
        self.myLayout.setSpacing(0)
        self.myLayout.addWidget(self.leftMenu)
        self.myLayout.addWidget(VLine())
        self.myLayout.addWidget(self.simulationArea)
        self.setLayout(self.myLayout)

    def get_item_at(self, row: int, col: int) -> Union[GridItem,None]:
        '''
        Returns the item stored in the cell at the location (row, col) within the grid.

        :param row: The row number of the target cell.
        :type row: int

        :param col: The column number of the target cell.
        :type col: int

        :return: Returns the item held by the cell if it exists, otherwise returns None.
        :rtype: GridItem | None
        '''
        return self.simulationArea.get_item_at(row, col)
    
    def connect_play_button(self, func: Callable) -> None:
        '''
        Connects a function to the play button to be called when the button is clicked.

        :param func: A function to be called when the button is clicked.
        :type func: Callable

        :return: This function does not return anything.
        :rtype: None
        '''
        self.leftMenu.connect_play_button(func)

    def connect_stop_button(self, func: Callable) -> None:
        '''
        Connects a function to stop button to be called when the button is clicked.

        :param func: A function to be called when the button is clicked.
        :type func: Callable
        
        :return: This function does not return anything.
        :rtype: None
        '''
        self.leftMenu.connect_stop_button(func)

    def connect_exit_button(self, func: Callable) -> None:
        '''
        Connects a function to the exit button to be called when the button is clicked.

        :param func: A function to be called when the button is clicked.
        :type func: Callable
        
        :return: This function does not return anything.
        :rtype: None
        '''
        self.leftMenu.connect_exit_button(func)

    def get_grid_size(self) -> tuple[int, int]:
        '''
        Getter method for the size of the grid.

        :return: Returns a tuple of grid size in the form (number of rows, number of columns).
        :rtype: tuple[int, int]
        '''
        return self.simulationArea.get_grid_size()

    def get_lasers(self) -> list:
        '''
        Returns a list of all instances of :class:`Laser` objects within the grid.

        :return: Returns a list of laser objects. In case no lasers exist, returns an empty list.
        :rtype: list
        '''
        return self.simulationArea.get_lasers()
    
    def show_photon(self) -> None:
        '''
        Shows the photon on the screen.

        :return: This method does not return anything.
        :rtype: None
        '''
        self.simulationArea.show_photon()

    def hide_photon(self) -> None:
        '''
        Hides the photon.

        :return: This function does not return anything.
        :rtype: None
        '''
        self.simulationArea.hide_photon()

    def move_photon(self, start_cell:tuple[int, int], end_cell:tuple[int, int], orientation=None) -> None:
        '''
        Shows animation of a photon moving from a starting grid cell to another grid cell then hides it again.

        :param start_cell: The cell position that the photon should start at, given in the form of (row, column). 
        :type start_cell: tuple[int, int]

        :param end_cell: The cell position that the photon should end at, given in the form of (row, column). 
        :type end_cell: tuple[int, int]

        :param orientation: The orientation of the photon's movement (right, left, up, down). Used to make the photon's start and end positions appear at the edge of the cell rather than at its center.
        :type orientation: int

        :return: This function does not return anything.
        :rtype: None
        '''
        self.simulationArea.move_photon(start_cell, end_cell, orientation)
    

class Ui_MainWindow(object):
    '''
    The main UI window class, holding all UI components of the application.

    :ivar centralWidget: The application's central widget, holding all other components within the window.
    :vartype centralWidget: CentralWidget
    '''
    def setupUi(self, MainWindow:QMainWindow, **kwargs) -> None:
        '''
        Sets up the UI window and all of of its components, controlling them during the lifetime of the application.

        :param MainWindow: The mainwindow controller class, responsible for orchestrating the entire application logic.
        :type MainWindow: QMainWindow

        :return: This method does not return anything.
        :rtype: None
        '''
        # register icons
        icons[Laser.__name__]             = LASER_ICON
        icons[Detector.__name__]          = DETECTOR_ICON
        icons[BeamSplitter.__name__]      = BEAM_SPLITTER_ICON
        icons[PolarBeamSplitter.__name__] = POLAR_BEAM_SPLITTER_ICON
        icons[Mirror.__name__]            = MIRROR_ICON


        # register text
        texts[Laser.__name__]             = LASER_TEXT
        texts[Detector.__name__]          = DETECTOR_TEXT
        texts[BeamSplitter.__name__]      = BEAM_SPLITTER_TEXT
        texts[PolarBeamSplitter.__name__] = POLAR_BEAM_SPLITTER_TEXT
        texts[Mirror.__name__]            = MIRROR_TEXT

        # register components classes
        components[Laser.__name__]             = Laser
        components[Detector.__name__]          = Detector
        components[BeamSplitter.__name__]      = BeamSplitter
        components[PolarBeamSplitter.__name__] = PolarBeamSplitter
        components[Mirror.__name__]            = Mirror

        
        # import icons
        for comp in icons:
            icons[comp] = [QIcon(icons[comp])]

            for angle in [90, 180, 270]:
                icons[comp].append(rotate_icon(icons[comp][0], angle))


            
        # Create MainWindow ColorPalette
        palette = MainWindow.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(BACKGROUND_COLOR))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT_COLOR))


        # Set MainWindow attributes
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1001, 563)
        MainWindow.setMinimumSize(QSize(1000, 500))
        MainWindow.setPalette(palette)
        
        # Create central widget
        self.centralWidget = CentralWidget(parent=MainWindow)
        MainWindow.setCentralWidget(self.centralWidget)

    def get_item_at(self, row: int, col: int) -> Union[GridItem,None]:
        '''
        Returns the item stored in the cell at the location (row, col) within the grid.

        :param row: The row number of the target cell.
        :type row: int

        :param col: The column number of the target cell.
        :type col: int

        :return: Returns the item held by the cell if it exists, otherwise returns None.
        :rtype: GridItem | None
        '''
        return self.centralWidget.get_item_at(row, col)
    
    def connect_play_button(self, func: Callable) -> None:
        '''
        Connects a function to :attr:`playButton` to be called when the button is clicked.

        :param func: A function to be called when the button is clicked.
        :type func: Callable

        :return: This function does not return anything.
        :rtype: None
        '''
        self.centralWidget.connect_play_button(func)

    def connect_stop_button(self, func: Callable) -> None:
        '''
        Connects a function to stop button to be called when the button is clicked.

        :param func: A function to be called when the button is clicked.
        :type func: Callable
        
        :return: This function does not return anything.
        :rtype: None
        '''
        self.centralWidget.connect_stop_button(func)

    def connect_exit_button(self, func: Callable) -> None:
        '''
        Connects a function to the exit button to be called when the button is clicked.

        :param func: A function to be called when the button is clicked.
        :type func: Callable
        
        :return: This function does not return anything.
        :rtype: None
        '''
        self.centralWidget.connect_exit_button(func)

    def get_grid_size(self) -> tuple[int, int]:
        '''
        Getter method for the size of the grid.

        :return: Returns a tuple of grid size in the form (number of rows, number of columns).
        :rtype: tuple[int, int]
        '''
        return self.centralWidget.get_grid_size()

    def get_lasers(self) -> list:
        '''
        Returns a list of all instances of :class:`Laser` objects within the grid.

        :return: Returns a list of laser objects. In case no lasers exist, returns an empty list.
        :rtype: list
        '''
        # HACK: add functionality for the grid to record each added element instead of traversal
        return self.centralWidget.get_lasers()

    def show_photon(self) -> None:
        '''
        Shows the photon on the screen.

        :return: This method does not return anything.
        :rtype: None
        '''
        self.centralWidget.show_photon()

    def hide_photon(self) -> None:
        '''
        Hides the photon.

        :return: This function does not return anything.
        :rtype: None
        '''
        self.centralWidget.hide_photon()

    def move_photon(self, start_cell:tuple[int, int], end_cell:tuple[int, int], orientation=None) -> None:
        '''
        Shows animation of a photon moving from a starting grid cell to another grid cell then hides it again.

        :param start_cell: The cell position that the photon should start at, given in the form of (row, column). 
        :type start_cell: tuple[int, int]

        :param end_cell: The cell position that the photon should end at, given in the form of (row, column). 
        :type end_cell: tuple[int, int]

        :param orientation: The orientation of the photon's movement (right, left, up, down). Used to make the photon's start and end positions appear at the edge of the cell rather than at its center.
        :type orientation: int

        :return: This function does not return anything.
        :rtype: None
        '''
        self.centralWidget.move_photon(start_cell, end_cell, orientation)


    def visualize_vector(self, vector: np.ndarray) -> None:
        '''
        Vizualizes a given vector of entries in a table.

        :param vector: The vector of entires to be visualized.
        :type vector: numpy.ndarray

        :return: This method does not return anything.
        :rtype: None
        '''
        # Open the visualization window
        self.visualization_window = VectorWindow(vector)
        self.visualization_window.show()


class VectorWindow(QWidget):
    '''
    A table to visualize a vector's entires within a window.

    :ivar table: A table of vector's enties.
    :vartype table: QTableWidget
    '''
    def __init__(self, vector:np.ndarray) -> None:
        '''
        Initializes a :class:`VectorWindow` instance.

        :param vector: The vector whose entires are to be visualized. 
        :type vector: np.ndarray

        :return: This method does not return anything.
        :rtype: None
        '''
        super().__init__()
        self.setWindowTitle("Quantum State Vector")
        self.setGeometry(200, 200, 200, 400)

        # Create a table to display the vector
        self.table = QTableWidget(self)

        # row count is the same as the vector's length
        self.table.setRowCount(len(vector))

        # One column for label and one for amplitude
        self.table.setColumnCount(2)

        # Column headers
        self.table.setHorizontalHeaderLabels(["Label", "Value"])
        self.table.verticalHeader().setVisible(False)  # Hide row numbers

        # Fill the table with vector values
        for i, value in enumerate(vector):
            self.table.setItem(i, 0, QTableWidgetItem(f"|{i}>"))
            self.table.setItem(i, 1, QTableWidgetItem(str(round(value, 5))))

        # Set table dimensions
        self.table.resize(200, 400)
        self.table.setFixedSize(200, 400)