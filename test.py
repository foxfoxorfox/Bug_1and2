import pygame
import math

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bug1 Algorithm Demo")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
GREEN = (0, 200, 0)

# bug와 goal
bug_pos = [100, 100]
goal_pos = [700, 500]
bug_speed = 2

# 상태
drawing = False
obstacles = []   # 완성된 다각형들
current_poly = []  # 현재 그리고 있는 다각형
moving = False

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def line_intersects(p1, p2, q1, q2):
    """두 선분이 교차하는지 검사"""
    def ccw(a, b, c):
        return (c[1]-a[1])*(b[0]-a[0]) > (b[1]-a[1])*(c[0]-a[0])
    return ccw(p1,q1,q2) != ccw(p2,q1,q2) and ccw(p1,p2,q1) != ccw(p1,p2,q2)

def point_in_polygon(point, poly):
    """점이 다각형 내부에 있는지 (Ray casting)"""
    x, y = point
    inside = False
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and \
           (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi):
            inside = not inside
    return inside

def collides(p1, p2, polygons):
    """p1→p2 선분이 어떤 다각형과 충돌하는지 검사"""
    for poly in polygons:
        n = len(poly)
        for i in range(n):
            j = (i + 1) % n
            if line_intersects(p1, p2, poly[i], poly[j]):
                return True
    return False

def move_bug(bug_pos, goal_pos, obstacles):
    """Bug1 이동 step"""
    dx, dy = goal_pos[0]-bug_pos[0], goal_pos[1]-bug_pos[1]
    dist = math.hypot(dx, dy)
    if dist == 0:
        return bug_pos
    step = (dx/dist*bug_speed, dy/dist*bug_speed)
    new_pos = [bug_pos[0]+step[0], bug_pos[1]+step[1]]

    if collides(bug_pos, new_pos, obstacles) or point_in_polygon(new_pos, sum(obstacles, [])):
        # 충돌 시: 간단히 bug를 시계방향으로 회전 (벽 따라가기)
        angle = math.atan2(dy, dx) - math.pi/2  # 시계방향
        new_pos = [bug_pos[0] + math.cos(angle)*bug_speed,
                   bug_pos[1] + math.sin(angle)*bug_speed]
    return new_pos

# 메인 루프
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 좌클릭: 장애물 시작
                drawing = True
                current_poly = [event.pos]

            elif event.button == 3:  # 우클릭: bug 이동 시작
                moving = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:  # 좌클릭 끝 → 다각형 닫기
                drawing = False
                if len(current_poly) > 2:
                    if current_poly[0] != current_poly[-1]:
                        current_poly.append(current_poly[0])  # 자동으로 닫기
                    obstacles.append(current_poly)
                current_poly = []

        elif event.type == pygame.MOUSEMOTION and drawing:
            current_poly.append(event.pos)

    # bug 이동
    if moving and distance(bug_pos, goal_pos) > 5:
        bug_pos = move_bug(bug_pos, goal_pos, obstacles)

    # 장애물 그리기
    for poly in obstacles:
        if len(poly) > 1:
            pygame.draw.polygon(screen, GREEN, poly, 2)

    if len(current_poly) > 1:
        pygame.draw.lines(screen, GREEN, False, current_poly, 2)

    # bug, goal 그리기
    pygame.draw.circle(screen, RED, (int(bug_pos[0]), int(bug_pos[1])), 5)
    pygame.draw.circle(screen, BLUE, goal_pos, 7)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
