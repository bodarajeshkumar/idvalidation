"""
Flask Backend API for Data Retrieval System
Provides REST APIs for data retrieval and status monitoring
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import threading
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

from api_client import APIConfig
from orchestrator import DataOrchestrator

app = Flask(__name__)
# Enable CORS for all origins (OpenShift routes)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": False
    }
})

# Global state management
retrieval_state = {
    'status': 'not_started',  # not_started, processing, finished, error, cancelled
    'start_date': None,
    'end_date': None,
    'progress': {
        'total_records': 0,
        'completed_months': 0,
        'total_months': 0,
        'current_month': None,
        'percentage': 0.0
    },
    'error': None,
    'start_time': None,
    'end_time': None,
    'stats': None
}

retrieval_thread = None
cancellation_flag = False
session_start_record_count = 0  # Track records at session start

# History file path
HISTORY_FILE = Path(__file__).parent.parent / 'retrieval_history.json'


def load_history():
    """Load retrieval history from file"""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []


def save_to_history(start_date, end_date, stats, status):
    """Save completed retrieval to history"""
    history = load_history()
    
    # Calculate duration
    if retrieval_state['start_time'] and retrieval_state['end_time']:
        start_dt = datetime.fromisoformat(retrieval_state['start_time'])
        end_dt = datetime.fromisoformat(retrieval_state['end_time'])
        duration_seconds = (end_dt - start_dt).total_seconds()
    else:
        duration_seconds = stats.get('duration_seconds', 0) if stats else 0
    
    # Format duration as human-readable
    minutes = int(duration_seconds // 60)
    seconds = int(duration_seconds % 60)
    duration_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
    
    history_entry = {
        'start_date': start_date,
        'end_date': end_date,
        'timestamp': retrieval_state['end_time'],
        'status': status,
        'records': stats.get('total_records', 0) if stats else 0,
        'duration': duration_str,
        'duration_seconds': duration_seconds,
        'records_per_second': stats.get('records_per_second', 0) if stats else 0
    }
    
    # Add to beginning of history (most recent first)
    history.insert(0, history_entry)
    
    # Keep only last 50 entries
    history = history[:50]
    
    # Save to file
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")


def load_env_config():
    """Load configuration from environment variables or .env file"""
    import os
    
    # Try to get from environment variables first (for OpenShift/containers)
    api_base_url = os.getenv('API_BASE_URL')
    api_key = os.getenv('API_KEY')
    api_password = os.getenv('API_PASSWORD')
    
    if api_base_url and api_key and api_password:
        # Running in container with env vars
        return {
            'API_BASE_URL': api_base_url,
            'API_KEY': api_key,
            'API_PASSWORD': api_password
        }
    
    # Fall back to .env file for local development
    env_vars = {}
    env_path = Path(__file__).parent.parent / '.env'
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except FileNotFoundError:
        raise Exception("Configuration not found! Set API_BASE_URL, API_KEY, and API_PASSWORD environment variables or create .env file")
    
    return env_vars


def run_retrieval_async(start_date, end_date):
    """Run data retrieval in async context"""
    global retrieval_state, cancellation_flag
    
    try:
        # Load configuration
        env_vars = load_env_config()
        
        config = APIConfig(
            base_url=env_vars.get('API_BASE_URL', ''),
            api_key=env_vars.get('API_KEY', ''),
            password=env_vars.get('API_PASSWORD', ''),
            page_size=5000  # Larger page size for fewer requests
        )
        
        # Create orchestrator
        output_dir = Path(__file__).parent.parent / 'output'
        checkpoint_file = Path(__file__).parent.parent / 'retrieval_checkpoint.json'
        
        orchestrator = DataOrchestrator(
            config=config,
            output_dir=str(output_dir),
            output_format='jsonl',
            checkpoint_file=str(checkpoint_file)
        )
        
        # Set cancellation callback
        def check_cancellation():
            return cancellation_flag
        
        orchestrator.set_cancellation_callback(check_cancellation)
        
        # Run retrieval
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        stats = loop.run_until_complete(
            orchestrator.run(
                start_date=start_date,
                end_date=end_date,
                resume=True
            )
        )
        
        loop.close()
        
        # Check if cancelled
        if cancellation_flag:
            retrieval_state['status'] = 'cancelled'
            retrieval_state['end_time'] = datetime.now().isoformat()
            retrieval_state['error'] = 'Retrieval cancelled by user'
            # Save cancelled retrieval to history
            save_to_history(
                retrieval_state['start_date'],
                retrieval_state['end_date'],
                retrieval_state.get('stats'),
                'cancelled'
            )
        else:
            # Update state with final stats
            retrieval_state['status'] = 'finished'
            retrieval_state['end_time'] = datetime.now().isoformat()
            retrieval_state['stats'] = {
                'total_records': stats.total_records,
                'completed_months': stats.completed_months,
                'total_months': stats.total_months,
                'duration_seconds': stats.duration_seconds,
                'records_per_second': stats.records_per_second
            }
            retrieval_state['progress']['percentage'] = 100.0
            # Save successful retrieval to history
            save_to_history(
                retrieval_state['start_date'],
                retrieval_state['end_date'],
                retrieval_state['stats'],
                'finished'
            )
        
    except Exception as e:
        retrieval_state['status'] = 'error'
        retrieval_state['error'] = str(e)
        retrieval_state['end_time'] = datetime.now().isoformat()
        # Save error to history
        save_to_history(
            retrieval_state.get('start_date'),
            retrieval_state.get('end_date'),
            retrieval_state.get('stats'),
            'error'
        )


def start_retrieval_thread(start_date, end_date):
    """Start retrieval in a background thread"""
    global retrieval_thread, retrieval_state, cancellation_flag, session_start_record_count
    
    # Reset cancellation flag
    cancellation_flag = False
    
    # Count existing records before starting
    output_dir = Path(__file__).parent.parent / 'output'
    session_start_record_count = 0
    if output_dir.exists():
        for file in output_dir.glob('*.jsonl'):
            try:
                with open(file, 'r') as f:
                    session_start_record_count += sum(1 for _ in f)
            except:
                pass
    
    retrieval_state['status'] = 'processing'
    retrieval_state['start_date'] = start_date
    retrieval_state['end_date'] = end_date
    retrieval_state['start_time'] = datetime.now().isoformat()
    retrieval_state['error'] = None
    retrieval_state['progress'] = {
        'total_records': 0,
        'completed_months': 0,
        'total_months': 0,
        'current_month': None,
        'percentage': 0.0
    }
    
    retrieval_thread = threading.Thread(
        target=run_retrieval_async,
        args=(start_date, end_date)
    )
    retrieval_thread.daemon = True
    retrieval_thread.start()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Get current retrieval status
    Returns: status (not_started, processing, finished, error) and progress info
    """
    # Update progress from checkpoint if processing
    if retrieval_state['status'] == 'processing':
        checkpoint_file = Path(__file__).parent.parent / 'retrieval_checkpoint.json'
        if checkpoint_file.exists():
            import json
            try:
                with open(checkpoint_file, 'r') as f:
                    checkpoint = json.load(f)
                    completed = len(checkpoint.get('completed_months', []))
                    in_progress = len(checkpoint.get('in_progress', {}))
                    
                    # Calculate total records from output files
                    output_dir = Path(__file__).parent.parent / 'output'
                    total_records = 0
                    if output_dir.exists():
                        for file in output_dir.glob('*.jsonl'):
                            try:
                                with open(file, 'r') as f:
                                    total_records += sum(1 for _ in f)
                            except:
                                pass
                    
                    # Subtract records that existed before this session started
                    session_records = total_records - session_start_record_count
                    
                    retrieval_state['progress']['completed_months'] = completed
                    retrieval_state['progress']['total_records'] = session_records
                    
                    # Estimate percentage (assuming 24 months total)
                    if retrieval_state['start_date'] and retrieval_state['end_date']:
                        from datetime import datetime as dt
                        start = dt.strptime(retrieval_state['start_date'], '%Y-%m-%d')
                        end = dt.strptime(retrieval_state['end_date'], '%Y-%m-%d')
                        total_months = (end.year - start.year) * 12 + (end.month - start.month) + 1
                        retrieval_state['progress']['total_months'] = total_months
                        retrieval_state['progress']['percentage'] = (completed / total_months * 100) if total_months > 0 else 0
            except:
                pass
    
    return jsonify(retrieval_state)


