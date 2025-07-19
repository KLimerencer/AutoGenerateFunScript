#!/usr/bin/env python3
"""
Music beat detection GUI interface

Provides a graphical interface to select audio files, set parameters, and generate funscripts
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import tempfile
import subprocess
import sys

# Global variable
MOVIEPY_AVAILABLE = False

# Dependency check function
def check_and_install_dependencies():
    """Check and install missing dependencies"""
    global MOVIEPY_AVAILABLE
    missing_deps = []
    
    # Check librosa
    try:
        import librosa
    except ImportError:
        missing_deps.append("librosa")
    
    # Check numpy
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    # Check matplotlib
    try:
        import matplotlib
    except ImportError:
        missing_deps.append("matplotlib")
    
    # Check moviepy
    try:
        from moviepy import VideoFileClip
        MOVIEPY_AVAILABLE = True
    except ImportError:
        missing_deps.append("moviepy")
        MOVIEPY_AVAILABLE = False
    
    # If there are missing dependencies, try to install them
    if missing_deps:
        print(f"Missing dependencies: {missing_deps}")
        print("Attempting to install missing dependencies...")
        
        try:
            for dep in missing_deps:
                print(f"Installing {dep}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"{dep} installed successfully")
            
            # Recheck moviepy
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

# Check dependencies at startup
if not check_and_install_dependencies():
    print("Warning: Some dependencies could not be installed automatically")
    print("Please install manually: pip install -r requirements.txt")

# Import detector (after dependency check)
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
        # 修复：初始化temp_audio_file属性，防止后续报错
        self.temp_audio_file = None
        
        # Check if detector is available
        if AdvancedDrumBeatDetector is None:
            messagebox.showerror("Error", "Advanced detector not available. Please check dependencies.")
            root.destroy()
            return
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.file_type = tk.StringVar(value="audio")  # "audio" or "video"
        
        # State variable
        self.processing = False
        
        # Check moviepy status
        if not MOVIEPY_AVAILABLE:
            print("Warning: MoviePy not available. Video processing will not work.")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🎵 Music Beat Detection Tool", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Dependency status
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Show dependency status
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
        
        # File selection area
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # File type selection
        ttk.Label(file_frame, text="File Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        type_frame = ttk.Frame(file_frame)
        type_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(type_frame, text="Audio File", 
                       variable=self.file_type, value="audio", 
                       command=self.on_file_type_change).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(type_frame, text="Video File", 
                       variable=self.file_type, value="video", 
                       command=self.on_file_type_change).pack(side=tk.LEFT)
        
        # Input file selection
        ttk.Label(file_frame, text="Input File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        input_entry = ttk.Entry(file_frame, textvariable=self.input_file, width=50)
        input_entry.grid(row=1, column=1, padx=(10, 5), pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_input).grid(row=1, column=2, pady=5)
        
        # Output file selection
        ttk.Label(file_frame, text="Output File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        output_entry = ttk.Entry(file_frame, textvariable=self.output_file, width=50)
        output_entry.grid(row=2, column=1, padx=(10, 5), pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_output).grid(row=2, column=2, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        self.process_button = ttk.Button(button_frame, text="Start Detection", 
                                       command=self.start_processing, style="Accent.TButton")
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT)
        
        # Progress bar frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(progress_frame, mode='determinate', length=400, maximum=100)
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Progress percentage label
        self.progress_label = ttk.Label(progress_frame, text="0%", width=5)
        self.progress_label.grid(row=0, column=1)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", font=("Arial", 10))
        self.status_label.grid(row=6, column=0, columnspan=2, pady=5)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding="5")
        log_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.log_text = tk.Text(log_frame, height=8, width=70)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def on_file_type_change(self):
        """Handle file type change"""
        # Clear current file selection
        self.input_file.set("")
        self.output_file.set("")
        
    def browse_input(self):
        """Browse input file"""
        if self.file_type.get() == "audio":
            filename = filedialog.askopenfilename(
                title="Select Audio File",
                filetypes=[
                    ("Audio Files", "*.mp3 *.wav *.flac *.m4a *.ogg"),
                    ("MP3 Files", "*.mp3"),
                    ("WAV Files", "*.wav"),
                    ("All Files", "*.*")
                ]
            )
        else:  # video
            filename = filedialog.askopenfilename(
                title="Select Video File",
                filetypes=[
                    ("Video Files", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv"),
                    ("MP4 Files", "*.mp4"),
                    ("AVI Files", "*.avi"),
                    ("All Files", "*.*")
                ]
            )
            
        if filename:
            self.input_file.set(filename)
            # Auto set output file name
            base_name = os.path.splitext(os.path.basename(filename))[0]
            output_name = f"{base_name}.funscript"
            self.output_file.set(output_name)
            
    def browse_output(self):
        """Browse output file"""
        filename = filedialog.asksaveasfilename(
            title="Save funscript file",
            defaultextension=".funscript",
            filetypes=[("Funscript Files", "*.funscript"), ("All Files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
            
    def log_message(self, message):
        """Add log message"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_progress(self, value, status_text=""):
        """Update progress bar"""
        self.progress['value'] = value
        self.progress_label.config(text=f"{int(value)}%")
        if status_text:
            self.status_label.config(text=status_text)
        self.root.update_idletasks()
        
    def start_processing(self):
        """Start processing"""
        if self.processing:
            return
            
        # Validate input
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select input file")
            return
            
        if not self.output_file.get():
            messagebox.showerror("Error", "Please select output file")
            return
            
        if not os.path.exists(self.input_file.get()):
            messagebox.showerror("Error", "Input file does not exist")
            return
            
        # Start processing
        self.processing = True
        self.process_button.config(state='disabled')
        self.progress['value'] = 0
        self.progress_label.config(text="0%")
        self.status_label.config(text="Processing...")
        self.log_text.delete(1.0, tk.END)
        
        # Process in a new thread
        thread = threading.Thread(target=self.process_audio)
        thread.daemon = True
        thread.start()
        
    def process_audio(self):
        """Process audio file"""
        try:
            input_file = self.input_file.get()
            
            # If video file, extract audio first
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
            
            # Create detector
            detector = AdvancedDrumBeatDetector(audio_file)
            
            # Load audio
            detector.load_audio()
            self.log_message("Audio loading completed")
            self.update_progress(40, "Audio loading completed")
            
            # Detect beats
            self.log_message("Detecting beats...")
            self.update_progress(50, "Detecting beats...")
            detector.detect_beats_librosa()
            self.log_message("Beat detection completed")
            self.update_progress(70, "Beat detection completed")
            
            # Export funscript
            self.log_message("Exporting funscript...")
            self.update_progress(80, "Exporting funscript...")
            detector.export_funscript(self.output_file.get())
            self.log_message("Funscript export completed")
            self.update_progress(90, "Funscript export completed")
            
            self.log_message("Processing completed!")
            self.update_progress(100, "Processing completed!")
            messagebox.showinfo("Complete", "Funscript file generated successfully!")
            
        except Exception as e:
            error_msg = f"Error during processing: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", error_msg)
            
        finally:
            # Clean up temp files
            if self.temp_audio_file and os.path.exists(self.temp_audio_file):
                try:
                    os.remove(self.temp_audio_file)
                    self.log_message("Temporary file cleaned up")
                except:
                    pass
            # Restore UI state
            self.root.after(0, self.finish_processing)
            
    def extract_audio_from_video(self, video_path):
        """Extract audio from video"""
        try:
            # Check if moviepy is available
            if not MOVIEPY_AVAILABLE:
                raise Exception("MoviePy library not found. Please install it with: pip install moviepy")
            
            self.log_message("Loading video file...")
            self.update_progress(15, "Loading video file...")
            
            # Create temp audio file
            temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_audio.close()
            self.temp_audio_file = temp_audio.name
            
            # Extract audio
            from moviepy import VideoFileClip
            video = VideoFileClip(video_path)
            audio = video.audio
            
            if audio is None:
                video.close()
                raise Exception("Video file has no audio track")
            
            self.log_message("Extracting audio from video...")
            self.update_progress(20, "Extracting audio from video...")
                
            # Save audio to temp file
            audio.write_audiofile(self.temp_audio_file)
            
            # Close video file
            video.close()
            
            self.log_message("Audio extraction completed successfully")
            return self.temp_audio_file
            
        except Exception as e:
            # Clean up temp files
            if hasattr(self, 'temp_audio_file') and self.temp_audio_file and os.path.exists(self.temp_audio_file):
                try:
                    os.remove(self.temp_audio_file)
                except:
                    pass
            raise Exception(f"Audio extraction failed: {str(e)}")
            
    def finish_processing(self):
        """Finish processing, restore UI state"""
        self.processing = False
        self.process_button.config(state='normal')
        self.progress['value'] = 0
        self.progress_label.config(text="0%")
        self.status_label.config(text="Ready")

def main():
    """Main function"""
    root = tk.Tk()
    app = DrumBeatDetectorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 