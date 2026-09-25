# Lilly scoring library

`lilly_scoring` is a pure Python scoring library. It does not import Kerykeion,
FastAPI, SQLAlchemy, or application entities. Callers provide already-calculated
chart facts through `ChartInput`, then call `score_chart()`.

```python
from lilly_scoring import ChartInput, PlanetInput, PlanetName, score_chart

result = score_chart(ChartInput(
    planets=(
        PlanetInput(PlanetName.SUN, longitude=10.0, house=1,
                    retrograde=False, daily_motion=0.99),
        # Supply the other six classical planets.
    ),
    house_cusps={number: (number - 1) * 30.0 for number in range(1, 13)},
))
```

Longitudes use decimal degrees in `[0, 360)`; values outside this range are
normalized. `daily_motion` is the absolute-comparable motion over 24 hours in
degrees. Each planet result keeps `essential` and `accidental` sections separate,
and every awarded rule is represented by a `ScoreItem` with a stable code, label,
points, explanation, and optional related body.

The tables in `dignity_tables.py` are data, separate from the rule engine, so a
different school or revised research table can be introduced without rewriting
the calculation flow.
