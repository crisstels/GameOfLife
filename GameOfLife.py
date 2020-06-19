#!/usr/bin/python3
import copy
from tkinter import *


def next_cell_state(neighbours_sum=0, me_alive=False):
    return (neighbours_sum == 3 and not me_alive) or (1 < neighbours_sum < 4 and me_alive)


"""def gen_form(name='', x=0, y=0):
    objects = {
        'block': [[x, y], [x + 1, y], [x, y + 1], [x + 1, y + 1]],
        'tub': [[x, y + 1], [x + 1, y], [x + 1, y + 2], [x + 2, y + 1]],
        'boat': [[x, y + 1], [x + 1, y], [x + 1, y + 2], [x + 2, y + 1], [x + 2, y + 2]],
        'rpentomino': [[x, y + 1], [x + 1, y], [x + 1, y + 1], [x + 1, y + 2], [x + 2, y]],
        'LWSS': [[x, y + 2], [x + 1, y], [x + 1, y + 2], [x + 2, y + 1], [x + 2, y + 2]]

    }

    if name in objects:
        return objects[name]
    else:
        return []"""


class GamePlay:
    # param kwargs configuration object
    def __init__(self, tk_root, **kwargs):
        alive = []
        self.w_width = 100
        self.w_height = 100
        self.c_width = 600
        self.c_height = 600
        self.world = None
        self.canvas = None
        self.history = []

        for key, value in kwargs.items():
            if key == 'world':
                self.world = value
            if key == 'alive':
                alive = value
            if key == 'width':
                self.w_width = value
            if key == 'height':
                self.w_height = value
            if key == 'c_width':
                self.c_width = value
            if key == 'c_height':
                self.c_height = value
            if key == 'canvas':
                self.canvas = value

        if self.world is None:
            self.generate_world(self.w_width, self.w_height, alive)
        if self.canvas is not Canvas:
            self.canvas = Canvas(tk_root, width=self.c_width, height=self.c_height)

        tk_root.bind("<KeyPress>", self.keydown)
        tk_root.bind("<Button-1>", self.onclick)
        tk_root.bind("<B1-Motion>", self.drag)

        self.history_position = 0
        self.add_to_history()

        self.pause = False
        self.dragFirst = None

    def get_cell(self, x, y):
        return self.world[y][x]

    def set_cell(self, x, y, alive=False):
        if self.valid_index(x, y):
            self.world[y][x] = alive

    # generates a world
    def generate_world(self, width=None, height=None, alive=None):
        if alive is None:
            alive = []
        if width is None:
            width = self.w_width
        if height is None:
            height = self.w_height

        self.world = []
        row = []

        for _ in range(width):
            row.append(0)
        for _ in range(height):
            self.world.append(copy.deepcopy(row))
        for cell in alive:
            x = cell[0]
            y = cell[1]
            if self.valid_index(x, y):
                self.set_cell(x, y, True)

    # checks whether index is in range
    def valid_index(self, x, y):
        return len(self.world) > 1 and 0 <= x < len(self.world[0]) and 0 <= y < len(self.world)

    # returns dead or living cell
    def cell_alive(self, x, y):
        if self.valid_index(x, y):
            return self.get_cell(x, y)
        else:
            return False

    # checks the neighbourhood of a cell
    def neighbours_alive(self, x, y):
        # checks out the living neighbours
        counter = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if self.cell_alive(x + i, y + j):
                    counter += 1
        return counter

    # generates the next game step
    def next_step(self):
        if self.world is None:
            return
        new_world = copy.deepcopy(self.world)

        for y in range(self.w_height):
            for x in range(self.w_width):
                neighbours_sum = self.neighbours_alive(x, y)
                me_alive = self.cell_alive(x, y)
                new_world[y][x] = next_cell_state(neighbours_sum, me_alive)

        if new_world == self.world:
            return

        self.world = new_world
        self.add_to_history()
        self.history_position += 1

    # adds a black rectangle for a alive cell
    def render_cell(self, x, y):
        cell_w = self.c_width / self.w_width
        cell_h = self.c_height / self.w_height

        start_x = cell_w * x
        start_y = cell_h * y

        stop_x = start_x + cell_w - 1
        stop_y = start_y + cell_h - 1

        self.canvas.create_rectangle(start_x, start_y, stop_x, stop_y, fill='black')

    # renders the world
    def render_world(self):
        self.canvas.delete(ALL)
        for y in range(self.w_height):
            for x in range(self.w_width):
                if self.cell_alive(x, y):
                    self.render_cell(x, y)
        self.canvas.pack()

    # endless loop, ends by pausing the game
    def update_loop(self):
        if self.pause:
            return
        try:
            self.next_step()
            self.render_world()
            self.canvas.after(16, self.update_loop)
        except(KeyboardInterrupt, Exception):
            print("loop ended")

    # handles keydown events
    def keydown(self, e):
        if e.keysym == 'space':
            self.pause = not self.pause
        if not self.pause:
            self.history = self.history[0:self.history_position + 1]
            self.world = self.history[self.history_position]
            self.update_loop()
            return

        if e.keysym == 'Right' and self.pause:
            if self.history_position >= len(self.history) - 1:
                self.next_step()
            else:
                self.history_fw()

        if e.keysym == 'Left' and self.pause:
            self.history_bw()

        if e.keysym == 's':
            self.generate_world()
            self.backup_history()
            self.pause = True

        if e.keysym == 'd':
            self.canvas.delete('all')

        self.render_world()

    # toggles cell_alive state
    def onclick(self, e):
        x = int(e.x / (self.c_width / self.w_width))
        y = int(e.y / (self.c_height / self.w_height))

        self.dragFirst = self.get_cell(x, y)

        self.set_cell(x, y, not self.get_cell(x, y))
        self.backup_history()
        self.render_world()

    # handle mouse behaviour
    def drag(self, e):
        x = int(e.x / (self.c_width / self.w_width))
        y = int(e.y / (self.c_height / self.w_height))

        self.set_cell(x, y, not self.dragFirst)
        self.backup_history()
        self.render_world()

    # adds current state to the game history
    def add_to_history(self):
        self.history.append(copy.deepcopy(self.world))

    # adds currents state to the backup
    def backup_history(self):
        self.history[self.history_position] = self.world

    # move a step backwards in history
    def history_bw(self):
        self.history_position = max(0, self.history_position - 1)
        self.world = self.history[self.history_position]

    # move a step forward in history
    def history_fw(self):
        self.history_position = min(len(self.history) - 1, self.history_position)
        self.world = self.history[self.history_position]


def main():
    root = Tk()
    game = GamePlay(root)
    root.mainloop()


if __name__ == '__main__': main()
