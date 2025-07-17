import sys
from manage import main


if __name__ == '__main__':
     [sys.argv[0], "makemigrations", "models"]
     main([sys.argv[0], "makemigrations", "models"])
     main([sys.argv[0], "migrate"])