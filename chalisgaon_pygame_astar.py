import pygame
import math
from road_graph import load_graph, graph_to_grid_nodes
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Shortest Path Search")

RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
PURPLE = (128,0,128)
ORANGE = (255,165,0)
GREY = (128,128,128)
TURQUOISE = (64,224,204)

class Cell:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row*width
        self.y = col*width
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
    
    def is_wall(self):
        return self.color == BLACK
    
    def is_start(self):
        return self.color == ORANGE
    
    def is_end(self):
        return self.color == TURQUOISE
    
    def reset(self):
        self.color = WHITE

    def set_close(self):
        self.color = RED

    def set_open(self):
        self.color = GREEN

    def set_wall(self):
        self.color = BLACK

    def set_start(self):
        self.color = ORANGE

    def set_end(self):
        self.color = TURQUOISE

    def set_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self,grid):
        self.neighbors = []
        #down
        if self.row < self.total_rows-1 and not grid[self.row+1][self.col].is_wall():
            self.neighbors.append(grid[self.row+1][self.col])
        #up
        if self.row > 0 and not grid[self.row-1][self.col].is_wall():
            self.neighbors.append(grid[self.row-1][self.col])
        #left
        if self.col > 0 and not grid[self.row][self.col-1].is_wall():
            self.neighbors.append(grid[self.row][self.col-1])
        #right
        if self.col < self.total_rows-1 and not grid[self.row][self.col+1].is_wall():
            self.neighbors.append(grid[self.row][self.col+1])


    def __lt__(self, other):
        return False


def h(p1,p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def backtrack(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.set_path()
        draw()

def aStar(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {} #parent (to backtrack)
    g_score = {cell: float("inf") for row in grid for cell in row} #initialising g score for every cell as 'infinity'
    g_score[start] = 0
    f_score = {cell: float("inf") for row in grid for cell in row} #initialising g score for every cell as 'infinity'
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            backtrack(came_from, end, draw)
            end.set_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current]+1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count +=1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.set_open()
        draw()

        if current != start:
            current.set_close()

    return False            


def make_grid(rows,width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            cell = Cell(i, j, gap, rows)
            grid[i].append(cell)
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0,i*gap), (width,i*gap))
        pygame.draw.line(win, GREY, (i*gap,0), (i*gap,width))

def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for cell in row:
            cell.draw(win)

    draw_grid(win,rows, width)
    pygame.display.update()

def get_click_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap
    return row, col

def draw_line_between(grid, start_pos, end_pos):
    r1, c1 = start_pos
    r2, c2 = end_pos

    # Move row-wise first
    row_step = 1 if r2 > r1 else -1
    for r in range(r1, r2 + row_step, row_step):
        if 0 <= r < len(grid) and 0 <= c1 < len(grid[0]):
            grid[r][c1].reset()

    # Then move col-wise
    col_step = 1 if c2 > c1 else -1
    for c in range(c1, c2 + col_step, col_step):
        if 0 <= r2 < len(grid) and 0 <= c < len(grid[0]):
            grid[r2][c].reset()


def main(win, width):
    ROWS = 400
    grid = make_grid(ROWS, width)

    # Step 1: Set everything to wall
    for row in grid:
        for cell in row:
            cell.set_wall()

    # Step 2: Load graph and convert to grid positions
    G = load_graph()
    grid_positions = graph_to_grid_nodes(G, ROWS)

    # Step 3: Mark all nodes as white
    for row, col in grid_positions.values():
        if 0 <= row < ROWS and 0 <= col < ROWS:
            grid[row][col].reset()

    # Step 4: Mark edges (paths) as white lines
    for u, v in G.edges():
        if u in grid_positions and v in grid_positions:
            draw_line_between(grid, grid_positions[u], grid_positions[v])

    start = None
    end = None
    run = True

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_click_pos(pos, ROWS, width)
                cell = grid[row][col]
                if not start and not cell.is_wall():
                    start = cell
                    start.set_start()
                elif not end and not cell.is_wall():
                    end = cell
                    cell.set_end()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_click_pos(pos, ROWS, width)
                cell = grid[row][col]
                if cell == start:
                    start = None
                elif cell == end:
                    end = None
                else:
                    cell.reset()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for cell in row:
                            cell.update_neighbors(grid)
                    aStar(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_z:
                    start = None
                    end = None
                    main(win, width)
    pygame.quit()

main(WIN, WIDTH)
