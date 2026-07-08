import pygame
try:
    pygame.init()
    print("Pygame đã cài thành công!")
    pygame.quit()
except Exception as e:
    print(f"Lỗi: {e}")