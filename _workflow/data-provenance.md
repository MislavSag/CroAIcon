# Data provenance notes

Raw data stays out of git. This file is the record of where it came from and what state it is in.

## GFI base

- **Source.** FINA annual financial reports.
- **Table.** `db_afs`. One row per firm and year, 2002 to 2024.
- **Trusted columns.** `employeecounteop` (employees, end of period), `nacerev21` (NKD 2007 activity area, A to U).
- **Not trusted yet.** Financial columns (revenue, profit, debt). Keep them out of posts until cleaned and confirmed.
- **Caution.** A rising firm count partly reflects wider coverage of the base, not only real growth. Employee counts are headcounts and more robust.

## Adding a dataset

For each new source, record the origin, the table, the columns you rely on, the columns you do not yet trust, and any caution a reader of a post should know.
