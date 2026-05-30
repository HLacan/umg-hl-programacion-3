import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from interfaz.app import TotitoApp

if __name__ == '__main__':
    app = TotitoApp()
    app.mainloop()

