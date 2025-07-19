#!/usr/bin/env python3
"""
音乐鼓点检测GUI界面

提供图形界面来选择音频文件、设置参数并生成funscript
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import tempfile
import subprocess
import sys

# 全局变量
MOVIEPY_AVAILABLE = False

# 依赖检查函数
def check_and_install_dependencies():
    """检查并安装缺失的依赖"""
    global MOVIEPY_AVAILABLE
    missing_deps = []
    
    # 检查librosa
    try:
        import librosa
    except ImportError:
        missing_deps.append("librosa")
    
    # 检查numpy
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    # 检查matplotlib
    try:
        import matplotlib
    except ImportError:
        missing_deps.append("matplotlib")
    
    # 检查moviepy
    try:
        from moviepy import VideoFileClip
        MOVIEPY_AVAILABLE = True
    except ImportError:
        missing_deps.append("moviepy")
        MOVIEPY_AVAILABLE = False
    
    # 如果有缺失的依赖，尝试安装
    if missing_deps:
        print(f"Missing dependencies: {missing_deps}")
        print("Attempting to install missing dependencies...")
        
        try:
            for dep in missing_deps:
                print(f"Installing {dep}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"{dep} installed successfully")
            
            # 重新检查moviepy
            try:
                from moviepy import VideoFileClip
                MOVIEPY_AVAILABLE = True
                print("MoviePy available after installation")
            except ImportError:
                MOVIEPY_AVAILABLE = False
                print("MoviePy still not available")
                
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            return False
    
    return True

# 在启动时检查依赖
if not check_and_install_dependencies():
    print("Warning: Some dependencies could not be installed automatically")
    print("Please install manually: pip install -r requirements.txt")

# 导入检测器（在依赖检查之后）
try:
    from advanced_detector import AdvancedDrumBeatDetector
except ImportError as e:
    print(f"Error importing advanced_detector: {e}")
    AdvancedDrumBeatDetector = None

class DrumBeatDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Beat Detection Tool")
        self.root.geometry("700x600")
        
        # 检查检测器是否可用
        if AdvancedDrumBeatDetector is None:
            messagebox.showerror("Error", "Advanced detector not available. Please check dependencies.")
            root.destroy()
            return
        
        # 变量
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.file_type = tk.StringVar(value="audio")  # "audio" or "video"
        self.use_onset = tk.BooleanVar(value=False)
        self.onset_threshold = tk.DoubleVar(value=0.5)
        self.beat_threshold = tk.DoubleVar(value=0.5)
        self.visualize = tk.BooleanVar(value=False)
        self.temp_audio_file = None
        
        # 状态变量
        self.processing = False
        
        # 检查moviepy状态
        if not MOVIEPY_AVAILABLE:
            print("Warning: MoviePy not available. Video processing will not work.")
        
        self.create_widgets()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="🎵 Music Beat Detection Tool", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 依赖状态
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # 显示依赖状态
        deps_status = []
        try:
            import librosa
            deps_status.append("✓ librosa")
        except ImportError:
            deps_status.append("✗ librosa")
            
        try:
            import numpy
            deps_status.append("✓ numpy")
        except ImportError:
            deps_status.append("✗ numpy")
            
        try:
            import matplotlib
            deps_status.append("✓ matplotlib")
        except ImportError:
            deps_status.append("✗ matplotlib")
            
        if MOVIEPY_AVAILABLE:
            deps_status.append("✓ moviepy")
        else:
            deps_status.append("✗ moviepy")
        
        status_text = " | ".join(deps_status)
        status_label = ttk.Label(status_frame, text=f"Dependencies: {status_text}", font=("Arial", 9))
        status_label.pack()
        
        if not MOVIEPY_AVAILABLE:
            warning_label = ttk.Label(status_frame, text="⚠ Video processing disabled (moviepy not available)", 
                                    foreground="orange", font=("Arial", 9))
            warning_label.pack()
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 文件类型选择
        ttk.Label(file_frame, text="File Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        type_frame = ttk.Frame(file_frame)
        type_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(type_frame, text="Audio File", 
                       variable=self.file_type, value="audio", 
                       command=self.on_file_type_change).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(type_frame, text="Video File", 
                       variable=self.file_type, value="video", 
                       command=self.on_file_type_change).pack(side=tk.LEFT)
        
        # 输入文件选择
        ttk.Label(file_frame, text="Input File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        input_entry = ttk.Entry(file_frame, textvariable=self.input_file, width=50)
        input_entry.grid(row=1, column=1, padx=(10, 5), pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_input).grid(row=1, column=2, pady=5)
        
        # 输出文件选择
        ttk.Label(file_frame, text="Output File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        output_entry = ttk.Entry(file_frame, textvariable=self.output_file, width=50)
        output_entry.grid(row=2, column=1, padx=(10, 5), pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_output).grid(row=2, column=2, pady=5)
        
        # 参数设置区域
        param_frame = ttk.LabelFrame(main_frame, text="Detection Parameters", padding="10")
        param_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 检测类型选择
        ttk.Label(param_frame, text="Detection Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        type_frame = ttk.Frame(param_frame)
        type_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(type_frame, text="Beat Points (Regular rhythm)", 
                       variable=self.use_onset, value=False).pack(anchor=tk.W)
        ttk.Radiobutton(type_frame, text="Onset Points (Sound changes, more sensitive)", 
                       variable=self.use_onset, value=True).pack(anchor=tk.W)
        
        # 阈值设置
        ttk.Label(param_frame, text="Onset Threshold:").grid(row=1, column=0, sticky=tk.W, pady=5)
        onset_scale = ttk.Scale(param_frame, from_=0.1, to=1.0, variable=self.onset_threshold, 
                               orient=tk.HORIZONTAL, length=200)
        onset_scale.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Label(param_frame, textvariable=tk.StringVar(value="0.5")).grid(row=1, column=2, pady=5)
        
        ttk.Label(param_frame, text="Beat Threshold:").grid(row=2, column=0, sticky=tk.W, pady=5)
        beat_scale = ttk.Scale(param_frame, from_=0.1, to=1.0, variable=self.beat_threshold, 
                              orient=tk.HORIZONTAL, length=200)
        beat_scale.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Label(param_frame, textvariable=tk.StringVar(value="0.5")).grid(row=2, column=2, pady=5)
        
        # 选项设置
        option_frame = ttk.Frame(param_frame)
        option_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=10)
        
        ttk.Checkbutton(option_frame, text="Generate Visualization", 
                       variable=self.visualize).pack(anchor=tk.W)
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        self.process_button = ttk.Button(button_frame, text="Start Detection", 
                                       command=self.start_processing, style="Accent.TButton")
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT)
        
        # 进度条框架
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # 进度条
        self.progress = ttk.Progressbar(progress_frame, mode='determinate', length=400, maximum=100)
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 进度百分比标签
        self.progress_label = ttk.Label(progress_frame, text="0%", width=5)
        self.progress_label.grid(row=0, column=1)
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="Ready", font=("Arial", 10))
        self.status_label.grid(row=6, column=0, columnspan=2, pady=5)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding="5")
        log_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.log_text = tk.Text(log_frame, height=8, width=70)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def on_file_type_change(self):
        """文件类型改变时的处理"""
        # 清空当前选择的文件
        self.input_file.set("")
        self.output_file.set("")
        
    def browse_input(self):
        """浏览输入文件"""
        if self.file_type.get() == "audio":
            filename = filedialog.askopenfilename(
                title="选择音频文件",
                filetypes=[
                    ("音频文件", "*.mp3 *.wav *.flac *.m4a *.ogg"),
                    ("MP3文件", "*.mp3"),
                    ("WAV文件", "*.wav"),
                    ("所有文件", "*.*")
                ]
            )
        else:  # video
            filename = filedialog.askopenfilename(
                title="选择视频文件",
                filetypes=[
                    ("视频文件", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv"),
                    ("MP4文件", "*.mp4"),
                    ("AVI文件", "*.avi"),
                    ("所有文件", "*.*")
                ]
            )
            
        if filename:
            self.input_file.set(filename)
            # 自动设置输出文件名
            base_name = os.path.splitext(os.path.basename(filename))[0]
            output_name = f"{base_name}.funscript"
            self.output_file.set(output_name)
            
    def browse_output(self):
        """浏览输出文件"""
        filename = filedialog.asksaveasfilename(
            title="保存funscript文件",
            defaultextension=".funscript",
            filetypes=[("Funscript文件", "*.funscript"), ("所有文件", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
            
    def log_message(self, message):
        """添加日志消息"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_progress(self, value, status_text=""):
        """更新进度条"""
        self.progress['value'] = value
        self.progress_label.config(text=f"{int(value)}%")
        if status_text:
            self.status_label.config(text=status_text)
        self.root.update_idletasks()
        
    def start_processing(self):
        """开始处理"""
        if self.processing:
            return
            
        # 验证输入
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select input file")
            return
            
        if not self.output_file.get():
            messagebox.showerror("Error", "Please select output file")
            return
            
        if not os.path.exists(self.input_file.get()):
            messagebox.showerror("Error", "Input file does not exist")
            return
            
        # 开始处理
        self.processing = True
        self.process_button.config(state='disabled')
        self.progress['value'] = 0
        self.progress_label.config(text="0%")
        self.status_label.config(text="Processing...")
        self.log_text.delete(1.0, tk.END)
        
        # 在新线程中处理
        thread = threading.Thread(target=self.process_audio)
        thread.daemon = True
        thread.start()
        
    def process_audio(self):
        """处理音频文件"""
        try:
            input_file = self.input_file.get()
            
            # 如果是视频文件，先提取音频
            if self.file_type.get() == "video":
                self.log_message("Video file detected, extracting audio...")
                self.update_progress(5, "Starting video processing...")
                audio_file = self.extract_audio_from_video(input_file)
                if not audio_file:
                    raise Exception("Audio extraction failed")
                self.update_progress(30, "Audio extraction completed")
            else:
                audio_file = input_file
                self.log_message("Loading audio file...")
                self.update_progress(10, "Loading audio file...")
            
            # 创建检测器
            detector = AdvancedDrumBeatDetector(audio_file)
            
            # 加载音频
            detector.load_audio()
            self.log_message("Audio loading completed")
            self.update_progress(40, "Audio loading completed")
            
            # 检测鼓点
            self.log_message("Detecting beats...")
            self.update_progress(50, "Detecting beats...")
            detector.detect_beats_advanced(
                onset_threshold=self.onset_threshold.get(),
                beat_threshold=self.beat_threshold.get()
            )
            self.log_message("Beat detection completed")
            self.update_progress(70, "Beat detection completed")
            
            # 导出funscript
            self.log_message("Exporting funscript...")
            self.update_progress(80, "Exporting funscript...")
            detector.export_funscript(
                self.output_file.get(), 
                use_onset=self.use_onset.get()
            )
            self.log_message("Funscript export completed")
            self.update_progress(90, "Funscript export completed")
            
            # 生成可视化（如果需要）
            if self.visualize.get():
                self.log_message("Generating visualization...")
                self.update_progress(95, "Generating visualization...")
                viz_file = os.path.splitext(self.output_file.get())[0] + "_visualization.png"
                detector.visualize_detection(viz_file)
                self.log_message(f"Visualization saved: {viz_file}")
            
            self.log_message("Processing completed!")
            self.update_progress(100, "Processing completed!")
            messagebox.showinfo("Complete", "Funscript file generated successfully!")
            
        except Exception as e:
            error_msg = f"Error during processing: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", error_msg)
            
        finally:
            # 清理临时文件
            if self.temp_audio_file and os.path.exists(self.temp_audio_file):
                try:
                    os.remove(self.temp_audio_file)
                    self.log_message("Temporary file cleaned up")
                except:
                    pass
            # 恢复UI状态
            self.root.after(0, self.finish_processing)
            
    def extract_audio_from_video(self, video_path):
        """从视频中提取音频"""
        try:
            # 检查moviepy是否可用
            if not MOVIEPY_AVAILABLE:
                raise Exception("MoviePy library not found. Please install it with: pip install moviepy")
            
            self.log_message("Loading video file...")
            self.update_progress(15, "Loading video file...")
            
            # 创建临时音频文件
            temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_audio.close()
            self.temp_audio_file = temp_audio.name
            
            # 提取音频
            video = VideoFileClip(video_path)
            audio = video.audio
            
            if audio is None:
                video.close()
                raise Exception("Video file has no audio track")
            
            self.log_message("Extracting audio from video...")
            self.update_progress(20, "Extracting audio from video...")
                
            # 保存音频到临时文件
            audio.write_audiofile(self.temp_audio_file)
            
            # 关闭视频文件
            video.close()
            
            self.log_message("Audio extraction completed successfully")
            return self.temp_audio_file
            
        except Exception as e:
            # 清理临时文件
            if hasattr(self, 'temp_audio_file') and self.temp_audio_file and os.path.exists(self.temp_audio_file):
                try:
                    os.remove(self.temp_audio_file)
                except:
                    pass
            raise Exception(f"Audio extraction failed: {str(e)}")
            
    def finish_processing(self):
        """完成处理，恢复UI状态"""
        self.processing = False
        self.process_button.config(state='normal')
        self.progress['value'] = 0
        self.progress_label.config(text="0%")
        self.status_label.config(text="Ready")

def main():
    """主函数"""
    root = tk.Tk()
    app = DrumBeatDetectorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 