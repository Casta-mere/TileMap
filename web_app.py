"""
Web Interface for Tile Map Downloader
Provides a user-friendly interface for selecting areas and downloading tiles
"""
from flask import Flask, render_template, request, jsonify, send_file
import json
import threading
from pathlib import Path
from tile_downloader import TileDownloader

app = Flask(__name__)

# Global state for download tasks
download_tasks = {}
task_id_counter = 0
task_lock = threading.Lock()


# Area presets (Province/City/District examples)
AREA_PRESETS = {
    'china': {
        'beijing': {
            'name': '北京市',
            'bounds': {'lat1': 40.2, 'lon1': 115.7, 'lat2': 39.4, 'lon2': 117.4}
        },
        'shanghai': {
            'name': '上海市',
            'bounds': {'lat1': 31.4, 'lon1': 121.2, 'lat2': 30.9, 'lon2': 121.9}
        },
        'guangzhou': {
            'name': '广州市',
            'bounds': {'lat1': 23.4, 'lon1': 113.0, 'lat2': 22.9, 'lon2': 113.6}
        },
        'shenzhen': {
            'name': '深圳市',
            'bounds': {'lat1': 22.8, 'lon1': 113.8, 'lat2': 22.4, 'lon2': 114.6}
        },
        'tiananmen': {
            'name': '天安门广场',
            'bounds': {'lat1': 39.92, 'lon1': 116.38, 'lat2': 39.88, 'lon2': 116.42}
        }
    }
}


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html', 
                         area_presets=AREA_PRESETS,
                         styles=TileDownloader.STYLES)


@app.route('/api/presets')
def get_presets():
    """Get area presets"""
    return jsonify(AREA_PRESETS)


@app.route('/api/download', methods=['POST'])
def start_download():
    """Start a download task"""
    global task_id_counter
    
    data = request.json
    
    # Extract parameters
    lat1 = float(data.get('lat1'))
    lon1 = float(data.get('lon1'))
    lat2 = float(data.get('lat2'))
    lon2 = float(data.get('lon2'))
    zoom_min = int(data.get('zoom_min', 10))
    zoom_max = int(data.get('zoom_max', 15))
    style = data.get('style', 'standard')
    stitch = data.get('stitch', True)
    
    # Validate zoom levels
    if zoom_min < 0 or zoom_max > 19 or zoom_min > zoom_max:
        return jsonify({'error': 'Invalid zoom levels'}), 400
    
    zoom_levels = list(range(zoom_min, zoom_max + 1))
    
    # Create task
    with task_lock:
        task_id = task_id_counter
        task_id_counter += 1
    
    task = {
        'id': task_id,
        'status': 'running',
        'progress': 0,
        'results': None,
        'stitched_image': None
    }
    download_tasks[task_id] = task
    
    # Start download in background thread
    def download_thread():
        try:
            downloader = TileDownloader(output_dir=f'tiles/task_{task_id}', style=style)
            results = downloader.download_area(lat1, lon1, lat2, lon2, zoom_levels)
            
            task['results'] = results
            
            # Stitch if requested
            if stitch and zoom_levels:
                max_zoom = max(zoom_levels)
                try:
                    stitched_path = downloader.stitch_tiles(max_zoom)
                    task['stitched_image'] = stitched_path
                except Exception as e:
                    print(f"Stitching error: {str(e)}")
            
            task['status'] = 'completed'
            
        except Exception as e:
            task['status'] = 'failed'
            task['error'] = str(e)
            print(f"Download error: {str(e)}")
    
    thread = threading.Thread(target=download_thread)
    thread.daemon = True
    thread.start()
    
    return jsonify({'task_id': task_id})


@app.route('/api/status/<int:task_id>')
def get_status(task_id):
    """Get task status"""
    task = download_tasks.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(task)


@app.route('/api/download_image/<int:task_id>')
def download_image(task_id):
    """Download stitched image"""
    task = download_tasks.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    if not task.get('stitched_image'):
        return jsonify({'error': 'No stitched image available'}), 404
    
    return send_file(task['stitched_image'], as_attachment=True)


if __name__ == '__main__':
    # Create templates directory
    Path('templates').mkdir(exist_ok=True)
    Path('static').mkdir(exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
