import pyautogui
import time

print("Di chuột đến vị trí nút cần click... (ấn Ctrl+C để thoát)\n")

try:
    while True:
        x, y = pyautogui.position()
        print(f"Vị trí hiện tại: x={x}, y={y}", end="\r")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nKết thúc đo tọa độ.")
