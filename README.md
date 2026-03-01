# Hackathon 2024 - Cloud Cost Anomaly Detection

## Project Overview
This repository contains a hackathon prototype for detecting unusual cloud billing behavior and surfacing it in a web dashboard.

The current solution combines:
- A Next.js frontend dashboard (`SRC/user-interface`)
- A Node.js + Express API layer (`SRC/server`)
- Python preprocessing and anomaly scripts (`SRC/server`, `SRC/Data`, `SRC/Pate`)
- CSV-based runtime data storage (`SRC/server/runTimeData`)

The project focuses on three alert states:
- Fine
- Warning
- Alert

## Architecture At A Glance
High-level data flow:
1. Frontend requests service metadata and timeseries from the Node API.
2. Node API loads data from service-specific CSV files.
3. Python setup scripts split large billing data into per-service runtime files.
4. Anomaly outputs are read and merged with cost data for display.
5. Manual rule definitions can be saved and applied for manual anomaly events.

For deeper detail, see [ARCHITECTURE.md](./ARCHITECTURE.md).

## Repository Layout
- `SRC/user-interface`: Next.js frontend (dashboard, focused service view, settings, reports)
- `SRC/server`: Express backend and Python setup bridge
- `SRC/server/runTimeData`: Service-level runtime CSV data and anomaly artifacts
- `SRC/Data`: Data exploration and model experiments (Prophet, LSTM, preprocessing)
- `SRC/Pate`: PATE metric code and experiments
- `visualization` and `SRC/visualisation`: plotting scripts and generated images

## Quick Start
Full setup instructions: [SETUP.md](./SETUP.md)

Short version:
1. Start backend:
   - `cd SRC/server`
   - `npm install`
   - `node index.js`
2. Start frontend:
   - `cd SRC/user-interface`
   - `npm install`
   - `npm run dev`
3. Open `http://localhost:3000`

## Demo Screenshots
Dashboard outputs currently stored in the repository:

![Dashboard Output 1](<SRC/visualisation/ChatGPT outputs/output.png>)

![Dashboard Output 2](<SRC/visualisation/ChatGPT outputs/output(1).png>)

## Documentation
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [SETUP.md](./SETUP.md)
- [DATASET.md](./DATASET.md)
- [CONTRIBUTING.md](./CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)
- [REPO_HYGIENE.md](./REPO_HYGIENE.md)

## Status
This repository reflects a hackathon development snapshot. It includes working prototype components plus research and experimental artifacts.
