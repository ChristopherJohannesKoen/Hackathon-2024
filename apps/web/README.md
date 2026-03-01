# User Interface

## Overview
This folder contains the Next.js frontend for the Cloud Cost Anomaly Detection dashboard.

## Run Locally
```bash
npm install
npm run dev
```

Default URL:
- `http://localhost:3000`

## Backend Dependency
The app expects the API server to run at:
- `http://localhost:3001`

Primary routes:
- `/` dashboard
- `/focus/[id]` service focus view
- `/reports` reports table
- `/globalsettings` manual rule settings
