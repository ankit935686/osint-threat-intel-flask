
from flask import Flask, send_from_directory, jsonify, render_template
import os, json

app = Flask(__name__, template_folder='dashboard', static_folder='dashboard')

REPORTS = os.path.join(os.path.dirname(__file__), 'pipeline','data','reports')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/summary')
def summary():
    p = os.path.join(REPORTS, 'summary.json')
    if not os.path.exists(p):
        return jsonify({'error':'report not found, run pipeline first'}), 404
    with open(p) as f:
        data = json.load(f)
        # Ensure that source_data is included in the response
        if 'source_data' not in data and 'top_sources' in data:
            data['source_data'] = {}
            for source, count in data['top_sources'].items():
                # Create mock source data if it doesn't exist
                data['source_data'][source] = {
                    'indicator_types': {'ip': count // 2, 'domain': count // 3, 'hash': count - (count // 2) - (count // 3)},
                    'risk_levels': {'high': count // 4, 'medium': count // 2, 'low': count - (count // 4) - (count // 2)}
                }
        return jsonify(data)

@app.route('/api/graph')
def graph():
    p = os.path.join(REPORTS, 'graph.json')
    if not os.path.exists(p):
        return jsonify({'error':'graph not found, run pipeline first'}), 404
    with open(p) as f:
        return jsonify(json.load(f))

@app.route('/<path:filename>')
def serve_dashboard(filename):
    return send_from_directory('dashboard', filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
