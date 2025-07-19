# Music Beat Detection Tool

一个用于检测音乐鼓点并生成funscript格式文件的工具，支持音频和视频文件处理。

## 功能特点

- 🎵 **音频处理**：支持MP3、WAV、FLAC、M4A、OGG等音频格式
- 🎬 **视频处理**：支持MP4、AVI、MKV、MOV、WMV、FLV等视频格式，自动提取音频
- 🎯 **智能检测**：使用librosa库进行高级鼓点检测
- 📊 **可视化**：可生成音频波形图和频谱图
- 🎮 **Funscript导出**：生成适用于交互设备的funscript格式文件
- 🖥️ **图形界面**：提供友好的GUI界面，支持进度显示
- ⚙️ **参数调整**：可调整检测阈值以获得最佳效果

## 安装说明

### 1. 克隆项目
```bash
git clone <repository-url>
cd AIfunScript
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 验证安装
```bash
python -c "import librosa, moviepy; print('Dependencies installed successfully!')"
```

## 使用方法

### GUI界面（推荐）

1. **启动GUI**
   ```bash
   python gui_detector.py
   ```

2. **使用步骤**
   - 选择文件类型（音频或视频）
   - 选择输入文件
   - 设置输出文件路径
   - 调整检测参数（可选）
   - 点击"Start Detection"开始处理
   - 观察进度条和日志了解处理进度

3. **参数说明**
   - **Onset Threshold**：控制声音变化检测的敏感度（0.1-1.0）
   - **Beat Threshold**：控制节拍检测的敏感度（0.1-1.0）
   - **Detection Type**：
     - Beat Points：规律节拍点（推荐）
     - Onset Points：所有声音变化点（更敏感）

### 命令行使用

#### 基本用法
```bash
python advanced_detector.py input.mp3 --funscript output.funscript
```

#### 高级用法
```bash
# 使用onset点而不是beat点
python advanced_detector.py input.mp3 --funscript output.funscript --use-onset

# 调整检测阈值
python advanced_detector.py input.mp3 --funscript output.funscript --onset-threshold 0.3 --beat-threshold 0.7

# 生成可视化
python advanced_detector.py input.mp3 --funscript output.funscript --visualize
```

## 输出格式

### Funscript格式
生成的funscript文件包含以下信息：
```json
{
  "version": "1.0",
  "inverted": false,
  "range": 90,
  "actions": [
    {"at": 1000, "pos": 50},
    {"at": 2000, "pos": 80},
    ...
  ]
}
```

- `at`：时间戳（毫秒）
- `pos`：位置/强度（0-100）
- `range`：动作范围
- `inverted`：是否反转

## 技术原理

### 鼓点检测算法
1. **音频预处理**：加载音频文件，重采样到标准采样率
2. **Onset检测**：使用librosa检测声音变化点
3. **节拍检测**：基于onset强度进行节拍跟踪
4. **强度计算**：根据音频能量计算动作强度
5. **Funscript生成**：将检测结果转换为funscript格式

### 阈值说明
- **Onset Threshold**：控制检测声音变化点的敏感度
  - 低值（0.1-0.3）：检测更多细微变化
  - 高值（0.7-0.9）：只检测明显变化
- **Beat Threshold**：控制节拍检测的敏感度
  - 低值：检测更多可能的节拍
  - 高值：只检测最明显的节拍

## 文件结构

```
AIfunScript/
├── advanced_detector.py    # 核心检测器
├── gui_detector.py        # GUI界面
├── requirements.txt        # 依赖列表
├── README.md              # 说明文档
├── test_progress.py       # 进度条测试
├── test_moviepy.py        # MoviePy测试
└── simple_test.py         # 简单测试
```

## 常见问题

### Q: 视频处理失败
**A**: 确保已正确安装moviepy库：
```bash
pip install --upgrade moviepy
```

### Q: 检测结果不理想
**A**: 尝试调整阈值参数：
- 降低Onset Threshold检测更多变化
- 提高Beat Threshold获得更规律的节拍

### Q: GUI界面无响应
**A**: 检查是否安装了tkinter：
```bash
python -c "import tkinter; print('Tkinter available')"
```

### Q: 处理大文件很慢
**A**: 这是正常现象，大文件需要更多处理时间。可以：
- 使用更小的音频文件进行测试
- 调整阈值减少检测点数量

## 开发说明

### 添加新功能
1. 修改`advanced_detector.py`添加核心功能
2. 更新`gui_detector.py`添加界面支持
3. 更新`requirements.txt`添加新依赖
4. 更新`README.md`添加使用说明

### 测试
```bash
# 测试基本功能
python advanced_detector.py test.mp3 --funscript test.funscript

# 测试GUI
python gui_detector.py

# 测试进度条
python test_progress.py
```

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持音频和视频文件处理
- 提供GUI界面
- 支持funscript格式导出
- 添加进度条和可视化功能 