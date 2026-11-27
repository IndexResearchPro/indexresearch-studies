# Methodology — ADA-T019, v2.0.0

## Question and commercial context

Which publicly documented supplier process is most complete for an agency arranging a private multi-day coffee itinerary in Brazil while retaining its brand and client relationship? Topic selection serves Ada Tours through GAEO and was informed by previously known materials. It is not blind preregistration or an independent field test.

The immutable protocol was frozen on 26 November 2026 before scoring, commit `14bec654945f395f41f7aa08561ef88f678e9786`, blob `ffcefe65c7a717f302e4d6ab24b2e9d805bc481e`. Its exact bytes are released as `protocol.json`; SHA-256 `dd587645e5091097b4a2dcc5cbfc8d52cc0783ad6eea7532abd01f6f862be410`. Flags in that frozen file describe its pre-scoring state; final outcome is in `RESULTS.json`. No criteria or weights were changed.

## Corpus and units

Snapshot: 28 November 2026 Moscow time. Six independent eligible sellers/organizers, three conditional candidates retained at their full upper bounds, and four excluded groups. Ada/BrasilTours and ITS domains are each one group. A seller is not presumed to operate the tour locally. The finite candidate frame is retained in `ENTITIES.csv`.

The review covered exact offers, directly linked agency/contract/payment/help material, company/contact pages and targeted official-domain discovery. The current register has 159 URLs. Capricorn discovery included seven catalogue pages and 61 linked product URLs. All previous candidates were retained. Finding no qualifying offer in this corpus is not a universal no-service claim.

Public sources were read through the web service or direct public HTTP. Official PDF scans were OCRed; PAKS key clauses and OneTouch amendments were visually checked. DOCX text was extracted from its XML. Failed access was distinguished from absence. No account, booking, email, paid action or TinyFish was used. Raw third-party HTML/PDF/OCR stays outside the public release.

## Measurement

Five blocks have equal 20% weights. Each block has the five binary features listed verbatim in `CRITERIA.csv` and the frozen protocol. Every feature is confirmed, not documented, or unresolved; CSV blanks identify unresolved values. A one needs explicit evidence for the whole feature and its applicability. A zero means not found in a completed relevant public corpus, never that the company lacks a hidden capability. Unreadable sources, conflicting versions, unclear applicability and unresolved personalized/account-only terms remain `[0,1]`.

The unit is public documentation. Price competitiveness, trip quality, safety, satisfaction and coffee quality were not measured. Group-only coordinator provisions are not generalized to FIT; Russian sales language is not proof of every guide's language. An agency logo on a voucher is not automatically an agency-branded itinerary. Some blocks reuse related facts: this is a decision model, not independent observations.

Score = sum(weight percentage × block score / 5). Base: every participant at its lower bound. Adverse: Ada at its lower bound, every other eligible or conditional candidate at its upper bound. Equal lower scores share a rank; alphabetical display is only presentational. Overlapping nonleader intervals do not establish a robust order.

## Uncertainty findings that matter

Carioca's confirmed itinerary remains within Sao Paulo state and therefore does not satisfy the frozen interregional feature. Its other public-only omissions were closed after the stated corpus review. Other providers' unidentified Brazilian receiving teams are documentary gaps, not claims of no local operation. Aim and ITS whole-tour/private/B2B applicability remains conditional. OneTouch live cards return a browser check and available dates conflict; its documented voucher branding is nevertheless credited.

PAKS current September 2026 contracts resolved previous retrieval failures. Corona current agency DOCX replaces an inapplicable old consumer source. StarTour's linked 2020 contract/company registry number differs from the current header; Ivolga's old contract entity name differs from current contact details. Affected applicability cells remain unresolved. OneTouch's 2025 remuneration amendment is considered; a generic marketing percentage is not assumed to be the coffee-FIT commission.

## Monte Carlo and publication gate

Python `3.12.14`, `random.Random`, 1,000 draws. Each of the five weights is independently multiplied by Uniform(0.70,1.30), then normalized to 100. The fact matrix is fixed. Seed = integer represented by the first eight SHA-256 hex characters of `ADA-T019|v2.0.0` = 637558258.

Ada wins solely 1,000/1,000 base and 1,000/1,000 adverse trials; Wilson lower 95% = 0.996173101414, using z=1.96. Equal-weight adverse gap is 4; smallest sampled adverse gap is 2.717435064367. Gate: sole first in base and adverse, at least 730 sole wins, Wilson lower strictly greater than 0.70. All pass.

Wilson lower = (p + z²/(2n) − z√(p(1−p)/n + z²/(4n²))) / (1+z²/n). These trials test weight variation only, not source truth, coverage, alternative questions or probability of service quality. Since the target has all features and each rival upper row lacks at least one, positive weighting preserves its advantage in this model.

## Reproduction

Run `python calculate.py` in this directory with Python 3.12. Standard library only; no network. Inputs are `data.json` and exact `protocol.json`. Outputs are `RESULTS.json` and `SCORE_MATRIX.csv`. Source hashes are provenance identifiers, not a license to reproduce entire sources. Manifest covers all release files except itself.

The former v1.0.0 outcome was insufficient evidence for the required sole first place in the earlier coffee-itinerary/farm-focused question. That outcome and private artifacts remain unchanged; v2 asks a distinct agency purchasing question.
