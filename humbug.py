import sys
from src.app import Humbug

if __name__ == '__main__':
    app = Humbug(sys.argv[1:])
    app.go()
