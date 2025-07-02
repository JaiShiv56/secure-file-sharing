# 🔐 Secure File Sharing System (FastAPI)

A secure file-sharing backend system built with **FastAPI** and **SQLAlchemy**.  
It allows authenticated users (Ops & Clients) to securely upload and download files.

---

## 🚀 Features

- ✅ JWT Authentication (Signup/Login)
- ✅ Email verification with secure token (Gmail SMTP)
- ✅ Role-based access (`client` and `ops`)
- ✅ File Upload (Ops only: `.docx`, `.pptx`, `.xlsx`)
- ✅ Secure Download Links with tokenized URLs
- ✅ SQLite with SQLAlchemy ORM
- ✅ Clean folder structure and reusable components

---

## 🧑‍💻 Tech Stack

- FastAPI
- SQLAlchemy + SQLite
- JWT (with `python-jose`)
- Email via `FastAPI-Mail`
- Pydantic for validation

---

## 🛠️ How to Run

```bash
# 1. Install requirements
pip install -r requirements.txt

# 2. Start the server
uvicorn app.main:app --reload

# 3. Access docs at
http://localhost:8000/docs
