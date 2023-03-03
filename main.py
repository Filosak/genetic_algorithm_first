import pygame
import time
import random
pygame.init()


#variables
width = 700
height = 700
grid_size = 50
number_of_moves = 300
population = 2000
curr_moves = 1
generation = 1
block_size = width // grid_size
players = []
player_positions = []
players_in_finish = []
number_of_moves_list = [number_of_moves]
list_instructions = ["move_up", "move_down", "move_left", "move_right"]
walls_possitions = []
run = True
start = False

auto_move = pygame.USEREVENT + 1
pygame.time.set_timer(auto_move, 10)


# 0 = nothing
# 1 = player
# 2 = end point
# 3 - wall
board = [[0 for _ in range(grid_size)] for _ in range(grid_size)]

point_pos = (49, 49)
board[point_pos[0]][point_pos[1]] = 2 

for y, x in walls_possitions:
    board[y][x] = 3

# screen
screen = pygame.display.set_mode((width, height))
screen.fill((255,255,255))

# functions
def draw_players_to_board(players, player_positions):
    for y, x in player_positions:
        board[y][x] = 0
    
    for y, x in walls_possitions:
        board[y][x] = 3

    board[point_pos[0]][point_pos[1]] = 2

    player_positions = []

    for player in players:
        y, x = player.pos

        if player.is_best == True:
            board[y][x] = 2
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


class Player:
    def __init__(self, inctructions):
        self.pos = (0, 0)
        self.moves = 0
        self.instructions = inctructions
        self.is_best = False

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

    def calculate_distance(self, point_pos):
        return point_pos[0] - self.pos[0] + point_pos[1] - self.pos[1] + 1
    
    def check_for_end(self, point_pos):
        if self.calculate_distance(point_pos) == 1:
            return True




def create_population(size):
    for i in range(0, size):
        p = Player([random.choice(list_instructions) for _ in range(number_of_moves)])
        players.append(p)



def calculate_fitness(players):
    distance_list = {}
    running_fitness = 0

    for player in players:
        curr_fitness = 1 / ((player.calculate_distance(point_pos) + (player.moves * 0.2)) **2)
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

        new_players.append(Player(new_instructions))

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
    best_p = Player(best_parent)
    best_p.is_best = True

    parents = get_parent(fittnes_list)
    players = mutate(parents, best_p)

    return players


def get_best(fittnes_list):
    return max(fittnes_list)






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
                    print("generation: ", generation, " | least moves = ", min(number_of_moves_list))
                    number_of_moves = min(number_of_moves_list)

                    players = create_new_gen(players)
                    players_in_finish = []
                    number_of_moves_list = [number_of_moves]

                    curr_moves = 1
                    generation += 1
                    continue
                
                for i, player in enumerate(players):
                    if i in players_in_finish:
                        continue

                    player.move()

                    if player.check_for_end(point_pos) == True:
                        players_in_finish.append(i)
                        number_of_moves_list.append(player.moves)

                player_positions = draw_players_to_board(players, player_positions)
                draw_screen(board)
                pygame.display.update()    


        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_s:
                start = True
        
        if pygame.mouse.get_pressed()[0]:
            try:
                x, y = pygame.mouse.get_pos()
                y //= block_size
                x //= block_size

                if x >= grid_size or y >= grid_size or x < 0 or y < 0:
                    continue
                
                board[y][x] = 3
                walls_possitions.append((y, x))

                draw_screen(board)
                pygame.display.update() 

            except AttributeError:
                pass

        



pygame.quit()



# if event.type == pygame.MOUSEBUTTONDOWN:
#             if button.check():
                # x, y = pygame.mouse.get_pos()
                # y //= block_size
                # x //= block_size
                
                # board[y][x] = 3
                # walls_possitions.append((y, x))

                # draw_screen(board)
                # pygame.display.update()  