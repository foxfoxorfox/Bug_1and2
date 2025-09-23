import pygame
import math

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bug1")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
LIGHTG = (200, 200, 200)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)

# def =====================================================
bug_pos = [100, 100]
goal_point = [700, 500]
bug_size = 4
speed = 1
moving = False
contact = False

drawing = False
obj = []
past = []
edgpos = None
enlep = [-2, -2]
# func =====================================================
def distance(p1, p2):
    return math.hypot(p2[0]-p1[0], p2[1]-p1[1])

def normal_move(bug_pos, goal_point):
    dx = goal_point[0]-bug_pos[0]
    dy = goal_point[1]-bug_pos[1]
    dist = math.hypot(dx, dy)
    if dist < 1:
        bug_pos[0], bug_pos[1] = goal_point
    else:
        bug_pos[0] += dx / dist
        bug_pos[1] += dy / dist

def bug1alg_move(bug_pos, edgpos, obj_exp, past, enlep):
    if enlep[0] == -2:
        to = (edgpos - 1) % len(obj_exp)
        bug_pos[0], bug_pos[1] = obj_exp[to]
        if to == enlep[1]:
            enlep[1] = -2
            return None
        else:
            return to
    else:
        to = (edgpos + 1) % len(obj_exp)
        bug_pos[0], bug_pos[1] = obj_exp[to]
        past.append(obj_exp[to])
        if distance(obj_exp[to], goal_point) <= distance(obj_exp[enlep[1]], goal_point):
            enlep[1] = to
        if to == enlep[0]:
            enlep[0] = -2
        return to

def connect(obj):
    if len(obj) < 2:
        return []
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
        return []
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

# main =====================================================
running = True
while running:
    screen.fill(WHITE)

    obj_exp = []
    if drawing:
        if len(obj) > 2:
            pygame.draw.lines(screen, BLACK, False, obj, 2)
    else:
        if len(obj) > 2:
            obj_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            obj_surf.fill((0,0,0,0))
            pygame.draw.polygon(obj_surf, LIGHTG, obj)
            obj_mask = pygame.mask.from_surface(obj_surf)
            expan = obj_mask.copy()
            for dx in range(-bug_size, bug_size+1):
                for dy in range(-bug_size, bug_size+1):
                    if dx*dx + dy*dy <= bug_size*bug_size:
                        expan.draw(obj_mask, (dx, dy))
            obj_exp = expan.outline()
            pygame.draw.polygon(obj_surf, BLACK, obj, width=1)
            screen.blit(obj_surf, (0,0))

    bug_surf = pygame.Surface((bug_size*2, bug_size*2), pygame.SRCALPHA)
    bug_surf.fill((0,0,0,0))
    pygame.draw.circle(bug_surf, RED, (bug_size, bug_size), bug_size)
    bug_mask = pygame.mask.from_surface(bug_surf)
    screen.blit(bug_surf, (bug_pos[0]-bug_size, bug_pos[1]-bug_size))

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

    if moving and obj_exp:
        if contact:
            if edgpos == None:
                prev_pos = bug_pos.copy()
                normal_move(bug_pos, goal_point)
                contact = False
            else:
                edgpos = bug1alg_move(bug_pos, edgpos, obj_exp, past, enlep)
        else:
            prev_pos = bug_pos.copy()
            normal_move(bug_pos, goal_point)
            offset_x = bug_pos[0]-bug_size
            offset_y = bug_pos[1]-bug_size
            
            if obj_mask.overlap(bug_mask, (int(offset_x), int(offset_y))):
                bug_pos = prev_pos
                min_dist = float('inf')
                for i, pt in enumerate(obj_exp):
                    d = distance(pt, bug_pos)
                    if d < min_dist:
                        min_dist = d
                        edgpos = i
                enlep[0] = edgpos
                enlep[1] = edgpos
                contact = True
        if distance(bug_pos, goal_point) == 0:
            moving = False

    pygame.display.flip()
    clock.tick(180)

pygame.quit()
