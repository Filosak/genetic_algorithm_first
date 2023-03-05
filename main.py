import pygame
import time
import random
pygame.init()


#variables
width = 700
height = 700
grid_size = 20
number_of_moves = grid_size * 10
population = 1000
curr_moves = 1
generation = 1
mode = "wall"
block_size = width // grid_size
players = []
player_positions = []
players_in_finish = []
list_instructions = ["move_up", "move_down", "move_left", "move_right"]
walls_possitions = []
coins_possitions = []
coins_distance = []
run = True
start = False
finish_possition = None
min_moves = None

auto_move = pygame.USEREVENT + 1
pygame.time.set_timer(auto_move, 10)


# 0 = nothing
# 1 = player
# 2 = end point
# 3 - wall
# 4 - best player
# 5 - coin
board = [[0 for _ in range(grid_size)] for _ in range(grid_size)]

# screen
screen = pygame.display.set_mode((width, height))
screen.fill((255,255,255))

# functions
def put_objects_to_board():
    for y, x in player_positions:
        board[y][x] = 0
    
    for y, x in walls_possitions:
        board[y][x] = 3

    for y, x in coins_possitions[:len(coins_possitions)-1]:
        board[y][x] = 5

    board[coins_possitions[-1][0]][coins_possitions[-1][1]] = 2

def draw_players_to_board(players, player_positions):
    if start == True:
        put_objects_to_board()

    player_positions = []

    for player in players:
        y, x = player.pos

        if player.is_best == True:
            board[y][x] = 4
        else:
            board[y][x] = 1

        player_positions.append(player.pos)

    return player_positions
    


def draw_screen(board):
    screen.fill((255,255,255))

    for x in range(0, len(board)):
        for j in range(0, len(board[0])):
            if board[x][j] == 0:
                pygame.draw.rect(screen, (255,255,255), pygame.Rect(block_size * j, block_size * x, block_size, block_size))
            elif board[x][j] == 1:
                pygame.draw.rect(screen, (0,0,0), pygame.Rect(block_size * j, block_size * x, block_size, block_size))
            elif board[x][j] == 2:
                pygame.draw.rect(screen, (0,255,0), pygame.Rect(block_size * j, block_size * x, block_size, block_size))
            elif board[x][j] == 3:
                pygame.draw.rect(screen, (255,0,0), pygame.Rect(block_size * j, block_size * x, block_size, block_size))
            elif board[x][j] == 4:
                pygame.draw.rect(screen, (0,0,255), pygame.Rect(block_size * j, block_size * x, block_size, block_size))
            elif board[x][j] == 5:
                pygame.draw.rect(screen, (255,255,0), pygame.Rect(block_size * j, block_size * x, block_size, block_size))


class Player:
    def __init__(self, inctructions, coins_possitions):
        self.pos = (0, 0)
        self.moves = 0
        self.instructions = inctructions
        self.is_best = False
        self.collected_coins = 0
        self.c_pos = coins_possitions
        self.fitnes_sum = 0
        self.finished_fitness = 0

    def move(self):
        getattr(self, self.instructions[self.moves])()
        self.moves += 1

    def move_up(self):
        if self.pos[0] != 0 and board[self.pos[0]-1][self.pos[1]] != 3:
            self.pos = (self.pos[0]-1, self.pos[1])
            
    def move_down(self):
        if self.pos[0] != grid_size - 1 and board[self.pos[0]+1][self.pos[1]] != 3:
            self.pos = (self.pos[0]+1, self.pos[1])

    def move_left(self):
        if self.pos[1] != 0 and board[self.pos[0]][self.pos[1]-1] != 3:
            self.pos = (self.pos[0], self.pos[1] - 1)

    def move_right(self):
        if self.pos[1] != grid_size - 1 and board[self.pos[0]][self.pos[1]+1] != 3:
            self.pos = (self.pos[0], self.pos[1] + 1)

    def calculate_distance(self):
        return abs(self.c_pos[self.collected_coins][0] - self.pos[0]) + abs(self.c_pos[self.collected_coins][1] - self.pos[1]) + 1
    
    def check_for_end(self):
        if self.calculate_distance() == 1 and self.collected_coins == len(self.c_pos) - 1:
            self.finished_fitness = 5
            return True
        
        elif self.calculate_distance() == 1:
            self.fitnes_sum += 1 / ((0.7 + self.moves / coins_distance[self.collected_coins] * 0.3) ** 2)
            self.collected_coins += 1




def create_population(size):
    for i in range(0, size):
        p = Player([random.choice(list_instructions) for _ in range(number_of_moves)], coins_possitions)
        players.append(p)



