#!/usr/bin/env python3
"""
Advanced music beat detector

Includes visualization and more detailed detection options
"""

import librosa
import numpy as np
import json
import os
import argparse

class AdvancedDrumBeatDetector:
    def __init__(self, audio_path: str):
        self.audio_path = audio_path
        self.y = None
        self.sr = None
        self.onset_frames = None
        self.onset_times = None

    def load_audio(self, sr=None):
        print(f"Loading audio file: {self.audio_path}")
        self.y, self.sr = librosa.load(self.audio_path, sr=sr)
        print(f"Audio loaded - Sample rate: {self.sr}Hz, Duration: {len(self.y)/self.sr:.2f}s")

    def detect_beats_librosa(self):
        print("Detecting main musical beats (using librosa.beat.beat_track)...")
        if self.y is None or self.sr is None:
            self.load_audio()
        tempo, beat_frames = librosa.beat.beat_track(y=self.y, sr=self.sr)
        self.onset_frames = beat_frames
        self.onset_times = librosa.frames_to_time(beat_frames, sr=self.sr)
        print(f"Detected {len(self.onset_times)} main beats")

    def export_funscript(self, output_path: str = "output.funscript"):
        if self.onset_frames is None or self.onset_times is None:
            print("No beats detected, cannot export funscript. Please run detection first.")
            return
        onset_env = librosa.onset.onset_strength(y=self.y, sr=self.sr)
        times = self.onset_times
        indices = self.onset_frames
        valid_mask = indices < len(onset_env)
        indices = indices[valid_mask]
        times = times[valid_mask]
        actions = []
        t_ms_list = [int(t * 1000) for t in times]
        onset_strengths = onset_env[indices] if len(indices) > 0 else np.array([])
        max_strength = onset_strengths.max() if len(onset_strengths) > 0 else 1
        main_points = []
        for t_ms, strength in zip(t_ms_list, onset_strengths):
            # Nonlinear normalization (sqrt) to enhance high-intensity beats
            norm_strength = int(30 + (100 - 30) * ((strength / max_strength) ** 0.5)) if max_strength > 0 else 100
            norm_strength = min(100, max(30, norm_strength))
            actions.append({"at": t_ms, "pos": norm_strength})
            main_points.append((t_ms, norm_strength))
        # Insert a low point (pos=0) between each pair of main beats
        for i in range(len(main_points) - 1):
            t1, s1 = main_points[i]
            t2, s2 = main_points[i+1]
            mid = (t1 + t2) // 2
            actions.append({"at": mid, "pos": 0})
        # Sort actions by time and remove duplicates (keep first occurrence)
        actions = sorted(actions, key=lambda x: x["at"])
        deduped = []
        seen = set()
        for act in actions:
            if act["at"] not in seen:
                deduped.append(act)
                seen.add(act["at"])
        funscript = {
            "actions": deduped,
            "inverted": False,
            "metadata": {
                "creator": "AIfunScript",
                "description": "",
                "duration": int(len(self.y) / self.sr) if self.y is not None and self.sr else 0,
                "license": "",
                "notes": "",
                "performers": [],
                "script_url": "",
                "tags": [],
                "title": "",
                "type": "basic",
                "video_url": ""
            },
            "range": 100,
            "version": "1.0"
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(funscript, f, indent=2)
        print(f"Funscript exported: {output_path}")
        print(f"Total actions: {len(deduped)}")


def main():
    parser = argparse.ArgumentParser(description='Advanced music beat detection tool')
    parser.add_argument('audio_file', help='Path to audio file')
    parser.add_argument('--funscript', help='Output funscript file path', default='output.funscript')
    args = parser.parse_args()
    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file '{args.audio_file}' does not exist")
        return
    detector = AdvancedDrumBeatDetector(args.audio_file)
    try:
        detector.load_audio()
        detector.detect_beats_librosa()
        detector.export_funscript(args.funscript)
        print("\nFunscript export completed!")
    except Exception as e:
        print(f"Error during processing: {e}")

if __name__ == "__main__":
    main() 