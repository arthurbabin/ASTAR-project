import pygame
import random

# COLORS
BORDER_COLOR    = (35,35,35)
BG_COLOR        = (  0,  0,  0)
OBSTACLE_COLOR  = (70, 70, 70)
END_COLOR       = (255,  0,  0)
EXPLORED_COLOR  = (0, 97, 0)
TBEXPLORED_COLOR = (0,  151,  0)
START_COLOR     = (255,255,255)
PATH_COLOR      = (0, 130, 255)

### VARIABLES #############

size_grid = (30,30) #(horizontally>1,vertically>1)
size_cell = (30,30) #in pixels
margin = 3 #in pixels
width, height = size_cell
grid,costs,explored,toBeExplored,parents=[[]]*5
start,end=[(0,0)]*2
done,ready,pathFound,finished = [False]*4

### FUNCTIONS #############
def changeNatureOfCell(c,r,newNature):
    try:
        if grid[r][c]>=0:
            grid[r][c] = newNature #don't modify the START and the END
    except:
        pass

def getCellFromCoordinates(x_c, y_c):
    return (x_c // (width + margin), y_c // (height + margin))

def mouseModification(x_c,y_c,newNature):
    c,r=getCellFromCoordinates(x_c,y_c)
    changeNatureOfCell(c,r,newNature)

def setRandomStartEnd():
    start = random.randint(0,(size_grid[0]-1)//2),random.randint(0,(size_grid[1]-1)//2)
    end = start
    while end==start:
        end = random.randint((size_grid[0]-1)//2,size_grid[0]-1),random.randint((size_grid[1]-1)//2,size_grid[1]-1)
    return start,end

def checkObstacle(cell):
    nature = grid[cell[1]][cell[0]]
    return nature!=1 and nature!=-2 and nature!=2

def getListOfNeighbours(cell):
    c,r=cell
    Ldiag,Lperp=[],[]
    neighbours={}
    if c==0:
        if r==0:
            Lperp=[(c+1,r),(c,r+1)]
            Ldiag=[(c+1,r+1)]
        elif r==size_grid[0]-1:
            Lperp=[(c+1,r),(c,r-1)]
            Ldiag=[(c+1,r-1)]
        else:
            Lperp=[(c+1,r),(c,r+1),(c,r-1)]
            Ldiag=[(c+1,r+1),(c+1,r-1)]
    elif c==size_grid[1]-1:
        if r==0:
            Lperp=[(c-1,r),(c,r+1)]
            Ldiag=[(c-1,r+1)]
        elif r==size_grid[0]-1:
            Lperp=[(c-1,r),(c,r-1)]
            Ldiag=[(c-1,r-1)]
        else:
            Lperp=[(c-1,r),(c,r+1),(c,r-1)]
            Ldiag=[(c-1,r+1),(c-1,r-1)]
    elif r==0:
        Lperp=[(c+1,r),(c,r+1),(c-1,r)]
        Ldiag=[(c+1,r+1),(c-1,r+1)]
    elif r==size_grid[0]-1:
        Lperp=[(c+1,r),(c-1,r),(c,r-1)]
        Ldiag=[(c+1,r-1),(c-1,r-1)]
    else:
        Lperp=[(c+1,r),(c,r+1),(c-1,r),(c,r-1)]
        Ldiag=[(c+1,r+1),(c-1,r+1),(c+1,r-1),(c-1,r-1)]
    Lperp=list(filter(checkObstacle,Lperp))
    Ldiag=list(filter(checkObstacle,Ldiag))
    for i in Lperp:
        neighbours[i]="perp"
    for i in Ldiag:
        neighbours[i]="diag"
    return neighbours

def hCost(c,r):
    dx = abs(c-end[0])
    dy = abs(r-end[1])
    if dx==0:
        return dy*10
    elif dy==0:
        return dx*10
    else:
        m1 = max(dx,dy)
        m2 = min(dx,dy)
        return m2*14+(m1-m2)*10

def initPathFindingVariables():
    grid = [[0 for x in range(size_grid[0])] for y in range(size_grid[1])] #grid of cells
    parents = [[(0,0) for x in range(size_grid[0])] for y in range(size_grid[1])]
    costs = [[[hCost(x,y),0,] for x in range(size_grid[0])] for y in range(size_grid[1])] # f,g costs for each cell (h cost is precomputed and added to f cost)
    explored = []
    toBeExplored = [start]
    grid[start[1]][start[0]]=-2
    grid[end[1]][end[0]]=-1
    parents[start[1]][start[0]]=start
    return grid,costs,explored,toBeExplored,parents

def nextToBeExplored(l):
    try:
        res = l[0]
        cost_res = costs[res[1]][res[0]][0]
        
        for i in l[1:]:
            if costs[i[1]][i[0]][0]<cost_res:
                res = i
                cost_res = costs[i[1]][i[0]][0]
        return res
    except:
        assert "Error no path found"
        pass 
def handleEvent(e):
    global ready
    global done
    if event.type == pygame.QUIT:            
            done = True
    elif not ready:
        if event.type == pygame.KEYDOWN:
            if event.key ==pygame.K_SPACE:
                ready = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button==1:
                mouseModification(x,y,1)
            elif event.button==3:
                mouseModification(x,y,0)
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]==1:           
                mouseModification(x,y,1)
            elif pygame.mouse.get_pressed()[2]==1:
                    mouseModification(x,y,0)

def processNextCell():
    global explored, toBeExplored, grid, parents, pathFound
    current = nextToBeExplored(toBeExplored)
    currentGCost = costs[current[1]][current[0]][1]
    toBeExplored.remove(current)
    if current==end:
        pathFound=True
    currentNeighbours=getListOfNeighbours(current)
    for n in currentNeighbours.keys():
        if n not in explored:
            newFCost=currentGCost+(costs[n[1]][n[0]][0]-costs[n[1]][n[0]][1])
            if currentNeighbours[n]=="diag":
                newFCost+=14
            else:
                newFCost+=10
            if newFCost<costs[n[1]][n[0]][0] or n not in toBeExplored:
                costs[n[1]][n[0]][0]=newFCost
                parents[n[1]][n[0]]=current
                if n not in toBeExplored:
                    toBeExplored.append(n)
                    if grid[n[1]][n[0]]==0:
                        grid[n[1]][n[0]]=2
    if grid[current[1]][current[0]]==2:
        grid[current[1]][current[0]]=3
    explored.append(current)

def updateGrid():
    global screen, grid, size
    screen.fill(BORDER_COLOR)
    for row in range(size_grid[1]):        
        for column in range(size_grid[0]):
            if grid[row][column]==-1:
                color = END_COLOR
            elif grid[row][column]==-2:
                color = START_COLOR
            elif grid[row][column]==1:                
                color = OBSTACLE_COLOR
            elif grid[row][column]==2 and not pathFound:
                color = EXPLORED_COLOR
            elif grid[row][column]==3 and not pathFound:
                color = TBEXPLORED_COLOR
            elif grid[row][column]==4:
                color = PATH_COLOR   
            else:                
                color = BG_COLOR            
            pygame.draw.rect(screen, color, [margin + (margin + width) * column, margin + (margin + height) * row, width, height])
            # display the costs on the cells
            # hCostsurface = font.render(str(costs[row][column][0]), False, (20,20,20))				    
            # screen.blit(hCostsurface,(2*margin + (margin + width) * column, 2*margin + (margin + height) * row)

### MAIN ##################
pygame.init()
size = (size_grid[0]*(width+margin)+margin,size_grid[1]*(height+margin)+margin+3*height)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("A* Algorithm")
pygame.font.init()
font = pygame.font.SysFont('dejavusans', 20)

start,end = setRandomStartEnd()
grid,costs,explored,toBeExplored,parents = initPathFindingVariables()
p=end
clock = pygame.time.Clock()
i=0
while not done:
    if i%10==0:
        pygame.image.save(screen,"ASTAR/screenshots/screenshot"+str(i)+".jpg")
    i+=1
    ### Main event loop
    for event in pygame.event.get():        
        handleEvent(event)
    x,y = pygame.mouse.get_pos()
    ### Compute the steps in order to find the path   
    if ready and not pathFound and i%3==0:
        processNextCell()
    
    if pathFound and not finished:
        while parents[p[1]][p[0]]!=p:
            if grid[p[1]][p[0]]!=-1:
                grid[p[1]][p[0]]=4
            p = parents[p[1]][p[0]]
    ###  Draw the steps
    updateGrid()
    tutoSurface = font.render("Left-Click to put walls | Right-Click to delete wall | Space to find the path", False, (255,255,255))				    
    screen.blit(tutoSurface,(2*width,size_grid[1]*(height+margin)+height))
    pygame.display.flip()   
    clock.tick(60)

pygame.quit()