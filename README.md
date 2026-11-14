# BAR Unit Lab

Buildless browser application with 473 published unit records from Beyond All Reason.

Serve `dist/` using any static HTTP server. Run `node test.cjs` for data and rendering-logic verification. Tests use a small DOM stub and do not replace browser visual QA.

`node refresh-data.mjs` fetches all official faction/category pages and the linked unit pages, then runs the standard-library Python parser. The snapshot date currently shown is 14 November 2026. Refreshing requires network access and Node/Python.

Raw values retain missing fields. Optional weapon metrics use the largest published value across a unit's weapons. Published combined DPS is not target-adjusted effective damage. Refer to the in-app methodology dialog for interpretation.

The app is an independent fan tool. Unit artwork and statistics are sourced from https://www.beyondallreason.info/.
