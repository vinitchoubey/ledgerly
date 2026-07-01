# Ledgerly — AI-Powered Expense Tracker

A full-stack personal finance app that uses AI to scan receipts and track spending.

## Features
- Upload a receipt image — AI extracts all line items automatically
- Manual expense entry with date and category
- Per-user accounts with secure login/signup
- Monthly spending dashboard with 12-month history
- AI-optimized daily budget limit based on remaining balance

## Tech Stack
- **Frontend**: React, Vite
- **Backend**: FastAPI, Python
- **Database**: SQLite (SQLAlchemy ORM)
- **AI**: Groq LLaMA 4 Scout vision model
- **Auth**: JWT tokens, bcrypt password hashing
- **Optimization**: Google OR-Tools GLOP linear solver
- **Deployment**: Docker

## Running Locally

### Prerequisites
- Docker Desktop
- A Groq API key from [console.groq.com](https://console.groq.com)

### Setup
1. Clone the repo: