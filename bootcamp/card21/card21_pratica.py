import cv2
import numpy as np

# Variáveis globais para armazenar a posição do mouse
mouse_x, mouse_y = 0, 0

# Função de callback do mouse
def mouse_callback(event, x, y, flags, param):
    global mouse_x, mouse_y
    if event == cv2.EVENT_MOUSEMOVE:
        mouse_x, mouse_y = x, y

cap = cv2.VideoCapture(0)

# Configurar a janela e o callback do mouse
cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", mouse_callback)

while True:
    _, frame = cap.read()
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # PURPLE MASK
    low = np.array([140, 160, 92])
    high = np.array([142, 190, 125])
    purple = cv2.inRange(hsv_frame, low, high)
    result = cv2.bitwise_and(frame, frame, mask=purple)

    # Obter valores RGB e HSV do pixel sob o mouse
    if 0 <= mouse_y < frame.shape[0] and 0 <= mouse_x < frame.shape[1]:
        rgb_pixel = frame[mouse_y, mouse_x]  # BGR
        hsv_pixel = hsv_frame[mouse_y, mouse_x]
        # Texto com valores RGB e HSV
        rgb_text = f"RGB: ({rgb_pixel[2]}, {rgb_pixel[1]}, {rgb_pixel[0]})"
        hsv_text = f"HSV: ({hsv_pixel[0]}, {hsv_pixel[1]}, {hsv_pixel[2]})"
        # Desenhar os valores na imagem
        cv2.putText(frame, rgb_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, hsv_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Desenhar um pequeno círculo na posição do mouse
        cv2.circle(frame, (mouse_x, mouse_y), 3, (0, 255, 0), -1)

    # Exibir imagens
    cv2.imshow("Frame", frame)
    cv2.imshow("Roxin", result)

    key = cv2.waitKey(1)
    if key == 27:
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
