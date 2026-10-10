from sqlalchemy import text
from core.db import get_engine


def fetch_all(query, params=None):
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        return [dict(row._mapping) for row in result]


def execute(query, params=None):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(query), params or {})


# ---------- STUDENT DATA ----------

def my_attendance(sid):
    return fetch_all("""
        SELECT s.subject_name,
               SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present,
               SUM(CASE WHEN a.status='Absent' THEN 1 ELSE 0 END) AS absent,
               COUNT(*) AS total,
               ROUND(100.0 * SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)
                     / COUNT(*), 1) AS pct
        FROM attendance a
        JOIN subjects s ON a.subject_id = s.subject_id
        WHERE a.student_id = :sid
        GROUP BY s.subject_id, s.subject_name
    """, {"sid": sid})


def my_marks(sid):
    return fetch_all("""
        SELECT s.subject_name, a.name AS assessment, a.type,
               m.marks_obtained, a.max_marks,
               ROUND(100.0 * m.marks_obtained / a.max_marks, 1) AS pct
        FROM marks m
        JOIN assessments a ON m.assessment_id = a.assessment_id
        JOIN subjects s ON a.subject_id = s.subject_id
        WHERE m.student_id = :sid
        ORDER BY s.subject_name, a.name
    """, {"sid": sid})


def my_subject_averages(sid):
    return fetch_all("""
        SELECT s.subject_name,
               ROUND(AVG(100.0 * m.marks_obtained / a.max_marks), 1) AS avg_pct
        FROM marks m
        JOIN assessments a ON m.assessment_id = a.assessment_id
        JOIN subjects s ON a.subject_id = s.subject_id
        WHERE m.student_id = :sid
        GROUP BY s.subject_id, s.subject_name
        ORDER BY avg_pct DESC
    """, {"sid": sid})


# ---------- SUBJECTS ----------

def get_all_subjects():
    return fetch_all("SELECT * FROM subjects ORDER BY subject_name")


def add_subject(code, name):
    execute("""
        INSERT INTO subjects (subject_code, subject_name)
        VALUES (:c, :n)
    """, {"c": code, "n": name})


def subject_exists(code):
    rows = fetch_all("SELECT 1 FROM subjects WHERE subject_code = :c", {"c": code})
    return len(rows) > 0


# ---------- ENTRY ----------

def add_attendance(sid, subject_id, class_date, status):
    execute("""
        INSERT INTO attendance (student_id, subject_id, class_date, status)
        VALUES (:sid, :sub, :date, :status)
        ON DUPLICATE KEY UPDATE status = :status
    """, {"sid": sid, "sub": subject_id, "date": class_date, "status": status})


def get_or_create_assessment(subject_id, name, atype, max_marks):
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT assessment_id FROM assessments
            WHERE subject_id = :s AND name = :n
        """), {"s": subject_id, "n": name}).fetchone()
    if row:
        return row[0]
    with engine.begin() as conn:
        result = conn.execute(text("""
            INSERT INTO assessments (subject_id, name, type, max_marks)
            VALUES (:s, :n, :t, :m)
        """), {"s": subject_id, "n": name, "t": atype, "m": max_marks})
        return result.lastrowid


def add_mark(sid, assessment_id, marks):
    execute("""
        INSERT INTO marks (student_id, assessment_id, marks_obtained)
        VALUES (:sid, :aid, :m)
        ON DUPLICATE KEY UPDATE marks_obtained = :m
    """, {"sid": sid, "aid": assessment_id, "m": marks})


# ---------- TEACHER ----------

def get_all_students_only():
    return fetch_all("""
        SELECT * FROM students 
        WHERE role = 'student' OR role IS NULL 
        ORDER BY name
    """)