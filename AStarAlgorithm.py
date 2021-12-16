import math
import pygame
from queue import PriorityQueue

# Game window data
WIDTH = 600
WINDOW = pygame.display.set_mode((WIDTH,WIDTH))

# Color value data RGB values
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 128, 0)

# Each square in the grid is considered a "Node", each contains data such as color (status) and position
class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE
        
    def is_end(self):
        return self.color == BLUE

    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE
        
    def make_end(self):
        self.color = BLUE    
        
    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    # Checks for possible neighbor in a given direction (up, down, left, or right) from current node
    def update_neighbors(self, grid):
        self.neighbors = []

        # Checks for DOWN neighbor
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])

        # Checks for UP neighbor
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])

        # Checks for RIGHT neighbor
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])

        # Checks for LEFT neighbor
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

# Hueristic algorithm "Manhattan distance", shortest 'L' shaped distance, ignoring barriers, from start to end
def h(h1, h2):
    x1, y1 = h1
    x2, y2 = h2
    return abs(x1-x2) + abs(y1-y2)

# work backwards from end to start, building the best path
def build_path(last_node, current, draw):
    while current in last_node:
        current = last_node[current]
        current.make_path()
        draw()


# Main A* pathfinding algorithm (could be subbed for any other pathing algorithm) using PriorityQueue Package (heap sort)
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))

    # previous node
    last_node = {}

    # tracks shortest distance from start to current node
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0

    # measures shortest distance from current node to end node, ignores barriers
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    #check if node is in queue or not
    open_set_hash = {start}

    # if open set is not empty, then run algorithm, allows user to quit if there are errors
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        # sets current to node with minimum f-score, uses heap sort
        current = open_set.get()[2]
        open_set_hash.remove(current)

        # creates final path and exits
        if current == end:
            build_path(last_node, end, draw)
            end.make_end()
            return True

        # if end is not found, consider neighbors to find next node in best path
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            # if g-score is lower elsewhere, set that as the new g-score
            if temp_g_score < g_score[neighbor]:
                last_node[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        # closes current node after consideration
        if current != start:
            current.make_closed()

    return False


# creates node grid within window based on grid size
def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i,j, gap, rows)
            grid[i].append(node)
    return grid


# Draws each individual node on screen
def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    pygame.display.update()

# mouse click position data
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col




# MAIN FUNCTION
def main(win, width):
    ROWS = 60
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    while run:
        draw(win, grid, ROWS, width)

        # Quit condition
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            # Left mouse button press, set node to either starting, ending, or barrier
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]

                # Always place start node first
                if not start and node != end:
                    start = node
                    start.make_start()

                # Place end node second
                elif not end and node != start:
                    end = node
                    end.make_end()

                # Place barriers after start and end nodes placed
                elif node != end and node != start:
                    node.make_barrier()
            
            # Right mouse button press, sets any node to white while the algorithm is not running
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = end
                elif node == end:
                    end = None

            # Spacebar, updates neighbors
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    # Calls A-star algorithm function
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                # Press 'C', "clears" all nodes and sets all nodes to white
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)


    pygame.quit()

# Call main function
main(WINDOW, WIDTH)
