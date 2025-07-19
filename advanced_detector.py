#!/usr/bin/env python3
"""
高级音乐鼓点检测器

包含可视化功能和更详细的检测选项
"""

import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from typing import List, Dict, Tuple, Optional
import argparse

class AdvancedDrumBeatDetector:
    def __init__(self, audio_path: str):
        """
        初始化高级鼓点检测器
        
        Args:
            audio_path: 音频文件路径
        """
        self.audio_path = audio_path
        self.y = None
        self.sr = None
        self.tempo = None
        self.beats = None
        self.onset_frames = None
        self.onset_times = None
        self.beat_times = None
        
    def load_audio(self, sr: Optional[int] = None):
        """
        加载音频文件
        
        Args:
            sr: 采样率，None表示使用原始采样率
        """
        print(f"正在加载音频文件: {self.audio_path}")
        self.y, self.sr = librosa.load(self.audio_path, sr=sr)
        print(f"音频加载完成 - 采样率: {self.sr}Hz, 时长: {len(self.y)/self.sr:.2f}秒")
        
    def detect_beats_advanced(self, hop_length: int = 512, 
                            onset_threshold: float = 0.5,
                            beat_threshold: float = 0.5):
        """
        高级鼓点检测
        
        Args:
            hop_length: 跳跃长度
            onset_threshold: onset检测阈值
            beat_threshold: 节拍检测阈值
        """
        print("正在进行高级鼓点检测...")
        
        # 获取onset检测
        self.onset_frames = librosa.onset.onset_detect(
            y=self.y,
            sr=self.sr,
            hop_length=hop_length
        )
        
        # 获取节拍时间
        self.tempo, self.beats = librosa.beat.beat_track(
            y=self.y, 
            sr=self.sr,
            hop_length=hop_length,
            onset_envelope=librosa.onset.onset_strength(
                y=self.y, sr=self.sr, hop_length=hop_length
            ),
            trim=False
        )
        
        # 转换为时间戳
        self.onset_times = librosa.frames_to_time(self.onset_frames, sr=self.sr)
        self.beat_times = librosa.frames_to_time(self.beats, sr=self.sr)
        
        tempo_value = float(self.tempo) if hasattr(self.tempo, '__iter__') else self.tempo
        print(f"检测完成 - 节拍速度: {tempo_value:.1f} BPM")
        print(f"检测到 {len(self.beat_times)} 个节拍点")
        print(f"检测到 {len(self.onset_times)} 个onset点")
        
    def visualize_detection(self, save_path: Optional[str] = None):
        """
        可视化检测结果
        
        Args:
            save_path: 保存图片的路径，None表示显示图片
        """
        if self.y is None or self.beat_times is None:
            print("请先加载音频并检测鼓点")
            return
            
        # 创建图形
        fig, axes = plt.subplots(3, 1, figsize=(15, 10))
        
        # 1. 波形图
        librosa.display.waveshow(self.y, sr=self.sr, alpha=0.6, ax=axes[0])
        axes[0].set_title('音频波形')
        axes[0].set_ylabel('振幅')
        
        # 标记节拍点
        for beat_time in self.beat_times:
            axes[0].axvline(x=beat_time, color='red', alpha=0.7, linestyle='--')
        
        # 标记onset点
        for onset_time in self.onset_times:
            axes[0].axvline(x=onset_time, color='blue', alpha=0.7, linestyle=':')
        
        # 2. 频谱图
        D = librosa.amplitude_to_db(np.abs(librosa.stft(self.y)), ref=np.max)
        librosa.display.specshow(D, sr=self.sr, x_axis='time', y_axis='log', ax=axes[1])
        axes[1].set_title('频谱图')
        
        # 3. Onset强度图
        onset_env = librosa.onset.onset_strength(y=self.y, sr=self.sr)
        times = librosa.times_like(onset_env, sr=self.sr)
        axes[2].plot(times, onset_env, label='Onset强度')
        axes[2].set_title('Onset强度')
        axes[2].set_xlabel('时间 (秒)')
        axes[2].set_ylabel('强度')
        
        # 标记检测到的onset点
        for onset_time in self.onset_times:
            axes[2].axvline(x=onset_time, color='red', alpha=0.7, linestyle='--')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"可视化图片已保存: {save_path}")
        else:
            plt.show()
            
    def get_detailed_annotations(self) -> Dict:
        """
        获取详细的注释信息
        
        Returns:
            包含详细信息的字典
        """
        beat_annotations = []
        for i, beat_time in enumerate(self.beat_times):
            annotation = {
                "timestamp": beat_time,
                "time_formatted": self._format_time(beat_time),
                "label": "beat",
                "confidence": 0.8,
                "index": i,
                "bpm_position": (i + 1) * 60 / self.tempo if self.tempo > 0 else 0
            }
            beat_annotations.append(annotation)
            
        onset_annotations = []
        for i, onset_time in enumerate(self.onset_times):
            annotation = {
                "timestamp": onset_time,
                "time_formatted": self._format_time(onset_time),
                "label": "onset",
                "confidence": 0.7,
                "index": i
            }
            onset_annotations.append(annotation)
            
        return {
            "audio_file": self.audio_path,
            "tempo": self.tempo,
            "sample_rate": self.sr,
            "duration": len(self.y) / self.sr,
            "total_beats": len(self.beat_times),
            "total_onsets": len(self.onset_times),
            "beats": beat_annotations,
            "onsets": onset_annotations
        }
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间为 MM:SS.mmm 格式"""
        minutes = int(seconds // 60)
        secs = float(seconds % 60)
        return f"{minutes:02d}:{secs:06.3f}"
    
    def export_detailed_json(self, output_path: str = "detailed_beats.json"):
        """导出详细的JSON格式"""
        data = self.get_detailed_annotations()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"详细JSON文件已导出: {output_path}")
    
    def export_csv(self, output_path: str = "beats.csv"):
        """导出为CSV格式"""
        import csv
        
        data = self.get_detailed_annotations()
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['时间戳', '格式化时间', '标签', '置信度', '索引', 'BPM位置'])
            
            for beat in data['beats']:
                writer.writerow([
                    beat['timestamp'],
                    beat['time_formatted'],
                    beat['label'],
                    beat['confidence'],
                    beat['index'],
                    beat.get('bpm_position', '')
                ])
            
            for onset in data['onsets']:
                writer.writerow([
                    onset['timestamp'],
                    onset['time_formatted'],
                    onset['label'],
                    onset['confidence'],
                    onset['index'],
                    ''
                ])
        
        print(f"CSV文件已导出: {output_path}")
    
    def print_detailed_summary(self):
        """打印详细的检测结果摘要"""
        if not self.beat_times:
            print("请先进行鼓点检测")
            return
            
        print("\n" + "="*60)
        print("高级鼓点检测结果摘要")
        print("="*60)
        print(f"音频文件: {self.audio_path}")
        tempo_value = float(self.tempo) if hasattr(self.tempo, '__iter__') else self.tempo
        print(f"节拍速度: {tempo_value:.1f} BPM")
        print(f"音频时长: {len(self.y)/self.sr:.2f} 秒")
        print(f"检测到节拍点: {len(self.beat_times)} 个")
        print(f"检测到onset点: {len(self.onset_times)} 个")
        
        # 计算节拍间隔
        if len(self.beat_times) > 1:
            intervals = np.diff(self.beat_times)
            avg_interval = np.mean(intervals)
            std_interval = np.std(intervals)
            print(f"平均节拍间隔: {avg_interval:.3f} 秒 (±{std_interval:.3f})")
        
        print("\n前10个节拍点:")
        for i, beat_time in enumerate(self.beat_times[:10]):
            print(f"  {i+1:2d}. {self._format_time(beat_time)}")
        
        if len(self.beat_times) > 10:
            print(f"  ... 还有 {len(self.beat_times) - 10} 个节拍点")
        
        print("\n前10个onset点:")
        for i, onset_time in enumerate(self.onset_times[:10]):
            print(f"  {i+1:2d}. {self._format_time(onset_time)}")
        
        if len(self.onset_times) > 10:
            print(f"  ... 还有 {len(self.onset_times) - 10} 个onset点")

    def export_funscript(self, output_path: str = "output.funscript", use_onset: bool = False):
        """
        导出为funscript格式
        Args:
            output_path: 输出文件路径
            use_onset: True使用onset点，False使用beat点
        """
        # 计算onset强度
        onset_env = librosa.onset.onset_strength(y=self.y, sr=self.sr)
        
        if use_onset:
            # 使用onset点
            times = self.onset_times
            indices = self.onset_frames
            point_type = "onset"
        else:
            # 使用beat点
            times = librosa.frames_to_time(self.beats, sr=self.sr)
            indices = self.beats
            point_type = "beat"
        
        actions = []
        if len(indices) == 0:
            print(f"没有检测到{point_type}点，无法导出funscript")
            return
            
        # 获取点对应的onset强度
        strengths = onset_env[indices]
        
        # 归一化强度到0~100
        min_strength = float(np.min(strengths))
        max_strength = float(np.max(strengths))
        
        if max_strength - min_strength < 1e-6:
            norm_strengths = np.full_like(strengths, 50)
        else:
            norm_strengths = 100 * (strengths - min_strength) / (max_strength - min_strength)
        
        for t, s in zip(times, norm_strengths):
            actions.append({
                "at": int(t * 1000),
                "pos": int(np.clip(s, 0, 100))
            })
            
        funscript = {
            "version": "1.0",
            "inverted": False,
            "actions": actions
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            import json
            json.dump(funscript, f, indent=2)
            
        print(f"funscript文件已导出: {output_path}")
        print(f"使用了 {len(actions)} 个{point_type}点")
        if not use_onset:
            tempo_value = float(self.tempo) if hasattr(self.tempo, '__iter__') else self.tempo
            print(f"平均节拍间隔: {60.0/tempo_value:.2f} 秒")
        else:
            tempo_value = float(self.tempo) if hasattr(self.tempo, '__iter__') else self.tempo
            print(f"平均onset间隔: {len(times)/len(times)*60/tempo_value:.2f} 秒")

def main():
    parser = argparse.ArgumentParser(description='高级音乐鼓点检测工具')
    parser.add_argument('audio_file', help='音频文件路径')
    parser.add_argument('--funscript', help='导出funscript文件路径')
    parser.add_argument('--use-onset', action='store_true', help='使用onset点而不是beat点')
    parser.add_argument('--visualize', action='store_true', help='生成可视化图片')
    parser.add_argument('--save-plot', help='保存可视化图片的路径')
    parser.add_argument('--json', help='导出JSON文件路径', default='detailed_beats.json')
    parser.add_argument('--csv', help='导出CSV文件路径', default='beats.csv')
    parser.add_argument('--onset-threshold', type=float, default=0.5, help='onset检测阈值')
    parser.add_argument('--beat-threshold', type=float, default=0.5, help='节拍检测阈值')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.audio_file):
        print(f"错误: 音频文件 '{args.audio_file}' 不存在")
        return
    
    # 创建检测器
    detector = AdvancedDrumBeatDetector(args.audio_file)
    
    try:
        # 加载音频
        detector.load_audio()
        
        # 检测鼓点
        detector.detect_beats_advanced(
            onset_threshold=args.onset_threshold,
            beat_threshold=args.beat_threshold
        )
        
        # 只导出funscript
        if args.funscript:
            detector.export_funscript(args.funscript, use_onset=args.use_onset)
            return
        
        # 打印详细摘要
        detector.print_detailed_summary()
        
        # 导出文件
        detector.export_detailed_json(args.json)
        detector.export_csv(args.csv)
        
        # 可视化
        if args.visualize or args.save_plot:
            detector.visualize_detection(args.save_plot)
        
        print("\n所有文件导出完成!")
        
    except Exception as e:
        print(f"处理过程中出现错误: {e}")

if __name__ == "__main__":
    main() 