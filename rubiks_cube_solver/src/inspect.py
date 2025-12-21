"""
Cube Inspection Tools - For debugging and analyzing cube states.

This module provides tools to inspect cube state, find pieces,
and verify solver progress.
"""

from typing import Tuple, Optional, List
from dataclasses import dataclass
from src.cube_state import CubeState


class PieceNotFoundError(Exception):
    """Raised when a piece cannot be found on the cube."""

    def __init__(self, colors: Tuple[str, ...], cube_state: CubeState):
        self.colors = colors
        self.cube_state = cube_state
        super().__init__(
            f"Piece with colors {colors} not found on cube.\n"
            f"Cube state:\n{cube_state}"
        )


@dataclass
class EdgeRef:
    """Reference to an edge piece on the cube."""
    face1: str
    pos1: int
    face2: str
    pos2: int
    color1: str
    color2: str

    def __str__(self):
        return f"Edge({self.face1}[{self.pos1}]={self.color1}, {self.face2}[{self.pos2}]={self.color2})"


@dataclass
class CornerRef:
    """Reference to a corner piece on the cube."""
    face1: str
    pos1: int
    face2: str
    pos2: int
    face3: str
    pos3: int
    color1: str
    color2: str
    color3: str

    def __str__(self):
        return f"Corner({self.face1}[{self.pos1}]={self.color1}, {self.face2}[{self.pos2}]={self.color2}, {self.face3}[{self.pos3}]={self.color3})"


# Edge piece definitions: (face, position, adjacent_face, adjacent_position)
EDGE_POSITIONS = [
    ('U', 1, 'B', 1),   # UB edge
    ('U', 3, 'L', 1),   # UL edge
    ('U', 5, 'R', 1),   # UR edge
    ('U', 7, 'F', 1),   # UF edge
    ('F', 3, 'L', 5),   # FL edge
    ('F', 5, 'R', 3),   # FR edge
    ('F', 7, 'D', 1),   # FD edge
    ('B', 3, 'R', 5),   # BR edge
    ('B', 5, 'L', 3),   # BL edge
    ('B', 7, 'D', 5),   # BD edge
    ('L', 7, 'D', 3),   # LD edge
    ('R', 7, 'D', 7),   # RD edge
]

# Corner piece definitions: (face, position, adjacent_face1, position1, adjacent_face2, position2)
CORNER_POSITIONS = [
    ('U', 0, 'L', 2, 'B', 2),   # ULB corner
    ('U', 2, 'B', 0, 'R', 2),   # UBR corner
    ('U', 6, 'F', 0, 'L', 0),   # UFL corner
    ('U', 8, 'R', 0, 'F', 2),   # URF corner
    ('D', 0, 'F', 6, 'L', 8),   # DFL corner
    ('D', 2, 'L', 6, 'B', 8),   # DLB corner
    ('D', 6, 'R', 8, 'F', 8),   # DRF corner
    ('D', 8, 'B', 6, 'R', 6),   # DBR corner
]


def find_edge(cube: CubeState, color1: str, color2: str,
              max_iterations: int = 24) -> EdgeRef:
    """
    Find an edge piece with the given colors.

    Args:
        cube: Current cube state
        color1: First color
        color2: Second color
        max_iterations: Maximum search iterations (prevents infinite loops)

    Returns:
        EdgeRef containing edge information

    Raises:
        PieceNotFoundError: If edge not found within max_iterations
    """
    iterations = 0

    for edge_def in EDGE_POSITIONS:
        iterations += 1
        if iterations > max_iterations:
            raise PieceNotFoundError((color1, color2), cube)

        face1, pos1, face2, pos2 = edge_def
        sticker1 = cube.get_sticker(face1, pos1)
        sticker2 = cube.get_sticker(face2, pos2)

        if (sticker1 == color1 and sticker2 == color2) or \
           (sticker1 == color2 and sticker2 == color1):
            return EdgeRef(face1, pos1, face2, pos2, sticker1, sticker2)

    raise PieceNotFoundError((color1, color2), cube)


def find_corner(cube: CubeState, color1: str, color2: str, color3: str,
                max_iterations: int = 24) -> CornerRef:
    """
    Find a corner piece with the given colors (in any order).

    Args:
        cube: Current cube state
        color1: First color
        color2: Second color
        color3: Third color
        max_iterations: Maximum search iterations

    Returns:
        CornerRef containing corner information

    Raises:
        PieceNotFoundError: If corner not found within max_iterations
    """
    colors = {color1, color2, color3}
    iterations = 0

    for corner_def in CORNER_POSITIONS:
        iterations += 1
        if iterations > max_iterations:
            raise PieceNotFoundError((color1, color2, color3), cube)

        face1, pos1, face2, pos2, face3, pos3 = corner_def
        sticker1 = cube.get_sticker(face1, pos1)
        sticker2 = cube.get_sticker(face2, pos2)
        sticker3 = cube.get_sticker(face3, pos3)

        if {sticker1, sticker2, sticker3} == colors:
            return CornerRef(face1, pos1, face2, pos2, face3, pos3,
                           sticker1, sticker2, sticker3)

    raise PieceNotFoundError((color1, color2, color3), cube)


