"""
Tile Downloader Module
Downloads map tiles from various tile servers
"""
import os
import math
import requests
import threading
from pathlib import Path
from PIL import Image
from typing import Tuple, List
from concurrent.futures import ThreadPoolExecutor, as_completed


class TileDownloader:
    """Download and manage map tiles"""
    
    # Map style configurations
    STYLES = {
        'standard': 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        'satellite': 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        'hybrid': 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        'terrain': 'https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
        'dark': 'https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}',
        # OpenStreetMap alternatives
        'osm_standard': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        'osm_dark': 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}.png',
    }
    
    def __init__(self, output_dir: str = 'tiles', style: str = 'standard'):
        """
        Initialize tile downloader
        
        Args:
            output_dir: Directory to save tiles
            style: Map style to use
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.style = style
        self.tile_url = self.STYLES.get(style, self.STYLES['standard'])
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.lock = threading.Lock()
        self.downloaded_count = 0
        self.total_tiles = 0
        
    @staticmethod
    def lat_lon_to_tile(lat: float, lon: float, zoom: int) -> Tuple[int, int]:
        """
        Convert latitude/longitude to tile coordinates
        
        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            zoom: Zoom level
            
        Returns:
            Tuple of (x, y) tile coordinates
        """
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return x, y
    
    @staticmethod
    def tile_to_lat_lon(x: int, y: int, zoom: int) -> Tuple[float, float]:
        """
        Convert tile coordinates to latitude/longitude
        
        Args:
            x: Tile x coordinate
            y: Tile y coordinate
            zoom: Zoom level
            
        Returns:
            Tuple of (lat, lon) in degrees
        """
        n = 2.0 ** zoom
        lon = x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
        lat = math.degrees(lat_rad)
        return lat, lon
    
    def get_tile_bounds(self, lat1: float, lon1: float, lat2: float, lon2: float, zoom: int) -> Tuple[int, int, int, int]:
        """
        Get tile coordinate bounds for a geographic area
        
        Args:
            lat1, lon1: First corner coordinates
            lat2, lon2: Second corner coordinates
            zoom: Zoom level
            
        Returns:
            Tuple of (min_x, min_y, max_x, max_y)
        """
        x1, y1 = self.lat_lon_to_tile(lat1, lon1, zoom)
        x2, y2 = self.lat_lon_to_tile(lat2, lon2, zoom)
        
        min_x = min(x1, x2)
        max_x = max(x1, x2)
        min_y = min(y1, y2)
        max_y = max(y1, y2)
        
        return min_x, min_y, max_x, max_y
    
    def download_tile(self, x: int, y: int, zoom: int) -> bool:
        """
        Download a single tile
        
        Args:
            x: Tile x coordinate
            y: Tile y coordinate
            zoom: Zoom level
            
        Returns:
            True if successful, False otherwise
        """
        zoom_dir = self.output_dir / str(zoom) / str(x)
        zoom_dir.mkdir(parents=True, exist_ok=True)
        
        tile_path = zoom_dir / f'{y}.png'
        
        # Skip if already downloaded
        if tile_path.exists():
            with self.lock:
                self.downloaded_count += 1
            return True
        
        try:
            url = self.tile_url.format(x=x, y=y, z=zoom)
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                with open(tile_path, 'wb') as f:
                    f.write(response.content)
                with self.lock:
                    self.downloaded_count += 1
                return True
            else:
                print(f"Failed to download tile {zoom}/{x}/{y}: Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error downloading tile {zoom}/{x}/{y}: {str(e)}")
            return False
    
    def download_area(self, lat1: float, lon1: float, lat2: float, lon2: float, 
                     zoom_levels: List[int], max_workers: int = 10) -> dict:
        """
        Download tiles for a geographic area at multiple zoom levels
        
        Args:
            lat1, lon1: First corner coordinates
            lat2, lon2: Second corner coordinates
            zoom_levels: List of zoom levels to download
            max_workers: Number of concurrent download threads
            
        Returns:
            Dictionary with download statistics
        """
        results = {
            'total_tiles': 0,
            'downloaded': 0,
            'failed': 0,
            'zoom_levels': {}
        }
        
        for zoom in zoom_levels:
            print(f"\nDownloading zoom level {zoom}...")
            min_x, min_y, max_x, max_y = self.get_tile_bounds(lat1, lon1, lat2, lon2, zoom)
            
            tiles = []
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    tiles.append((x, y, zoom))
            
            self.total_tiles = len(tiles)
            self.downloaded_count = 0
            results['total_tiles'] += len(tiles)
            
            print(f"Total tiles to download: {len(tiles)}")
            
            # Download tiles with thread pool
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(self.download_tile, x, y, z) for x, y, z in tiles]
                
                for i, future in enumerate(as_completed(futures)):
                    if (i + 1) % 100 == 0 or (i + 1) == len(tiles):
                        print(f"Progress: {self.downloaded_count}/{self.total_tiles} tiles")
                    
                    if future.result():
                        results['downloaded'] += 1
                    else:
                        results['failed'] += 1
            
            results['zoom_levels'][zoom] = {
                'tiles': len(tiles),
                'bounds': (min_x, min_y, max_x, max_y)
            }
        
        return results
    
    def stitch_tiles(self, zoom: int, output_file: str = None) -> str:
        """
        Stitch tiles together into a single large image
        
        Args:
            zoom: Zoom level to stitch
            output_file: Output file path (optional)
            
        Returns:
            Path to the stitched image
        """
        zoom_dir = self.output_dir / str(zoom)
        
        if not zoom_dir.exists():
            raise ValueError(f"No tiles found for zoom level {zoom}")
        
        # Find all tiles
        tiles = {}
        for x_dir in zoom_dir.iterdir():
            if x_dir.is_dir():
                x = int(x_dir.name)
                for tile_file in x_dir.glob('*.png'):
                    y = int(tile_file.stem)
                    tiles[(x, y)] = tile_file
        
        if not tiles:
            raise ValueError(f"No tiles found for zoom level {zoom}")
        
        # Get bounds
        x_coords = [coord[0] for coord in tiles.keys()]
        y_coords = [coord[1] for coord in tiles.keys()]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        # Calculate image size (assuming 256x256 tiles)
        tile_size = 256
        width = (max_x - min_x + 1) * tile_size
        height = (max_y - min_y + 1) * tile_size
        
        print(f"Creating stitched image: {width}x{height} pixels")
        
        # Create large image
        stitched = Image.new('RGB', (width, height))
        
        # Paste tiles
        total = len(tiles)
        for i, ((x, y), tile_path) in enumerate(tiles.items()):
            try:
                tile_img = Image.open(tile_path)
                pos_x = (x - min_x) * tile_size
                pos_y = (y - min_y) * tile_size
                stitched.paste(tile_img, (pos_x, pos_y))
                
                if (i + 1) % 100 == 0 or (i + 1) == total:
                    print(f"Stitching progress: {i + 1}/{total} tiles")
                    
            except Exception as e:
                print(f"Error stitching tile {x}/{y}: {str(e)}")
        
        # Save stitched image
        if output_file is None:
            output_file = self.output_dir / f'stitched_zoom_{zoom}.png'
        else:
            output_file = Path(output_file)
        
        print(f"Saving stitched image to {output_file}")
        stitched.save(output_file, 'PNG')
        
        return str(output_file)


if __name__ == '__main__':
    # Example usage
    downloader = TileDownloader(output_dir='tiles', style='standard')
    
    # Beijing area example (Tiananmen Square)
    lat1, lon1 = 39.92, 116.38
    lat2, lon2 = 39.88, 116.42
    
    # Download zoom levels 10-15
    results = downloader.download_area(lat1, lon1, lat2, lon2, zoom_levels=[10, 11, 12])
    
    print("\nDownload complete!")
    print(f"Total tiles: {results['total_tiles']}")
    print(f"Downloaded: {results['downloaded']}")
    print(f"Failed: {results['failed']}")
    
    # Stitch the highest zoom level
    max_zoom = max(results['zoom_levels'].keys())
    print(f"\nStitching tiles for zoom level {max_zoom}...")
    output_path = downloader.stitch_tiles(max_zoom)
    print(f"Stitched image saved to: {output_path}")
