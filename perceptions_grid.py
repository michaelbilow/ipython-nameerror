import math
from perceptions_cell import *
import Image, ImageDraw

class PGrid:
    def __init__(self,grid = None,length=10,width=10,bc='Torus',randomize = 0,skepticism = 0):
        if grid is not None:
            self.length = len(grid[0])
            self.width = len(grid[1])
        else:
            self.length = length
            self.width = width
        
        self.grid = [['' for j in range(self.width)] for i in range(self.length)]
        for i in range(self.length):
            for j in range(self.width):
                if grid:
                    self.grid[i][j] = PCell(grid[i][j],randomize = randomize,skepticism = skepticism)
                else:
                    self.grid[i][j] = PCell()
        ## The grid is represented as an empty list located at every point
        ## in the length and width.
        self.boundary_conditions = bc
        return
      
    def __str__(self):
        output = '\n'.join(['\t'.join([str(self.grid[i][j]) for j in range(self.width)]) for i in range(self.length)])
        return output
    
    def draw(self, outputfn = 'SHITTER.JPG',cell_size = 5,borders=False):
        img = Image.new("RGB", (cell_size*self.length, cell_size*self.width), "#FFFFFF")
        draw = ImageDraw.Draw(img)
        grid = self.grid
        length = self.length
        width = self.width
        for i in range(length):
            for j in range(width):
                cell_value = grid[i][j].value
                if cell_value == 1024:
                    pass
                red_value = hex(cell_value/2-257)
                blue_value = hex(255-cell_value/2)
                green_value = hex(255-abs(256-cell_value/2))
                raw_colors = [red_value,green_value,blue_value]
                raw_colors = [color[:-1] if color[-1] == 'L' else color for color in raw_colors]
                raw_colors = [color.split('x') for color in raw_colors]
                clean_colors = [color[1].zfill(2) if color[0] != '-0' else '00' for color in raw_colors]
                hex_color = '#'
                fill_color = '#' + ''.join(clean_colors)
                box = [(cell_size * i, cell_size*j), (cell_size * (i+1),cell_size * (j+1))]
                if borders:
                    draw.rectangle(box,outline = "#000000", fill = fill_color)
                else:
                    draw.rectangle(box, fill = fill_color)
        img.save(outputfn, "JPEG")
        return

    def to_list(self):
        return [self.grid[i][j] for i in range(self.length) for j in range(self.width)]
    
###The raw nearest neighbors are ordered: Self, NW, N, NE, E, SE, S, SW, W 
#    def neighbors(self,i,j):
#        
#        raw_neighbors = [(i,j),(i-1,j-1),(i-1,j),(i-1,j+1), (i,j+1), (i+1,j+1),
#                         (i+1,j),(i+1,j-1),(i,j-1)]
#        
#        bc = self.boundary_conditions
#        if bc == 'Fixed':
#            N = range(1,4)
#            S = range(3,6)
#            E = range(5,8)
#            W = (7,8,1)
#            avoidset = []
#            if i == 0:
#                avoidset.extend(N)
#            elif i == self.length - 1:
#                avoidset.extend(S)
#            
#            if j == 0:
#                avoidset.extend(W)
#            elif j == self.width - 1:
#                avoidset.extend(E)
#            
#            good_neighbors = []
#            for i in range(8):
#                if i in avoidset:
#                    continue
#                else:
#                    good_neighbors.append(raw_neighbors[i])        
#        elif bc == 'Torus':
#            good_neighbors = raw_neighbors
#        
#        ## Duplicate neighbors can emerge under rare conditions
#        ## e.g. length or width <= 2.  This is a fast but not
#        ## order-stable way to remove duplicates.
#        neighbor_set = set([(x[0] % self.length, x[1] % self.width) for x in good_neighbors])
#        return list(neighbor_set)

    def neighbors(self,i,j):
        
        raw_neighbors = [(i-1,j), (i,j+1), (i+1,j), (i,j-1)]
        
        bc = self.boundary_conditions
        if bc == 'Fixed':
            good_neighbors = raw_neighbors
        elif bc == 'Torus':
            good_neighbors = raw_neighbors
        
        ## Duplicate neighbors can emerge under rare conditions
        ## e.g. length or width <= 2.  This is a fast but not
        ## order-stable way to remove duplicates.
        neighbor_set = set([(x[0] % self.length, x[1] % self.width) for x in good_neighbors])
        return list(neighbor_set)

############################################################
############################################################
##                  MUTATOR METHODS                    #####
############################################################
############################################################

## The following methods change the internal state of the grid
## or the cells in the grid.

## reset_clocks changes the rep_start of every element of the grid, to avoid
## possible purifying selection towards any number.  It can be run every ~100-1000
## fractional generations.
    def reset_rep_start(self):
        random.seed()
        for i in range(self.length):
            for j in range(self.width):
                self.grid[i][j][0].set_rep_start(random.random())
        return


def read_Grid2D_from_text_file(input_fn):
    input_file = open(input_fn,'r')
    input_file.readline()
    length = input_file.readline().strip().split(':')[-1]
    width = input_file.readline().strip().split(':')[-1]
    boundary_conditions = input_file.readline().strip().split(':')[-1]
    
    length = int(length.strip())
    width = int(width.strip())
    boundary_conditions = boundary_conditions.strip()
    
    input_file.readline()
    grid = [line.strip().split('\t') for line in input_file]
    return Grid2D(length,width,boundary_conditions,grid)
