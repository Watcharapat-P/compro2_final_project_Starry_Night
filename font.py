import pygame
def waitenter():
    print('Waiting for ENTER...')
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                if event.key == 13:
                    return

pygame.init()
sf = pygame.display.set_mode((1400, 600))
sf.fill((255, 255, 255, 0))
fonts = pygame.font.get_fonts()
fonts.sort()
for idx, font in enumerate(fonts):
    if idx and idx % 20 == 0:
        pygame.display.update()
        waitenter()
        sf.fill((255, 255, 255, 0))

    try:
        py_font = pygame.font.SysFont(font, 16)
    except Exception as e:
        continue
    text_sf = py_font.render(f'{font}: Ông Medvedev: Thế chiến sẽ nổ nếu Mỹ tấn công mục tiêu ở', False, pygame.Color('black'))
    sf.blit(text_sf, (0, (idx % 20) * 24))