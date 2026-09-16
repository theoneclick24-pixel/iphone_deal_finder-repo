# iPhone Deal Finder — AGENTS.md

## 1. Project purpose

Build a SaaS platform that helps users identify potentially profitable used-iPhone listings in their operational local market.

The product must eventually support:
- multiple users
- user-specific settings and operational markets
- shared reference market data
- multiple data sources
- cloud deployment
- subscription billing

The MVP must be small, testable, and deployable without requiring a rewrite for multi-user SaaS operation.

---

## 2. Core business concepts

### Operational market

The operational market is the city/market where a user actually intends to buy.

Listings from the user's operational market can become opportunities.

Example:
- User operational market: Maturín
- Facebook Marketplace listing in Maturín: operational candidate
- Facebook Marketplace listing in Caracas: reference data only

Never treat a listing from another city as an operational buying opportunity merely because its price is attractive.

### Reference market

Reference data is used to estimate market value. It may come from:
- the operational city
- other cities
- historical observations
- Amazon or other approved reference sources

Reference data and operational candidate data must remain conceptually separate throughout the system.

### Product identity

The core analysis must distinguish, at minimum:
- exact iPhone model
- storage capacity
- color when available
- condition

Do not mix different storage capacities into the same market statistic.

### Condition

Condition may include:
- battery health
- screen condition
- body/scratches
- Face ID
- camera
- other documented defects

Condition adjustments must be configurable and evidence-based. Do not invent arbitrary financial discounts in code.

---

## 3. SaaS / multi-user architecture

The application must be designed as a future multi-tenant SaaS from the beginning.

### User-owned data

User-owned data must be isolated between users. Examples:
- account
- settings
- operational market
- saved listings
- opportunities
- notes
- preferences

A user must never see another user's private data.

### Shared data

Shared/reference data may be reusable across users when appropriate. Examples:
- product catalog
- locations
- normalized model information
- market reference observations/statistics
- approved source metadata

Do not duplicate shared reference data unnecessarily for every user.

### Authentication

Authentication must exist in the MVP. The initial MVP does not need social login or billing, but it must have a sound user/account foundation.

### Configuration

Never hardcode one user's city, budget, or preferences into business logic.

User settings should determine:
- operational market
- minimum budget
- maximum budget
- minimum desired profit
- future preferences

---

## 4. Technology stack

Initial stack:
- Backend: Django
- Database: PostgreSQL
- Frontend for MVP: Django Templates + Bootstrap
- Development environment: Docker + Python virtual environment
- Version control: Git

Do not introduce Next.js, Redis, Celery, microservices, Kubernetes, or other infrastructure unless there is a demonstrated requirement.

The architecture should remain modular inside the Django monolith so components can be separated later if scale requires it.

---

## 5. Data-source architecture

Data sources must be implemented as replaceable adapters/pipelines.

Conceptually:

Source Adapter -> Raw/normalized listing -> Core domain -> Market/Opportunity engines

Future examples:
- Facebook Marketplace
- WhatsApp groups/statuses
- Amazon/reference sources
- other marketplaces

The core application must not depend directly on one source's scraping format or DOM structure.

---

## 6. CRITICAL: Facebook Marketplace feasibility gate

Facebook/Meta actively detects and blocks unauthorized scraping and uses rate limits, data limits, behavioral/pattern detection, blocking, investigations, and enforcement against suspected scrapers. Meta explicitly distinguishes authorized collection from unauthorized scraping in its public help material. Therefore Facebook collection is a technical AND policy/compliance risk and must be validated before building a large automated ingestion system.

Source: Meta Help Center — Data scraping and what can you do to protect your information on Facebook.

### Required approach

Before investing heavily in the full SaaS, perform a small feasibility proof for the Facebook Marketplace data path.

The proof should answer:
1. Can the desired listing fields be captured reliably from the user's normal Marketplace browsing workflow?
2. Which fields are actually available and stable?
3. Can the data be collected without bypassing authentication, anti-bot controls, CAPTCHAs, rate limits, access controls, or other technical restrictions?
4. Is the resulting workflow acceptable under Meta's current terms/policies and suitable for a future commercial product?
5. Can the method scale beyond one user without creating an unacceptable reliability or compliance risk?

### Important boundary

Do NOT design, implement, or recommend mechanisms whose purpose is to evade Meta's anti-bot/anti-scraping systems or disguise automated activity as human activity.

Do NOT implement:
- CAPTCHA bypass
- fingerprint spoofing
- stealth browser techniques intended to avoid detection
- rotating accounts/proxies to circumvent blocks
- credential/session theft
- rate-limit circumvention
- hidden API reverse engineering intended to bypass access restrictions

A browser extension or browser-assisted workflow may be evaluated as a feasibility prototype only when it operates through the user's normal authenticated browser session and does not attempt to defeat access controls or anti-bot measures. The prototype must not automatically navigate or harvest at scale merely to avoid detection.