@app.route('/api/retrieve', methods=['POST'])
def start_retrieval():
    """
    Start data retrieval process
    Request body: { "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD" }
    """
    global retrieval_state
    
    # Check if already processing
    if retrieval_state['status'] == 'processing':
        return jsonify({
            'error': 'Retrieval already in progress',
            'message': 'Cannot start new retrieval while another is processing'
        }), 409
    
    # Get request data
    data = request.get_json()
    
    if not data or 'start_date' not in data or 'end_date' not in data:
        return jsonify({
            'error': 'Missing required fields',
            'message': 'Both start_date and end_date are required'
        }), 400
    
    start_date = data['start_date']
    end_date = data['end_date']
    
    # Validate date format
    try:
        from datetime import datetime as dt
        dt.strptime(start_date, '%Y-%m-%d')
        dt.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({
            'error': 'Invalid date format',
            'message': 'Dates must be in YYYY-MM-DD format'
        }), 400
    
    # Start retrieval in background thread
    start_retrieval_thread(start_date, end_date)
    
    return jsonify({
        'message': 'Retrieval started successfully',
        'start_date': start_date,
        'end_date': end_date,
        'status': 'processing'
    }), 202


@app.route('/api/reset', methods=['POST'])
def reset_status():
    """Reset the retrieval status (for testing/debugging)"""
    global retrieval_state
    
    if retrieval_state['status'] == 'processing':
        return jsonify({
            'error': 'Cannot reset while processing',
            'message': 'Wait for current retrieval to finish'
        }), 409
    
    retrieval_state['status'] = 'not_started'
    retrieval_state['start_date'] = None
    retrieval_state['end_date'] = None
    retrieval_state['progress'] = {
        'total_records': 0,
        'completed_months': 0,
        'total_months': 0,
        'current_month': None,
        'percentage': 0.0
    }
    retrieval_state['error'] = None
    retrieval_state['start_time'] = None
    retrieval_state['end_time'] = None
    retrieval_state['stats'] = None
    
    return jsonify({
        'message': 'Status reset successfully',
        'status': 'not_started'
    })


@app.route('/api/stop', methods=['POST'])
def stop_retrieval():
    """Stop the current retrieval process"""
    global retrieval_state, cancellation_flag
    
    if retrieval_state['status'] != 'processing':
        return jsonify({
            'error': 'No retrieval in progress',
            'message': 'Cannot stop when not processing'
        }), 400
    
    # Set cancellation flag
    cancellation_flag = True
    
    return jsonify({
        'message': 'Cancellation requested. Retrieval will stop after current batch.',
        'status': 'cancelling'
    })


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get retrieval history"""
    history = load_history()
    return jsonify({
        'history': history,
        'count': len(history)
    })


if __name__ == '__main__':
    print("=" * 80)
    print("Data Retrieval Backend API Server")
    print("=" * 80)
    print("\nAvailable Endpoints:")
    print("  GET  /api/health   - Health check")
    print("  GET  /api/status   - Get retrieval status")
    print("  GET  /api/history  - Get retrieval history")
    print("  POST /api/retrieve - Start data retrieval")
    print("  POST /api/stop     - Stop current retrieval")
    print("  POST /api/reset    - Reset status (for testing)")
    print("\nServer starting on http://localhost:5001")
    print("=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
