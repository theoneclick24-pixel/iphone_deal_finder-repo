# iPhone Deal Finder — Project Context for Antigravity

## 1. What we are building

We are building a web-based tool that helps a user identify potentially profitable used-iPhone buying opportunities in their local market.

The initial use case is a buyer who wants to:
- find used iPhones within a configurable budget,
- understand the local buying market,
- compare local listings against broader market reference data,
- account for device condition,
- estimate potential resale value and margin,
- and quickly identify listings worth investigating or negotiating.

The product is intended to evolve from a personal MVP into a cloud-hosted, multi-user SaaS that could eventually charge a monthly subscription.

The application therefore must be designed from the beginning so it can later support:
- multiple users,
- user-specific settings and data isolation,
- shared/reference market data,
- multiple acquisition pipelines,
- cloud deployment,
- usage limits and subscriptions.

Do not build a disposable personal script that would require a rewrite to become a SaaS.

---

## 2. Core business logic

The product distinguishes two concepts that must never be conflated:

### Operational market

The operational market is the city/market where the user actually buys.

Example:
- User's operational market: Maturín, Monagas
- A Facebook Marketplace listing in Maturín: can be an operational buying candidate
- A listing in Caracas: reference data only, unless explicitly configured otherwise

Listings from other cities must NOT automatically become buying opportunities just because they appear cheaper.

### Reference market

Reference data exists to estimate what a product may be worth.

It may include:
- the user's operational city,
- other cities,
- historical observations,
- Amazon or other reference sources.

Reference information and operational buying candidates must remain conceptually separate throughout the system.

### Product identity

Analysis must distinguish at minimum:
- exact iPhone model,
- storage capacity,
- color when available,
- condition.

Different storage capacities must never be silently combined into one market statistic.

### Condition

Condition can materially affect value. Relevant attributes may include:
- battery health,
- screen condition,
- body/scratches,
- Face ID,
- camera,
- other documented defects.

Condition adjustments must eventually be configurable and evidence-based. Do not invent arbitrary dollar deductions just to make a demo look convincing.

---

## 3. Real-world buying workflow to support

The user's real process is approximately:

1. Open Facebook Marketplace in the user's local city.
2. Search for iPhones.
3. Inspect different listings and conditions.
4. Compare prices.
5. Shortlist the best candidates.
6. Negotiate with sellers later through a separate CRM/messaging workflow.

The negotiation/CRM portion is explicitly out of scope for the first MVP.

The MVP should focus on the discovery and valuation side of the workflow.

---

## 4. SaaS direction

This must become a multi-user SaaS in the future.

### User-owned data

Examples:
- account,
- settings,
- operational market,
- saved listings,
- opportunities,
- notes,
- preferences.

User-owned data must be isolated between users.

### Shared/reference data

Examples:
- product catalog,
- locations,
- normalized product information,
- market reference observations/statistics,
- approved source metadata.

Shared/reference data may be reused across users where appropriate.

Do not unnecessarily duplicate shared reference information for every user.

### Authentication

Authentication belongs in the MVP. We do not need social login or payment integration yet, but the user/account foundation must be sound.

Do not hardcode one user's city, budget, or preferences into business logic.

---

## 5. Planned technology direction

The intended application stack is:

- Backend: Django
- Database: PostgreSQL
- MVP frontend: Django Templates + Bootstrap
- Development environment: Docker + Python virtual environment
- Version control: Git/GitHub

The preferred architecture is a modular Django monolith, not a microservice architecture.

Do not introduce Next.js, Redis, Celery, Kubernetes, API gateways, or other infrastructure unless a concrete requirement is demonstrated.

The architecture should still be modular enough that individual components can later be separated if scale genuinely requires it.

---

# 6. IMPORTANT: Facebook Marketplace feasibility comes first

Before investing heavily in Django, PostgreSQL, the SaaS dashboard, or automated ingestion, we need an early feasibility gate for Facebook Marketplace.

The reason is strategic: Facebook/Meta can restrict or block unauthorized automated data collection. We do not want to spend weeks building a system around a data source that turns out to be technically unreliable or unsuitable for commercial use.

The feasibility phase is therefore a deliberate risk-reduction step.

### Goal of the feasibility phase

Determine whether the necessary Marketplace information can be obtained reliably through a workflow that is technically sustainable and appropriate for a future commercial product.

