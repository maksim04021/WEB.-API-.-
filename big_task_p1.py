import pygame
import sys
import requests
from io import BytesIO

W, H = 600, 600
BACKGROUND_COLOR = (200, 200, 200)
TEXT_COLOR = (0, 0, 0)
INPUT_BOX_COLOR = (255, 255, 255)
BUTTON_COLOR = (0, 128, 255)
BUTTON_TEXT_COLOR = (255, 255, 255)
FONT_SIZE = 24
SMALL_FONT_SIZE = 18
MAP_W, MAP_H = 600, 400

LATITUDE = 55.75
LONGITUDE = 37.62
ZOOM = 12
API_KEY = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
MAP_X = (W - MAP_W) // 2
MAP_Y = 200

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption('Миникарта (большая задача)')
font = pygame.font.Font(None, FONT_SIZE)
small_font = pygame.font.Font(None, SMALL_FONT_SIZE)


class InputBox:
    def __init__(self, x, y, width, height, text='', label=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = INPUT_BOX_COLOR
        self.text = text
        self.label = label
        self.txt_surface = font.render(text, True, TEXT_COLOR)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = INPUT_BOX_COLOR if not self.active else (200, 200, 255)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = font.render(self.text, True, TEXT_COLOR)
        return False

    def update(self):
        self.rect.w = max(200, self.txt_surface.get_width() + 10)

    def draw(self, screen):
        label_surface = small_font.render(self.label, True, TEXT_COLOR)
        screen.blit(label_surface, (self.rect.x, self.rect.y - small_font.get_height()))
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


class Button:
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = BUTTON_COLOR
        self.text = text
        self.callback = callback
        self.text_surface = font.render(text, True, BUTTON_TEXT_COLOR)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surface, self.text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()


def load_map(latitude, longitude, zoom):
    ll = f"{longitude},{latitude}"
    url = f"https://static-maps.yandex.ru/1.x/?ll={ll}&z={zoom}&l=map&size={MAP_W},{MAP_H}&apikey={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        image_data = BytesIO(response.content)
        return pygame.image.load(image_data, 'map.png')
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return None
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None


def update_map():
    global LATITUDE, LONGITUDE, ZOOM, map_image

    try:
        LATITUDE = float(lat_input.text)
        LONGITUDE = float(lon_input.text)
        ZOOM = int(zoom_input.text)
    except ValueError:
        print("Некорректный ввод координат или масштаба.")
        return

    map_image = load_map(LATITUDE, LONGITUDE, ZOOM)


lat_input = InputBox(100, 50, 200, 30, str(LATITUDE), 'Широта')
lon_input = InputBox(100, 100, 200, 30, str(LONGITUDE), 'Долгота')
zoom_input = InputBox(100, 150, 200, 30, str(ZOOM), 'Масштаб')
update_button = Button(350, 100, 150, 40, "Обновить карту", update_map)

map_image = load_map(LATITUDE, LONGITUDE, ZOOM)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        lat_input.handle_event(event)
        lon_input.handle_event(event)
        zoom_input.handle_event(event)
        update_button.handle_event(event)

    lat_input.update()
    lon_input.update()
    zoom_input.update()

    screen.fill(BACKGROUND_COLOR)

    lat_input.draw(screen)
    lon_input.draw(screen)
    zoom_input.draw(screen)
    update_button.draw(screen)

    if map_image:
        screen.blit(map_image, (MAP_X, MAP_Y))

    pygame.display.flip()

pygame.quit()
sys.exit()
