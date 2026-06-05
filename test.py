from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://postgres:1234@localhost:5432/bookstore"
)

try:
    with engine.connect():
        print("Password is correct!")
except Exception as e:
    print("Failed:", e)