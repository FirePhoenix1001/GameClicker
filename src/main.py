import sys
import os
import tkinter as tk

# Add the current directory to sys.path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.GUI import IntegratedGUI

def main():
    try:
        root = tk.Tk()
        app = IntegratedGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"程式啟動失敗: {e}")
        input("按任意鍵結束...")

if __name__ == "__main__":
    main()
