#!/usr/bin/python3
# ^^ note the python directive on the first line
# COMP3411/9814 agent initiation file 
# requires the host to be running before the agent
# typical initiation would be (file in working directory, port = 31415)
#        python3 agent.py -p 31415
# created by Leo Hoare
# with slight modifications by Alan Blair

import sys
import socket
import random
from collections import deque

tools = {}
treasure = {}
obstacles = {}
position = (80, 80)


# declaring visible grid to agent
view = [['' for _ in range(5)] for _ in range(5)]
game_map = [['' for _ in range(160)] for _ in range(160)]

def process_view(view):
    # Initialize dictionaries for tools, treasure, and obstacle
    new_element = {}

    # Iterate over each row in the grid (view)
    for row_index, row in enumerate(view):
        for col_index, element in enumerate(row):
            if element != ' ': 
                new_element.append((row_index, col_index))
            # Check what element we are dealing with and categorize it
            if element == 'X':  # Axe (Tool)
                if 'X' not in tools:
                    tools['X'] = []
                tools['X'].append((row_index, col_index))
            elif element == 'K':  # Key (Tool)
                if 'K' not in tools:
                    tools['K'] = []
                tools['K'].append((row_index, col_index))
            elif element == 'D':  # Dynamite (Tool)
                if 'D' not in tools:
                    tools['D'] = []
                tools['D'].append((row_index, col_index))
            elif element == 'T':  # Treasure
                treasure[(row_index, col_index)] = 'Treasure'
            elif element == '*':  # Wall (Obstacle)
                if '*' not in obstacles:
                    obstacles['*'] = []
                obstacles['*'].append((row_index, col_index))
            elif element == 'T':  # Tree (Obstacle)
                if 'T' not in obstacles:
                    obstacles['T'] = []
                obstacles['T'].append((row_index, col_index))
            elif element == 'R':  # Raft (Obstacle)
                if 'R' not in obstacles:
                    obstacles['R'] = []
                obstacles['R'].append((row_index, col_index))
            elif element == '~':  # water (Obstacle)
                if '~' not in obstacles:
                    obstacles['~'] = []
                obstacles['~'].append((row_index, col_index))

       
    return tools, treasure, obstacles

def update_map(position, new_elements):

    x, y = position[0] - 80, position[1] - 80
    for key, e in new_elements.items():
        location = (e[0]+x,e[1]+y)
        if 0 <= location[0] < 160 and 0 <= location[1] < 160:
            game_map[location[0],location[1]] = key

    return game_map


def bfs(start, goal, game_map):
    # 四个方向：上、下、左、右
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    queue = deque([(start, [start])])  # 队列中的元素是 (当前位置, 路径)
    visited = set()
    visited.add(start)

    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == goal:
            return path

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 160 and 0 <= ny < 160 and (nx, ny) not in visited and game_map[nx][ny] != '*':  
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))

    return None  # 如果没有路径



# function to take get action from AI or user
def get_action(view):

    ## REPLACE THIS WITH AI CODE TO CHOOSE ACTION ##
    tools, treasure, obstacles = process_view(view)
    print("Tools:", tools)
    print("Treasure:", treasure)
    print("Obstacles:", obstacles)

     # 如果 treasure 字典中有宝藏，则使用 BFS 寻找宝藏
    if treasure:
        treasure_position = next(iter(treasure))  
        path = bfs(position, treasure_position, game_map)


    # # input loop to take input from user (only returns if this is valid)
    # while True:
    #     inp = input("Enter Action(s): ")
    #     inp.strip()
    #     final_string = ''
    #     for char in inp:
    #         if char in ['f','l','r','c','u','b','F','L','R','C','U','B']:
    #             final_string += char
    #             if final_string:
    #                  return final_string[0]

# helper function to print the grid
def print_grid(view):
    print('+-----+')
    for ln in view:
        print("|"+str(ln[0])+str(ln[1])+str(ln[2])+str(ln[3])+str(ln[4])+"|")
    print('+-----+')

if __name__ == "__main__":

    # checks for correct amount of arguments 
    if len(sys.argv) != 3:
        print("Usage Python3 "+sys.argv[0]+" -p port \n")
        sys.exit(1)

    port = int(sys.argv[2])

    # checking for valid port number
    if not 1025 <= port <= 65535:
        print('Incorrect port number')
        sys.exit()

    # creates TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
         # tries to connect to host
         # requires host is running before agent
         sock.connect(('localhost',port))
    except (ConnectionRefusedError):
         print('Connection refused, check host is running')
         sys.exit()

    # navigates through grid with input stream of data
    i=0
    j=0
    while True:
        data=sock.recv(100)
        if not data:
            exit()
        for ch in data:
            if (i==2 and j==2):
                view[i][j] = '^'
                view[i][j+1] = chr(ch)
                j+=1 
            else:
                view[i][j] = chr(ch)
            j+=1
            if j>4:
                j=0
                i=(i+1)%5
        if j==0 and i==0:
            print_grid(view) # COMMENT THIS OUT ON SUBMISSION
            action = get_action(view) # gets new actions
            sock.send(action.encode('utf-8'))

    sock.close()