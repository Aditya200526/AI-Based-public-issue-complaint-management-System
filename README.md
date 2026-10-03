# 🏛️ AI-Based Public Issue Complaint Management System

**Report • Manage • Track**

A complete web platform for citizens to report public issues (potholes, streetlights, water leakage, drainage, garbage etc.) and for administrators to manage and track them — powered by AI-assisted categorization.

Built for Hackathon by **Chaitanya Patwari & Akash**

---

## ✨ Features

- User Registration & Login
- Submit Complaint with Category, Description, Landmark & Image
- **AI-assisted automatic categorization**
- Unique Complaint ID generation
- Status Tracking (Pending → In Progress → Resolved)
- Admin Dashboard with statistics & filters
- Modern responsive UI

---

## 🛠️ Technology Stack

| Layer     | Technology              |
|-----------|-------------------------|
| Frontend  | HTML, CSS, JavaScript   |
| Backend   | Python, Flask           |
| Database  | SQLite                  |
| AI        | Keyword + Rule based    |
| Tools     | VS Code, Git, GitHub    |

---

## 🚀 How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the application
```bash
python app.py
```

### 3. Open in browser
```
http://127.0.0.1:5000
```

---

## 👤 Demo Accounts

| Role  | Email            | Password  |
|-------|------------------|-----------|
| Admin | admin@civic.ai   | admin123  |
| User  | Register any new account |

---

## 📁 Project Structure

```
AI_Public_Complaint_System/
├── app.py                  # Main Flask application + AI logic
├── requirements.txt
├── README.md
├── static/
│   ├── css/style.css
│   └── uploads/            # Complaint images stored here
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── user_dashboard.html
    ├── submit_complaint.html
    ├── track.html
    └── admin_dashboard.html
```

---

## 🔄 Live Demo Flow (for presentation)

1. Open the application and log in as a **user** (register first).
2. Submit a sample complaint: “Streetlight Not Working near ABC School”.
3. Leave category on **Auto** — AI will detect “Streetlight / Electricity”.
4. Add landmark and optionally an image.
5. Open **Admin Dashboard** (login as admin@civic.ai).
6. Change status: Pending → In Progress → Resolved.
7. Return to User Dashboard / Track page and show the updated status.

---

## 🤖 AI Assistance

The system analyzes the complaint description using keyword matching and suggests the most appropriate category:

- Streetlight / Electricity
- Road / Pothole
- Water Supply
- Drainage / Sewage
- Garbage / Sanitation
- Other

AI is an **assistance layer** — final decisions remain with the admin.

---

## 📌 Current Scope & Future Scope

**Current:**
- Centralized complaint management
- User + Admin dashboards
- AI categorization
- Image upload & status tracking

**Future:**
- Government / Municipal API integration
- GPS-based location
- Real-time notifications
- Automatic department assignment
- AI image analysis
- Analytics dashboard

---

## 📄 License

This project is created for educational / hackathon purposes.
