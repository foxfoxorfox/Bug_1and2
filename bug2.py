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
found = []
edgpos = None
lep = []
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
        bug_pos[0] += dx / dist
        bug_pos[1] += dy / dist

def is_contact(bug_pos, obj, past, threshold=2.0):
    for p in obj:
        if math.hypot(bug_pos[0]-p[0], bug_pos[1]-p[1]) < threshold:
            if p in past:
                return None
            else:
                bug_pos[0], bug_pos[1] = p
                past.append(p)
                return obj.index(p)
    return None

def bug2alg_move(bug_pos, edgpos, obj, past, lep):
    to = None
    if edgpos + 1 < len(obj):
        to = edgpos + 1
    else:
        to = 0
    bug_pos[0] = obj[to][0]
    bug_pos[1] = obj[to][1]
    past.append(obj[to])
    if distance(obj[to], goal_point) <= distance(obj[enlep[1]], goal_point):
        lep[1] = to
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
                past = []
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
            edgpos = bug2alg_move(bug_pos, edgpos, obj, past, enlep)
            if edgpos == None:
                contact = False
                enlep = [-2, -2]
                
        else:
            normal_move(bug_pos, goal_point)
            edgpos = is_contact(bug_pos, obj, past)
            if edgpos != None:
                enlep[0] = edgpos
                enlep[1] = edgpos
                contact = True
        # 도착
        if distance(bug_pos, goal_point) == 0:
            print(len(obj))
            moving = False
    pygame.display.flip()
    clock.tick(150)

pygame.quit()