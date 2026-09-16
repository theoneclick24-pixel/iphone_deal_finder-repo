# iPhone Deal Finder — Master Architectural Specification & Agent Guidelines (AGENTS.md)

## 1. Executive Summary & Vision
iPhone Deal Finder is a multi-tenant SaaS platform that empowers electronics buyers and deal-hunters to identify, evaluate, and capitalize on profitable used iPhone listings in their operational market.

### Core Business Unit Economics & Criteria
- **Target Purchase Range:** $100 – $250 per device (Configurable per user).
- **Target Resale Timeframe:** Fast turnover (1 to 2 weeks).
- **Target Minimum Profit:** $30 minimum profit margin per device (Configurable per user; Ideal: $40 – $50+).
- **Usability Priorities:**
  1. **Functional:** Real-time accuracy in market reference data and valuation formulas.
  2. **Practical:** Faster and easier to use than manual spreadsheet/browsing analysis.
  3. **UI/UX Friendly:** Clean dashboard with actionable opportunity alerts, profit calculations, and clear explanation codes.

---

## 2. Core Business Logic & Mandatory Domain Rules

### Operational Market vs. Reference Market (CRITICAL SEPARATION)
- **Operational Market:** The specific city/market where the user buys and flips devices (e.g., Maturín, Monagas).
  - Listings from the operational market are candidates to become **Operational Opportunities**.
- **Reference Market:** Price observations from other cities (e.g., Caracas, Valencia) or external platforms (e.g., Amazon Refurbished).
  - Used *exclusively* for computing market statistics (averages, medians, P25, P75) and measuring local market speculation.
  - **MANDATORY RULE:** Never classify a listing from a non-operational city as an operational buying opportunity, regardless of how attractive the price appears.

### Strict Data Integrity & No Fake Inferences
- **NEVER invent or guess attributes:** If color, storage, battery %, screen condition, or defects are not explicitly present in raw data, they MUST be recorded as `NULL` / `Unspecified`. Never hardcode arbitrary defaults.
- **NO fake profit or offset calculations:** Valuation and profit margin calculations MUST be backed by real reference evidence (Amazon Used Reference Price, Regional Medians), NOT arbitrary offsets (e.g. `price + 60`).

---

## 3. Mandatory Layered Architecture Specification

```text
                         ┌──────────────────────┐
                         │       CLIENTES       │
                         │ Web / futuro móvil   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    PRESENTATION      │
                         │ Dashboard / UI       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     APPLICATION      │
                         │ Use Cases / API      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       DOMAIN         │
                         │ Reglas de negocio    │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       DATA INGESTION          MARKET DATA          USER DATA
       / ADAPTERS              / ANALYTICS           / AUTH
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │   INFRASTRUCTURE     │
                         │ PostgreSQL / Redis   │
                         │ Storage / Jobs       │
                         └──────────────────────┘
```

### Layer Responsibilities
1. **Presentation Layer (`apps.presentation` / Templates):** Render UI, receive user clicks. Must NEVER calculate medians, profit, or condition adjustments.
2. **Application Layer (`apps.application`):** Use cases (e.g., `AnalyzeListing`, `CalculateMarketReference`, `DetectOpportunity`). Coordinates workflows without hardcoding business rules in UI or API.
3. **Domain Layer (`apps.domain`):** Pure business logic (Model, Storage, Color, Condition, Fair Valuation, Opportunity Detection). Knows NOTHING about Facebook, WhatsApp, or HTML.
4. **Data Ingestion / Adapters (`apps.adapters`):** Source adapters (Facebook, WhatsApp, Amazon, Manual). Converts source-specific raw data into canonical `NormalizedListing`.
5. **Normalization Layer (`apps.normalization`):** Transforms raw titles and descriptions into standardized canonical domain objects.
6. **Market Data Layer (`apps.market`):** Stores and calculates market observations, medians, P25, P75, and Amazon reference benchmarks. Does NOT decide what to buy.
7. **Valuation Layer (`apps.valuation`):** Calculates condition deductions and fair estimated resale value based on market reference evidence.
8. **Opportunity Engine (`apps.opportunities`):** Evaluates if a listing meets user-specific operational city, budget range, and profit margin target.
9. **User / Auth Layer (`apps.accounts`):** Manages user accounts, operational market setting, budget limits, and target profit margins.
10. **Infrastructure Layer (`config`, Docker, PostgreSQL):** Database persistence, background jobs, external API clients.

---

## 4. Architectural Rules for Agents

```markdown
## Architectural Separation Rules
1. The system MUST be modular. Each module has ONE clear responsibility.
2. Source-specific logic must stay inside source adapters (`apps/adapters/`).
3. Business rules must NOT depend on a specific data source.
4. Presentation logic (templates/views) must NOT contain business rules or financial calculations.
5. Market reference data must remain strictly separate from operational user opportunities.
6. Valuation logic must remain separate from opportunity detection logic.
7. Authentication and user configuration must remain separate from market analysis.
8. Data attributes (color, storage, defects) must NEVER be invented; missing attributes remain NULL.
9. New data sources must be added through Adapters producing canonical `NormalizedListing` objects.
```

---

## 5. Development Roadmap

- **Phase 0:** Specification & Git Setup (Completed).
- **Phase 1:** Data Normalization & Adapter Prototype (Completed & Refined).
- **Phase 2:** Containerized Environment (Docker + PostgreSQL + Django).
- **Phase 3:** User Accounts & Operational Settings (Completed).
- **Phase 4:** Product Catalog Domain (Completed).
- **Phase 5:** Data Ingestion Adapters & Condition Engine (Refined to Layered Architecture).
- **Phase 6:** Market Reference & Amazon Speculation Engine (Evidence-based).
- **Phase 7:** Valuation Engine & Opportunity Engine (Clean Domain/Application Layer).
- **Phase 8:** Presentation Layer / User Dashboard (Decoupled from business logic).
- **Phase 9:** Multi-Source Adapter Expansion (WhatsApp, Amazon Refurbished API/Scraper).
- **Phase 10:** CRM & Seller Negotiation Helper.
- **Phase 11:** Production Cloud Deployment & SaaS Subscription Billing.