We are primarily interested in whether we can identify and capture, at minimum:
- listing title,
- price,
- listing URL when available,
- visible location when available,
- basic product attributes such as model/storage when present.

The first proof should be small and observable. We do NOT need mass collection yet.

### IMPORTANT BOUNDARY

Do not design or implement techniques intended to evade Meta's anti-bot, anti-scraping, authentication, CAPTCHA, rate-limit, or access-control mechanisms.

Do not implement or recommend:
- CAPTCHA bypass,
- fingerprint spoofing,
- stealth automation intended to avoid detection,
- rotating accounts/proxies to circumvent blocks,
- credential/session theft,
- rate-limit circumvention,
- hidden API reverse engineering intended to bypass restrictions,
- mechanisms whose primary purpose is to disguise automated activity as human activity.

A browser-assisted/local prototype may be evaluated when it operates through the user's normal authenticated browser workflow and only examines information available to that user in the page.

Do not turn the feasibility test into a large-scale harvesting system.

### What the feasibility test must answer

1. Can the required listing information be captured reliably?
2. Which fields are available consistently?
3. Which fields are ambiguous or missing?
4. How stable is the extraction across multiple relevant Marketplace pages?
5. Does the approach rely on fragile page structure?
6. Does the approach require actions that would create technical, policy, or commercial risk?
7. Is the result suitable as a foundation for a future SaaS integration?

### Feasibility outcome

At the end of the test, produce a clear outcome:

- **GO** — the collection path appears technically viable and suitable enough to justify building the platform around it.
- **CONDITIONAL GO** — the concept works, but important limitations require a safer/user-assisted or narrower workflow.
- **NO-GO** — the collection path is too unreliable, restricted, or unsuitable for the intended commercial product.

If it is a NO-GO, do not force the architecture around Facebook. Keep the core platform and source-adapter interface intact and evaluate alternatives such as:
- manual entry,
- user-assisted import,
- user-provided URLs/data,
- permitted APIs or partner access where available,
- other sources with clearer commercial collection rights.

The core product must remain useful without depending entirely on one acquisition mechanism.

---

## 7. The first technical prototype

The first prototype is intentionally small and independent from Django.

Its purpose is only to validate the Facebook Marketplace data path.

The prototype may be a local browser extension/browser-assisted experiment.

The prototype should:
- operate through the user's normal browser session,
- inspect the page information available to the user,
- produce local test output,
- make missing or ambiguous fields visible,
- preserve enough raw information to inspect extraction quality.

Do not prematurely build:
- the complete scraper,
- a background harvesting system,
- mass automation,
- authentication automation,
- CRM,
- messaging automation,
- cloud ingestion workers.

The key question is whether a reliable normalized listing can be produced from the user's normal Marketplace workflow.

Example conceptual output:

```json
{
  "title": "iPhone 13 128GB",
  "price": 185,
  "location": "Maturín",
  "url": "...",
  "raw_text": "..."
}
```

The exact implementation is intentionally left open. Antigravity should first inspect the current prototype and project files, understand the goal, and choose an appropriate implementation strategy.

Do not assume a specific selector, DOM structure, Facebook endpoint, or scraping technique without evidence from the current environment.

---

## 8. Current development sequence

### Phase 0 — Context and architecture

- Understand this document.
- Understand the business model.
- Preserve the operational-market vs reference-market distinction.
- Preserve the future SaaS/multi-user requirement.
- Keep acquisition sources behind replaceable adapters/pipelines.

### Phase 1 — Facebook Marketplace feasibility gate

Build and test the smallest reasonable browser-assisted proof required to answer the feasibility questions above.

Deliverables:
- local proof-of-concept,
- sample raw output,
- sample normalized output where possible,
- field reliability notes,
- limitations and failure cases,
- technical/commercial risk notes,
- GO / CONDITIONAL GO / NO-GO recommendation.

Do not begin the full SaaS implementation until the feasibility result is understood.

### Phase 2 — Development environment

After the feasibility gate:
- verify/install Python only if needed,
- verify/install Docker only if needed,
- verify/install Git only if needed,
- set up Django,
- set up PostgreSQL,
- create project structure.

### Phase 3 — SaaS foundations

- users,
- authentication,
- user settings,
- operational market,
- user data isolation.

### Phase 4 — Product/catalog domain

- Product,
- exact model,
- storage,
- color,
- location catalog.

