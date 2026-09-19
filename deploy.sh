#!/usr/bin/env bash
set -e
# Initialize git if needed
if [ ! -d ".git" ]; then
  git init
fi
# Add all files and commit
git add .
git commit -m "Deploy Paladin with UI improvements" || true
# Set remote (replace with your fork if desired)
git remote remove origin || true
git remote add origin https://github.com/patelrushi2307-cmd/Paladin.git
# Push to GitHub
git push -u origin main --force
# Install Vercel CLI if not present
if ! command -v vercel >/dev/null 2>&1; then
  npm i -g vercel
fi
# Deploy to Vercel (ensure VERCEL_TOKEN env var is set)
vercel --prod