def calculate_fitness(players):
    distance_list = {}
    running_fitness = 0

    for player in players:
        curr_fitness = 1 / ((player.calculate_distance() * 0.7 + player.moves / coins_distance[player.collected_coins] * 0.3) ** 2) + player.fitnes_sum + player.finished_fitness

        distance_list[curr_fitness + running_fitness] = player
        running_fitness += curr_fitness

    keys = list(distance_list.keys())
    best_parent_key = [keys[0], distance_list[keys[0]]]

    for i in range(1, len(keys)):
        curr_diff = keys[i] - keys[i-1]

        if curr_diff > best_parent_key[0]:
            best_parent_key = [curr_diff, distance_list[keys[i]]]

    return distance_list, best_parent_key[1].instructions[:] 



def mutate(parents, best_parent):
    mutate_chance = 0.02
    new_players = []

    for parent in parents:
        new_instructions = parent.instructions[:]

        for i in range(0, len(new_instructions)):
            if random.random() < mutate_chance:
                new_instructions[i] = random.choice(list_instructions)

        new_players.append(Player(new_instructions, coins_possitions))

    new_players.append(best_parent)
    return new_players



def get_parent(distance_list):
    nums = list(distance_list.keys())
    parents = []

    for _ in range(0, population-1):
        target = random.uniform(0, nums[-1] + nums[-1] - nums[-2])	

        s = 0
        e = len(distance_list)
        
        while s < e:
            mid = (s+e) // 2

            if nums[mid] > target:
                e = mid -1
            elif nums[mid] < target:
                s = mid + 1
            else:
                break
        
        parents.append(distance_list[nums[mid]])

    return parents


def create_new_gen(players):
    fittnes_list, best_parent = calculate_fitness(players)
    best_p = Player(best_parent, coins_possitions)
    best_p.is_best = True

    parents = get_parent(fittnes_list)
    players = mutate(parents, best_p)

    return players


def calculate_coins_distance():
    for i, vals in enumerate(coins_possitions):
        y, x = vals

        if i == 0:
            curr_distance = y + x
        else:
            curr_distance = abs(coins_possitions[i-1][1] - x) + abs(coins_possitions[i-1][0] - y)
        
        coins_distance.append(curr_distance)




create_population(population)
player_positions = draw_players_to_board(players, player_positions)

draw_screen(board)
pygame.display.update()

# main loop
while run:

    for event in pygame.event.get():

        if start == True:
            if event.type == auto_move:
                curr_moves += 1 

                if curr_moves > number_of_moves:
                    print("generation: ", generation, " | least moves = ", min_moves)

                    if min_moves != None:
                        number_of_moves = min(min_moves, number_of_moves)
                    
                    min_moves = None

                    players = create_new_gen(players)
                    players_in_finish = []

                    curr_moves = 1
                    generation += 1
                    continue
                
                for i, player in enumerate(players):
                    if i in players_in_finish:
                        continue

                    player.move()

                    if player.check_for_end() == True:
                        players_in_finish.append(i)

                        if min_moves == None:
                            min_moves = player.moves + 1

                player_positions = draw_players_to_board(players, player_positions)
                draw_screen(board)
                pygame.display.update()    


        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                run = False

            elif event.key == pygame.K_1:
                mode = "wall"

            elif event.key == pygame.K_2:
                mode = "coin"

            elif event.key == pygame.K_3:
                mode = "finish"

            elif event.key == pygame.K_s:
                coins_possitions.append(finish_possition)
                calculate_coins_distance()
                start = True
        
        if pygame.mouse.get_pressed()[0]:
            try:
                x, y = pygame.mouse.get_pos()
                y //= block_size
                x //= block_size

                if x >= grid_size or y >= grid_size or x < 0 or y < 0:
                    continue
                
                if mode == "wall":
                    if (y, x) not in walls_possitions:
                        board[y][x] = 3
                        walls_possitions.append((y, x))

                elif mode == "coin":
                    if (y, x) not in coins_possitions:
                        board[y][x] = 5
                        coins_possitions.append((y, x))
                
                elif mode == "finish":
                    if finish_possition == None:
                        board[y][x] = 2
                        finish_possition = (y, x)


                draw_screen(board)
                pygame.display.update() 

            except AttributeError:
                pass

        

pygame.quit()


# to do
# pick only the top 10% / 25% of players to make children

# multiprocesing maybe ?? hmmm


# note to myself
# I accualy have a terminal brain cancer and dementia go kys
# new enemy fittnes function pls man i have a familys