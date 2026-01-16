# CostIQ MVP Implementation Plan

This document outlines the technical and product implementation plan for the CostIQ MVP, a B2B SaaS helping mid-size hospitals identify actionable operational savings.

## 1. System Architecture & Folder Structure

We will use a **Monorepo** structure to keep frontend and backend tightly coupled for the MVP.

### Folder Structure
```
costiq/
├── docs/                       # Documentation
├── backend/                    # Python + FastAPI
│   ├── app/
│   │   ├── api/                # API Route handlers
│   │   │   ├── v1/             # Versioning
│   │   │   │   ├── auth.py
│   │   │   │   ├── uploads.py
│   │   │   │   ├── processing.py
│   │   │   │   └── dashboard.py
│   │   ├── core/               # Config, Security, DB connections
│   │   ├── models/             # SQLAlchemy / Pydantic models
│   │   ├── services/           # Business logic
│   │   │   ├── normalization.py
│   │   │   ├── rules_engine/   # The core logic modules
│   │   │   │   ├── procurement.py
│   │   │   │   ├── inventory.py
│   │   │   │   ├── labor.py
│   │   │   │   └── __init__.py
│   │   │   └── pdf_generator.py # Report generation
│   │   └── main.py             # Entry point
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # React + Next.js
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Routes
│   │   ├── services/           # API methods
│   │   ├── context/            # State management
│   │   └── styles/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml          # For local dev orchestration
└── README.md
```

## 2. API Design (FastAPI)

### Authentication (`/api/v1/auth`)
- `POST /login`: Email/Password login. Returns JWT.
- `POST /register`: (Internal/Admin only for MVP) Create hospital tenant.

### File Ingestion (`/api/v1/uploads`)
- `POST /upload`: Multipart form data upload for CSVs.
  - Type param: `po`, `invoice`, `inventory`, `equipment`, `labor`.
  - Performs validation (schema check).
- `GET /history`: List previous uploads and their status.

### Processing & Analysis (`/api/v1/analyze`)
- `POST /run`: Trigger the rule engine on latest data.
- `GET /status/{job_id}`: Check progress of analysis.

### Dashboard & Reporting (`/api/v1/dashboard`)
- `GET /summary`: High-level stats (Total Spend Analyzed, Identified Savings, Top Categories).
- `GET /findings`: Detailed list of cost leakage findings.
- `GET /report/pdf`: Generate and download the Cost Optimization Diagnostic PDF.

## 3. Data Models

We will use a relational database (PostgreSQL is recommended, SQLite for dev).

**Organization (Hospital)**
- `id`, `name`, `settings` (JSON)

**User**
- `id`, `email`, `hashed_password`, `role`, `org_id`

**UploadBatch**
- `id`, `org_id`, `filename`, `file_type` (Enum), `status`, `upload_date`

**ProcurementData** (Raw/Normalized)
- `id`, `batch_id`, `vendor_name`, `item_sku`, `item_description`, `unit_price`, `quantity`, `po_date`, `contract_price_ref`

**InventoryData**
- `id`, `batch_id`, `sku`, `location`, `quantity_on_hand`, `expiry_date`, `last_usage_date`

**LaborData**
- `id`, `batch_id`, `department`, `shift_date`, `staff_id`, `hours_worked`, `overtime_hours`, `patient_volume_metric`

**Finding** (The Output)
- `id`, `org_id`, `batch_id`
- `category` (e.g., "Price Variance")
- `severity` (High, Medium, Low)
- `description` (e.g., "Vendor X charged 15% above contract")
- `potential_savings` (Decimal)
- `status` (Open, Reviewed, Ignored)

## 4. Rule Logic (Plain English)

These rules run against the normalized data to generate `Findings`.

### 1. Vendor Price Variance
*Logic*: Group purchases by SKU. Calculate the mean unit price. Flag any Invoice where `unit_price` > `mean_price` + threshold (e.g., 10%) OR `unit_price` > `contract_price` (if available).
*Insight*: "You paid $50 for Syringe X in Dept A but $40 in Dept B."

### 2. Contract vs. Invoice Mismatch
*Logic*: Join Invoice items with Contract Pricing table on SKU. Flag where Invoice `unit_price` > Contract `agreed_price`.
*Insight*: "Vendor charged $120, contract rate is $100. Overcharge."

### 3. Emergency Procurement Premium
*Logic*: Flag POs marked as "Rush" or "Emergency" or those created < 24 hours before delivery. Compare price vs. standard POs for same item.
*Insight*: "Rush shipping added 20% cost to this order."

### 4. Overstocking & Expiry Risk
*Logic*: Calculate `days_on_hand` = `quantity_on_hand` / `daily_usage_rate`.
- If `days_on_hand` > 90 (configurable), flag as Overstock.
- If `expiry_date` - `today` < 30 days and `quantity` > `projected_usage`, flag as Expiry Risk.
*Insight*: "$5k worth of reagents expiring in 2 weeks."

### 5. Equipment Underutilization
*Logic*: Compare `equipment_active_hours` vs `department_operating_hours`. If usage < 20% (configurable), flag.
*Insight*: "MRI Machine #2 used only 15% of the time."

### 6. Overtime vs. Patient Volume Mismatch
*Logic*: Correlate `overtime_hours` with `patient_census` per day/shift. If overtime is High but patient volume is Low/Normal, flag anomaly.
*Insight*: "High overtime spend on Tuesday despite low patient census."

## 5. MVP Milestones (Day 1–30)

### Week 1: Foundation & Ingestion
- [ ] Set up Repo, FastAPI, Next.js, and DB.
- [ ] Implement Basic Auth.
- [ ] Build CSV Upload API & Frontend Component.
- [ ] Implement Data Normalization (standardizing column names from CSVs).

### Week 2: Core Logic Implementation
- [ ] Implement Rule 1 & 2 (Price Variance & Contract Mismatch).
- [ ] Implement Rule 4 (Overstocking).
- [ ] Create `Findings` database table to store results.
- [ ] Basic "Run Analysis" button on Frontend.

### Week 3: Advanced Rules & Dashboard
- [ ] Implement Rules 3, 5, & 6.
- [ ] Build Dashboard UI (Cards for Total Savings, Charts for Category breakdown).
- [ ] Display list of Findings in a table.

### Week 4: Reporting & Polish
- [ ] Implement PDF Generator (using libraries like `ReportLab` or `WeasyPrint`).
- [ ] Generate "Cost Optimization Diagnostic" document from `Findings`.
- [ ] Final UI Polish (CSS, Loading states).
- [ ] End-to-end testing with sample datasets.