### Phase 5 — Listings and condition

- Listing,
- source,
- price,
- location,
- condition,
- battery,
- screen,
- body,
- Face ID,
- camera.

### Phase 6 — Market Reference Engine

- market observations,
- operational/local reference,
- other-city reference,
- historical observations,
- median,
- average,
- P25,
- P75,
- sample size.

### Phase 7 — Valuation Engine

- reference value,
- condition adjustments,
- estimated value,
- configurable business rules.

### Phase 8 — Opportunity Engine

Only listings from the user's operational market can become operational opportunities.

Consider:
- purchase price,
- budget range,
- estimated value,
- condition,
- minimum desired profit,
- explanation/reason codes.

Do not create unexplained opaque scoring as the first implementation.

### Phase 9 — Private dashboard

- opportunity list,
- filters,
- product detail,
- valuation explanation,
- market reference view.

### Phase 10 — MVP hardening

- automated tests,
- user-isolation tests,
- error handling,
- security basics,
- Dockerized deployment setup.

### Phase 11 — Cloud deployment

- production configuration,
- managed PostgreSQL,
- secrets/environment variables,
- HTTPS/domain,
- logs,
- monitoring,
- backups.

### Phase 12 — More data sources

Only after the core product works:
- Marketplace adapter if the Phase 1 result justifies it,
- Amazon/reference adapter,
- WhatsApp ingestion strategy,
- other approved sources.

### Phase 13 — Product expansion

Later:
- alerts,
- saved searches,
- CRM/negotiation tracking,
- notifications.

### Phase 14 — Commercial SaaS

Later:
- subscriptions,
- Stripe or similar billing provider,
- plans,
- limits,
- trial logic if desired,
- billing/account portal,
- business/admin metrics.

---

## 9. Data-source architecture

Every data acquisition source must ultimately feed a common internal listing representation.

Conceptually:

```text
Source
  ↓
Adapter / Pipeline
  ↓
Raw data
  ↓
Normalization
  ↓
Normalized Listing
  ↓
Core domain
  ↓
Market / Valuation / Opportunity engines
```

Potential sources in the future:
- Facebook Marketplace,
- WhatsApp groups/statuses,
- Amazon/reference sources,
- other marketplaces.

The core domain must not depend on a Facebook-specific DOM format or on one source's implementation details.

---

## 10. AI agent working rules

Antigravity should work incrementally.

Do NOT attempt to build the entire project in one task.

For each task:
1. inspect the current project,
2. understand the relevant requirements,
3. explain the intended change briefly,
4. implement only the scoped change,
5. run appropriate tests/checks,
6. report what changed,
7. report limitations or failures,
8. avoid unrelated refactors.

Do not silently change the architecture.

Do not add dependencies unless they are justified by the current task.

Do not invent business rules when requirements are unspecified.

When there is uncertainty, preserve flexibility in the architecture and document the uncertainty.

---

## 11. Important product principles

The priority order is:

1. It must work.
2. It must be practical enough that using the tool is easier than doing the analysis manually.
3. It must have good UX.
4. It must be maintainable.
5. It must be ready to evolve into a commercial SaaS.

The application should reduce the manual workflow, not replace it with a more complicated workflow.

Do not optimize for technical sophistication at the expense of usefulness.

---

## 12. Out of scope for the first MVP

Do not implement these yet:
- automated Facebook messaging,
- CRM/negotiation automation,
- WhatsApp automation,
- mobile application,
- subscription billing,
- complex ML/AI price prediction,
- elaborate opportunity scoring,
- microservices,
- mass scraping infrastructure.

These may be future phases.

---

## 13. Definition of MVP success

The MVP is successful when:

1. A user can register/login.
2. A user can configure an operational city, budget range, and minimum desired profit.
3. User-owned data is isolated.
4. Products can be represented by exact model and storage.
5. Listings can enter the system through an initial safe/manual or validated source path.
6. Condition can be recorded.
7. Market reference statistics can be calculated.
8. Operational-market listings can be evaluated for opportunity status.
9. Other-city data remains reference data unless explicitly configured otherwise.
10. Estimated value and potential margin are explainable.
11. The dashboard displays the user's opportunities.
12. The application runs with PostgreSQL and can be deployed to the cloud.

Automated Facebook collection is NOT a prerequisite for declaring the core product architecture successful. It is a source-integration question governed by the feasibility gate above.
