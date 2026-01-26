import multiprocessing
import tkinter as tk
from tkinter import Tk

from src.gui import DigitRecognitionApp

if __name__ == "__main__":
    multiprocessing.freeze_support()
    root: Tk = tk.Tk()
    app: DigitRecognitionApp = DigitRecognitionApp(root)
    root.mainloop()
