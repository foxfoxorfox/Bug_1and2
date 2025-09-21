import pygame
import math

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bug1")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
GREEN = (0, 200, 0)

# def ====================================================================================
bug_pos = [100, 100]
goal_point = [700, 500]

bug_size = 4
speed = 1
moving = False

contact = False
# direction = [(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]

drawing = False
obj = []
edgpos = None
enlep = [-2, -2]
# funtion =====================================================================================
#거리측정
def distance(p1, p2):
    return math.hypot(p2[0]-p1[0], p2[1]-p1[1])

#일반이동
def normal_move(bug_pos, goal_point):
    dx = goal_point[0]-bug_pos[0]
    dy = goal_point[1]-bug_pos[1]
    dist = math.hypot(dx, dy)
    if dist < 1:
        bug_pos[0], bug_pos[1] = goal_point
    else:
        bug_pos[0] += round(dx / dist)
        bug_pos[1] += round(dy / dist)

def is_contact(bug_pos, obj, threshold=1.0):
    for p in obj:
        if math.hypot(bug_pos[0]-p[0], bug_pos[1]-p[1]) < threshold:
            bug_pos[0], bug_pos[1] = p
            return obj.index(p)
    return None

# def search_np(prev, curr, obj):
#     dx, dy = curr[0] - prev[0], curr[1] - prev[1]
#     dirs = [(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]
#     dir_idx = dirs.index((dx, dy))
#     for i in range(8):
#         ndx, ndy = dirs[(dir_idx + i) % 8]
#         nx, ny = curr[0] + ndx, curr[1] + ndy
#         if (nx, ny) in obj:
#             return (nx, ny)

def bug1alg_move(bug_pos, edgpos, obj, enlep):
    to = None
    if enlep[0] == -2:
        if edgpos == enlep[1]:
            to = None
        else:
            if edgpos - 1 < 0:
                to = len(obj) - 1
            else:
                to = edgpos - 1
            bug_pos[0] = obj[to][0]
            bug_pos[1] = obj[to][1]
    else:
        if edgpos + 1 < len(obj):
            to = edgpos + 1
        else:
            to = 0
        bug_pos[0] = obj[to][0]
        bug_pos[1] = obj[to][1]
        if distance(obj[to], goal_point) <= distance(obj[enlep[1]], goal_point):
            enlep[1] = to
        if to == enlep[0]:
            enlep[0] = -2
    return to

def connect(obj):
    if len(obj) < 2:
        return
    start = obj[0]
    end = obj[-1]
    if start != end:
        dx = start[0] - end[0]
        dy = start[1] - end[1]
        dist = math.hypot(dx, dy)
        steps = int(dist)
        if steps == 0:
            return
        for i in range(1, steps + 1):
            t = i / steps
            x = round(end[0] + dx * t)
            y = round(end[1] + dy * t)
            obj.append([x, y])

def smooth(obj):
    if len(obj) < 2:
        return
    new_obj = []
    for i in range(len(obj)-1):
        start = obj[i]
        end = obj[i+1]
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dist = math.hypot(dx, dy)
        steps = int(dist)
        for j in range(steps):
            t = j / dist
            x = round(start[0] + dx * t)
            y = round(start[1] + dy * t)
            new_obj.append([x, y])
    new_obj.append(obj[-1])
    return new_obj
# =====================================================================================
running = True
while running:
    screen.fill(WHITE)

    if len(obj) > 1:
        pygame.draw.lines(screen, BLACK, False, obj, 2)

    pygame.draw.circle(screen, RED, (int(bug_pos[0]), int(bug_pos[1])), bug_size)
    pygame.draw.circle(screen, BLUE, goal_point, 4)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                drawing = True
                obj = []
                obj.append(list(event.pos))
            elif event.button == 3:
                bug_pos = [100, 100]
                moving = True
        elif event.type == pygame.MOUSEMOTION:
            if drawing:
                obj.append(list(event.pos))
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                connect(obj)
                obj = smooth(obj)
                drawing = False

    if moving:
        if contact:
            edgpos = bug1alg_move(bug_pos, edgpos, obj, enlep)
            if edgpos == None:
                contact = False
                enlep = [-2, -2]
                ## fix needed
        else:
            normal_move(bug_pos, goal_point)
            edgpos = is_contact(bug_pos, obj)
            if edgpos != None:
                enlep[0] = edgpos
                enlep[1] = edgpos
                contact = True
        # 도착
        if distance(bug_pos, goal_point) == 0:
            moving = False
    pygame.display.flip()
    clock.tick(60)

pygame.quit()