from flask import Flask, render_template, jsonify, send_from_directory
import os
import json
from datetime import datetime
from pathlib import Path

app = Flask(__name__, static_folder='static')

# Configuration
DATA_DIR = os.environ.get('DATA_DIR', '/data')
CONFIG_DIR = os.environ.get('CONFIG_DIR', '/config')

# Ensure config directory exists
os.makedirs(CONFIG_DIR, exist_ok=True)


def get_log_files():
    """Get all log files from the data directory"""
    log_files = []
    try:
        data_path = Path(DATA_DIR)
        if data_path.exists():
            for log_file in data_path.glob('*.log'):
                stats = log_file.stat()
                log_files.append({
                    'name': log_file.name,
                    'path': str(log_file),
                    'size': stats.st_size,
                    'modified': datetime.fromtimestamp(stats.st_mtime).isoformat()
                })
            # Also check for txt files
            for log_file in data_path.glob('*.txt'):
                stats = log_file.stat()
                log_files.append({
                    'name': log_file.name,
                    'path': str(log_file),
                    'size': stats.st_size,
                    'modified': datetime.fromtimestamp(stats.st_mtime).isoformat()
                })
    except Exception as e:
        print(f"Error reading log files: {e}")
    
    return sorted(log_files, key=lambda x: x['modified'], reverse=True)


def read_log_file(filename):
    """Read content of a log file"""
    try:
        file_path = Path(DATA_DIR) / filename
        if file_path.exists() and file_path.is_file():
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    except Exception as e:
        print(f"Error reading log file {filename}: {e}")
    return None


def tail_log_file(filename, lines=100):
    """Get last N lines from a log file"""
    try:
        file_path = Path(DATA_DIR) / filename
        if file_path.exists() and file_path.is_file():
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
    except Exception as e:
        print(f"Error tailing log file {filename}: {e}")
    return []


# Web UI Routes
@app.route('/')
def index():
    """Main page showing list of log files"""
    log_files = get_log_files()
    return render_template('index.html', log_files=log_files)


@app.route('/log/<filename>')
def view_log(filename):
    """View a specific log file"""
    content = read_log_file(filename)
    if content is None:
        return "Log file not found", 404
    return render_template('log_view.html', filename=filename, content=content)


# API Routes for miner controller
@app.route('/api/logs')
def api_list_logs():
    """API: Get list of all log files"""
    log_files = get_log_files()
    return jsonify({
        'success': True,
        'logs': log_files,
        'count': len(log_files)
    })


@app.route('/api/log/<filename>')
def api_get_log(filename):
    """API: Get full content of a log file"""
    content = read_log_file(filename)
    if content is None:
        return jsonify({
            'success': False,
            'error': 'Log file not found'
        }), 404
    
    return jsonify({
        'success': True,
        'filename': filename,
        'content': content,
        'lines': content.count('\n') + 1
    })


@app.route('/api/log/<filename>/tail')
@app.route('/api/log/<filename>/tail/<int:lines>')
def api_tail_log(filename, lines=100):
    """API: Get last N lines of a log file"""
    log_lines = tail_log_file(filename, lines)
    if not log_lines:
        return jsonify({
            'success': False,
            'error': 'Log file not found or empty'
        }), 404
    
    return jsonify({
        'success': True,
        'filename': filename,
        'lines': log_lines,
        'count': len(log_lines)
    })


@app.route('/api/log/<filename>/search/<query>')
def api_search_log(filename, query):
    """API: Search for a term in a log file"""
    content = read_log_file(filename)
    if content is None:
        return jsonify({
            'success': False,
            'error': 'Log file not found'
        }), 404
    
    matching_lines = []
    for line_num, line in enumerate(content.split('\n'), 1):
        if query.lower() in line.lower():
            matching_lines.append({
                'line_number': line_num,
                'content': line
            })
    
    return jsonify({
        'success': True,
        'filename': filename,
        'query': query,
        'matches': matching_lines,
        'count': len(matching_lines)
    })


@app.route('/api/status')
def api_status():
    """API: Get system status"""
    log_files = get_log_files()
    return jsonify({
        'success': True,
        'status': 'online',
        'data_dir': DATA_DIR,
        'config_dir': CONFIG_DIR,
        'log_count': len(log_files),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return send_from_directory(app.static_folder, 'favicon.svg', mimetype='image/svg+xml')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