def edge_solved(cube: CubeState, edge: EdgeRef) -> bool:
    """
    Check if an edge is in its solved position with correct orientation.

    Args:
        cube: Current cube state
        edge: Edge reference

    Returns:
        True if edge is solved
    """
    # Get target colors based on center colors
    target1 = cube.get_sticker(edge.face1, 4)  # Center of face1
    target2 = cube.get_sticker(edge.face2, 4)  # Center of face2

    # Check if edge matches center colors
    current1 = cube.get_sticker(edge.face1, edge.pos1)
    current2 = cube.get_sticker(edge.face2, edge.pos2)

    return current1 == target1 and current2 == target2


def corner_solved(cube: CubeState, corner: CornerRef) -> bool:
    """
    Check if a corner is in its solved position with correct orientation.

    Args:
        cube: Current cube state
        corner: Corner reference

    Returns:
        True if corner is solved
    """
    # Get target colors based on center colors
    target1 = cube.get_sticker(corner.face1, 4)
    target2 = cube.get_sticker(corner.face2, 4)
    target3 = cube.get_sticker(corner.face3, 4)

    # Check if corner matches center colors
    current1 = cube.get_sticker(corner.face1, corner.pos1)
    current2 = cube.get_sticker(corner.face2, corner.pos2)
    current3 = cube.get_sticker(corner.face3, corner.pos3)

    return (current1 == target1 and current2 == target2 and current3 == target3)


def edge_oriented(cube: CubeState, edge: EdgeRef, primary_face: str) -> bool:
    """
    Check if an edge is oriented correctly relative to a primary face.

    An edge is "oriented" if its primary face color (e.g., white for top layer)
    is on the correct face.

    Args:
        cube: Current cube state
        edge: Edge reference
        primary_face: The primary face to check orientation against

    Returns:
        True if edge is oriented correctly
    """
    primary_color = cube.get_sticker(primary_face, 4)  # Center color

    # Check if the primary color is on the primary face side of the edge
    if edge.face1 == primary_face:
        return cube.get_sticker(edge.face1, edge.pos1) == primary_color
    elif edge.face2 == primary_face:
        return cube.get_sticker(edge.face2, edge.pos2) == primary_color
    else:
        # Edge doesn't touch primary face
        return False


def cube_to_pretty_string(cube: CubeState, highlight_positions: Optional[List[Tuple[str, int]]] = None) -> str:
    """
    Create a pretty string representation of the cube with optional highlighting.

    Args:
        cube: Cube state to display
        highlight_positions: List of (face, position) tuples to highlight

    Returns:
        Pretty formatted string
    """
    highlight_set = set(highlight_positions) if highlight_positions else set()

    def format_sticker(face: str, pos: int) -> str:
        sticker = cube.get_sticker(face, pos)
        if (face, pos) in highlight_set:
            return f"[{sticker}]"
        return f" {sticker} "

    lines = []
    lines.append("=" * 60)
    lines.append("CUBE STATE")
    lines.append("=" * 60)
    lines.append("")

    # Top face (U)
    lines.append("         UP (U)")
    for row in range(3):
        line = "      "
        for col in range(3):
            pos = row * 3 + col
            line += format_sticker('U', pos)
        lines.append(line)

    lines.append("")
    lines.append("LEFT(L)   FRONT(F)   RIGHT(R)   BACK(B)")

    # Middle row
    for row in range(3):
        line = ""
        for face in ['L', 'F', 'R', 'B']:
            for col in range(3):
                pos = row * 3 + col
                line += format_sticker(face, pos)
            line += "  "
        lines.append(line)

    lines.append("")
    lines.append("        DOWN (D)")

    # Bottom face (D)
    for row in range(3):
        line = "      "
        for col in range(3):
            pos = row * 3 + col
            line += format_sticker('D', pos)
        lines.append(line)

    lines.append("")
    lines.append("=" * 60)

    return '\n'.join(lines)


def count_solved_pieces(cube: CubeState) -> Tuple[int, int]:
    """
    Count how many edges and corners are solved.

    Args:
        cube: Cube state

    Returns:
        Tuple of (solved_edges, solved_corners)
    """
    solved_edges = 0
    solved_corners = 0

    # Check edges
    for edge_def in EDGE_POSITIONS:
        face1, pos1, face2, pos2 = edge_def
        edge = EdgeRef(face1, pos1, face2, pos2,
                      cube.get_sticker(face1, pos1),
                      cube.get_sticker(face2, pos2))
        if edge_solved(cube, edge):
            solved_edges += 1

    # Check corners
    for corner_def in CORNER_POSITIONS:
        face1, pos1, face2, pos2, face3, pos3 = corner_def
        corner = CornerRef(face1, pos1, face2, pos2, face3, pos3,
                          cube.get_sticker(face1, pos1),
                          cube.get_sticker(face2, pos2),
                          cube.get_sticker(face3, pos3))
        if corner_solved(cube, corner):
            solved_corners += 1

    return (solved_edges, solved_corners)
