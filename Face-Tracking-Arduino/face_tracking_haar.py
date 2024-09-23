import cv2
import numpy as np
import serial
from picamera2 import Picamera2
import time

# Настройки для Arduino
SERIAL_PORT = '/dev/ttyUSB0'  # Замените на ваш порт, например '/dev/ttyACM0'
BAUD_RATE = 9600
SENSITIVITY = 0.1  # Чувствительность движения сервоприводов

# Абсолютный путь к классификатору лиц
face_cascade_path = '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(face_cascade_path)

# Проверка загрузки классификатора
if face_cascade.empty():
    raise IOError(f"Не удалось загрузить каскад Хаара по пути: {face_cascade_path}")

# Подключение к Arduino
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    ser.flush()
    print(f"Подключено к Arduino через {SERIAL_PORT}")
except serial.SerialException as e:
    ser = None
    print(f"Не удалось подключиться к Arduino: {e}")

# Функция для отправки команд на Arduino
def send_command(angle_x, angle_y):
    if ser:
        command = f"X:{angle_x},Y:{angle_y}\n"
        ser.write(command.encode())
        print(f"Отправлено: {command.strip()}")
    else:
        print(f"Команда: X={angle_x}, Y={angle_y}")

# Инициализация камеры
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

# Основной цикл
try:
    while True:
        frame = picam2.capture_array()

        # Преобразование изображения в оттенки серого для детекции лиц
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Обнаружение лиц
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Если лица найдены
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                cx = x + w // 2
                cy = y + h // 2

                # Рисование прямоугольника вокруг каждого лица
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

                # Расчет отклонения от центра кадра
                frame_center_x = frame.shape[1] // 2
                frame_center_y = frame.shape[0] // 2
                delta_x = cx - frame_center_x
                delta_y = cy - frame_center_y

                # Расчет углов для сервоприводов
                angle_x = int(90 + delta_x * SENSITIVITY)
                angle_y = int(90 + delta_y * SENSITIVITY)

                # Ограничение углов до 0-180
                angle_x = max(0, min(180, angle_x))
                angle_y = max(0, min(180, angle_y))

                # Отправка команды на Arduino
                send_command(angle_x, angle_y)

        # Отображение видео с рамками вокруг лиц
        cv2.imshow('Face Tracking', frame)

        # Выход при нажатии 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Прерывание пользователем")

# Освобождение ресурсов
picam2.stop()
cv2.destroyAllWindows()
if ser:
    ser.close()
print("Программа завершена.")
