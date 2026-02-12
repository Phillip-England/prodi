# Prodi - Chick-fil-A Productivity Tracker

A web app that accepts a CSV file of daily sales data for two Chick-fil-A locations (Southroads and Utica) and generates line graphs comparing actual productivity against target productivity.

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

No manual dependency installation needed — `uv` handles everything automatically.

## Usage

```bash
# Run on default port (5000)
uv run app.py

# Run on a specific port
uv run app.py --port 8080
uv run app.py -p 8080
```

Then open `http://localhost:<port>` in your browser.

## How It Works

1. Upload a CSV file using the web form.
2. Optionally pick a **start date** and **end date** using the calendar widgets to filter to a specific time range. Leave blank to include all data.
3. The app parses the CSV and generates 3 graphs:
   - **Southroads** — Actual vs Target Productivity
   - **Utica** — Actual vs Target Productivity
   - **Combined Total** — Actual vs Target Productivity
4. Graphs display on the page with green/red shading to show where actual productivity is above or below target. Sundays are excluded automatically.
5. Click the **Download** button below any graph to save it as a PNG.

## CSV Format

The CSV must have the following structure:

- **Row 1**: Group headers (`SOUTHROADS`, `UTICA`, `TOTAL`)
- **Row 2**: Column headers
- **Row 3+**: Data rows

| Column | Description |
|--------|-------------|
| DATE | Date in `MM/DD/YY` format |
| DOW | Day of week |
| *(empty)* | Separator column |
| SALES | Daily sales ($) |
| TP HOURS | Time punch hours |
| PROD | Actual productivity ($/hr) |
| PROD TARGET | Target productivity ($/hr) |
| PROD GAP | Difference between target and actual |

This pattern of 5 data columns + 1 separator repeats 3 times: once for Southroads, once for Utica, and once for the Combined Total. See `data.csv` for a working example.

## Project Structure

```
prodi/
├── app.py              # Flask app (CSV parsing, graph generation, routes)
├── data.csv            # Example data file
├── templates/
│   └── index.html      # Upload form and graph display
├── static/
│   └── graphs/         # Generated graph PNGs (created at runtime)
└── README.md
```
