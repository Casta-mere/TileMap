# TileMap - 瓦片地图下载工具

一个功能强大的瓦片地图下载工具，支持从 Google Maps 和 OpenStreetMap 下载地图瓦片，并自动拼接成完整的大图。

## 功能特性

✅ **Web 界面** - 提供友好的 Web 界面，可视化选择下载区域  
✅ **区域选择** - 支持预设区域（省/市/区）和自定义坐标选择  
✅ **多层级下载** - 可以选择下载多个缩放层级（0-19）  
✅ **多种样式** - 支持多种地图样式（标准、卫星、混合、地形、深色等）  
✅ **自动拼接** - 自动将最高层级的瓦片拼接成完整大图  
✅ **多线程下载** - 使用多线程加速下载过程  
✅ **断点续传** - 自动跳过已下载的瓦片  

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 方式1：使用 Web 界面（推荐）

1. 启动 Web 服务器：

```bash
python web_app.py
```

2. 在浏览器中打开：`http://localhost:5000`

3. 在 Web 界面中：
   - 选择预设区域或在地图上点击两个点选择自定义区域
   - 设置缩放层级范围（层级越高，图片越详细）
   - 选择地图样式（标准、卫星、深色等）
   - 点击"开始下载"
   - 下载完成后，可以下载拼接好的大图

### 方式2：直接使用 Python 模块

```python
from tile_downloader import TileDownloader

# 创建下载器，选择样式
downloader = TileDownloader(output_dir='tiles', style='standard')

# 定义下载区域（纬度1，经度1，纬度2，经度2）
lat1, lon1 = 39.92, 116.38  # 天安门区域
lat2, lon2 = 39.88, 116.42

# 下载多个缩放层级
results = downloader.download_area(
    lat1, lon1, lat2, lon2, 
    zoom_levels=[10, 11, 12, 13]
)

print(f"下载完成！总瓦片数: {results['total_tiles']}")

# 拼接最高层级的瓦片
stitched_path = downloader.stitch_tiles(13)
print(f"拼接图片保存在: {stitched_path}")
```

## 支持的地图样式

- **standard** - Google Maps 标准地图
- **satellite** - Google Maps 卫星图
- **hybrid** - Google Maps 混合图（卫星+标注）
- **terrain** - Google Maps 地形图
- **dark** - Google Maps 深色地图
- **osm_standard** - OpenStreetMap 标准地图
- **osm_dark** - OpenStreetMap 深色地图

## 预设区域

Web 界面提供了以下预设区域：

- 北京市
- 上海市
- 广州市
- 深圳市
- 天安门广场

可以在 `web_app.py` 中的 `AREA_PRESETS` 字典添加更多预设区域。

## 缩放层级说明

- **0-2**: 世界/大洲级别（非常粗略）
- **3-7**: 国家/省份级别
- **8-11**: 城市级别
- **12-15**: 街道级别
- **16-19**: 建筑物级别（非常详细）

⚠️ **注意**: 层级越高，下载的瓦片数量呈指数增长。例如，层级15的某区域可能有数千个瓦片。

## 文件结构

```
TileMap/
├── tile_downloader.py    # 核心下载模块
├── web_app.py             # Web 服务器
├── templates/
│   └── index.html         # Web 界面模板
├── requirements.txt       # Python 依赖
└── README.md              # 使用文档
```

## 下载的文件结构

```
tiles/
└── task_0/                # 任务ID
    ├── 10/                # 缩放层级
    │   ├── 123/          # X坐标
    │   │   ├── 456.png   # Y坐标瓦片
    │   │   └── 457.png
    │   └── 124/
    ├── 11/
    ├── 12/
    └── stitched_zoom_12.png  # 拼接的大图
```

## 技术实现

- **Flask** - Web 框架
- **Leaflet.js** - 交互式地图
- **Pillow** - 图像处理和拼接
- **Requests** - HTTP 请求
- **Threading** - 多线程下载

## 注意事项

1. 请遵守地图服务提供商的使用条款
2. 不要过度频繁请求，建议设置合理的下载速度
3. 大范围、高层级的下载会产生大量瓦片，注意磁盘空间
4. 下载的地图仅供个人学习研究使用

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
