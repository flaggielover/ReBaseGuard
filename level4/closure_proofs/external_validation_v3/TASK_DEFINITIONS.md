# Frozen V3 task definitions

## A — MetroPT-3 industrial compressor

- Source: UCI 791, DOI `10.24432/C5VW3R`, CC BY 4.0.
- Aggregate ten-second readings into 15-minute means; a bin is eligible only
  with at least 72 raw readings. Preserve observation-time order and do not
  interpolate gaps.
- Target: mean `Oil_temperature`.
- Features: target lags 1, 2, 4, 8, 24, 96; contemporaneous non-target analog
  and state sensors; gap indicator; daily and weekly sine/cosine terms.
- Model: ridge regression, lambda 1, fit on train only. Feature centering/scales
  and residual scale come from train only.
- Splits after lag construction: chronological 20/30/50.
- Target ARL: 32 observations (8 observed hours).
- Natural block: 192 observations; moving-block length one such block.

## B — Online Retail II demand

- Source: UCI 502, DOI `10.24432/C5CG6D`, CC BY 4.0.
- Parse both worksheets chronologically. Retain rows with positive quantity and
  nonnegative unit price. Aggregate gross positive units by clock hour, fill
  missing clock hours with zero, and transform the target with `log1p`.
- Features: target lags 1, 2, 24, 168 and daily/weekly sine/cosine terms.
- Model: ridge regression, lambda 1, fit on train only. Feature centering/scales
  and residual scale come from train only.
- Splits after lag construction: chronological 20/30/50.
- Target ARL: 24 observations (24 clock hours).
- Natural block: 168 observations; moving-block length one such block.

Both tasks use one matched residual stream for P0/P1/P2. No feature, model,
threshold, rho, intervention, or event location is tuned on V3 evaluation data.