### Feasibility prototype scope

Keep the first test deliberately small and observable. Target only the minimum fields needed to validate the product concept, for example:
- title
- price
- listing URL when available
- visible location when available
- basic visible product attributes such as model/storage if present

The prototype should output normalized test data locally and should make it obvious when a field is missing or ambiguous.

If the direct Marketplace path proves unreliable, blocked, or unsuitable for commercial use, do NOT force the architecture around it. Keep the core platform and adapter interface intact and evaluate alternative acquisition methods such as:
- user-assisted/manual import
- user-provided URLs/data
- permitted APIs or partner access if available
- browser-assisted capture that remains within permitted use
- other data sources with clearer commercial collection rights

The core SaaS must remain useful independently of one specific collection mechanism.

---

## 7. Development roadmap

### Phase 0 — Product and architecture specification
- finalize domain model
- finalize shared vs user-owned data boundaries
- define acceptance criteria
- create AGENTS.md

### Phase 1 — Facebook Marketplace feasibility gate
Build a very small browser-assisted/local prototype to evaluate whether the necessary visible Marketplace fields can be captured reliably and permissibly.

Deliverables:
- proof-of-concept collector
- sample raw output
- field reliability notes
- compliance/terms review notes
- go/no-go decision for automated Marketplace ingestion

This phase does NOT mean bypassing Meta protections.

### Phase 2 — Development environment
- VS Code + coding agent
- Git/GitHub
- Python
- Docker
- PostgreSQL
- Django

### Phase 3 — SaaS foundations
- users
- authentication
- user settings
- operational market
- data isolation

### Phase 4 — Product/catalog domain
- Product
- model
- storage
- color
- locations

### Phase 5 — Listings and condition
- Listing
- source
- price
- location
- condition
- battery
- screen
- body
- Face ID
- camera

### Phase 6 — Market Reference Engine
- observations
- local reference data
- other-city reference data
- median/average/P25/P75
- sample size
- historical observations

### Phase 7 — Valuation Engine
- reference value
- condition adjustments
- estimated value
- configurable business rules

### Phase 8 — Opportunity Engine
- only operational-market listings can become operational opportunities
- budget limits
- minimum profit
- margin calculation
- explanation/reason codes

### Phase 9 — Private dashboard
- opportunity list
- filters
- product detail
- valuation explanation
- market reference display

### Phase 10 — MVP hardening
- automated tests
- data isolation tests
- error handling
- security basics
- Dockerized deployment setup

### Phase 11 — Cloud deployment
- production configuration
- managed PostgreSQL
- secrets/environment variables
- domain/HTTPS
- logs/monitoring
- backups

### Phase 12 — Data-source expansion
- Marketplace adapter, only if Phase 1 is technically and commercially viable
- Amazon/reference adapter
- other approved sources
- WhatsApp ingestion strategy

### Phase 13 — Product expansion
- alerts
- saved searches
- CRM/negotiation tracking
- user notifications

### Phase 14 — Commercial SaaS
- subscriptions
- Stripe or equivalent billing provider
- plans
- usage limits
- trial period if desired
- account/billing portal
- admin/business metrics

---

## 8. AI coding-agent rules

Agents must work incrementally.

Never ask the agent to build the entire product in one step.

Every task should specify:
1. context
2. exact requirement
3. constraints
4. expected files/behavior
5. tests
6. verification steps

Agents must:
- read this file before substantial work
- preserve existing architecture
- avoid unrelated changes
- explain significant architectural decisions
- add tests for important business rules
- run checks/tests after meaningful changes
- report failures instead of hiding them
- avoid adding dependencies without justification

Do not silently rewrite architecture.

---

## 9. Security and privacy

- Never commit secrets.
- Use environment variables for credentials/configuration.
- Never expose another user's private data.
- Treat marketplace/seller information carefully.
- Do not store more personal information than required for the product.
- Do not collect credentials for external platforms.
- Do not implement mechanisms to bypass access controls.

---

## 10. MVP definition of done

The MVP is successful when:

1. A user can register/login.
2. A user can configure an operational city, budget range, and minimum profit.
3. Users are isolated from each other.
4. Products can be represented by exact model and storage.
5. Listings can be entered/imported through an initial safe/manual path.
6. Condition can be recorded.
7. Market reference statistics can be calculated.
8. Listings from the operational city can be evaluated for opportunity status.
9. Listings from other cities remain reference data unless explicitly configured otherwise.
10. Estimated value and potential margin are explainable.
11. The dashboard displays the user's opportunities.
12. The application runs against PostgreSQL and can be containerized/deployed.

The MVP does not require:
- automated Facebook scraping
- automated Facebook messaging
- CRM
- WhatsApp automation
- subscriptions
- mobile applications

Those are later phases.
