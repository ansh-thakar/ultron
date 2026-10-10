# 🔴 ULTRON — Student Academic Management & Analytics System

[![Live Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ultron-9.streamlit.app/)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.x-FF4B4B)
![MySQL](https://img.shields.io/badge/mysql-8.4-4479A1)
![TiDB](https://img.shields.io/badge/TiDB-Cloud-DC150D)
![License](https://img.shields.io/badge/license-MIT-green)

A web-based academic management platform where students track their own attendance and marks, view personalized analytics, and consult an AI assistant for insights. Teachers can monitor any student's performance through the same dashboard.

**🌐 Live Demo:** [https://ultron-9.streamlit.app/](https://ultron-9.streamlit.app/)

---

## 📖 Overview

**ULTRON** solves three problems in traditional academic management:

1. **Scattered data** — attendance and marks live in Excel sheets or paper registers
2. **No real-time visibility** — students don't know their standing until exam results
3. **Zero personalization** — teachers can't quickly spot at-risk students

ULTRON centralizes the data, auto-generates analytics, and adds an AI layer for conversational insights.

---

## ✨ Features

### 👨‍🎓 Student Mode
- Secure login / signup
- Personal dashboard with attendance % and average score
- Add subjects, attendance records, and test scores
- View 4 interactive charts (bar + pie)
- Chat with ULTRON AI about personal performance

### 👨‍🏫 Teacher Mode
- Dedicated teacher login flow
- Sidebar dropdown to select any student
- View any student's complete analytics
- Read-only view (cannot modify student data)

### 📊 Analytics
- Attendance % per subject
- Average score per subject
- Strongest and weakest subject detection
- Color-coded performance indicators (red / gold / green)
- Full marks breakdown table

### 🤖 ULTRON AI
- Powered by **Google Gemini 2.5 Flash**
- Context-aware — receives the student's actual data
- Answers in plain English with bullet points
- Domain-specific system prompt (academic focus)

---

## 🏗️ Architecture
