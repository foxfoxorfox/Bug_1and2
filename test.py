import pygame
import math

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bug1 + Mask")
clock = pygame.time.Clock()

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
LIGHTG = (200, 200, 200)

# 버그 기본값
bug_pos = [100, 100]
goal_point = [700, 500]
bug_size = 5
speed = 1
moving = False
contact = False

# 도형 관련
drawing = False
obj = []
obj_mask = None
outline = []
outline_index = 0

# 거리 계산 함수
def distance(p1, p2):
    return math.hypot(p2[0]-p1[0], p2[1]-p1[1])

# 목표점으로 직선 이동
def normal_move(bug_pos, goal_point):
    dx = goal_point[0] - bug_pos[0]
    dy = goal_point[1] - bug_pos[1]
    dist = math.hypot(dx, dy)
    if dist < 1:
        bug_pos[0], bug_pos[1] = goal_point
    else:
        bug_pos[0] += dx / dist
        bug_pos[1] += dy / dist

# 외곽선을 따라 이동
def follow_outline(bug_pos, outline, idx):
    if not outline:
        return idx
    idx = (idx + 1) % len(outline)
    bug_pos[0], bug_pos[1] = outline[idx]
    return idx

# =====================================================================
running = True
while running:
    screen.fill(WHITE)

    # 도형 그리기 & mask 갱신
    if len(obj) > 2:
        obj_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        obj_surf.fill((0, 0, 0, 0))
        pygame.draw.polygon(obj_surf, LIGHTG, obj)          # 도형 내부
        pygame.draw.polygon(obj_surf, BLACK, obj, width=2)  # 외곽선
        obj_mask = pygame.mask.from_surface(obj_surf)
        screen.blit(obj_surf, (0, 0))

    # 버그 그리기
    bug_surf = pygame.Surface((bug_size*2, bug_size*2), pygame.SRCALPHA)
    bug_surf.fill((0,0,0,0))
    pygame.draw.circle(bug_surf, RED, (bug_size, bug_size), bug_size)
    bug_mask = pygame.mask.from_surface(bug_surf)
    screen.blit(bug_surf, (int(bug_pos[0]-bug_size), int(bug_pos[1]-bug_size)))

    # 목표점
    pygame.draw.circle(screen, BLUE, goal_point, 4)

    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 왼쪽 버튼 → 도형 그리기 시작
                drawing = True
                obj = [list(event.pos)]
            elif event.button == 3:  # 오른쪽 버튼 → bug 이동 시작
                bug_pos = [100, 100]
                moving = True
                contact = False
                outline = []
                outline_index = 0
        elif event.type == pygame.MOUSEMOTION:
            if drawing:
                obj.append(list(event.pos))
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                drawing = False
                if len(obj) > 2:
                    # outline 저장
                    temp_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    pygame.draw.polygon(temp_surf, (255,255,255), obj)
                    temp_mask = pygame.mask.from_surface(temp_surf)
                    outline = temp_mask.outline()
                    outline_index = 0

    # 버그 이동 처리
    if moving:
        if contact and outline:
            outline_index = follow_outline(bug_pos, outline, outline_index)
        else:
            normal_move(bug_pos, goal_point)
            # 충돌 판정
            if obj_mask:
                offset = (int(bug_pos[0]-bug_size), int(bug_pos[1]-bug_size))
                if bug_mask.overlap(obj_mask, (-offset[0], -offset[1])):
                    contact = True


        # 목표 도달
        if distance(bug_pos, goal_point) < 2:
            moving = False
            print("도착!")

    pygame.display.flip()
    clock.tick(120)

pygame.quit()
