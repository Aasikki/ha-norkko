# ha-norkko — Norkko Pollen Home Assistant integration

This custom integration fetches daily pollen situation and forecast data published by Norkko (Turku University) and exposes per-location sensors for current situation and forecast per pollen type.

Key features:
- Current situation entities for each pollen type (severity as text: `none`, `mild`, `moderate`, `high`).
- Forecast entities per pollen type with the forecast period prepended to the state.
- GUI setup via config flow — choose one of the available locations from a dropdown.

Installation

Manual (for testing locally):

1. Copy the `custom_components/ha_norkko` folder into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. In Home Assistant, go to Settings → Integrations → Add Integration and search for `ha_norkko`.

Using HACS (recommended):

1. In HACS, go to Settings → Custom repositories.
2. Add this repository URL (`https://github.com/Aasikki/ha-norkko`) and set the category to **Integration**.
3. Once added, search for `ha-norkko` in HACS and install it.
4. Restart Home Assistant and add the integration from Settings → Integrations.

Configuration

The integration uses a config flow; no YAML configuration is required. You can add multiple entries (one per location).

License

This project follows the license in the repository root.

Contributing and support

Open issues or PRs on the repository for improvements, bug reports, or translations.
