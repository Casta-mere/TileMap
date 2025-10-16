#!/usr/bin/env python
"""
Example CLI script for downloading tiles
Demonstrates how to use the TileDownloader class directly
"""
from tile_downloader import TileDownloader
import argparse


def main():
    parser = argparse.ArgumentParser(
        description='下载地图瓦片并拼接成大图',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 下载天安门区域，标准样式，层级10-12
  python example_download.py --lat1 39.92 --lon1 116.38 --lat2 39.88 --lon2 116.42 --zoom 10 12 --style standard
  
  # 下载上海市，卫星图样式，层级8-10
  python example_download.py --lat1 31.4 --lon1 121.2 --lat2 30.9 --lon2 121.9 --zoom 8 10 --style satellite
  
  # 下载深圳市，深色样式，层级11-13，不拼接
  python example_download.py --lat1 22.8 --lon1 113.8 --lat2 22.4 --lon2 114.6 --zoom 11 13 --style dark --no-stitch
        """
    )
    
    parser.add_argument('--lat1', type=float, required=True, help='第一个点的纬度')
    parser.add_argument('--lon1', type=float, required=True, help='第一个点的经度')
    parser.add_argument('--lat2', type=float, required=True, help='第二个点的纬度')
    parser.add_argument('--lon2', type=float, required=True, help='第二个点的经度')
    parser.add_argument('--zoom', type=int, nargs=2, default=[10, 12], 
                       metavar=('MIN', 'MAX'),
                       help='缩放层级范围 (默认: 10 12)')
    parser.add_argument('--style', type=str, default='standard',
                       choices=list(TileDownloader.STYLES.keys()),
                       help='地图样式 (默认: standard)')
    parser.add_argument('--output', type=str, default='tiles',
                       help='输出目录 (默认: tiles)')
    parser.add_argument('--workers', type=int, default=10,
                       help='并发下载线程数 (默认: 10)')
    parser.add_argument('--no-stitch', action='store_true',
                       help='不拼接图片')
    
    args = parser.parse_args()
    
    # 创建下载器
    print(f"初始化下载器...")
    print(f"  样式: {args.style}")
    print(f"  输出目录: {args.output}")
    downloader = TileDownloader(output_dir=args.output, style=args.style)
    
    # 下载区域
    zoom_levels = list(range(args.zoom[0], args.zoom[1] + 1))
    print(f"\n下载区域:")
    print(f"  坐标1: ({args.lat1}, {args.lon1})")
    print(f"  坐标2: ({args.lat2}, {args.lon2})")
    print(f"  层级: {args.zoom[0]}-{args.zoom[1]} ({len(zoom_levels)} 个层级)")
    print(f"  并发线程: {args.workers}")
    
    # 估算瓦片数量
    total_estimate = 0
    for zoom in zoom_levels:
        min_x, min_y, max_x, max_y = downloader.get_tile_bounds(
            args.lat1, args.lon1, args.lat2, args.lon2, zoom
        )
        count = (max_x - min_x + 1) * (max_y - min_y + 1)
        total_estimate += count
        print(f"    层级 {zoom}: ~{count} 个瓦片")
    
    print(f"  预计总数: ~{total_estimate} 个瓦片")
    
    response = input("\n确认开始下载? (y/n): ")
    if response.lower() != 'y':
        print("已取消")
        return
    
    # 开始下载
    print("\n开始下载...")
    results = downloader.download_area(
        args.lat1, args.lon1, args.lat2, args.lon2,
        zoom_levels=zoom_levels,
        max_workers=args.workers
    )
    
    # 显示结果
    print("\n" + "="*60)
    print("下载完成!")
    print(f"  总瓦片数: {results['total_tiles']}")
    print(f"  成功下载: {results['downloaded']}")
    print(f"  失败: {results['failed']}")
    print(f"  成功率: {results['downloaded']/results['total_tiles']*100:.1f}%")
    
    # 拼接最高层级
    if not args.no_stitch and zoom_levels:
        max_zoom = max(zoom_levels)
        print(f"\n拼接层级 {max_zoom} 的瓦片...")
        try:
            output_path = downloader.stitch_tiles(max_zoom)
            print(f"拼接完成！保存在: {output_path}")
        except Exception as e:
            print(f"拼接失败: {str(e)}")
    
    print("="*60)


if __name__ == '__main__':
    main()
