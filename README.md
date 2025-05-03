# Household Services Application

## 👤 Student Details

- **Name**: [Deepak kumar]
- **Roll Number**: [22f3000107]
- **Department**: [Modern Application Development 1]
- **Institute**: [IIT Madras,Chennai]

---

## 📌 Project Overview

This is a multi-user web application designed to facilitate household service management. It provides a platform where **Customers** can request home services, **Service Professionals** can register and respond to those requests, and **Admins** can manage the platform.

### 🧩 Problem Statement

Build a complete household services management system that:
- Allows customers to book services like cleaning, electrician, AC repair, etc.
- Enables service professionals to register, get verified, and manage service requests.
- Gives admin full control to approve/reject professionals, manage services, and monitor all users.

### 🛠️ Approach

- Flask is used as the backend framework with SQLite for the database.
- HTML, CSS (Bootstrap), and Jinja2 for templating.
- Admin panel for approvals and management.
- Role-based access for customers, professionals, and admins.

---

## 🧰 Frameworks and Libraries Used

- **Python 3.x**
- **Flask**
- **Flask-SQLAlchemy**
- **Jinja2**
- **Bootstrap 4**
- **SQLite3**

---

## 🗃️ ER Diagram

See the included ER diagram file/image in the project documentation folder or in the `Project Report.pdf`.  
It includes:
- `User` (base model with roles)
- `Customer`, `ServiceProfessional` (role-specific details)
- `Service` (service metadata)
- `ServiceRequest` (core request workflow)

---

## 📡 API Resource Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/register` | GET, POST | Register a new user |
| `/login` | GET, POST | User login based on role |
| `/admin/dashboard` | GET | Admin dashboard |
| `/admin/review-professional` | GET | View and approve/reject professionals |
| `/professional/dashboard` | GET | Dashboard for service professionals |
| `/customer/dashboard` | GET | Dashboard for customers |
| `/request-service` | GET, POST | Customer can request a service |
| `/close-request/<id>` | POST | Professional closes a completed request |
| `/rate-service/<id>` | POST | Customer rates the service after completion |

---

## 📂 Project Structure
HouseholdServicesSubmission/
│
├── Code/
│ ├── app.py
│ ├── controllers.py
│ ├── instance/
│ │ └── HSA.sqlite3
│ ├── models.py
│ ├── requirements.txt
│ ├── routes.py
│ ├── static/
│ │ ├── login.css
│ │ └── style.css
│ └── templates/
│ └── [All HTML templates]
│
├── Project Report.pdf
├── README.md


---

## 📺 Project Video

[Google Drive Link to Presentation Video](https://drive.google.com/file/d/1_-DCD_60kWwTBcbKyzEGKV9PKkaw7DjF/view?usp=drive_link
)

---

## ⚙️ Setup Instructions

1. Clone or extract the folder.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
3.Install dependencies:
  pip install -r requirements.txt

4.Run the app:
  flask run

