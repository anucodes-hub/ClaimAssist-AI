**ClaimAssist AI**

ClaimAssist AI is an intelligent, full-stack insurance claim processing platform designed to simplify documentation, validation, and submission workflows for policyholders.

It reduces claim rejections caused by documentation errors by leveraging AI-driven OCR, NLP-based rule extraction, and dynamic insurer-specific document validation.

---

## 🌟 Problem Statement

Insurance claim documentation is complex and varies by:

- Insurer
- Policy type
- Claim category
- Regulatory requirements

Missing or incorrect documents lead to:

- Claim delays
- Rejections
- Financial stress during emergencies

ClaimAssist solves this using AI-powered document intelligence and workflow automation.

---

## 🧠 Key Features

### ✅ Smart Document Checklist Generator
- Generates insurer-specific required documents dynamically
- Based on policy type (Health, Life, Vehicle, Travel, Property)

### 📄 AI-Based OCR Validation
- Extracts text from uploaded documents
- Validates structured and unstructured data
- Flags missing or incorrect submissions

### 🔐 Secure Authentication
- JWT-based authentication
- Role-based access (User / Admin)

### 📊 Claim Dashboard
- Total claims overview
- Approved / Pending / Rejected statistics
- Claim amount tracking
- Submission and approval dates

### 🏛 DigiLocker Integration (India Stack)
- Secure document retrieval via API Setu
- Government-authenticated document validation

### ☁ Secure Storage
- AWS S3 for encrypted document storage
- AES-256 encryption enabled

---

## 🏗 Architecture

### 🔹 Frontend
- HTML, CSS, JavaScript
- Responsive UI
- Modular component structure

### 🔹 Backend
- FastAPI (Python)
- JWT Authentication
- PostgreSQL (structured claim data)
- SQLAlchemy ORM

### 🔹 AI & Processing
- Grok AI > API(chatbot)
- Tesseract(OCR)
- OpenCV (Blur detection & document preprocessing)
- NLP-based rule extraction from policy PDFs

### 🔹 Storage & Infrastructure
- PostgreSQL (Claims, Users, Status tracking)
- AWS S3 (Document storage)
- API Setu (DigiLocker access)

---

## 🛠 Tech Stack

| Layer        | Technology |
|--------------|------------|
| Frontend     | HTML, CSS, JavaScript |
| Backend      | FlaskAPI |
| Database     | PostgreSQL |
| ORM          | SQLAlchemy |
| Auth         | JWT |
| OCR          | Tesseract |
| CV           | OpenCV |
| Storage      | AWS S3 |
| Integration  | API Setu (DigiLocker) |

---

Team: ParallelX