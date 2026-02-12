# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "flask",
#     "pandas",
#     "matplotlib",
# ]
# ///

import os
import io
import uuid
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from flask import Flask, request, render_template, send_from_directory

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'graphs')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def parse_csv(file_stream):
    """Parse the uploaded CSV and return a DataFrame with clean columns."""
    df = pd.read_csv(file_stream, header=None, skiprows=2)

    col_map = {
        0: 'date', 1: 'dow',
        5: 'sr_prod', 6: 'sr_target',
        11: 'ut_prod', 12: 'ut_target',
        17: 'tot_prod', 18: 'tot_target',
    }
    df = df.rename(columns=col_map)
    df = df[['date', 'dow', 'sr_prod', 'sr_target', 'ut_prod', 'ut_target', 'tot_prod', 'tot_target']]

    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y', errors='coerce')

    for col in ['sr_prod', 'sr_target', 'ut_prod', 'ut_target', 'tot_prod', 'tot_target']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(subset=['date'])

    # Exclude Sundays
    df = df[df['date'].dt.dayofweek != 6]

    return df


def make_graph(df, prod_col, target_col, title, filepath):
    """Generate a line graph comparing actual productivity vs target."""
    mask = df[prod_col].notna() & df[target_col].notna() & (df[prod_col] != 0)
    plot_df = df[mask].copy()

    if plot_df.empty:
        return False

    fig, ax = plt.subplots(figsize=(14, 5))

    ax.plot(plot_df['date'], plot_df[target_col], label='Target Productivity',
            color='#2196F3', linewidth=1.5, linestyle='--', marker='o', markersize=5)
    ax.plot(plot_df['date'], plot_df[prod_col], label='Actual Productivity',
            color='#FF5722', linewidth=1.5, marker='o', markersize=5)

    ax.fill_between(plot_df['date'], plot_df[prod_col], plot_df[target_col],
                     where=(plot_df[prod_col] >= plot_df[target_col]),
                     interpolate=True, alpha=0.15, color='green', label='Above Target')
    ax.fill_between(plot_df['date'], plot_df[prod_col], plot_df[target_col],
                     where=(plot_df[prod_col] < plot_df[target_col]),
                     interpolate=True, alpha=0.15, color='red', label='Below Target')

    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Productivity ($/hr)')
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(plot_df['date'])
    ax.set_xticklabels([d.strftime('%m/%d') for d in plot_df['date']],
                        rotation=90, fontsize=7)
    fig.tight_layout()
    fig.savefig(filepath, dpi=150)
    plt.close(fig)
    return True


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('csv_file')
        if not file or file.filename == '':
            return render_template('index.html', error='Please select a CSV file.')

        try:
            stream = io.StringIO(file.stream.read().decode('utf-8'))
            df = parse_csv(stream)
        except Exception as e:
            return render_template('index.html', error=f'Error parsing CSV: {e}')

        # Apply date range filter
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        if start_date:
            df = df[df['date'] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df['date'] <= pd.to_datetime(end_date)]

        if df.empty:
            return render_template('index.html', error='No data found for the selected date range.')

        batch = uuid.uuid4().hex[:8]
        graphs = []

        configs = [
            ('sr_prod', 'sr_target', 'Southroads - Productivity vs Target', f'southroads_{batch}.png'),
            ('ut_prod', 'ut_target', 'Utica - Productivity vs Target', f'utica_{batch}.png'),
            ('tot_prod', 'tot_target', 'Combined Total - Productivity vs Target', f'total_{batch}.png'),
        ]

        for prod_col, target_col, title, filename in configs:
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if make_graph(df, prod_col, target_col, title, filepath):
                graphs.append(filename)

        return render_template('index.html', graphs=graphs, start_date=start_date, end_date=end_date)

    return render_template('index.html')


@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Chick-fil-A Productivity Tracker')
    parser.add_argument('-p', '--port', type=int, default=5000, help='Port to run on (default: 5000)')
    args = parser.parse_args()
    app.run(debug=True, port=args.port)
