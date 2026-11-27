# SIKE FORENSICS

SIKE FORENSICS is an evidence-first web workspace for investigating images, video and audio. It combines deterministic file identity, metadata/provenance inspection, classical forensic signals, optional licensed AI detectors, normalized evidence fusion and reproducible case reports.

## Current capabilities

- Image, video and audio intake with a 250 MB upload guard.
- File validation before analysis.
- SHA-256 evidence identity and deterministic case ID.
- Image dimensions, format, EXIF and pixel statistics.
- JPEG/WEBP ELA, noise residual, DCT/frequency, bit-plane and copy-move candidate signals.
- C2PA/content-credential marker inspection.
- Video container metadata and audio metadata.
- Detector registry with commercial-license gating.
- Optional ForensiX runtime adapter; no third-party detector code is copied into the core.
- Explicit detector status: disabled, planned or available. No fabricated AI scores.
- Multi-signal evidence fusion with uncertainty bands.
- Persistent JSON case records.
- HTML case reports.
- Downloadable evidence package containing the case record and package instructions.
- Metadata-cleaning endpoint that produces a derivative and reports original/cleaned hashes.
- Structured removal-request workflow.
- Responsive light investigation dashboard with tabs for Overview, Metadata, Provenance, AI Detection, Pixel Forensics, Video, Audio, Evidence, Reports, Evidence Package, Cleaning and Removal Request.
- API and unit-test foundation.

## Important forensic rule

A detector score, ELA result, metadata field or C2PA marker is an indicator, not automatically proof of authenticity or manipulation. SIKE FORENSICS therefore keeps raw signals, sources, reliability and limitations visible and uses an explicit INCONCLUSIVE state.

## Architecture

```
frontend/                 Next.js investigation UI
backend/app/main.py      FastAPI API
backend/app/services/    validation, analysis, provenance, evidence, reports, cleaning
backend/config/          model/license registry
backend/tests/            automated tests
docs/                     setup and licensing documentation
```

The expensive AI layer is intentionally adapter-based. Production model weights must be separately verified for commercial use before enabling them.

## Run locally

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

Open the frontend shown by Next.js.

## Optional ForensiX runtime

The adapter is disabled by default. Enable only after installing a compatible, commercially permitted runtime and checking every model/weight license:

```bash
SIKE_ENABLE_FORENSIX=1
```

Do not enable a model merely because its repository contains the model. Check code, weight, dataset and usage restrictions in `docs/UPSTREAM_COMPONENTS.md` and `backend/config/models.json`.

## API

- `GET /health`
- `POST /api/v1/analyze`
- `GET /api/v1/cases/{case_id}`
- `GET /api/v1/cases/{case_id}/report.html`
- `GET /api/v1/cases/{case_id}/package`
- `POST /api/v1/report`
- `POST /api/v1/clean`
- `POST /api/v1/removal-request`

## Testing

From `backend/`:

```bash
pytest
```

Before production, add GPU-model integration tests, corpus-level calibration tests, adversarial tests, queue tests and retention/security tests.

## Licensing

The SIKE orchestration code is separate from third-party model code and weights. See `THIRD_PARTY_NOTICES.md`, `docs/UPSTREAM_COMPONENTS.md` and `docs/MODEL_REGISTRY.md`.

Current commercial build policy: do not ship components marked non-commercial or whose model/weight terms have not been independently verified.
