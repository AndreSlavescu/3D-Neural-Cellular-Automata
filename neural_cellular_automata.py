import time
import threading
from enum import Enum
from panda3d.core import Point3
from direct.showbase.ShowBase import ShowBase
from direct.task import Task

class Entities(Enum):
    SURVIVAL = {4, 5}  
    BIRTH = {4, 5} 
    COUNTER = 5

class Cell:
    def __init__(self, cube, state):
        self.cube = cube  
        self.state = state 
        self.next_state = None 
        self.counter = 0 
        self.update_color()

    def update_color(self):
        if self.state:
            self.cube.setColor((0, 1, 0, 1))  
        elif self.counter > 0:
            self.cube.setColor((1, 1, 0, 1))  
        else:
            self.cube.setColor((1, 0, 0, 1)) 

class GridManager:
    def __init__(self, render, loader):
        self.grid_size = 20
        self.cube_distance = 0.55
        self.start_pos = -(self.grid_size - 1) * self.cube_distance / 2
        self.grid_node = render.attachNewNode("GridNode")
        self.grid_node.setHpr(30, 30, 0)
        self.grid = self.setup_grid(render, loader) 

    def setup_grid(self, render, loader):
        grid = [[[None for _ in range(self.grid_size)] for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    cube = loader.loadModel("models/box")
                    cube.setScale(0.25, 0.25, 0.25)
                    cube.setPos(Point3(self.start_pos + x * self.cube_distance, self.start_pos + y * self.cube_distance, self.start_pos + z * self.cube_distance))
                    cube.reparentTo(self.grid_node)
                    start_nodes = [(4, 4, 4), (4, 4, 5), (4, 5, 4), (4, 5, 5), (4, 4, 6), (4, 6, 4)]
                    is_middle_cube = (x, y, z) in start_nodes
                    grid[x][y][z] = Cell(cube, is_middle_cube)
                    grid[x][y][z].update_color() 
        return grid

    def count_neighbors(self, x, y, z):
        alive_neighbors = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                for dz in range(-1, 2):
                    if dx == dy == dz == 0:
                        continue  
                    nx, ny, nz = x + dx, y + dy, z + dz
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and 0 <= nz < self.grid_size:
                        if self.grid[nx][ny][nz].state:
                            alive_neighbors += 1
        return alive_neighbors
    
    def update_next_state(self):
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    cell = self.grid[x][y][z]
                    neighbors = self.count_neighbors(x, y, z)
                    if cell.state:
                        if neighbors not in Entities.SURVIVAL.value:  
                            cell.next_state = False  
                            cell.counter = Entities.COUNTER.value
                        else:
                            cell.next_state = True
                    else:
                        if neighbors in Entities.BIRTH.value: 
                            cell.next_state = True
                        else:
                            cell.next_state = False

    def update(self):
        update_thread = threading.Thread(target=self.update_next_state)
        update_thread.start()
        update_thread.join()  

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                for z in range(self.grid_size):
                    cell = self.grid[x][y][z]

                    if cell.next_state == False and cell.state == True:
                        cell.counter -= 1
                        if cell.counter == 0:
                            cell.next_state = False  

                    cell.state = cell.next_state 
                    cell.update_color()  

                    if cell.state or cell.counter > 0:
                        cell.cube.show()
                    else:
                        cell.cube.hide()

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.grid_manager = GridManager(self.render, self.loader)
        self.taskMgr.add(self.camera_task, "camera_task")
        self.taskMgr.add(self.rotate_grid_task, "rotate_grid_task")
        self.taskMgr.add(self.update_task, "update_task")

    def camera_task(self, task):
        self.camera.setPos(0, -30, 10)
        self.camera.lookAt(Point3(0, 0, 0))
        return Task.cont  

    def rotate_grid_task(self, task):
        angle_degrees = task.time * 6.0
        self.grid_manager.grid_node.setHpr(30, 30, angle_degrees)
        return Task.cont

    def update_task(self, task):
        time.sleep(0.1)
        self.grid_manager.update()
        return Task.cont

app = MyApp()
app.run()
