# SIKE FORENSICS setup and production checklist

## Local development
1. Start FastAPI on port 8000.
2. Start Next.js with `NEXT_PUBLIC_API_URL=http://localhost:8000`.
3. Upload a small valid image first.
4. Confirm the case ID equals the first 12 characters of the SHA-256.
5. Open the report and evidence package.
6. Run `pytest`.

## Production checklist
- Put the API behind TLS and an authenticated gateway.
- Restrict CORS to the deployed frontend origin.
- Add per-user/tenant authorization before exposing case IDs.
- Store case records in a database/object store with explicit retention.
- Never expose local filesystem paths to clients.
- Add antivirus/content scanning and decompression/resource limits.
- Add rate limits and request size limits at the edge.
- Run AI inference in isolated workers with CPU/GPU resource limits.
- Pin model versions and store checksums.
- Log model ID, version, configuration and analysis timestamp with every inference.
- Calibrate detector thresholds on a representative corpus.
- Keep an inconclusive band; do not force binary decisions.
- Preserve the original evidence hash even when creating cleaned derivatives.
- Review every third-party model and weight license before commercial deployment.
