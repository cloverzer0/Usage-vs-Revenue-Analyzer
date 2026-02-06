# Usage vs Revenue Analyzer - Frontend

Modern Next.js 14 frontend for the Usage vs Revenue Analyzer dashboard.

## Tech Stack

- **Next.js 14** - Full-stack React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Beautiful, accessible component library
- **Radix UI** - Headless UI primitives
- **Recharts** - Interactive data visualizations
- **date-fns** - Date formatting utilities

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Backend API running on `http://localhost:8000`

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Dashboard page
│   └── globals.css         # Global styles
├── components/
│   ├── ui/                 # shadcn/ui components
│   ├── summary-cards.tsx   # Metric summary cards
│   ├── time-series-chart.tsx
│   ├── feature-metrics-table.tsx
│   └── date-range-picker.tsx
├── lib/
│   ├── api.ts              # API client functions
│   ├── types.ts            # TypeScript interfaces
│   ├── format.ts           # Formatting utilities
│   └── utils.ts            # General utilities
└── public/                 # Static assets
```

## Features

- **Real-time Data Fetching** - Connects to FastAPI backend
- **Interactive Charts** - Time-series visualization with Recharts
- **Date Range Filtering** - Custom date range selection
- **Responsive Design** - Mobile-friendly layout
- **Type Safety** - Full TypeScript coverage
- **Accessible UI** - WCAG compliant components

## API Integration

The frontend connects to the FastAPI backend at:

- `GET /api/health` - Health check
- `GET /api/dashboard` - Dashboard data
- `GET /api/features` - Feature metrics
- `GET /api/timeseries` - Time-series data

## Building for Production

```bash
npm run build
npm start
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

