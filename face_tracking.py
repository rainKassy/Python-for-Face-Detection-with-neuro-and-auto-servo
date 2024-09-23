import cv2
import numpy as np
import serial
from picamera2 import Picamera2
import time

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600
SENSITIVITY = 0.05
NEUTRAL_POSITION_TIMEOUT = 1  # Ожидание перед возвратом камеры в нейтральное положение
MAX_ANGLE_STEP = 0.5  # Уменьшили шаг для плавного движения

current_angle_x = 90
current_angle_y = 90
last_face_time = time.time()  # Время последнего обнаружения лица

# Загрузка модели для распознавания лиц
net = cv2.dnn.readNetFromCaffe('deploy.prototxt', 'res10_300x300_ssd_iter_140000_fp16.caffemodel')

# Подключение к Arduino
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    ser.flush()
    print(f"Подключено к Arduino через {SERIAL_PORT}")
except serial.SerialException as e:
    ser = None
    print(f"Не удалось подключиться к Arduino: {e}")

# Отправка команд на сервоприводы
def send_command(angle_x, angle_y):
    if ser:
        command = f"X:{angle_x},Y:{angle_y}\n"
        ser.write(command.encode())
    else:
        print(f"Команда на Arduino не отправлена: X={angle_x}, Y={angle_y}")

# Настройка камеры Picamera2
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (320, 240)})
picam2.configure(config)
picam2.start()

# Функция для детекции лиц с помощью DNN
def detect_faces_dnn(frame):
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123], False, False)
    net.setInput(blob)
    detections = net.forward()
    faces = []

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:  # Порог уверенности
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            faces.append((startX, startY, endX - startX, endY - startY))
    return faces

# Плавное изменение углов
def smooth_angle_change(current_angle, target_angle, max_step):
    if abs(current_angle - target_angle) <= max_step:
        return target_angle
    return current_angle + max_step if current_angle < target_angle else current_angle - max_step

# Возврат камеры в нейтральное положение
def move_to_neutral():
    global current_angle_x, current_angle_y
    target_angle_x = 90
    target_angle_y = 90
    current_angle_x = smooth_angle_change(current_angle_x, target_angle_x, MAX_ANGLE_STEP)
    current_angle_y = smooth_angle_change(current_angle_y, target_angle_y, MAX_ANGLE_STEP)
    send_command(current_angle_x, current_angle_y)

# Главный цикл программы
def main_loop():
    global current_angle_x, current_angle_y, last_face_time
    while True:
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Обнаружение лиц
        faces = detect_faces_dnn(frame_bgr)

        if len(faces) > 0:
            largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
            (x, y, w, h) = largest_face
            cx = x + w // 2
            cy = y + h // 2

            frame_center_x = 320 // 2
            frame_center_y = 240 // 2
            delta_x = cx - frame_center_x
            delta_y = cy - frame_center_y

            print(f"Отклонение по X: {delta_x}, по Y: {delta_y}")

            # Пропорциональное управление движением сервоприводов
            control_x = (delta_x / 320) * 180
            control_y = (delta_y / 240) * 180

            target_angle_x = int(current_angle_x + control_x * SENSITIVITY)
            target_angle_y = int(current_angle_y + control_y * SENSITIVITY)

            target_angle_x = max(0, min(180, target_angle_x))
            target_angle_y = max(0, min(180, target_angle_y))

            current_angle_x = smooth_angle_change(current_angle_x, target_angle_x, MAX_ANGLE_STEP)
            current_angle_y = smooth_angle_change(current_angle_y, target_angle_y, MAX_ANGLE_STEP)

            send_command(current_angle_x, current_angle_y)
            last_face_time = time.time()

            # Рисуем квадраты вокруг лиц
            cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)

        else:
            print("Лицо не обнаружено.")
            if time.time() - last_face_time > NEUTRAL_POSITION_TIMEOUT:
                move_to_neutral()

        # Вывод видео на экран
        cv2.imshow('Face Tracking', frame_bgr)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == '__main__':
    main_loop()
    cv2.destroyAllWindows()
