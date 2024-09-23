#include <Servo.h>

// Создаем объекты для сервоприводов
Servo servoX;
Servo servoY;

// Пины для сервоприводов
const int servoXPin = 9;
const int servoYPin = 10;

// Переменные для углов сервоприводов
int angleX = 90;  // Начальное положение по оси X (по центру)
int angleY = 90;  // Начальное положение по оси Y (по центру)

// Границы углов для защиты сервоприводов
const int minAngle = 0;
const int maxAngle = 180;

// Порог для сглаживания данных (чтобы серво двигались плавно)
const int threshold = 5;

// Буфер для входящих данных
String inputString = "";
bool dataAvailable = false;

void setup() {
  // Инициализация сервоприводов
  servoX.attach(servoXPin);
  servoY.attach(servoYPin);

  // Устанавливаем начальные углы
  servoX.write(angleX);
  servoY.write(angleY);

  // Инициализация последовательного порта
  Serial.begin(9600);
  inputString.reserve(30); // Резервируем место для входящих данных
}

void loop() {
  // Чтение данных от Raspberry Pi
  if (Serial.available()) {
    char inChar = (char)Serial.read();
    // Проверяем конец строки
    if (inChar == '\n') {
      dataAvailable = true;
    } else {
      inputString += inChar;
    }
  }

  // Если данные получены, обрабатываем их
  if (dataAvailable) {
    // Парсинг данных и обновление углов сервоприводов
    parseData(inputString);

    // Сброс строки
    inputString = "";
    dataAvailable = false;
  }
}

void parseData(String data) {
  // Ищем запятую, разделяющую координаты X и Y
  int commaIndex = data.indexOf(',');

  // Если запятая найдена, разбиваем строку на X и Y
  if (commaIndex > 0) {
    int targetX = data.substring(0, commaIndex).toInt();
    int targetY = data.substring(commaIndex + 1).toInt();

    // Преобразование координат в углы для сервоприводов
    int newAngleX = map(targetX, 0, 640, minAngle, maxAngle);  // Предполагается, что ширина изображения 640
    int newAngleY = map(targetY, 0, 480, minAngle, maxAngle);  // Предполагается, что высота изображения 480

    // Плавное перемещение по оси X
    if (abs(newAngleX - angleX) > threshold) {
      angleX = constrain(newAngleX, minAngle, maxAngle);
      servoX.write(angleX);
    }

    // Плавное перемещение по оси Y
    if (abs(newAngleY - angleY) > threshold) {
      angleY = constrain(newAngleY, minAngle, maxAngle);
      servoY.write(angleY);
    }
  }
}
