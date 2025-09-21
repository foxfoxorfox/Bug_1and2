import pygame
import math

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bug1 with Perimeter Check")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)

bug_pos = [100, 100]
goal_point = [700, 500]
bug_size = 4
speed = 1
moving = False
contact = False

drawing = False
polygon = []   # 다각형 꼭짓점 리스트
edges = []     # 선분 리스트

# Bug1 상태 변수
hit_point = None
best_point = None
best_dist = float("inf")
wall_follow_distance = 0
total_perimeter = 0


# =================================================================
def distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def perimeter(edges):
    return sum(distance(e1, e2) for e1, e2 in edges)

def line_intersects(p1, p2, q1, q2):
    """두 선분이 교차하는지 확인"""
    def ccw(a, b, c):
        return (c[1] - a[1])*(b[0] - a[0]) > (b[1] - a[1])*(c[0] - a[0])
    return (ccw(p1, q1, q2) != ccw(p2, q1, q2)) and (ccw(p1, p2, q1) != ccw(p1, p2, q2))

def line_of_sight_clear(p1, p2, edges):
    """p1~p2 직선이 장애물과 교차하지 않는지 검사"""
    for e1, e2 in edges:
        if line_intersects(p1, p2, e1, e2):
            return False
    return True

def normal_move(bug_pos, goal_point, step=speed):
    dx = goal_point[0] - bug_pos[0]
    dy = goal_point[1] - bug_pos[1]
    dist = math.hypot(dx, dy)
    if dist < step:
        bug_pos[0], bug_pos[1] = goal_point
    else:
        bug_pos[0] += step * dx / dist
        bug_pos[1] += step * dy / dist

def nearest_edge_point(p, edges):
    """점 p에서 가장 가까운 선분 위 점 찾기"""
    best = None
    best_d = float("inf")
    for e1, e2 in edges:
        x1, y1 = e1
        x2, y2 = e2
        if (x1, y1) == (x2, y2):
            continue
        t = max(0, min(1, ((p[0]-x1)*(x2-x1)+(p[1]-y1)*(y2-y1)) / ((x2-x1)**2+(y2-y1)**2)))
        proj = (x1 + t*(x2-x1), y1 + t*(y2-y1))
        d = distance(p, proj)
        if d < best_d:
            best_d = d
            best = proj
    return best

def follow_wall(bug_pos, edges, step=speed):
    """벽을 따라 시계 방향으로 이동"""
    global wall_follow_distance
    # 단순하게: goal 방향과 수직인 방향을 따라 이동
    nearest = nearest_edge_point(bug_pos, edges)
    if not nearest:
        return
    dx = bug_pos[0] - nearest[0]
    dy = bug_pos[1] - nearest[1]
    norm = math.hypot(dx, dy)
    if norm == 0:
        dx, dy = 1, 0
        norm = 1
    dx /= norm; dy /= norm
    # 벽과 평행 방향 (시계 방향 회전)
    tx, ty = dy, -dx
    bug_pos[0] += step * tx
    bug_pos[1] += step * ty
    wall_follow_distance += step


# =================================================================
running = True
while running:
    screen.fill(WHITE)

    # 장애물 그리기
    if len(polygon) > 1:
        pygame.draw.lines(screen, BLACK, True, polygon, 2)

    pygame.draw.circle(screen, RED, (int(bug_pos[0]), int(bug_pos[1])), bug_size)
    pygame.draw.circle(screen, BLUE, goal_point, 5)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 좌클릭: 다각형 시작
                drawing = True
                polygon = [event.pos]
            elif event.button == 3:  # 우클릭: bug 이동 시작
                bug_pos = [100, 100]
                moving = True
                contact = False
                hit_point = None
                best_point = None
                best_dist = float("inf")
                wall_follow_distance = 0
                if len(polygon) > 2:
                    edges = [(polygon[i], polygon[(i+1) % len(polygon)]) for i in range(len(polygon))]
                    total_perimeter = perimeter(edges)
        elif event.type == pygame.MOUSEMOTION:
            if drawing:
                polygon.append(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                drawing = False

    # 이동 로직
    if moving and edges:
        if contact:  # 벽 따라가기
            follow_wall(bug_pos, edges)
            if line_of_sight_clear(bug_pos, goal_point, edges):
                d = distance(bug_pos, goal_point)
                if d < best_dist:
                    best_dist = d
                    best_point = bug_pos[:]
            # 경계 전체를 한 바퀴 돌았는지 확인
            if wall_follow_distance >= total_perimeter - 2:
                contact = False
                wall_follow_distance = 0
                if best_point:
                    bug_pos[:] = best_point[:]
                    best_point = None
                    best_dist = float("inf")
        else:  # 직진
            old_pos = bug_pos[:]
            normal_move(bug_pos, goal_point)
            # 장애물 충돌 검사
            if not line_of_sight_clear(old_pos, bug_pos, edges):
                contact = True
                hit_point = bug_pos[:]
                wall_follow_distance = 0

        # goal 도착
        if distance(bug_pos, goal_point) < 5:
            moving = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
