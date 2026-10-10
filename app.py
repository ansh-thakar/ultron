import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from core.auth import login, register, exists
from core.queries import (
    my_attendance, my_marks, my_subject_averages, get_all_students_only,
    get_all_subjects, add_subject, subject_exists,
    add_attendance, get_or_create_assessment, add_mark
)
from core.ai import ask_ultron

st.set_page_config(page_title="ULTRON", layout="wide")
st.logo("logo.jpg")

css = Path(__file__).parent / "assets" / "ultron.css"
st.markdown(f"<style>{css.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

st.title("ULTRON")
st.session_state.setdefault("user", None)
st.session_state.setdefault("messages", [])
st.session_state.setdefault("mode", None)

# ============================================================
# GATE
# ============================================================
if not st.session_state.user:

    # ---- ROLE SELECTION ----
    if st.session_state.mode is None:
        st.write("### Choose how to sign in")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👨‍🎓 Student", use_container_width=True):
                st.session_state.mode = "student"
                st.rerun()
        with col2:
            if st.button("👨‍🏫 Teacher", use_container_width=True):
                st.session_state.mode = "teacher"
                st.rerun()
        st.stop()

    role = st.session_state.mode
    st.write(f"### {role.title()} Access")

    t1, t2 = st.tabs(["Login", "Sign Up"])

    with t1:
        n = st.text_input("Name", key=f"{role}_login_name")
        p = st.text_input("Password", type="password", key=f"{role}_login_pwd")
        if st.button("Login", key=f"{role}_login_btn"):
            u = login(n, p, role)
            if u:
                st.session_state.user = u
                st.session_state.mode = None
                st.rerun()
            else:
                st.error(f"Invalid {role} credentials")

    with t2:
        n2 = st.text_input("New Name", key=f"{role}_reg_name")
        p2 = st.text_input("New Password", type="password", key=f"{role}_reg_pwd")
        if st.button("Create", key=f"{role}_reg_btn"):
            if exists(n2):
                st.error("Name taken")
            else:
                register(n2, p2, role)
                st.success(f"{role.title()} account created — please log in")

    if st.button("← Back"):
        st.session_state.mode = None
        st.rerun()

    st.stop()

# ============================================================
# LOGGED IN
# ============================================================
user = st.session_state.user
role = user.get("role") or "student"

with st.sidebar:
    st.write(f"**{user['name']}**")
    st.caption(f"Role: {role.title()}")
    if st.button("Logout"):
        st.session_state.user = None
        st.session_state.messages = []
        st.session_state.mode = None
        st.rerun()

# ---- Teacher: pick which student to view ----
if role == "teacher":
    students = get_all_students_only()
    if not students:
        st.warning("No students registered yet.")
        st.stop()

    names = [s["name"] for s in students]
    with st.sidebar:
        selected_name = st.selectbox("View student", names)

    selected = next(s for s in students if s["name"] == selected_name)
    sid = selected["student_id"]
    viewing_name = selected["name"]
    st.caption(f"👤 Viewing: **{viewing_name}**")
else:
    sid = user["student_id"]
    viewing_name = user["name"]

# ---- Fetch data ----
att = my_attendance(sid)
subs = my_subject_averages(sid)
mks = my_marks(sid)

att_ok = [a for a in att if pd.notna(a["pct"])]
subs_ok = [s for s in subs if pd.notna(s["avg_pct"])]
mks_ok = [m for m in mks if pd.notna(m["pct"])]

avg_att = sum(a["pct"] for a in att_ok) / len(att_ok) if att_ok else 0
avg_score = sum(s["avg_pct"] for s in subs_ok) / len(subs_ok) if subs_ok else 0

# ---- Tabs ----
if role == "teacher":
    tab_dash, tab_ai = st.tabs(["Dashboard", "AI"])
    tab_add = None
else:
    tab_dash, tab_add, tab_ai = st.tabs(["Dashboard", "Add", "AI"])

# ============================================================
# DASHBOARD
# ============================================================
with tab_dash:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Attendance", f"{avg_att:.1f}%")
    c2.metric("Average", f"{avg_score:.1f}%")
    c3.metric("Strongest", subs_ok[0]["subject_name"] if subs_ok else "—")
    c4.metric("Weakest", subs_ok[-1]["subject_name"] if subs_ok else "—")

    colors = ["#D4A24C", "#C8313E", "#6BCB77", "#5BC0DE", "#B39DDB", "#FF7A00"]

    # ---- Attendance ----
    if att_ok:
        col1, col2 = st.columns(2)
        names = [a["subject_name"] for a in att_ok]
        pcts = [float(a["pct"]) for a in att_ok]
        bar_colors = ["#C8313E" if p < 75 else "#D4A24C" if p < 85 else "#6BCB77" for p in pcts]

        with col1:
            fig, ax = plt.subplots(figsize=(5, 3.2))
            ax.bar(names, pcts, color=bar_colors)
            ax.set_ylim(0, 100)
            ax.set_title("Attendance (%)", fontsize=11, fontweight="bold")
            ax.set_ylabel("Percent", fontsize=9)
            plt.xticks(rotation=15, fontsize=9)
            plt.yticks(fontsize=9)
            plt.tight_layout()
            st.pyplot(fig)

        with col2:
            if sum(pcts) > 0:
                fig, ax = plt.subplots(figsize=(5, 3.2))
                ax.pie(pcts, labels=names, colors=colors[:len(names)],
                       autopct="%1.0f%%", textprops={"fontsize": 10},
                       wedgeprops={"edgecolor": "#0B1220", "linewidth": 2})
                ax.set_title("Attendance Split", fontsize=11, fontweight="bold")
                plt.tight_layout()
                st.pyplot(fig)

    # ---- Marks ----
    if mks_ok:
        col3, col4 = st.columns(2)

        with col3:
            labels = [m["subject_name"] + "\n" + m["assessment"] for m in mks_ok]
            pcts = [float(m["pct"]) for m in mks_ok]
            bar_colors = ["#C8313E" if p < 60 else "#D4A24C" if p < 80 else "#6BCB77" for p in pcts]
            fig, ax = plt.subplots(figsize=(5, 3.2))
            ax.bar(labels, pcts, color=bar_colors)
            ax.set_ylim(0, 100)
            ax.set_title("Marks (% Score)", fontsize=11, fontweight="bold")
            ax.set_ylabel("Percent", fontsize=9)
            plt.xticks(fontsize=8)
            plt.yticks(fontsize=9)
            plt.tight_layout()
            st.pyplot(fig)

        with col4:
            if subs_ok:
                names = [s["subject_name"] for s in subs_ok]
                vals = [float(s["avg_pct"]) for s in subs_ok]
                fig, ax = plt.subplots(figsize=(5, 3.2))
                ax.barh(names, vals, color=colors[:len(names)])
                ax.set_xlim(0, 100)
                ax.set_title("Subject Averages (%)", fontsize=11, fontweight="bold")
                ax.set_xlabel("Percent", fontsize=9)
                plt.xticks(fontsize=9)
                plt.yticks(fontsize=9)
                plt.tight_layout()
                st.pyplot(fig)

        st.dataframe(mks, use_container_width=True, hide_index=True)

    if not att_ok and not mks_ok:
        st.info("No data yet for this student.")

# ============================================================
# ADD (student only)
# ============================================================
if tab_add is not None:
    with tab_add:
        st.subheader("Add Subject")
        with st.form("sub_form"):
            s_code = st.text_input("Subject Code", placeholder="PY101")
            s_name = st.text_input("Subject Name", placeholder="Python Programming")
            if st.form_submit_button("Add Subject"):
                if not s_code or not s_name:
                    st.error("Both fields required")
                elif subject_exists(s_code):
                    st.error("Subject code already exists")
                else:
                    add_subject(s_code, s_name)
                    st.success(f"Added: {s_code} — {s_name}")

        st.divider()

        subjects = get_all_subjects()

        if not subjects:
            st.info("Add a subject first, then attendance and marks.")
        else:
            sub_map = {s["subject_name"]: s["subject_id"] for s in subjects}

            st.subheader("Add Attendance")
            with st.form("att_form"):
                a_sub = st.selectbox("Subject", list(sub_map.keys()))
                a_date = st.date_input("Class Date")
                a_status = st.radio("Status", ["Present", "Absent", "Late"], horizontal=True)
                if st.form_submit_button("Save Attendance"):
                    add_attendance(sid, sub_map[a_sub], a_date.strftime("%Y-%m-%d"), a_status)
                    st.success(f"Saved: {a_sub} on {a_date} → {a_status}")

            st.divider()

            st.subheader("Add Test Score")
            with st.form("mark_form"):
                m_sub = st.selectbox("Subject", list(sub_map.keys()))
                m_name = st.text_input("Test Name", placeholder="Unit Test 1")
                m_type = st.selectbox("Type", ["unit_test", "practical", "assignment", "final"])
                m_max = st.number_input("Out Of (Max Marks)", min_value=1.0, value=100.0, step=1.0)
                m_got = st.number_input("Marks Obtained", min_value=0.0, value=0.0, step=0.5)
                if st.form_submit_button("Save Score"):
                    if not m_name:
                        st.error("Test name required")
                    elif m_got > m_max:
                        st.error("Obtained can't exceed max")
                    else:
                        aid = get_or_create_assessment(sub_map[m_sub], m_name, m_type, m_max)
                        add_mark(sid, aid, m_got)
                        st.success(f"Saved: {m_sub} · {m_name} → {m_got}/{m_max}")

# ============================================================
# AI
# ============================================================
with tab_ai:
    ctx = f"Student: {viewing_name}\nAttendance: {att_ok}\nMarks: {mks_ok}"

    for m in st.session_state.messages:
        st.chat_message(m["role"]).write(m["content"])

    if q := st.chat_input("Ask…"):
        st.session_state.messages.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.write(q)
        with st.chat_message("assistant"):
            with st.spinner("ULTRON is thinking…"):
                r = ask_ultron(q, ctx)
            st.write(r)
        st.session_state.messages.append({"role": "assistant", "content": r})
