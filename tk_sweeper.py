from tkinter import *
from random import randint
from time import time


class Game:
    state = [9, 10, True]  # field side length, number of mines, flag that allows new game after the end of current game
    timeron = True  # allows timer to work

    def __init__(self):
        """inits parameters that are unaffected by a new game"""
        self.root = Tk()  # STARTING TKINTER MAINLOOP
        self.root.title('tksweeper')
        if not Game.state[2]:  # ends the game if needed
            self.root.destroy()
        Game.state[2] = False  # prevents infinite restart of the game when game window is closed
        self.root.resizable(height=False, width=False)  # prevents game window resize
        self.images = {-2: PhotoImage(file='blankplate.png'), -1: PhotoImage(file='mine.png'),
                       -3: PhotoImage(file='flag.png'), 0: PhotoImage(file='0.png'),
                       1: PhotoImage(file='1.png'), 2: PhotoImage(file='2.png'), 3: PhotoImage(file='3.png'),
                       4: PhotoImage(file='4.png'), 5: PhotoImage(file='5.png'), 6: PhotoImage(file='6.png'),
                       7: PhotoImage(file='7.png'), 8: PhotoImage(file='8.png'), 9: PhotoImage(file='smile.png'),
                       10: PhotoImage(file='grin.png'), 11: PhotoImage(file='boom.png')}  # creates image objects
        self.gamesize = IntVar()  # variable for choosing game size in menu
        self.gamesize.set(0)
        self.menu = Menu(self.root)  # creating menu
        self.root.config(menu=self.menu)
        self.newgamemenu = Menu(self.menu, tearoff=0)
        self.newgamemenu.add_radiobutton(label="Small", value=0, variable=self.gamesize, command=self.change_game_size)
        self.newgamemenu.add_radiobutton(label="Medium", value=1, variable=self.gamesize, command=self.change_game_size)
        self.newgamemenu.add_radiobutton(label="Big", value=2, variable=self.gamesize, command=self.change_game_size)
        self.menu.add_cascade(label="New game", menu=self.newgamemenu)
        self.reinit()  # inits other parameters
        self.root.mainloop()  # ending tkinter mainloop

    def reinit(self):
        """inits parameters that need reiniting at the start of every new game"""
        self.lost = False  # flag that current game have ended and further clicks on a game field will have no effect
        Game.timeron = True  # flag that allows game timer to encrease
        self.starttime = time()  # marks moment of the current game start
        self.size = Game.state[0]  # sets size of the game field
        self.n_mines = Game.state[1]  # sets number of mines
        self.field, self.field_view = self.create_field()  # creating two lists of game field state
        self.press = []  # list to put closured funtions for each Button on a game field
        self.tiles = []  # list tp put Gamebutton objects
        self.checked = set()  # set of indexes of tiles that has been cheked by expand_field function
        for i in range(self.size ** 2):  # filling list of closured functions for each Button
            self.press.append(self.make_f(i))

        self.frame1 = Frame(height=54)  # upper frame - for mine count, new game button and timer
        self.frame2 = Frame()  # lower frame - for game field
        self.frame1.pack(fill=X)
        self.frame2.pack()
        self.minedisplay = Label(self.frame1, text=f'{self.n_mines}', font='Impact 26')  # shows mine count
        self.minedisplay.place(x=self.size * 7, y=0)

        self.mainbutton = Button(self.frame1, image=self.images[9], command=self.newgame)  # start new game button
        self.mainbutton.place(x=self.size * 38 // 2 - 28, y=0)

        self.timer = Label(self.frame1, text='00:00', font='Impact 26')  # shows timer
        self.timer.place(x=self.size * 28, y=0)
        self.update_timer()  # calls for starting timer
        for i in range(self.size):  # creating Button for each cell, placing them into grid
            for j in range(self.size):
                self.tiles.append(Button(self.frame2, image=self.images[-2], bg='DimGray'))
                self.tiles[i * self.size + j].grid(row=i, column=j)
                self.tiles[i * self.size + j].bind('<Button>', self.press[i * self.size + j])

    def update_timer(self):
        """timer funtion"""
        if Game.timeron:
            now = -int(self.starttime - time())  # registers current moment
            self.timer.configure(text=now)  # updates timer label
            self.root.after(1000, self.update_timer)  # sets update timer interval

    def change_game_size(self):
        """changes game field size and starts new game """
        if self.gamesize.get() == 0:
            Game.state[0] = 9
            Game.state[1] = 10
        elif self.gamesize.get() == 1:
            Game.state[0] = 14
            Game.state[1] = 30
        elif self.gamesize.get() == 2:
            Game.state[0] = 18
            Game.state[1] = 50
        self.newgame()

    def create_field(self):
        """Returns 2 fields - one with mines and numbers (field) and anoter with tiles opened by player(field_view)"""
        n_mines = self.n_mines

        def count_adj_mines(_field: list, m: int) -> int:
            """Returns number of mines in tiles ajacent to field[i]"""
            n = 0
            for j in range(-1, 2):
                for k in range(-1, 2):  # doesn't allow to step out the game field
                    x = m % self.size + j
                    y = m // self.size + k
                    if x < 0 or x >= self.size or y < 0 or y >= self.size:
                        continue
                    if _field[y * self.size + x] == -1:  # mine found
                        n += 1
            return n

        field = [0] * self.size ** 2  # list for mines and numbers -1=mine, 0=clear cell, other=number of mines nearby
        while n_mines > 0:  # placing mines at random tiles
            i = randint(0, len(field) - 1)
            if field[i] == -1:
                continue
            field[i] = -1
            n_mines -= 1
        for i, v in enumerate(field):  # counts ajacent mines to each empty cell
            if v != -1:
                field[i] = count_adj_mines(field, i)
        field_view = [-2] * self.size ** 2  # list for opened tiles -2=not yet opened, other = copied from field list
        return field, field_view

    def make_f(self, i: int):
        """returns closured calling for mouse click function for given field index"""
        def f(event):
            mousebutton = int(str(event)[str(event).find('num=') + 4])  # gets n of mousebutton from event description
            return self.check_btn_call(i, mousebutton)
        return f

    def check_btn_call(self, i: int, mousebutton: int):
        """returns calling either for R or L click for given field index"""
        if mousebutton == 1:  # 1 = Left mouse button
            self.check_cell(i)
        elif mousebutton == 3:  # 3 = Right mouse button
            self.plant_flag(i)

    def check_cell(self, i: int):
        """left click on a Button with index i"""
        if not self.lost:  # function does not work if game have already ended
            if self.field_view[i] == -2:  # works only if button not yet checked
                self.field_view[i] = self.field[i]
                if self.field[i] == 0:  # found clear cell
                    self.tiles[i].config(bg='LightGrey', image=self.images[self.field[i]])  # changes button view
                    self.expand_view(i)  # expand view on other ajacent clear tiles
                    self.check_game_state()  # check for win
                if self.field[i] > 0:  # found a number
                    self.checked.add(i)
                    self.field_view[i] = self.field[i]
                    self.tiles[i].config(bg='LightGrey', image=self.images[self.field[i]])  # changes button view
                    self.check_game_state()  # check for win
                elif self.field[i] == -1:  # step on a mine
                    Game.timeron = False  # stops timer
                    self.lost = True  # prevents opening new tiles after game end
                    self.mainbutton.configure(image=self.images[11])  # changes
                    for j, v in enumerate(self.tiles):
                        if self.field[j] == -1:
                            self.field_view[j] = -1
                            v.configure(image=self.images[-1])  # shows all mines
                            if i == j:
                                continue
                            v.configure(state='disabled')  # shades all tiles exept last mine

    def plant_flag(self, i: int):
        """right click on a Button with index i"""
        if self.field_view[i] == -2:  # plants flag
            self.field_view[i] = -3
            self.tiles[i].config(bg='Khaki', image=self.images[-3])
            self.minedisplay.configure(text=f'{self.n_mines-self.field_view.count(-3)}')
            self.check_game_state()  # checks for a win
        elif self.field_view[i] == -3:  # removes flag
            self.field_view[i] = -2
            self.tiles[i].config(bg='DimGrey', image=self.images[-2])
            self.minedisplay.configure(text=f'{self.n_mines-self.field_view.count(-3)}')

    def expand_view(self, i: int):
        """if clear cell is opened - recurively opens all ajacent clear tiles"""
        if i not in self.checked:
            self.checked.add(i)
            tocheck = set()
            for j in range(-1, 2):
                for k in range(-1, 2):
                    x = int(i % self.size + j)
                    y = int(i // self.size + k)
                    if x < 0 or x >= self.size or y < 0 or y >= self.size or y * self.size + x in self.checked:
                        continue
                    self.field_view[y * self.size + x] = self.field[y * self.size + x]
                    self.tiles[y * self.size + x].config(bg='LightGrey', image=self.images[
                        self.field[y * self.size + x]])  # change tile view
                    if self.field[y * self.size + x] == 0:
                        tocheck.add(y * self.size + x)  # if opened tile is clear - marks it for further check
            tocheck -= self.checked  # removes already checked tiles from pending checks
            for i in tocheck:
                self.expand_view(i)  # calls for pending check

    def check_game_state(self):
        """Checks if player have won"""
        if self.field_view.count(-2) == 0:  # check that there is no unopened/unflagged tiles
            errs = 0
            for i in range(self.size):  # chek match of flag and mine adresses
                if self.field_view[i] == -3 and self.field[i] != -1:
                    errs += 1
            if errs == 0:
                Game.timeron = False  # stops timer
                self.mainbutton.configure(image=self.images[10])  # changes new game button view

    def newgame(self):
        """destroys all visual elements and calls for game reinit"""
        self.frame1.destroy()
        self.frame2.destroy()
        self.minedisplay.destroy()
        self.mainbutton.destroy()
        self.timer.destroy()
        for btn in self.tiles:
            btn.destroy()
        self.reinit()


if __name__ == "__main__":
    while Game.state[2]:
        game = Game()
