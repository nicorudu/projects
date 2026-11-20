# Bill of materials

`BOM.csv` is the single list of every physical part: what it is, the exact spec, where it was ordered and its status. Open it in Excel, Numbers or Google Sheets, or view it straight on GitHub.

- **IDs** are stable: `D` dock, `C` controller, `S` shared, `T` tools, `X` unused. Refer to parts by ID in notes and the build log (e.g. "C2 arrived, measured 17.2 mm").
- **status** values: `to order` → `ordering` → `ordered` → `arrived` → `installed`, plus `on hand`, `check`, `spare`, `cancelled`.
- Update the status the day a part arrives, and put caliper measurements in `notes`.
- Prices are what was paid (USD, per unit where qty > 1). For parts not bought yet, the price is an estimate. Blank means not recorded.
- **To shop:** use the newest `shopping-list-*.md` in this folder. It lists only what still needs buying, with the spec to match.

Order statuses were last confirmed on 2026-11-11. Rev 3 (2026-11-18) added C10, S6–S9, T6 and T7; items marked `check` need Nico to confirm he has them. A second audit the same day added C11, C12 and T8–T11, and moved S6 to `to order`.

**2026-11-19:** statuses were checked against Nico's AliExpress and Amazon order screenshots. Rows that say "Order seen 2026-11-19" are confirmed ordered. Nothing has been confirmed as arrived yet.
