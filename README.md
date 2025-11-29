# Fraud Sentinel Agent

**An Agentic AI Solution for Proactive Payment Security**

MumbaiHacks 2025 | FinTech Track  
Team Sometimes — Ashvatth Joshi & Jatin Vora

---

## Overview

Fraud Sentinel Agent is an autonomous AI system that proactively detects and prevents fraudulent transactions. It monitors real-time payment activity, analyzes SMS messages, URLs, QR codes, and transactions using a 5-layer Agentic AI architecture with Google Gemini AI integration.

---

## Problem Statement

India's digital payment ecosystem faces a surge in fraud with an 85% increase in UPI-related frauds in FY 2023–24 and over 22 lakh cybersecurity incidents reported in 2024. Existing systems are reactive—users lose funds first, then report later. Fraud Sentinel shifts from detection to prevention with real-time, self-learning protection.

---

## Architecture

### 5-Layer Agentic System

| Layer | Component    | Function                                     |
| ----- | ------------ | -------------------------------------------- |
| 1     | Agent Policy | Goal-driven decisions (PREVENT_FRAUD)        |
| 2     | Perception   | Data capturing (URLs, SMS, QR, Transactions) |
| 3     | Reasoning    | AI Brain (ML + NLP + Gemini AI)              |
| 4     | Action       | Autonomous control (ALLOW/WARN/BLOCK)        |
| 5     | Learning     | Feedback loop adaptation                     |

### Risk Classification

| Score | Level    | Action                |
| ----- | -------- | --------------------- |
| 0-39  | LOW      | Allow with monitoring |
| 40-69 | MEDIUM   | Show warning          |
| 70-99 | HIGH     | Block automatically   |
| 100+  | CRITICAL | Emergency block       |

---

## Tech Stack

| Component     | Technology                 |
| ------------- | -------------------------- |
| Mobile App    | Flutter + Dart             |
| Backend Logic | Python + FastAPI           |
| Auth Service  | Node.js + Express + Prisma |
| AI/ML         | Google Gemini Pro          |
| Database      | SQLite + PostgreSQL        |

---

## Features

- **SMS Fraud Detection:** Real-time monitoring, fake KYC scam detection, phishing link identification
- **URL Analysis:** Domain verification, SSL validation, typosquatting detection, redirect chain analysis
- **QR Code Scanning:** UPI intent parsing, malicious QR detection
- **Transaction Monitoring:** New payee detection, unusual amount flagging, behavioral analysis

---

## API Endpoints

| Endpoint               | Method | Description                     |
| ---------------------- | ------ | ------------------------------- |
| `/analyze/url`         | POST   | Analyze URL for phishing/fraud  |
| `/analyze/sms`         | POST   | Analyze SMS for scam indicators |
| `/analyze/transaction` | POST   | Analyze payment transaction     |
| `/analyze/qr`          | POST   | Analyze QR code content         |
| `/feedback`            | POST   | Submit user feedback            |
| `/report/fraud`        | POST   | Report confirmed fraud          |
| `/dashboard/stats`     | GET    | Get detection statistics        |

---

## Quick Start

**Prerequisites:** Python 3.9+, Node.js 18+, Flutter 3.0+

```bash
# Auth Service
cd backend/auth && npm install && npx prisma generate && node server.js

# Logic Service
cd backend/logic && pip install -r requirements.txt && python main.py

# Mobile App
cd frontend/app && flutter pub get && flutter run
```

**Environment Variables:**

Create `.env` files in `backend/logic/` and `backend/auth/` with API keys for Gemini AI and Google OAuth.

---

## Outcome

- Real-time fraud prevention with 5-layer agentic architecture
- Google Gemini AI-powered intelligent analysis
- Self-learning system that adapts from user feedback
- Cross-platform mobile app with SMS monitoring

---

**License:** MIT © 2025 Team Sometimes
