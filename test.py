import pygame

pygame.init()

# 창 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("마우스로 그린 경로 따라 이동")

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)

clock = pygame.time.Clock()
running = True

drawing = False      # 마우스로 그리고 있는 중인지
path = []            # 사용자가 그린 경로 저장 (좌표 리스트)
pos_index = 0        # 점이 이동할 경로의 인덱스

mode = "draw"        # "draw" 상태에서 그림, "move" 상태에서 점 이동

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 마우스 버튼 눌렀을 때 → 그리기 시작
        if event.type == pygame.MOUSEBUTTONDOWN and mode == "draw":
            drawing = True
            path = []  # 새 경로
            pos_index = 0

        # 마우스 버튼 뗐을 때 → 그리기 종료 후 이동 모드로 전환
        if event.type == pygame.MOUSEBUTTONUP and mode == "draw":
            drawing = False
            if path:   # 경로가 있으면 이동 모드로
                mode = "move"

    # 마우스로 경로 그리기
    if drawing:
        pos = pygame.mouse.get_pos()
        path.append(pos)

    # 경로 그리기
    if len(path) > 1:
        pygame.draw.lines(screen, BLACK, False, path, 2)

    # 이동 모드일 때 점 이동
    if mode == "move" and path:
        if pos_index < len(path):
            x, y = path[pos_index]
            pygame.draw.circle(screen, RED, (x, y), 6)
            pos_index += 1  # 다음 점으로 이동
        else:
            # 이동이 끝나면 다시 그릴 수 있게 모드 초기화
            mode = "draw"

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
