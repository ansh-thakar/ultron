from sqlalchemy import text
from core.db import get_engine


def login(name, password, role):
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("""SELECT * FROM students 
                    WHERE name = :n AND password_hash = :p 
                    AND (role = :r OR (role IS NULL AND :r = 'student'))"""),
            {"n": name, "p": password, "r": role},
        ).fetchone()
    return dict(row._mapping) if row else None


def register(name, password, role):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""INSERT INTO students 
                    (student_id, name, password_hash, role) 
                    VALUES (:sid, :name, :pwd, :role)"""),
            {"sid": name, "name": name, "pwd": password, "role": role},
        )


def exists(name):
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT 1 FROM students WHERE name = :n"), {"n": name}
        ).fetchone()
    return row is not None