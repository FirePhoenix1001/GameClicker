import keyboard
import time

def trigger_keys(firstKey, secondKey, second):
    """一個通用的按鍵模擬函式"""
    print(f"執行熱鍵：按下 {firstKey} -> 按下 {secondKey} -> 釋放 {secondKey} -> 釋放 {firstKey}")
    keyboard.press(firstKey)
    time.sleep(second)
    keyboard.press(secondKey)
    time.sleep(second)
    keyboard.release(secondKey)
    time.sleep(second)
    keyboard.release(firstKey)

# --- 主程式：改用狀態輪詢（Polling）模式 ---

# 建立狀態旗標，用來記錄按鍵上一輪的狀態，以防止重複觸發
w_key_was_pressed = False
s_key_was_pressed = False
e_key_was_pressed = False
c_key_was_pressed = False

print("程式已啟動（輪詢模式）。")
# print(" - 按下 'w' 或 's' 測試。")
# print(" - 按下 'esc' 鍵即可安全退出程式。")

# 開始主迴圈，不斷檢查鍵盤狀態
while True:
    try:
        # 優先檢查退出鍵
        # if keyboard.is_pressed('esc'):
        #     print("\n偵測到 'esc'，程式即將結束。")
        #     break

        # --- 檢查 'w' 鍵 ---
        if keyboard.is_pressed('w'):
            # 如果 'w' 現在是按下的，但上一輪是放開的（也就是剛按下的那一瞬間）
            if not w_key_was_pressed:
                trigger_keys('p', 'd', 0.05)
                w_key_was_pressed = True # 更新旗標，表示 'w' 已經被按下了
        else:
            # 如果 'w' 現在是放開的，就重設旗標
            w_key_was_pressed = False

        # --- 檢查 's' 鍵 ---
        if keyboard.is_pressed('s'):
            if not s_key_was_pressed:
                trigger_keys('/', 'd', 0.05)
                s_key_was_pressed = True
        else:
            s_key_was_pressed = False

        # --- 檢查 'e' 鍵 ---
        if keyboard.is_pressed('e'):
            if not e_key_was_pressed:
                trigger_keys('p', 'f', 0.05)
                e_key_was_pressed = True
        else:
            e_key_was_pressed = False

        # --- 檢查 'c' 鍵 ---
        if keyboard.is_pressed('c'):
            if not c_key_was_pressed:
                trigger_keys('/', 'f', 0.05)
                c_key_was_pressed = True
        else:
            c_key_was_pressed = False

        # 短暫休息，避免 CPU 占用率 100%
        time.sleep(0.01)

    except Exception as e:
        print(f"\n發生錯誤: {e}")
        break

print("程式已結束。")