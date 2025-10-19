# 🧠 Fraud Sentinel Agent  
### An Agentic AI & Blockchain Solution for Proactive Payment Security  
**Event:** MumbaiHacks 2025 | FinTech Track  
**Team:** Sometimes  
**Built by:** Ashvatth Joshi & Jatin Vora  

---

## 🚨 Overview

**Fraud Sentinel Agent** is an **autonomous AI system** that proactively detects and prevents fraudulent transactions.  
It monitors real-time payment activity, analyzes risk patterns, and pauses suspicious payments before they complete — combining **Agentic AI** with **Blockchain verification** for trust and transparency.

---

## ⚠️ The Problem

India’s digital payment ecosystem faces a surge in fraud:
- 💸 **85% increase** in UPI-related frauds in FY 2023–24.  
- 🔐 **22 lakh+ cybersecurity incidents** reported in 2024.  
- ⚠️ Existing systems are **reactive** — users lose funds first, then report later.  

Fraud Sentinel aims to **shift from detection to prevention**, providing real-time, self-learning protection.

---

## 💡 The Solution

Fraud Sentinel acts as an **autonomous guardian** that continuously observes transactions and makes intelligent decisions on the fly.

### 🔁 Agentic Loop
1. **Perceive:** Monitors live payment channels (UPI/API/webhooks).  
2. **Reason:** Generates a real-time **risk score** using behavioral data.  
3. **Act:** Automatically **pauses** high-risk transactions and alerts the user.  
4. **Learn:** Adapts based on user feedback (“Approve” / “Block”).  

Result: a proactive, self-improving fraud prevention layer.

---

## 🔐 The Core Innovation — Agentic AI × Blockchain

### 🧠 Agentic AI (Decision Layer)
- Runs on **Supabase Edge Functions** (Node.js / Deno).  
- Executes real-time logic at the edge for instant decision-making.  
- Operates autonomously — no central dependency or human delay.

### ⛓️ Blockchain (Trust Layer)
- Uses **Ethers.js** and **Ethereum (Sepolia Testnet)**.  
- Records verified fraud events immutably on-chain.  
- Forms a **Decentralized Fraud Intelligence Network (DFIN)** for shared, tamper-proof fraud data.

Together, these create a transparent, verifiable defense system for digital payments.

---

## ⚙️ Tech Stack

| Layer | Technology | Purpose |
|--------|-------------|----------|
| **Frontend** | React.js + TypeScript + TailwindCSS + Zustand | Real-time dashboard & alerts |
| **Backend** | NestJS (Node.js) + Express | API orchestration & logic |
| **Database & Auth** | Supabase (PostgreSQL + Auth) | User accounts & fraud logs |
| **Agentic Core** | Supabase Edge Functions (Node.js/Deno) | Fraud detection engine |
| **Blockchain Layer** | Ethers.js + Solidity (Sepolia) | Immutable fraud registry |
| **DevOps / Infra** | Docker + Docker Compose | Containerized deployment |
| **Cloud & Monitoring** | AWS (S3, Lambda planned), Prometheus + Grafana (future) | Scalability & observability |
| **Automation / Alerts** | WebSockets + Resend (Email) | Real-time notifications |
| **AI/ML Extension (Planned)** | Python + Flask | Anomaly-based learning |

---

## 🚀 Hackathon MVP Goals

1. **User Onboarding:** Secure auth via Supabase.  
2. **Transaction Simulation:** Dashboard for mock payments.  
3. **Live Agent:** Edge Function running real-time risk analysis.  
4. **Alerts:** Instant “paused transaction” notifications.  
5. **On-Chain Proof:** Log confirmed frauds to Sepolia testnet.  

---

## 🧩 Architecture Overview

User (Frontend)
↓
Supabase Edge Function (Agent)
↓
Risk Evaluation → Pause/Approve
↓
Blockchain (Ethers.js + Ethereum)
↓
Immutable Fraud Record


---

## 📈 Future Scope

- Integrate ML models for adaptive risk prediction.  
- Expand DFIN for multi-bank participation.  
- Add mobile (Flutter) app support.  
- Multi-chain compatibility (Polygon, Base, Solana).  

---

## 🏁 Outcome

✅ Real-time fraud prevention  
✅ Blockchain-verified intelligence  
✅ Serverless, scalable infrastructure  
✅ End-to-end working MVP  

> **From detection to prevention — Fraud Sentinel makes digital payments truly secure.**

---

**License:** MIT © 2025 Team Sometimes
