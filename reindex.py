from src.index import reindex
from uno import app

if __name__ == '__main__':
    with app.app_context():
        reindex()
