import tkinter as tk
from app.tiff_compression_gui import TiffCompressorGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = TiffCompressorGUI(root)
    root.mainloop()