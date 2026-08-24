# Dataset discovery audit

Audit date: 2026-08-24. Only metadata, raw structure, missingness, chronology,
rough target dependence, and projected power were inspected. No detector or
reuse-policy comparison was run.

All four new candidates are hosted by the UCI Machine Learning Repository and
licensed CC BY 4.0. Checksums refer to the official downloaded archives.

| Candidate | Structure and provenance | Usable sequence | Outcome-blind decision |
|---|---|---:|---|
| Individual Household Electric Power Consumption, UCI 235 | 2,075,259 one-minute rows, 2006-12-16 to 2010-11-26; 25,979 missing target rows; complete timestamp span | 133,503 15-minute targets after the >=12/15 rule and causal lags | **Primary A**: long real household-load stream; projected gates pass |
| Metro Interstate Traffic Volume, UCI 492 | 48,204 rows, 2012-10-02 to 2018-09-30; 40,575 unique hourly timestamps; duplicate timestamps have identical targets | 40,575 hourly targets after deterministic duplicate aggregation | **Primary B**: independent traffic domain; projected gates pass |
| Beijing Multi-Site Air Quality, UCI 501 | 12 synchronized sites x 35,064 hourly timestamps, 2013-03-01 to 2017-02-28; 8,739 PM2.5 cells explicitly `NA` despite contrary API metadata | 34,523 city-median PM2.5 targets after >=8-site and causal-lag rules | **Primary C**: independent environmental domain; projected gates pass |
| ElectricityLoadDiagrams20112014, UCI 321 | 140,256 15-minute rows x 370 clients; no malformed rows; 249 MiB archive / 711 MB expanded | 139,584 aggregate targets; 156 clients meet the frozen structural stability rule | **Technical backup D**: qualifies, but energy-domain redundant and much more costly to reacquire |

Historical Stage-E Electricity (45,312), Air Quality (8,991 usable), and Bike
Sharing (17,379) were excluded from V2 selection because their confirmatory
outcomes are already known and pooling/rerunning them as confirmatory evidence
is forbidden. Their old results are motivation only.

The backup may replace a primary only if that primary becomes technically
unusable before its confirmatory outcomes are generated. An unfavorable,
null, or contradictory outcome is never a replacement reason.
