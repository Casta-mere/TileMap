# 快速开始指南

## 安装步骤

### 1. 克隆项目
```bash
git clone https://github.com/Casta-mere/TileMap.git
cd TileMap
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

依赖包括：
- Flask 3.0.0 - Web 框架
- Pillow 10.1.0 - 图像处理
- requests 2.31.0 - HTTP 请求
- geopy 2.4.1 - 地理信息处理

## 使用方法

### 方式一：Web 界面（最简单）

1. 启动服务器：
```bash
python web_app.py
```

2. 打开浏览器访问：`http://localhost:5000`

3. 在界面中操作：
   - 选择预设区域（如：北京市、上海市等）或在地图上点击选择
   - 设置缩放层级（建议 10-15，层级越高越详细但下载量越大）
   - 选择地图样式（标准、卫星、深色等）
   - 勾选"自动拼接最大层级的图片"
   - 点击"开始下载"

4. 等待下载完成后，点击"下载拼接图片"获取完整大图

### 方式二：命令行工具

基本用法：
```bash
python example_download.py --lat1 纬度1 --lon1 经度1 --lat2 纬度2 --lon2 经度2 --zoom 最小层级 最大层级
```

示例：

**下载天安门广场区域（层级 10-12）**
```bash
python example_download.py --lat1 39.92 --lon1 116.38 --lat2 39.88 --lon2 116.42 --zoom 10 12 --style standard
```

**下载上海市区（层级 8-10，卫星图）**
```bash
python example_download.py --lat1 31.4 --lon1 121.2 --lat2 30.9 --lon2 121.9 --zoom 8 10 --style satellite
```

**下载深圳市（层级 11-13，深色样式，不拼接）**
```bash
python example_download.py --lat1 22.8 --lon1 113.8 --lat2 22.4 --lon2 114.6 --zoom 11 13 --style dark --no-stitch
```

查看所有选项：
```bash
python example_download.py --help
```

### 方式三：在 Python 代码中使用

```python
from tile_downloader import TileDownloader

# 创建下载器
downloader = TileDownloader(
    output_dir='my_tiles',  # 输出目录
    style='standard'         # 地图样式
)

# 定义下载区域（天安门广场示例）
lat1, lon1 = 39.92, 116.38
lat2, lon2 = 39.88, 116.42

# 下载指定层级
results = downloader.download_area(
    lat1, lon1, lat2, lon2,
    zoom_levels=[10, 11, 12],  # 要下载的层级列表
    max_workers=10             # 并发线程数
)

# 查看下载结果
print(f"总瓦片数: {results['total_tiles']}")
print(f"成功下载: {results['downloaded']}")
print(f"失败: {results['failed']}")

# 拼接最高层级的瓦片
stitched_path = downloader.stitch_tiles(12)
print(f"拼接图片保存在: {stitched_path}")
```

## 选择合适的参数

### 缩放层级建议

| 层级 | 覆盖范围 | 用途 | 示例 |
|------|---------|------|------|
| 0-2  | 世界/大洲 | 全球地图 | 世界地图 |
| 3-7  | 国家/省份 | 大区域概览 | 中国全境 |
| 8-11 | 城市 | 城市地图 | 北京市 |
| 12-15 | 街区 | 街道详图 | 天安门周边 |
| 16-19 | 建筑物 | 建筑级别 | 单个建筑 |

⚠️ **重要提示**：
- 层级每增加1，瓦片数量增加 4 倍
- 层级 15 下载一个城市可能产生数万个瓦片文件
- 建议从小范围、低层级开始测试

### 地图样式说明

| 样式 | 说明 | 适用场景 |
|------|------|---------|
| standard | Google 标准地图 | 通用导航 |
| satellite | Google 卫星图 | 地形地貌分析 |
| hybrid | Google 混合图 | 卫星图+标注 |
| terrain | Google 地形图 | 高程地形 |
| dark | Google 深色地图 | 夜间模式 |
| osm_standard | OpenStreetMap | 开源标准地图 |
| osm_dark | OpenStreetMap 深色 | 开源深色地图 |

## 常见问题

### Q1: 如何找到我想下载区域的坐标？

**方法1**：使用本项目的 Web 界面，在地图上点击两个点

**方法2**：访问 Google Maps：
1. 在地图上右键点击目标位置
2. 选择"这是哪里？"
3. 底部会显示经纬度坐标

**方法3**：使用预设区域（已内置北京、上海等城市）

### Q2: 下载速度慢怎么办？

1. 增加并发线程数：`--workers 20`
2. 检查网络连接
3. 尝试使用 OpenStreetMap 样式（可能更快）
4. 减少下载范围或层级

### Q3: 下载的文件保存在哪里？

- Web 界面：`tiles/task_X/` 目录（X 为任务编号）
- 命令行：默认 `tiles/` 目录，可用 `--output` 指定
- Python 代码：由 `output_dir` 参数指定

### Q4: 如何只拼接不重新下载？

如果已有下载的瓦片文件：

```python
from tile_downloader import TileDownloader
downloader = TileDownloader(output_dir='已有瓦片的目录')
stitched_path = downloader.stitch_tiles(层级)
```

### Q5: 出现下载失败怎么办？

1. 检查网络连接
2. 重新运行下载命令（会自动跳过已下载的瓦片）
3. 尝试降低并发线程数
4. 检查磁盘空间是否充足

### Q6: 可以商业使用吗？

请务必遵守地图服务提供商的使用条款：
- Google Maps 有使用限制和条款
- OpenStreetMap 数据可免费使用但需要注明来源
- 建议仅用于个人学习研究

## 高级用法

### 自定义瓦片服务器

编辑 `tile_downloader.py` 中的 `STYLES` 字典：

```python
STYLES = {
    'my_custom': 'https://your-tile-server.com/{z}/{x}/{y}.png',
    # ... 其他样式
}
```

### 添加新的预设区域

编辑 `web_app.py` 中的 `AREA_PRESETS` 字典：

```python
AREA_PRESETS = {
    'china': {
        'my_city': {
            'name': '我的城市',
            'bounds': {
                'lat1': 纬度1, 'lon1': 经度1,
                'lat2': 纬度2, 'lon2': 经度2
            }
        },
        # ... 其他城市
    }
}
```

### 批量下载多个区域

创建脚本批量下载：

```python
from tile_downloader import TileDownloader

areas = {
    'beijing': (40.2, 115.7, 39.4, 117.4),
    'shanghai': (31.4, 121.2, 30.9, 121.9),
    'shenzhen': (22.8, 113.8, 22.4, 114.6),
}

downloader = TileDownloader()

for name, (lat1, lon1, lat2, lon2) in areas.items():
    print(f"Downloading {name}...")
    downloader.output_dir = f'tiles/{name}'
    results = downloader.download_area(
        lat1, lon1, lat2, lon2,
        zoom_levels=[10, 11, 12]
    )
    downloader.stitch_tiles(12)
```

## 技术支持

如有问题，请：
1. 查看 `README.md` 详细文档
2. 运行 `python test_integration.py` 检查环境
3. 在 GitHub 提交 Issue

## 许可证

MIT License - 可自由使用和修改
