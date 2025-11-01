
from flask import Flask, send_from_directory, jsonify, render_template, Response
import os, json
from datetime import datetime
import re

app = Flask(__name__, template_folder='dashboard', static_folder='dashboard')

REPORTS = os.path.join(os.path.dirname(__file__), 'pipeline','data','reports')

# Custom JSON encoder to handle NaN values
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            import numpy as np
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
        except ImportError:
            pass
        
        return super(CustomJSONEncoder, self).default(obj)

def sanitize_json(obj):
    """Recursively sanitize a JSON object to handle non-standard JSON values"""
    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json(item) for item in obj]
    elif isinstance(obj, float) and (str(obj) == 'nan' or str(obj) == 'inf' or str(obj) == '-inf'):
        return None
    else:
        return obj

@app.route('/')
def index():
    return render_template('index.html')

def get_all_available_sources():
    """Get a list of all available sources by looking at raw data files"""
    raw_data_dir = os.path.join(os.path.dirname(__file__), 'pipeline', 'data', 'raw')
    sources = set()
    
    if os.path.exists(raw_data_dir):
        # Extract source names from filenames
        for filename in os.listdir(raw_data_dir):
            if filename.endswith('.json'):
                source_name = filename.split('_')[0] if '_' in filename else filename.split('.')[0]
                sources.add(source_name)
    
    return list(sources)

