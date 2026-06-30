# Sector margin growth, 2021 to 2024

## Goal

Identify which GFI sector had the largest increase in margin from 2021 to 2024.

## Measure

- Use aggregate net margin by sector: net result / operating revenue.
- Use the physical `db_afs` codebook before treating financial columns as usable.
- Exclude financial sector K from the main ranking.
- Apply a minimum scale filter so tiny sectors do not win from noise.

## Steps

1. Confirm the physical labels for the revenue and net-result columns used in existing GFI scripts.
2. Query `db_afs` for 2021 and 2024 by NKD section.
3. Compute aggregate margin, change in percentage points, firm count, and revenue scale.
4. Report the top sectors with a caution that this is a quick diagnostic until the full financial-column audit is documented for a post.
