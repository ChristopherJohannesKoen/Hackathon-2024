# Architecture

## System Components
The project is built from four primary layers:

1. Frontend (`apps/web`)
   - Next.js app used for dashboard, focused service view, reports, and settings.
   - Calls backend endpoints on `http://localhost:3001`.

2. Node API (`apps/server/index.js`)
   - Express server exposing endpoints for:
     - service lookup
     - chart data retrieval
     - anomaly data retrieval
     - manual rule management
   - Reads CSV and JSON artifacts from `apps/server/runTimeData`.

3. Python pipelines (`apps/server/setup.py` and scripts under `SRC/Data`, `SRC/Pate`)
   - `setup.py` splits `bigData.csv` into per-service files in `runTimeData`.
   - Additional scripts perform anomaly experiments, forecasting, and metric evaluation.

4. Runtime CSV and JSON store (`apps/server/runTimeData`)
   - Service-specific folders hold:
     - `data.csv` (base timeseries)
     - `pateStandard...ProcessedData.csv` (anomaly outputs)
     - `man_anom.json` (manual anomalies when present)

## Requested Data Flow
Flow requested: frontend -> Node API -> Python pipelines -> runtime CSV

1. Frontend starts and requests services from:
   - `GET /getServices`

2. Node API returns ID-to-service mappings loaded during startup.

3. On startup, Node API runs:
   - `python setup.py`
   This Python step prepares per-service CSV files from `bigData.csv`.

4. Prepared files are stored in:
   - `apps/server/runTimeData/<Service Name>/data.csv`

5. Frontend requests chart data:
   - `POST /getData` or `POST /getDataVariableTime`
   Node API reads runtime CSV files and returns filtered/merged points.

6. Frontend requests anomaly overlays:
   - `POST /getAnonVariableTime` (model anomalies)
   - `POST /getManaulAnonVariableTime` (manual anomalies)

7. Manual rule configuration:
   - `POST /getRules`
   - `POST /saveRules`
   Rules are persisted to `apps/server/rules.json`.

## API Surface (Current)
- `GET /getServices`
- `GET /getFlags`
- `POST /getData`
- `POST /getDataVariableTime`
- `POST /getAnonVariableTime`
- `POST /getManaulAnonVariableTime`
- `POST /getServiceName`
- `POST /getRules`
- `POST /saveRules`

## Runtime Artifacts
Generated and updated artifacts in backend scope:
- `apps/server/ids.json`
- `apps/server/services.json`
- `apps/server/rules.json`
- `apps/server/runTimeData/<Service>/data.csv`
- `apps/server/runTimeData/<Service>/man_anom.json` (if manual rules are used)

## Notes
- Data exchange format is primarily JSON over HTTP and CSV on disk.
- This architecture favors hackathon speed and inspectability over strict service boundaries.
