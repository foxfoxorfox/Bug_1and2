import pygame
import math

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bug1 Multiple Obstacles")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
LIGHTG = (200, 200, 200)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)

# =====================================================
bug_pos = [100, 100]
goal_point = [700, 500]
bug_size = 4
speed = 1
moving = False

drawing = False
current_obj = []        # 마우스로 그리는 도형 임시 저장
objs = []               # 모든 도형 좌표 리스트
obj_masks = []          # 각 도형 마스크
obj_exps = []           # 각 도형 외곽점

contact = False
contact_obj_index = None
edgpos_list = []        # 각 도형 별 Bug1 위치
enlep_list = []         # 각 도형 별 최소 거리 추적

# =====================================================
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

def bug1alg_move(bug_pos, edgpos, obj_exp, enlep):
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

# =====================================================
running = True
while running:
    screen.fill(WHITE)

    # --------------------- 도형 그리기 ---------------------
    for i, obj in enumerate(objs):
        obj_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        obj_surf.fill((0,0,0,0))
        pygame.draw.polygon(obj_surf, LIGHTG, obj)
        pygame.draw.polygon(obj_surf, BLACK, obj, width=1)
        screen.blit(obj_surf, (0,0))

    if drawing and len(current_obj) > 1:
        pygame.draw.lines(screen, BLACK, False, current_obj, 2)

    # --------------------- 버그 그리기 ---------------------
    bug_surf = pygame.Surface((bug_size*2, bug_size*2), pygame.SRCALPHA)
    bug_surf.fill((0,0,0,0))
    pygame.draw.circle(bug_surf, RED, (bug_size, bug_size), bug_size)
    bug_mask = pygame.mask.from_surface(bug_surf)
    screen.blit(bug_surf, (bug_pos[0]-bug_size, bug_pos[1]-bug_size))

    pygame.draw.circle(screen, BLUE, goal_point, 4)

    # --------------------- 이벤트 처리 ---------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                drawing = True
                current_obj = [list(event.pos)]
            elif event.button == 3:
                bug_pos = [100, 100]
                moving = True
        elif event.type == pygame.MOUSEMOTION and drawing:
            current_obj.append(list(event.pos))
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drawing:
            connect(current_obj)
            current_obj = smooth(current_obj)
            # 도형 저장
            objs.append(current_obj)
            # 마스크 및 외곽 계산
            obj_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            obj_surf.fill((0,0,0,0))
            pygame.draw.polygon(obj_surf, LIGHTG, current_obj)
            mask = pygame.mask.from_surface(obj_surf)
            expan = mask.copy()
            for dx in range(-bug_size, bug_size+1):
                for dy in range(-bug_size, bug_size+1):
                    if dx*dx + dy*dy <= bug_size*bug_size:
                        expan.draw(mask, (dx, dy))
            obj_masks.append(mask)
            obj_exps.append(expan.outline())
            # Bug1 관련 초기화
            edgpos_list.append(None)
            enlep_list.append([-2,-2])
            drawing = False

    # --------------------- 이동 처리 ---------------------
    if moving:
        prev_pos = bug_pos.copy()
        normal_move(bug_pos, goal_point)
        contact = False
        contact_obj_index = None

        # 모든 도형과 충돌 체크
        for i, (mask, exp) in enumerate(zip(obj_masks, obj_exps)):
            offset_x = int(bug_pos[0]-bug_size)
            offset_y = int(bug_pos[1]-bug_size)
            if mask.overlap(bug_mask, (offset_x, offset_y)):
                bug_pos = prev_pos
                min_dist = float('inf')
                for j, pt in enumerate(exp):
                    d = distance(pt, bug_pos)
                    if d < min_dist:
                        min_dist = d
                        edgpos_list[i] = j
                        enlep_list[i] = [j,j]
                contact = True
                contact_obj_index = i
                break  # 한 도형만 접촉 처리

        # Bug1 알고리즘 적용
        if contact and contact_obj_index is not None:
            edgpos_list[contact_obj_index] = bug1alg_move(
                bug_pos,
                edgpos_list[contact_obj_index],
                obj_exps[contact_obj_index],
                enlep_list[contact_obj_index]
            )

        if distance(bug_pos, goal_point) < 1:
            moving = False

    pygame.display.flip()
    clock.tick(180)

pygame.quit()
