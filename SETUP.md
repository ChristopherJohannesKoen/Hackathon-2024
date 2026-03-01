# Setup Guide

## Prerequisites
- Node.js 18+ and npm
- Python 3.9+ (recommended)
- Git

## Required Data Files
The backend expects:
- `SRC/server/bigData.csv`

This file is used by `SRC/server/setup.py` to generate per-service runtime data in:
- `SRC/server/runTimeData`

## Windows Setup

### 1. Backend (Node API + Python prep)
```powershell
cd SRC\server
npm install
python -m pip install pandas
node index.js
```

Notes:
- On startup, `index.js` runs `python setup.py`.
- Keep this process running on `http://localhost:3001`.

### 2. Frontend (Next.js)
Open a second terminal:

```powershell
cd SRC\user-interface
npm install
npm run dev
```

Open:
- `http://localhost:3000`

## Linux/macOS Setup

### 1. Backend
```bash
cd SRC/server
npm install
python3 -m pip install pandas
node index.js
```

### 2. Frontend
In a second terminal:

```bash
cd SRC/user-interface
npm install
npm run dev
```

Open:
- `http://localhost:3000`

## Common Commands

Frontend:
```bash
cd SRC/user-interface
npm run dev
npm run build
npm run start
```

Backend:
```bash
cd SRC/server
node index.js
```

## Troubleshooting
- If frontend cannot fetch data, verify backend is running on port `3001`.
- If backend startup fails, confirm `bigData.csv` exists in `SRC/server`.
- If Python command fails, install dependencies and verify `python`/`python3` is on PATH.
- If cross-origin errors appear, verify frontend is served from `http://localhost:3000`.
