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

# Route to handle graph updates
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
    else:
        return jsonify({"error": "Invalid indicator"}), 400

    try:
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

    except Exception as e:
        # Handle errors gracefully
        return jsonify({"error": str(e)}), 500

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, port=5001)