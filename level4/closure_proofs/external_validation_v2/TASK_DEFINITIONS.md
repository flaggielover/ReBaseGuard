# Frozen task definitions

## Common chronology and model

Each task is reduced to one chronological scalar target. A deterministic ridge
model (`lambda = 1`) is fitted on the first 30% only. Feature centering/scaling
is fitted on that same block. The next 20% is calibration; the last 50% is
evaluation. Predictive models are never refitted. Causal lags and calendar
features use no future value. Residual scale is the train-block SD only.

## Task A — household power

- Source: UCI 235, DOI `10.24432/C58K54`.
- Target: `log1p` of mean `Global_active_power` in a 15-minute bin.
- A bin is eligible only with at least 12 of 15 real measurements.
- Features: target lags 1, 4, 96, 672; sine/cosine time-of-day, weekday, year.
- Target ARL: 240 observations; one week: 672 observations.

## Task B — metro traffic

- Source: UCI 492, DOI `10.24432/C5X60B`.
- Duplicate weather-description rows at a timestamp are aggregated; their
  traffic targets must agree.
- Target: `log1p(traffic_volume)`.
- Features: temperature, rain, snow, cloud cover, holiday indicator, and
  sine/cosine hour, weekday, year. No target lag is required across gaps.
- Target ARL: 60 observations; one week: 168 observations.

## Task C — Beijing air quality

- Source: UCI 501, DOI `10.24432/C5RK5G`.
- Target: `log1p` of the city median PM2.5 at an hour, requiring at least eight
  observed sites.
- Features: target lags 1, 24, 168; city medians of TEMP, PRES, DEWP, RAIN,
  WSPM; sine/cosine hour, weekday, year. All contemporaneous meteorology is
  measurement input, never a future value.
- Target ARL: 60 observations; one week: 168 observations.

## Backup D — load diagrams

The archive is UCI 321, DOI `10.24432/C58C86`. If and only if a primary is
technically unusable before outcomes, the backup target is `log1p` of mean load
over clients that are nonzero during the first seven days and positive in at
least 50% of all intervals. Features are lags 1, 4, 96, 672 plus calendar
terms. Target ARL is 240; a week is 672 observations.