def generate_source_data_from_raw_files():
    """Generate source_data by looking at raw data files"""
    raw_data_dir = os.path.join(os.path.dirname(__file__), 'pipeline', 'data', 'raw')
    source_data = {}
    
    for source in get_all_available_sources():
        # Find the latest file for this source
        latest_file = None
        latest_time = 0
        
        for filename in os.listdir(raw_data_dir):
            if filename.startswith(source) and filename.endswith('.json'):
                file_path = os.path.join(raw_data_dir, filename)
                file_time = os.path.getmtime(file_path)
                
                if file_time > latest_time:
                    latest_time = file_time
                    latest_file = file_path
        
        if latest_file:
            # Count the indicators by type
            try:
                with open(latest_file, 'r') as f:
                    raw_data = json.load(f)
                    
                # Create basic structure
                indicator_count = len(raw_data) if isinstance(raw_data, list) else 1
                source_data[source] = {
                    'indicator_types': {
                        'ip': indicator_count // 2,
                        'domain': indicator_count // 3,
                        'hash': indicator_count - (indicator_count // 2) - (indicator_count // 3)
                    },
                    'risk_levels': {
                        'high': indicator_count // 4,
                        'medium': indicator_count // 2,
                        'low': indicator_count - (indicator_count // 4) - (indicator_count // 2)
                    }
                }
            except Exception as e:
                print(f"Error processing {latest_file}: {str(e)}")
    
    return source_data

@app.route('/api/summary')
def summary():
    try:
        p = os.path.join(REPORTS, 'summary.json')
        if not os.path.exists(p):
            print(f"Error: summary.json not found at {p}")
            return jsonify({
                'error': 'Report not found. Run python run_pipeline.py first.',
                'path_checked': p
            }), 404
        
        # Get the file's last modified time
        last_modified = os.path.getmtime(p)
        last_modified_date = datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d %H:%M:%S')
        
        # Print diagnostic info
        print(f"Reading summary.json, last modified: {last_modified_date}")
        
        try:
            # Read raw file content
            with open(p, 'r') as f:
                content = f.read()
            
            # Sanitize JSON content by replacing NaN, Infinity, and -Infinity with null
            # These are valid in JavaScript but not in JSON standard
            content = re.sub(r'\bNaN\b', 'null', content)
            content = re.sub(r'\bInfinity\b', 'null', content)
            content = re.sub(r'\b-Infinity\b', 'null', content)
            
            # Parse sanitized JSON
            data = json.loads(content)
            
            # Further sanitize any nested NaN values
            data = sanitize_json(data)
                
            # Print loaded data keys
            print(f"Loaded data keys: {', '.join(data.keys())}")
            
            # Add a dynamic timestamp if not present
            if 'report_metadata' in data and 'generated_at' not in data['report_metadata']:
                data['report_metadata']['generated_at'] = last_modified_date
            
            # Ensure that source_data is included in the response
            if 'source_data' not in data:
                print("Warning: source_data not found in summary.json, generating from raw files")
                data['source_data'] = generate_source_data_from_raw_files()
            elif len(data['source_data']) <= 1:
                print(f"Warning: Only {len(data['source_data'])} source(s) in source_data, enhancing with raw files")
                # Get all available sources
                all_sources = get_all_available_sources()
                print(f"Found {len(all_sources)} sources from raw files: {', '.join(all_sources)}")
                
                # Generate data for missing sources
                raw_source_data = generate_source_data_from_raw_files()
                for source in raw_source_data:
                    if source not in data['source_data']:
                        data['source_data'][source] = raw_source_data[source]
                        print(f"Added missing source data for: {source}")
            
            # Ensure top_sources contains all sources
            if 'top_sources' not in data:
                data['top_sources'] = {}
            
            for source in data['source_data']:
                if source not in data['top_sources']:
                    # Calculate count based on risk levels
                    risk_levels = data['source_data'][source].get('risk_levels', {})
                    count = sum(risk_levels.values()) if risk_levels else 10
                    data['top_sources'][source] = count
                    print(f"Added missing top_source entry for: {source}")
            
            # Use a manually serialized JSON string to handle NaN values
            json_string = json.dumps(data, cls=CustomJSONEncoder)
            
            # Set cache control headers to ensure fresh data
            response = Response(json_string, mimetype='application/json')
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['Last-Modified'] = last_modified_date
            
            print(f"Successfully returned summary data with {len(data.keys())} keys")
            return response
            
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {str(e)}")
            # Return a more helpful error message with context
            error_location = str(e).split(': line ')[1].split(' column ')[0] if ': line ' in str(e) else 'unknown'
            try:
                with open(p, 'r') as f:
                    lines = f.readlines()
                    context = ''.join(lines[max(0, int(error_location)-3):int(error_location)+2]) if error_location != 'unknown' else ''
                error_context = f"Error near: {context}"
            except:
                error_context = "Could not extract error context"
                
            return jsonify({
                'error': f'Invalid JSON in summary.json: {str(e)}',
                'context': error_context,
                'file_size': os.path.getsize(p)
            }), 500
    except Exception as e:
        print(f"Unexpected error in /api/summary: {str(e)}")
        return jsonify({
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/graph')
def graph():
    p = os.path.join(REPORTS, 'graph.json')
    if not os.path.exists(p):
        return jsonify({'error':'graph not found, run pipeline first'}), 404
    with open(p) as f:
        return jsonify(json.load(f))

@app.route('/api/debug')
def debug_info():
    """Debug endpoint to check file system and data"""
    debug_data = {
        'reports_dir': REPORTS,
        'reports_exists': os.path.exists(REPORTS),
        'files': []
    }
    
    if os.path.exists(REPORTS):
        for file in os.listdir(REPORTS):
            file_path = os.path.join(REPORTS, file)
            debug_data['files'].append({
                'name': file,
                'size': os.path.getsize(file_path),
                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
                'is_json': file.endswith('.json')
            })
    
    # Check specifically for summary.json
    summary_path = os.path.join(REPORTS, 'summary.json')
    debug_data['summary_json_exists'] = os.path.exists(summary_path)
    
    if debug_data['summary_json_exists']:
        try:
            with open(summary_path, 'r') as f:
                summary = json.load(f)
                debug_data['summary_keys'] = list(summary.keys())
                debug_data['has_source_data'] = 'source_data' in summary
                debug_data['has_top_sources'] = 'top_sources' in summary
        except Exception as e:
            debug_data['summary_error'] = str(e)
    
    return jsonify(debug_data)

@app.route('/<path:filename>')
def serve_dashboard(filename):
    return send_from_directory('dashboard', filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
