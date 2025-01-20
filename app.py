from flask import Flask, render_template, jsonify, request
import sqlite3
import pandas as pd
import plotly.express as px

# Create the Flask app
app = Flask(__name__)

# Connect to your SQLite database
conn = sqlite3.connect("tsx_analysis.db", check_same_thread=False)

# Route to serve the homepage
@app.route('/')
def index_page():
    return render_template('index.html')  # Ensure index.html is in the "templates" folder

# Route to handle graph updates for individual indicators
@app.route('/update_chart', methods=['POST'])
def update_chart():
    selected_indicator = request.form['indicator']
    
    # Adjust queries based on the table structure
    if selected_indicator == 'TSX':
        query = "SELECT timestamp, close AS value FROM tsx_daily"
    elif selected_indicator == 'FX':
        query = "SELECT Price AS timestamp, Close AS value FROM fx_data"  # Adjusted to use 'Price'
    elif selected_indicator == 'Inflation':
        query = "SELECT date AS timestamp, CPI AS value FROM CPI_Inflation"  # Adjusted to use 'date'
    elif selected_indicator == 'Energy':
        query = "SELECT timestamp, close AS value FROM energy_sector"  # Energy sector
    elif selected_indicator == 'Financials':
        query = "SELECT timestamp, close AS value FROM financial_sector"  # Financials sector
    elif selected_indicator == 'Industrials':
        query = "SELECT timestamp, close AS value FROM industrial_sector"  # Industrials sector
    elif selected_indicator == 'IT':
        query = "SELECT timestamp, close AS value FROM IT_sector"  # IT sector
    elif selected_indicator == 'Materials':
        query = "SELECT timestamp, close AS value FROM materials_sector"  # Materials sector
    else:
        return jsonify({"error": "Invalid indicator"}), 400

    # Execute the query and process the data
    df = pd.read_sql(query, conn)
    df['timestamp'] = pd.to_datetime(df['timestamp'])  # Convert to datetime
    df.set_index('timestamp', inplace=True)

    # Generate the Plotly visualization
    fig = px.line(
        df,
        x=df.index,
        y='value',
        title=f"{selected_indicator} Over Time",
        labels={'x': 'Date', 'y': selected_indicator}
    )

    return jsonify(fig.to_json())

# Route to handle the combined chart
@app.route('/combined_chart', methods=['GET'])
def combined_chart():
    # Load TSX data
    tsx_query = "SELECT timestamp, close AS TSX FROM tsx_daily"
    tsx_data = pd.read_sql(tsx_query, conn)
    tsx_data['timestamp'] = pd.to_datetime(tsx_data['timestamp'])

    # Load FX data
    fx_query = "SELECT Price AS timestamp, Close AS FX FROM fx_data"
    fx_data = pd.read_sql(fx_query, conn)
    fx_data['timestamp'] = pd.to_datetime(fx_data['timestamp'])

    # Load Inflation data
    inflation_query = "SELECT date AS timestamp, CPI AS Inflation FROM CPI_Inflation"
    inflation_data = pd.read_sql(inflation_query, conn)
    inflation_data['timestamp'] = pd.to_datetime(inflation_data['timestamp'])

    # Merge all datasets on the timestamp
    combined_data = pd.merge(tsx_data, fx_data, on='timestamp', how='inner')
    combined_data = pd.merge(combined_data, inflation_data, on='timestamp', how='inner')

    # Generate the Plotly visualization
    fig = px.line(
        combined_data,
        x='timestamp',
        y=['TSX', 'FX', 'Inflation'],
        title="Combined Indicators Over Time",
        labels={'value': 'Indicator Value', 'variable': 'Indicator'},
    )

    return jsonify(fig.to_json())

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, port=5001)