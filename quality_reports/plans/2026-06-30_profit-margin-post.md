# Profit margin post

## Goal

Put a current Quarto post on the local blog so the sector margin result can be reviewed as a page.

## Scope

- Use the saved table `outputs/tables/sector_margin_growth_2021_2024.csv`.
- Build a house-style chart for the sector ranking.
- Add a post under `posts/`.
- Render the post and refresh the site output.

## Constraints

- Treat this as a reviewable analytical draft because it uses GFI financial columns.
- Keep method details readable. Do not expose physical `bNNN` codebook internals in the post body.
- The notes box must name the source, measures, scripts, and the financial-column caution.

## Verification

1. Rerun the margin build script.
2. Run the chart script.
3. Render the post with Quarto.
4. Run a QA pass and write a quality report.
