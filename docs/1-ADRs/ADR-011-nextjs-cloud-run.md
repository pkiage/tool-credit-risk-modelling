# ADR-011: Next.js Deployment on Cloud Run

| Field | Value |
|-------|-------|
| Status | Proposed |
| Author | Paul / Claude |
| Date | 2026-02-07 |

## Context

The Next.js frontend (`apps/web/`) is the only app in the monorepo without automated deployment. The FastAPI backend deploys to Cloud Run (ADR-009), and the Gradio demo deploys to HF Spaces. The web app needs a hosting platform that:

- Supports server-side middleware (cookie-based auth in `middleware.ts`)
- Fits within free tier for a demo/portfolio project
- Integrates with the existing GitHub Actions CI/CD pipeline
- Requires minimal new infrastructure

## Decision

Deploy the Next.js app to **Google Cloud Run** using a multi-stage Docker build and a GitHub Actions workflow that mirrors the existing API deployment.

### Infrastructure

| Setting | Value | Rationale |
|---------|-------|-----------|
| Memory | 512 Mi | Lighter than API (no sklearn/pandas) |
| CPU | 1 | Sufficient for SSR + middleware |
| Timeout | 60 s | No long-running operations |
| Min instances | 0 | Scale to zero (free tier) |
| Max instances | 2 | Cap runaway scaling |
| Port | 3000 | Next.js default |
| Auth | `--allow-unauthenticated` | App-level auth via cookies |

### Build Strategy

Multi-stage Docker build with `output: 'standalone'` in `next.config.ts`:

1. **deps** — `npm ci` installs node_modules (cached layer)
2. **builder** — `npm run build` with `NEXT_PUBLIC_API_URL` build arg
3. **runner** — Copies standalone `server.js` + static assets, runs as non-root `nextjs` user

Build context is `apps/web/` (not repo root), unlike the API Dockerfile which needs `shared/` and `data/`.

### Environment Variables

| Variable | Source | Injection |
|----------|--------|-----------|
| `NEXT_PUBLIC_API_URL` | `secrets.CREDIT_RISK_API_URL` | Docker build arg (inlined at build time) |

No new GitHub secrets required — reuses `GCP_SA_KEY`, `GCP_PROJECT_ID`, `GCP_REGION`, and `CREDIT_RISK_API_URL` from the API deployment.

### Free Tier Budget

| Resource | Free Tier Allowance | Expected Usage |
|----------|---------------------|----------------|
| Cloud Run requests | 2M / month | < 1K / month |
| Cloud Run vCPU | 180,000 s / month | < 200 s / month |
| Cloud Run memory | 360,000 GiB-s / month | < 500 GiB-s / month |
| Artifact Registry | 500 MB | ~200 MB (1 image) |

Combined with the API service, total usage remains well within free tier.

## Alternatives Considered

- **Vercel** — Zero-config for Next.js, free preview deploys, no cold starts. However, Hobby plan is non-commercial only, and using Cloud Run keeps all infrastructure on a single platform (GCP). Vercel remains a viable fallback if cold starts become problematic.
- **Cloudflare Pages** — Generous free tier but requires OpenNext adapter, 3 MB Worker size limit on free plan likely too small for Next.js + Recharts bundle.
- **Netlify** — Good Next.js support via OpenNext adapter, but 300 build-minutes/month cap and credit-based pricing for new accounts add uncertainty.

## Consequences

- Cold starts of ~2-4 s when the container scales from zero (lighter than the API's ~5-10 s since there is no ML model loading)
- `NEXT_PUBLIC_API_URL` is baked into the client bundle at build time; changing the API URL requires a redeploy of the web image
- The web and API services are independently deployable — changes to `apps/web/` do not trigger an API redeploy, and vice versa
- Future upgrade path: add `--min-instances=1` to eliminate cold starts (exits free tier, ~$5-10/mo for a lightweight Node.js container)
