from tkinter import Tk
from gui.file_cleaner_gui import FileCleanerGUI

def main():
    root = Tk()
    app = FileCleanerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()