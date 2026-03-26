import tkinter as tk
from gui import InventarioGUI


def main():
    root = tk.Tk()
    app = InventarioGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()