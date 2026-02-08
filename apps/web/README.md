# Credit Risk Platform - Web UI

Production Next.js web interface for the Credit Risk Modelling Platform.

## Live Deployment

**Production App:** [https://credit-risk-web-p24vtxpm5q-uc.a.run.app](https://credit-risk-web-p24vtxpm5q-uc.a.run.app)

Deployed on Google Cloud Run with automated CI/CD via GitHub Actions.

## Features

- **Model Training** - Configure and train credit risk models with custom hyperparameters
- **Predictions** - Submit loan applications and get default probability predictions
- **Model Comparison** - Compare performance metrics across multiple trained models
- **Interactive Charts** - ROC curves, confusion matrices, feature importance visualizations
- **Authentication** - Secure cookie-based authentication with API key verification

## Tech Stack

- **Framework:** Next.js 16.1.6 (App Router, TypeScript strict mode)
- **UI:** React 19, Tailwind CSS v4
- **Charts:** Recharts
- **Code Quality:** Biome (linting & formatting)
- **Deployment:** Google Cloud Run (Docker)

## Getting Started

### Prerequisites

- Node.js 20+
- npm

### Environment Variables

Create a `.env.local` file:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, set this to your deployed FastAPI backend URL.

### Development Server

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```text
app/
├── page.tsx           # Dashboard/home page
├── login/page.tsx     # Authentication
├── train/page.tsx     # Model training interface
├── predict/page.tsx   # Loan prediction interface
└── compare/page.tsx   # Model comparison

components/
├── charts/            # Visualization components
├── forms/             # Form components
├── layout/            # Header, nav, footer
└── ui/                # Base UI components

lib/
├── api-client.ts      # API integration
├── types.ts           # TypeScript interfaces
└── validation.ts      # Form validation
```

## API Integration

The web app connects to the FastAPI backend (`apps/api/`) for all data operations. See `lib/api-client.ts` for the API client implementation.

**Required Backend Endpoints:**

- `GET /health` - Health check
- `POST /auth/verify` - API key verification
- `POST /train` - Model training
- `POST /predict` - Predictions
- `GET /models` - List models
- `GET /models/{id}` - Model details
- `GET /models/{id}/results` - Training results
- `POST /models/{id}/persist` - Persist model

## Scripts

| Command | Description |
| ------- | ----------- |
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm start` | Start production server |
| `npm run lint` | Run Biome linter |
| `npm run format` | Format code with Biome |

## Deployment

See [ADR-011](../../docs/1-ADRs/ADR-011-nextjs-cloud-run.md) for deployment architecture details.

The app is automatically deployed to Google Cloud Run when changes are pushed to the `main` branch via the `.github/workflows/deploy-web-cloudrun.yml` workflow.
