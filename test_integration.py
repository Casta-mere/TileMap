#!/usr/bin/env python
"""
Integration test to verify all components work together
"""
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from tile_downloader import TileDownloader
        from web_app import app, AREA_PRESETS
        print("✓ All modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_tile_downloader():
    """Test TileDownloader functionality"""
    print("\nTesting TileDownloader...")
    try:
        from tile_downloader import TileDownloader
        
        # Test initialization
        downloader = TileDownloader(output_dir='/tmp/test_tiles', style='standard')
        print(f"✓ TileDownloader initialized with style: {downloader.style}")
        
        # Test coordinate conversion
        x, y = downloader.lat_lon_to_tile(39.9, 116.4, 10)
        print(f"✓ Coordinate conversion: (39.9, 116.4) -> tile ({x}, {y})")
        
        lat, lon = downloader.tile_to_lat_lon(x, y, 10)
        print(f"✓ Reverse conversion: tile ({x}, {y}) -> ({lat:.4f}, {lon:.4f})")
        
        # Test bounds calculation
        min_x, min_y, max_x, max_y = downloader.get_tile_bounds(
            39.92, 116.38, 39.88, 116.42, 12
        )
        tiles_count = (max_x - min_x + 1) * (max_y - min_y + 1)
        print(f"✓ Bounds calculation: {tiles_count} tiles at zoom 12")
        
        # Test available styles
        print(f"✓ Available styles: {len(downloader.STYLES)} ({', '.join(list(downloader.STYLES.keys())[:3])}...)")
        
        return True
        
    except Exception as e:
        print(f"✗ TileDownloader test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_app():
    """Test web application"""
    print("\nTesting Web App...")
    try:
        from web_app import app, AREA_PRESETS
        
        # Test preset areas
        china_presets = AREA_PRESETS.get('china', {})
        print(f"✓ Loaded {len(china_presets)} preset areas")
        
        # Test routes with test client
        with app.test_client() as client:
            # Test index page
            response = client.get('/')
            if response.status_code == 200:
                print(f"✓ Index page accessible (status: {response.status_code})")
            else:
                print(f"✗ Index page failed (status: {response.status_code})")
                return False
            
            # Test API endpoints
            response = client.get('/api/presets')
            if response.status_code == 200:
                data = response.json
                print(f"✓ Presets API working (returned {len(data.get('china', {}))} areas)")
            else:
                print(f"✗ Presets API failed (status: {response.status_code})")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Web app test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_example_script():
    """Test example CLI script"""
    print("\nTesting Example Script...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, 'example_download.py', '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and '下载地图瓦片' in result.stdout:
            print("✓ Example script help works")
            return True
        else:
            print(f"✗ Example script failed (return code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"✗ Example script test failed: {e}")
        return False

def test_documentation():
    """Test that documentation exists"""
    print("\nTesting Documentation...")
    try:
        files_to_check = [
            'README.md',
            'SUMMARY.md',
            'requirements.txt',
            'config.ini',
            '.gitignore'
        ]
        
        for filename in files_to_check:
            if Path(filename).exists():
                size = Path(filename).stat().st_size
                print(f"✓ {filename} exists ({size} bytes)")
            else:
                print(f"✗ {filename} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Documentation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("TileMap Integration Test Suite")
    print("="*60)
    
    tests = [
        test_imports,
        test_tile_downloader,
        test_web_app,
        test_example_script,
        test_documentation
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All tests passed! The implementation is complete and working.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
