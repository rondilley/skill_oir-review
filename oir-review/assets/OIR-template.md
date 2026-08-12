# Operational Investigation Report — [Case ID]

**Version:** v0.1 · **Status:** Interim | Final · **Issued:** YYYY-MM-DDTHH:MM:SSZ
**Author:** [role] · **Reviewed by:** [role] · **Handling:** [TLP / distribution / privilege legend]

> Write this assuming it will be read by someone who did not commission it —
> an auditor, a regulator, or opposing counsel. Remediation recommendations go
> in a separate document. Delete these italic notes before issuing.

---

## 1. Bottom line

*Five things, within 150 words. Executives, audit and counsel read this and
stop.*

**Severity:** [level] ([taxonomy name — e.g. NIST 800-61r2: functional impact
Medium; information impact Proprietary breach; recoverability Supplemented])

[One sentence, plainest available English: what happened, to what, between
which UTC times.]

[The key negative or positive finding, bounded — "No evidence of X was
observed in the sources and window described in §7."]

**Status:** Determined | Assessed | Under investigation. *[If determined:
"Determined at YYYY-MM-DDTHH:MM:SSZ by [role]." Determination timestamps
matter — several regulatory clocks start there, not at discovery.]*

**Decision required:** [what you need from the reader, or "none"].

**Report:** v[N], [Interim | Final]. *[Keep this inside the 150 words. A
reader who stops here has to know whether they are holding a settled
conclusion or a snapshot. Report status and determination status above are
different things; both are needed.]*

---

## 2. Scope, authority and status

- **What was investigated:** [systems, accounts, time window]
- **What was not:** [explicitly out of scope, and why]
- **Requested by / authority:** [role, date]
- **Investigation window:** YYYY-MM-DDTHH:MM:SSZ to YYYY-MM-DDTHH:MM:SSZ
- **Report status:** Interim / Final. *[If this supersedes a prior version,
  state which judgments changed and on what evidence — see §5.]*

---

## 3. Timeline

*Every row anchored to an artifact. Reconstructed events belong in §5, not
here. All times RFC 3339 UTC.*

| # | UTC timestamp | Event | Source system | Evidence |
|---|---|---|---|---|
| 1 | 2026-00-00T00:00:00Z | | | [E1] |
| 2 | | | | |

**Clock skew:** [Measured skew per host, with method — or "not measured on
[hosts]; see §7."]

---

## 4. Findings — observed

*Facts. What the artifacts show. If you write "which suggests", you have
crossed into §5.*

**F1.** [Declarative statement of what an artifact shows.] [E7] Source
coverage: [window].

**F2.** …

---

## 5. Assessments — judged

*Each assessment makes four moves. All four are required.*

**A1.**
1. **Judgment:** We assess it is [likelihood term] ([nn–nn%]) that […].
2. **Confidence:** [High | Moderate | Low] — [what drives it: quality,
   quantity and independence of sources, not how sure anyone feels].
3. **Alternatives considered:** […] — [what evidence discriminates between
   them, and whether it exists].
4. **This would change if:** [specific observable].

**A2.** …

**Changes from the previous version:** *[Which judgments moved, and on what
evidence. If none, say so — do not use boilerplate.]*

---

## 6. Impact and affected scope

*Every count bounded by what was searched. "Affected" and "potentially
affected" are separate columns.*

| Category | Confirmed affected | Potentially affected | Basis |
|---|---|---|---|
| Systems | | | [E] |
| Accounts | | | [E] |
| Records | | | [E] |
| Services / availability | | | [E] |

**Sensitive customer information:** [Was it accessed, or reasonably likely
accessed? If a "not reasonably likely to result in substantial harm or
inconvenience" determination has been made, record it and its timestamp. US
financial services — this is the most-missed field in most templates.]

**Data categories in scope:** [types, jurisdictions of data subjects]

---

## 7. Limitations and collection gaps

*The section most often skipped and the one that most determines whether a
negative finding survives contact with a regulator.*

- **Log retention by source:** [source: retention window; where the data
  stops existing]
- **Coverage gaps:** [hosts not imaged, sensors not deployed, sources whose
  local offset could not be recovered, periods with no telemetry]
- **Tooling limitations:** [what the tools could not see]
- **SOP deviations:** [any, with reason — deviations must be disclosed]
- **What would change the conclusions in this report:** [specific
  observables]

---

## 8. Evidence register

| ID | Source system (FQDN / role / owner) | Log type, product, version+build | Query (verbatim) | Retrieved (UTC) | Native TZ / normalised | Records | Hash (alg) | Retention | Custodian | SOP deviation |
|---|---|---|---|---|---|---|---|---|---|---|
| E1 | | | | | | | | | | |

**Human sources** *[interviews and statements carry as much risk as logs and
belong in the register too]*

| ID | Role (not name, unless required) | Date/time (UTC) | Conducted by | Topics | Notes location | Source descriptor |
|---|---|---|---|---|---|---|
| H1 | | | | | | |

**Not collected:** [artifacts that could not be obtained, and why —
reimaged host, aged-out log, sensor not deployed.]

**Preservation:** [When did a litigation hold issue, and what did it cover?
Which of the gaps above fall before that date and which after? Those are
different kinds of gap, and only one of them is just a limitation.]

**Distribution ledger:** [Which version went to whom, and when. A handling
legend records intent; this records fact, and a privilege analysis turns on
the fact.]

| Version | Recipient | Role / org | Date (UTC) | Basis |
|---|---|---|---|---|

*[Do not paste sample records, credentials, tokens or personal data into this
report — reference them by evidence ID. Assume it will be produced.]*

---

## Annex A — EU/UK *(complete only if EU or UK data subjects are in scope)*

*[GDPR Art. 33 awareness timestamp; supervisory authority; categories and
approximate number of data subjects and records; DPO contact. Note for
non-EU analysts: the 72-hour clock runs from awareness, not from
determination.]*

## Annex B — US financial services *(complete only if the entity is covered)*

*[Materiality determination status and timestamp; NYDFS §500.17 applicability;
banking-agency notification-incident assessment; Reg S-P determination;
GLBA notification-event assessment. Note: these are inputs for the people who
make those calls — do not make the calls in this report.]*

## Annex C — Extortion and sanctions *(complete only if a demand was made)*

*[Demand received (UTC), channel, amount, wallet or account identifiers as
evidence IDs. Sanctions screening: who screened, against which lists, when,
and the outcome. That record has to exist before any payment decision, and
NYDFS's 24-hour post-payment clock and 30-day written description both draw on
it. Do not record a payment recommendation here.]*

## Annex D — Non-US regulators *(complete only if in scope)*

*[NIS2: 24-hour early warning, 72-hour notification, one-month final report.
DORA. UK ICO. CERT-In 6 hours. Australia SOCI 12/72. Card-brand PFI. Keep the
ones the organisation is actually subject to and delete the rest.]*

## Annex E — Third-party / supply chain *(complete only if applicable)*

*[Is the organisation downstream of a provider's incident, or upstream of a
customer's? Provider, contractual notification terms, when they notified, what
they have and have not confirmed. Both NYDFS §500.17 and Reg S-P key on
service-provider events.]*

## Annex F — [Region] *(complete only if …)*

---

*Remediation recommendations: see [separate document reference].*
