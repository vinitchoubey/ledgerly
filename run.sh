#!/bin/bash

echo "Starting Ledgerly Deployment..."
set -e

if [ ! -f backend/.env ]; then
  echo "Missing backend/.env file."
  echo "Copy backend/.env.example to backend/.env and fill in your real values."
  exit 1
fi

echo "Cleaning up old containers..."
docker rm -f sb-backend sb-frontend 2>/dev/null || true

echo "Building Backend Container..."
cd backend
docker build -t smartbudget-backend .
docker run -d --name sb-backend -p 8000:8000 --env-file .env -v "$(pwd)/data:/app/data" smartbudget-backend
cd ..

echo "Building Frontend Container..."
cd frontend
docker build -t smartbudget-frontend .
docker run -d --name sb-frontend -p 5173:5173 smartbudget-frontend
cd ..

echo "Deployment Complete!"
echo "Backend running at: http://localhost:8000"
echo "Frontend running at: http://localhost:5173"