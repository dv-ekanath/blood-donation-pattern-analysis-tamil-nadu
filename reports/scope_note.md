# Scope Note: Sequential Mining → Temporal Mining

**Course:** Sequential and Spatial Data Mining
**Why this matters for the viva:** be ready to explain this in one breath.

## The gap

Classical sequential pattern mining (PrefixSpan, SPADE, GSP) needs an
**ordered sequence of discrete events per entity** — e.g. per-donor rows like
`[Donation@2021-03, Donation@2021-09, Donation@2022-01, ...]`.

Our primary dataset (`Blood Donation Portal Dataset`) only has:

- `Registration_Date`
- `Last_Donation_Date`
- `Total_Donations` (a count, not a log)

There is no per-donation timestamp log, so there is nothing to build an
*event sequence* out of. Applying PrefixSpan/SPADE here would mean
fabricating synthetic event timestamps — which is not defensible as data
mining, it's data generation.

## The substitution

Instead, the project treats **time itself as the mining axis** and applies
temporal data mining techniques to the fields that *do* exist:

| Sequential concept | Temporal substitute used here |
|---|---|
| Event order within an entity | Registration → Last Donation as a 2-point interval per donor |
| Frequent sequential patterns | Frequent *temporal* patterns: month/season of registration & last donation, aggregated across donors |
| Sequence support/confidence | District/season-level trend strength, seasonal index |
| Forecasting the next event | ARIMA/Prophet forecast of aggregate monthly donation volume |

This is applied at three levels:
1. **Per-donor derived temporal features** (recency, estimated frequency, tenure)
2. **Aggregate trend analysis** (rolling averages, seasonal decomposition)
3. **Forecasting** (ARIMA/Prophet on monthly aggregated counts, per district if volume allows)

## What to say in the viva

> "The dataset didn't support classical sequential pattern mining because it
> lacks per-event logs — only summary fields per donor. Rather than force-fit
> PrefixSpan onto data it wasn't designed for, I scoped the sequential
> component to temporal data mining: trend analysis, seasonal decomposition,
> and forecasting on the donation timeline, which is the closest rigorous
> equivalent given the data available. The spatial component still uses full
· classical methods — DBSCAN and KDE."

This is a **documented, defensible scope decision**, not a missed
requirement — keep this note updated if the dataset situation changes.
