# Product Requirements Document (MVP) for NYC Services GPT

## 1. Objective

Deliver a one-stop helper over NYC Open Data / DSS docs that lets users self-serve without human intervention.

## 2. Primary KPI

- **Self-Service Success Rate**
    - **Definition:** % of user queries fully answered (no fallback to human support or "I don't know" response).
    - **Baseline Measurement (Week 0):** Conduct 100-query pilot using synthetic seed set; expect ~50–60%.
    - **MVP Target:** ≥ 90% by Day 14 post-launch.

## 3. Out-of-Scope for MVP

- **Time-to-Answer:** average elapsed time per query
- **Page-Click Reduction:** # of pages/sites visited before resolution

*(These will be captured in later iterations after the core self-serve flow is solid.)*

## 4. Persona Example

- **Name:** Maria the Micro‑Entrepreneur
- **Background:** Single mother running a pop-up café; unfamiliar with NYC licensing.
- **Needs:** Plain‑language answers about permits & benefits in ≤20 sec.
- **Acceptance Criteria:** Given a question about "food cart permit," the agent returns 3 relevant steps with links, ≥90% accuracy.

## 5. Acceptance Criteria (for KPI)

- Run a 100-query pilot sample ≥ Day 14.
- ≥ 90 of those queries must be correctly answered end‑to‑end without human fallback.

## 6. Baseline Measurement Protocol

1. Assemble **100 synthetic queries** across top 5 services.
2. Run them through the RAG pipeline without any prompt‑tuning.
3. Annotate each response as "Correct" or "Needs Human."
4. Compute baseline Self-Service Success Rate = (#Correct / 100) × 100.

## 7. Synthetic Query Seed Set (100 questions)

**Services & Query Counts:**

- Unemployment Benefits: 20 questions
- SNAP (Food Stamps): 20 questions
- Medicaid (Health Coverage): 20 questions
- Cash Assistance: 20 questions
- Child Care Subsidy: 20 questions

### 1. Unemployment Benefits

1. How do I apply for unemployment benefits in NYC?
2. What documents are required for New York State unemployment?
3. Can I file an unemployment claim online from Staten Island?
4. What's the processing time for unemployment insurance?
5. Who qualifies for partial unemployment benefits?
6. How do I check my weekly unemployment payment status?
7. What happens if my unemployment claim is denied?
8. How do I appeal an unemployment benefits decision?
9. Are gig workers eligible for unemployment benefits?
10. How do I update my address on my unemployment account?
11. What is the maximum unemployment benefit amount in NYC?
12. Can I work part-time while receiving unemployment?
13. How do I report earnings while on unemployment?
14. What's "Extended Duration Benefits" and who qualifies?
15. How do I submit my weekly certification for benefits?
16. Are independent contractors covered?
17. Do I need an SSN to apply?
18. Can I get retroactive unemployment payments?
19. Where can I find phone support for unemployment issues?
20. How long do I have to file after losing my job?

### 2. SNAP (Food Stamps)

1. How do I apply for SNAP benefits in NYC?
2. What income limits apply to SNAP in New York?
3. Can I pre-screen for SNAP eligibility online?
4. What documents do I need for a SNAP interview?
5. How long does SNAP application processing take?
6. How do I check my EBT balance?
7. Can I use EBT at local farmers' markets?
8. How do I report a change in household size?
9. What happens if my SNAP case is closed?
10. How do I reapply for SNAP after denial?
11. Are college students eligible for SNAP?
12. How do I appeal a SNAP decision?
13. Can mixed-status families apply?
14. What expenses count toward SNAP income deductions?
15. How do I find my SNAP case worker's contact?
16. How do I request replacement EBT card?
17. Can I use my SNAP benefits on groceries delivered?
18. Are benefits loaded monthly or biweekly?
19. What outreach programs exist for seniors on SNAP?
20. How do I report lost SNAP benefits?

### 3. Medicaid (Health Coverage)

1. How do I apply for Medicaid in NYC?
2. What income qualifies me for Medicaid?
3. Can I enroll in Medicaid year-round?
4. How do I check my Medicaid application status?
5. What documents are required for Medicaid?
6. How do I renew my Medicaid coverage?
7. What happens if I miss my renewal deadline?
8. Can I switch from Emergency Medicaid to full coverage?
9. How do I add a newborn to my Medicaid plan?
10. What providers accept Medicaid in Brooklyn?
11. How do I request a Medicaid ID card replacement?
12. Are dental services covered?
13. How do I appeal a Medicaid denial?
14. Can I have Medicaid and marketplace insurance?
15. How do I report a change in income?
16. What long-term care services are covered?
17. How do I find transportation services under Medicaid?
18. What behavioral health services are included?
19. How do I get language interpretation for Medicaid services?
20. Can I keep Medicaid if I start working?

### 4. Cash Assistance

1. How do I apply for Cash Assistance in NYC?
2. What's the income cutoff for Family Assistance?
3. How does Safety Net Assistance differ?
4. What documents are needed for a cash assistance interview?
5. How long does approval take?
6. Can I work while on cash assistance?
7. How do I report earnings?
8. What are the work requirements?
9. How do I check my cash assistance payment status?
10. How do I change my bank account for direct deposit?
11. Can I receive cash assistance for non-citizen household members?
12. How do I appeal a cash assistance denial?
13. What sanctions apply for missed appointments?
14. How do I request an emergency cash grant?
15. Can I get cash assistance if I'm homeless?
16. How do I add a child to my case?
17. Are utilities included in the budget?
18. How do I find my cash assistance worker's contact?
19. What budget deductions apply (e.g. shelter, childcare)?
20. How do I renew my case after closure?

### 5. Child Care Subsidy

1. How do I apply for child care subsidy in NYC?
2. What income qualifies for child care assistance?
3. How do I find approved daycare providers?
4. What documents are required for application?
5. How long does the approval process take?
6. Can I keep subsidy if I change providers?
7. How do I report a change in work hours?
8. What if my income increases mid-year?
9. How do I check my subsidy payment status?
10. Can I use subsidy for after-school programs?
11. How do I appeal a subsidy denial?
12. Are summer camps covered?
13. How do I enroll my child under age 2?
14. What co‑payments apply?
15. How do I find caseworker contact info?
16. Can I get emergency child care assistance?
17. Is transportation to daycare covered?
18. How do I renew my subsidy annually?
19. What if my provider stops accepting subsidies?
20. Are there priority slots for special‑needs children?

## 8. Development Progress

**✅ Completed:**
- Ingestion chunker module complete (tested)
- API connectivity verified (OpenAI, Gemini, ElevenLabs)
- Project structure scaffolded with TODO comments

**🔄 Next Up:**
- Data processor & vector store implementation
- RAG pipeline integration
- Synthetic query evaluation framework 