import multiprocessing
import tkinter as tk

from src.gui import DigitRecognitionApp

if __name__ == "__main__":
    multiprocessing.freeze_support()
    root = tk.Tk()
    app = DigitRecognitionApp(root)
    root.mainloop()
