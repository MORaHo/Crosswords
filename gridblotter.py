import pygame as pg
import numpy
from gridder import grid_generator
import random
from bs4 import BeautifulSoup as bs
import requests

BLOT = 7
ROW = int(16)
SPACE = 40
COLUMN = int(16) 
EMPTY = 0
WIDTH = SPACE * (COLUMN-1)
HEIGHT = SPACE * (ROW-1)
LINE_COLOUR = (0,0,0)

URL = "https://www.crosswordnexus.com/finder.php?clue=&pattern="

run = True
board = grid_generator(ROW,COLUMN)

pg.init()
screen = pg.display.set_mode((WIDTH,HEIGHT),0,32)
default_font = pg.font.SysFont("Arial",SPACE-3)
pg.display.set_caption("Blotter")

def draw_board():

    screen.fill((255,255,255))
    for i in range(0,COLUMN-1):
        pg.draw.line(screen, LINE_COLOUR, ( SPACE * i , 0 ), ( SPACE * i, (ROW-1) * SPACE ), 1) # Vertical lines
    for j in range(0,ROW-1):
        pg.draw.line(screen, LINE_COLOUR, ( 0 , SPACE * j ), ( (COLUMN-1) * SPACE , SPACE * j), 1) # Horizontal lines
    
    for i in range(ROW-1):
        for j in range(COLUMN-1):
            if board[i][j]:
                rect = pg.Rect(0,0,SPACE-3,SPACE-3)
                rect.center = (j*SPACE+int(SPACE/2),i*SPACE+int(SPACE/2))
                pg.draw.rect(screen,(0,0,0),rect)
    pg.display.update()
draw_board() #I'm calling it so that it doesn't start on a black screen

def get_mouse_position():

    position = pg.mouse.get_pos()
    x_position = int((position[0]) // SPACE)
    y_position = int((position[1]) // SPACE)
    return y_position, x_position

while run:

    for event in pg.event.get():

        if event.type == pg.QUIT:
            run = False
        
        if event.type == pg.MOUSEBUTTONDOWN:

            mouse_position = get_mouse_position()
            row = mouse_position[0]
            column = mouse_position[1]
            
            if board[row][column] != BLOT:
                board[row][column] = BLOT
            else:
                board[row][column] = EMPTY
                
            draw_board()

def is_within_conditions(array,i):
    length = len(array)
    if i < length-1:
        if array[i] != array[i+1] and array[i] != array[i-1]:
            return True
        else:
            return False
    elif i == length-1:
        return True
    else:
        return False

def space_determiner():

    global horizontal_word_array
    global vertical_word_array
    horizontal_word_array = []
    vertical_word_array = []

    for j in range(ROW):
        row = board[j]
        joined_x = "".join([str(number) for number in row])
        for i in range(len(joined_x)):
            if i == "0": 
                if joined_x[i] == "0":
                    horizontal_word_array.append((j,i))
                elif joined_x[i+1] == "7":
                    horizontal_word_array.append((j,i))
                else:
                    continue
            if joined_x[i] == "0" and joined_x[i-1] != "0":
                horizontal_word_array.append((j,i))
            if joined_x[i] == "0":
                if joined_x[i+1] == "7":
                    horizontal_word_array.append((j,i))
    for i in range(COLUMN):
        joined_y = "".join([str(board[j][i]) for j in range(ROW)])
        for j in range(len(joined_y)):
            if j == "0": 
                if joined_y[j] == "0":
                    vertical_word_array.append((j,i))
                elif joined_y[j+1] == "7":
                    vertical_word_array.append((j,i))
                else:    
                    continue
            if joined_y[j] == "0" and joined_y[j-1] != "0":
                vertical_word_array.append((j,i))
            if joined_y[j] == "0":
                if joined_y[j+1] == "7":
                    vertical_word_array.append((j,i))
    
    # Pruning
    horizontal_word_array = [coordinate for i,coordinate in enumerate(horizontal_word_array) if is_within_conditions(horizontal_word_array,i)]
    vertical_word_array = [coordinate for i,coordinate in enumerate(vertical_word_array) if is_within_conditions(vertical_word_array,i)]
    if len(horizontal_word_array) % 2 != 0:
        horizontal_word_array = horizontal_word_array[:-1]
    if len(vertical_word_array) % 2 != 0:
        vertical_word_array = vertical_word_array[:-1]

space_determiner()

word_array = horizontal_word_array + vertical_word_array




while len(word_array) != 0:

    i = random.randint(0,int(len(word_array)/2)-1)

    word_length = word_array[2*i+1][0] - word_array[2*i][0] + word_array[2*i+1][1] - word_array[2*i][1] + 1
    #Instead of pruning I could have make it so that it skipped over any word that had length == 1, it would mean less calculation, but we wouldn't immediately know the number of words.
    start_pos = [word_array[2*i][0],word_array[2*i][1]]

    
    if word_array[2*i+1][0] - word_array[2*i][0] != 0: #vertical
        word = ""
        for v in range(word_length):
            letter_pos = [start_pos[0]+v,start_pos[1]]
            if board[letter_pos[0]][letter_pos[1]] != 0:
                word += board[letter_pos[0]][letter_pos[1]]
            else:
                word += "."
        #website search
        page = requests.get(URL + word)
        soup = bs(page.content, "html.parser")
        words = soup.find_all("a")
        words = [word for word in words if "/word/" in word["href"]]
        if len(words) == 0:
            word_array.pop(2*i)
            word_array.pop(2*i)
            continue
        word = words[0].text
        for n in range(word_length):
            letter_pos = [start_pos[0]+n,start_pos[1]]  
            board[letter_pos[0]][letter_pos[1]] = word[n]
        pass

    elif word_array[2*i+1][1] - word_array[2*i][1] != 0: #horizontal
        board_spaces = board[start_pos[0]][start_pos[1]:start_pos[1]+word_length]
        word = ""
        for w in range(word_length):
            if board_spaces[w] != 0:
                word += board_spaces[w]
            else:
                word += "."
        #website search
        page = requests.get(URL+word)
        soup = bs(page.content, "html.parser")
        words = soup.find_all("a")
        words = [word for word in words if "/word/" in word["href"]]
        if len(words) == 0:
            word_array.pop(2*i)
            word_array.pop(2*i)
            continue

        word = words[random.randint(0,len(words)-1)].text
        for m in range(word_length):
            letter_pos = [start_pos[0],start_pos[1]+m]
            board[letter_pos[0]][letter_pos[1]] = word[m]
        pass
        
    word_array.pop(2*i)
    word_array.pop(2*i)


def visualiser():
    for y in range(ROW):
        for x in range(COLUMN):
            if board[y][x] == 7 or board[y][x] == 0:
                continue
            letter_surface = default_font.render(board[y][x], True, pg.Color("#000000"))
            letter_rect = letter_surface.get_rect()
            letter_position = (x*SPACE+int(SPACE/2),y*SPACE+int(SPACE/2))
            letter_rect.center = letter_position
            screen.blit(letter_surface,letter_rect)
    pg.display.update()

visualiser()

run = True

while run:

    for event in pg.event.get():

        if event.type == pg.QUIT:
            run = False
        













