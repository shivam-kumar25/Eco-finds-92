from src.init_db import reset_db, init_db

if __name__ == '__main__':
    reset_db()
    init_db()
    print("Database has been reset and reinitialized successfully!")
