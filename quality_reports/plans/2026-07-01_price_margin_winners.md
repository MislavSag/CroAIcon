# Price and margin winners

## Goal

Estimate which Croatian NKD/NACE activities most plausibly profited from price growth in 2021 to 2024 by combining official Eurostat output-price indices with GFI margins and net results.

## Core idea

GFI alone cannot separate prices from quantities. The usable diagnostic is:

- official price index growth by NACE/NKD activity,
- GFI net-margin change for the same activity,
- GFI net-result change and 2024 revenue scale.

Activities with high price growth, rising margins, and rising net results are candidates for having profited from price growth. This is not a causal proof.

## Data

- Eurostat `sts_inpp_m`, Croatia, industrial producer prices, monthly.
- Eurostat `sts_sepp_q`, Croatia, service producer prices, quarterly.
- GFI `db_afs`, net result and operating revenue from the existing margin build.

## Steps

1. Inspect Eurostat dimensions and choose the populated index unit and unadjusted series for Croatia.
2. Pull 2021 and 2024 data, using annual averages from monthly/quarterly observations.
3. Map Eurostat `nace_r2` codes to GFI NKD detail codes where the code systems align.
4. Join price growth to GFI margin-growth tables.
5. Rank activities by a transparent diagnostic score and output the top candidates.
6. Save tables and, if the result is coherent, a scatter chart for review.

## Caveats

- Eurostat coverage is uneven. Industry coverage is much stronger than services.
- CPI/HICP categories are not NKD/NACE and should not be mixed into this first pass.
- Output price growth plus margin growth is evidence of pricing power, not proof of profiteering.
