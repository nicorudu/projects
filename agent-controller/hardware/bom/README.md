# Bill of materials

`BOM.csv` is the single list of every physical part: what it is, the exact spec, where it was ordered and its status. Open it in Excel, Numbers or Google Sheets, or view it straight on GitHub.

- **IDs** are stable: `D` dock, `C` controller, `S` shared, `T` tools, `X` unused. Refer to parts by ID in notes and the build log (e.g. "C2 arrived, measured 17.2 mm").
- **status** values: `to order` → `ordering` → `ordered` → `arrived` → `installed`, plus `on hand`, `check`, `spare`, `cancelled`.
- Update the status the day a part arrives, and put caliper measurements in `notes`.
- Prices are what was paid (USD, per unit where qty > 1). Blank means not recorded.

Status as of 2026-11-11.
