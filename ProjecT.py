import cv2
import mediapipe as mp
import numpy as np
import pygame
import sys

pygame.init()
pygame.mixer.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
screen_color = (200, 200, 200)
text_color = (0, 0, 0)
button_color = (0, 0, 255)
hover_color = (0, 100, 255)


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("musical_hands")

button_rect = pygame.Rect(300, 250, 200, 100)
button1_rect = pygame.Rect(70, 300, 160, 60)
button2_rect = pygame.Rect(300, 300, 160, 60)
button3_rect = pygame.Rect(530, 300, 160, 60)

button_visible = True
button1_visible = False
button2_visible = False
button3_visible = False

def draw_button1(is_hovered1):
    if button1_visible:
        color = button_color if is_hovered1 else hover_color
        pygame.draw.rect(screen, color, button1_rect)
        # Текст кнопки
        font = pygame.font.Font(None, 30)
        text = font.render("guitar", True, WHITE)
        text_rect = text.get_rect(center=button1_rect.center)
        screen.blit(text, text_rect)

def draw_button2(is_hovered2):
    if button2_visible:
        color = button_color if is_hovered2 else hover_color
        pygame.draw.rect(screen, color, button2_rect)
        # Текст кнопки
        font = pygame.font.Font(None, 30)
        text = font.render("piano", True, WHITE)
        text_rect = text.get_rect(center=button2_rect.center)
        screen.blit(text, text_rect)

def draw_button3(is_hovered3):
    if button3_visible:
        color = button_color if is_hovered3 else hover_color
        pygame.draw.rect(screen, color, button3_rect)
        # Текст кнопки
        font = pygame.font.Font(None, 30)
        text = font.render("drums", True, WHITE)
        text_rect = text.get_rect(center=button3_rect.center)
        screen.blit(text, text_rect)


def draw_button(is_hovered):
    if button_visible:
        color = button_color if is_hovered else hover_color
        pygame.draw.rect(screen, color, button_rect)
        # Текст кнопки
        font = pygame.font.Font(None, 40)
        text = font.render("start", True, WHITE)
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)

notes = []
instrument_selected = False
# Основной игровой цикл
running = True
while running:
    is_hovered = False
    is_hovered1 = False
    is_hovered2 = False
    is_hovered3 = False


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Проверяем, была ли нажата мышь
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if button_visible and button_rect.collidepoint(mouse_pos):
                button_visible = False
                button1_visible = True
                button2_visible = True
                button3_visible = True

            if button1_visible and button1_rect.collidepoint(mouse_pos): # guitar
                notes = [
                    pygame.mixer.Sound('G_B3.mp3'),
                    pygame.mixer.Sound('G_D3.mp3'),
                    pygame.mixer.Sound('G_E4.mp3'),
                    pygame.mixer.Sound('G_G3.mp3')
                ]
                instrument_selected = True

            if button2_visible and button2_rect.collidepoint(mouse_pos): #piano
                notes = [
                    pygame.mixer.Sound('noty-do.mp3'),
                    pygame.mixer.Sound('re.mp3'),
                    pygame.mixer.Sound('mi.mp3'),
                    pygame.mixer.Sound('fa.mp3')
                ]
                instrument_selected = True

            if button3_visible and button3_rect.collidepoint(mouse_pos): #drums
                notes = [
                    pygame.mixer.Sound('D_1.mp3'),
                    pygame.mixer.Sound('D_2.mp3'),
                    pygame.mixer.Sound('D_3.mp3'),
                    pygame.mixer.Sound('D_4.mp3')
                ]
                instrument_selected = True

            played_notes = [False] * len(notes)

            if (button1_visible and button1_rect.collidepoint(mouse_pos)) or (button2_visible and button2_rect.collidepoint(mouse_pos)) or (button3_visible and button3_rect.collidepoint(mouse_pos)):
                def get_points(landmark, shape):
                    points = []
                    for mark in landmark:
                        points.append([mark.x * shape[1], mark.y * shape[0]])
                    return np.array(points, dtype=np.int32)

                def palm_size(landmark, shape):
                    x1, y1 = landmark[0].x * shape[1], landmark[0].y * shape[0]
                    x2, y2 = landmark[5].x * shape[1], landmark[5].y * shape[0]
                    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** .5

                if instrument_selected:
                    handsDetector = mp.solutions.hands.Hands()
                    cap = cv2.VideoCapture(0)
                    while cap.isOpened():
                        ret, frame = cap.read()
                        if cv2.waitKey(1) & 0xFF == ord('q') or not ret:
                            break

                        flipped = np.fliplr(frame)
                        flippedRGB = cv2.cvtColor(flipped, cv2.COLOR_BGR2RGB)
                        results = handsDetector.process(flippedRGB)


                        if results.multi_hand_landmarks:
                            for hand_landmarks in results.multi_hand_landmarks:
                                mp.solutions.drawing_utils.draw_landmarks(flippedRGB, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
                                (x, y), r = cv2.minEnclosingCircle(get_points(hand_landmarks.landmark, flippedRGB.shape))
                                ws = palm_size(hand_landmarks.landmark, flippedRGB.shape)

                                x_tip_4 = int(hand_landmarks.landmark[4].x * flippedRGB.shape[1])
                                y_tip_4 = int(hand_landmarks.landmark[4].y * flippedRGB.shape[0])

                                for i in range(8, 21):
                                    x_tip_other = int(hand_landmarks.landmark[i].x * flippedRGB.shape[1])
                                    y_tip_other = int(hand_landmarks.landmark[i].y * flippedRGB.shape[0])

                                    distance = np.sqrt((x_tip_4 - x_tip_other) ** 2 + (y_tip_4 - y_tip_other) ** 2)


                                    note_index = (i - 8) // 4

                                    if 0 <= note_index < len(notes):  # Убедимся, что индекс в пределах массива
                                        if distance < 50:  # Если расстояние меньше порога
                                            if not played_notes[note_index]:  # Если нота еще не воспроизведена
                                                notes[note_index].play()  # Воспроизводим ноту
                                                played_notes[note_index] = True  # Отмечаем, что нота была сыграна
                                        else:
                                            # Сбрасываем состояние ноты, если расстояние увеличилось
                                            played_notes[note_index] = False

                        res_image = cv2.cvtColor(flippedRGB, cv2.COLOR_RGB2BGR)
                        cv2.imshow("Hands", res_image)

                    # освобождаем ресурсы
                    cap.release()
                    handsDetector.close()
                    cv2.destroyAllWindows()


    mouse_pos = pygame.mouse.get_pos()
    if button_rect.collidepoint(mouse_pos):
        is_hovered = True
    if button1_rect.collidepoint(mouse_pos):
        is_hovered1 = True
    if button2_rect.collidepoint(mouse_pos):
        is_hovered2 = True
    if button3_rect.collidepoint(mouse_pos):
        is_hovered3 = True

    screen.fill(screen_color)
    draw_button(is_hovered)
    draw_button1(is_hovered1)
    draw_button2(is_hovered2)
    draw_button3(is_hovered3)

    if button1_visible or button2_visible or button3_visible:
        font = pygame.font.Font(None, 50)
        text = font.render("choose instrument:", True, BLACK)
        text_rect = text.get_rect(center=(WIDTH // 2, 200))
        screen.blit(text, text_rect)

    pygame.display.flip()

pygame.quit()

