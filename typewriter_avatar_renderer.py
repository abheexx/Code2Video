import os
import json
import math
from typing import List, Dict, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from dataclasses import dataclass
import re

@dataclass
class WordTiming:
    word: str
    start_time: float
    end_time: float
    char_positions: List[float]  # Character-by-character timing

@dataclass
class LineData:
    words: List[WordTiming]
    start_time: float
    end_time: float
    text: str
    max_chars: int

class TypewriterAvatarRenderer:
    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_duration = 1.0 / fps
        
        # Load avatar image
        self.avatar_img = self._load_avatar()
        
        # Font settings
        self.font_size = 32
        self.font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", self.font_size)
        self.font_bold = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", self.font_size)
        
        # Text positioning
        self.text_margin = 50
        self.line_height = 40
        self.max_lines = 3
        self.max_chars_per_line = 60
        
        # Animation settings
        self.fade_duration = 0.5  # seconds
        self.typewriter_speed = 0.05  # seconds per character (adjustable)
        
        # Colors
        self.text_color = (255, 255, 255)  # White
        self.bold_color = (255, 255, 255)  # White (bold)
        self.background_color = (0, 0, 0, 180)  # Dark translucent background
        
    def _load_avatar(self) -> Image.Image:
        """Load and process avatar image"""
        avatar_path = "avatar_circular.png"
        if os.path.exists(avatar_path):
            img = Image.open(avatar_path).convert("RGBA")
            # Resize to reasonable size
            target_size = (200, 200)
            img = img.resize(target_size, Image.Resampling.LANCZOS)
            return img
        else:
            # Create a placeholder avatar
            img = Image.new("RGBA", (200, 200), (100, 150, 255, 255))
            return img
    
    def extract_word_timings(self, audio_file: str, text: str) -> List[WordTiming]:
        """Extract word-level timings using Whisper or estimate based on text length"""
        try:
            import whisper
            model = whisper.load_model("base")
            result = model.transcribe(audio_file, word_timestamps=True)
            
            word_timings = []
            for segment in result["segments"]:
                for word_info in segment.get("words", []):
                    word_timings.append(WordTiming(
                        word=word_info["word"].strip(),
                        start_time=word_info["start"],
                        end_time=word_info["end"],
                        char_positions=self._estimate_char_timings(word_info["word"], word_info["start"], word_info["end"])
                    ))
            return word_timings
        except ImportError:
            # Fallback: estimate timings based on text length and audio duration
            return self._estimate_word_timings(text, self._get_audio_duration(audio_file))
    
    def _estimate_char_timings(self, word: str, start_time: float, end_time: float) -> List[float]:
        """Estimate character-by-character timing within a word"""
        duration = end_time - start_time
        char_count = len(word)
        if char_count == 0:
            return []
        
        timings = []
        for i in range(char_count):
            char_time = start_time + (duration * i / char_count)
            timings.append(char_time)
        return timings
    
    def _estimate_word_timings(self, text: str, audio_duration: float) -> List[WordTiming]:
        """Estimate word timings based on text length and audio duration"""
        words = text.split()
        if not words:
            return []
        
        # Estimate average word duration
        avg_word_duration = audio_duration / len(words)
        
        word_timings = []
        current_time = 0.0
        
        for word in words:
            word_duration = avg_word_duration * (len(word) / 5.0)  # Adjust for word length
            end_time = current_time + word_duration
            
            word_timings.append(WordTiming(
                word=word,
                start_time=current_time,
                end_time=end_time,
                char_positions=self._estimate_char_timings(word, current_time, end_time)
            ))
            
            current_time = end_time
        
        return word_timings
    
    def _get_audio_duration(self, audio_file: str) -> float:
        """Get audio duration using ffprobe"""
        import subprocess
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "csv=p=0", audio_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return float(result.stdout.strip())
        except:
            return 10.0  # Default fallback
    
    def organize_text_into_lines(self, word_timings: List[WordTiming]) -> List[LineData]:
        """Organize words into lines with proper timing"""
        lines = []
        current_line_words = []
        current_line_text = ""
        current_line_start = 0.0
        
        for word_timing in word_timings:
            # Check if adding this word would exceed line length
            test_text = current_line_text + " " + word_timing.word if current_line_text else word_timing.word
            
            if len(test_text) > self.max_chars_per_line and current_line_words:
                # Complete current line
                line_end = word_timing.start_time
                lines.append(LineData(
                    words=current_line_words.copy(),
                    start_time=current_line_start,
                    end_time=line_end,
                    text=current_line_text,
                    max_chars=len(current_line_text)
                ))
                
                # Start new line
                current_line_words = [word_timing]
                current_line_text = word_timing.word
                current_line_start = word_timing.start_time
            else:
                # Add to current line
                current_line_words.append(word_timing)
                current_line_text = test_text
        
        # Add final line
        if current_line_words:
            lines.append(LineData(
                words=current_line_words,
                start_time=current_line_start,
                end_time=word_timings[-1].end_time if word_timings else current_line_start,
                text=current_line_text,
                max_chars=len(current_line_text)
            ))
        
        return lines
    
    def get_visible_lines_at_time(self, lines: List[LineData], time: float) -> List[Tuple[LineData, float]]:
        """Get which lines should be visible at a given time with fade effects"""
        visible_lines = []
        
        for i, line in enumerate(lines):
            # Check if line should be visible
            if time >= line.start_time - self.fade_duration:
                # Calculate fade progress
                if time < line.start_time:
                    fade_progress = (time - (line.start_time - self.fade_duration)) / self.fade_duration
                elif time > line.end_time:
                    fade_progress = 1.0 - ((time - line.end_time) / self.fade_duration)
                    if fade_progress <= 0:
                        continue
                else:
                    fade_progress = 1.0
                
                visible_lines.append((line, fade_progress))
                
                # Only show max_lines at a time
                if len(visible_lines) >= self.max_lines:
                    break
        
        return visible_lines
    
    def get_typing_progress(self, line: LineData, time: float) -> int:
        """Get how many characters should be typed at the current time"""
        if time < line.start_time:
            return 0
        
        # Calculate typing progress based on character timings
        total_chars = 0
        typed_chars = 0
        
        for word in line.words:
            word_chars = len(word.word)
            total_chars += word_chars
            
            if time >= word.end_time:
                typed_chars += word_chars
            elif time >= word.start_time:
                # Partial word typing
                for char_time in word.char_positions:
                    if time >= char_time:
                        typed_chars += 1
                    else:
                        break
        
        return min(typed_chars, len(line.text))
    
    def get_bold_positions(self, line: LineData, time: float) -> List[int]:
        """Get which characters should be bold at the current time"""
        bold_positions = []
        char_index = 0
        
        for word in line.words:
            word_chars = len(word.word)
            
            if time >= word.start_time and time <= word.end_time:
                # Word is currently being spoken - bold it
                for i in range(word_chars):
                    bold_positions.append(char_index + i)
            
            char_index += word_chars + 1  # +1 for space
        
        return bold_positions
    
    def render_frame(self, time: float, lines: List[LineData]) -> Image.Image:
        """Render a single frame with typewriter effect and proper timing"""
        # Create base image
        img = Image.new("RGBA", (self.width, self.height), (240, 248, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw avatar
        avatar_x = (self.width - self.avatar_img.width) // 2
        avatar_y = self.height // 2 - 150
        img.paste(self.avatar_img, (avatar_x, avatar_y), self.avatar_img)
        
        # Get visible lines
        visible_lines = self.get_visible_lines_at_time(lines, time)
        
        # Calculate text position (centered, above bottom)
        text_y = self.height - 200 - (len(visible_lines) * self.line_height)
        
        for i, (line, fade_progress) in enumerate(visible_lines):
            # Calculate typing progress
            typing_progress = self.get_typing_progress(line, time)
            bold_positions = self.get_bold_positions(line, time)
            
            # Get text to display (typewriter effect)
            display_text = line.text[:typing_progress]
            
            # Calculate text position
            text_bbox = draw.textbbox((0, 0), display_text, font=self.font)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = (self.width - text_width) // 2
            
            # Draw background if needed
            if fade_progress < 1.0:
                bg_alpha = int(255 * fade_progress)
                bg_color = (*self.background_color[:3], bg_alpha)
                bg_bbox = draw.textbbox((text_x - 10, text_y + i * self.line_height - 5), 
                                      display_text, font=self.font)
                bg_width = bg_bbox[2] - bg_bbox[0] + 20
                bg_height = bg_bbox[3] - bg_bbox[1] + 10
                
                bg_img = Image.new("RGBA", (bg_width, bg_height), bg_color)
                img.paste(bg_img, (text_x - 10, text_y + i * self.line_height - 5), bg_img)
            
            # Draw text with character-by-character styling
            current_x = text_x
            for char_idx, char in enumerate(display_text):
                # Choose font based on bold position
                if char_idx in bold_positions:
                    font_to_use = self.font_bold
                    color = self.bold_color
                else:
                    font_to_use = self.font
                    color = self.text_color
                
                # Apply fade effect
                alpha = int(255 * fade_progress)
                color_with_alpha = (*color, alpha)
                
                # Draw character
                draw.text((current_x, text_y + i * self.line_height), char, 
                         font=font_to_use, fill=color_with_alpha)
                
                # Move to next character position
                char_bbox = draw.textbbox((0, 0), char, font=font_to_use)
                current_x += char_bbox[2] - char_bbox[0]
        
        return img
    
    def create_video(self, audio_file: str, text: str, output_file: str = "typewriter_video.mp4"):
        """Create the complete typewriter-style video"""
        print("Extracting word timings...")
        word_timings = self.extract_word_timings(audio_file, text)
        
        print("Organizing text into lines...")
        lines = self.organize_text_into_lines(word_timings)
        
        print(f"Created {len(lines)} lines of text")
        for i, line in enumerate(lines):
            print(f"Line {i+1}: '{line.text}' ({line.start_time:.2f}s - {line.end_time:.2f}s)")
        
        # Calculate video duration
        total_duration = max(line.end_time for line in lines) + self.fade_duration
        total_frames = int(total_duration * self.fps)
        
        print(f"Creating video: {total_frames} frames at {self.fps} FPS")
        
        # Create temporary directory for frames
        os.makedirs("temp_frames", exist_ok=True)
        
        # Generate frames
        for frame_idx in range(total_frames):
            time = frame_idx * self.frame_duration
            
            # Render frame
            frame = self.render_frame(time, lines)
            
            # Save frame
            frame_path = f"temp_frames/frame_{frame_idx:06d}.png"
            frame.save(frame_path)
            
            if frame_idx % 30 == 0:
                print(f"Generated frame {frame_idx}/{total_frames}")
        
        # Combine with audio using ffmpeg
        print("Combining frames with audio...")
        import subprocess
        
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(self.fps),
            "-i", "temp_frames/frame_%06d.png",
            "-i", audio_file,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-shortest",
            output_file
        ]
        
        subprocess.run(cmd, check=True)
        
        # Clean up
        import shutil
        shutil.rmtree("temp_frames")
        
        print(f"Video created: {output_file}")
        return output_file

# Example usage
if __name__ == "__main__":
    renderer = TypewriterAvatarRenderer()
    
    # Example text and audio
    text = "Hello! This is a demonstration of the typewriter-style narration system. Each character appears in sync with the audio, and the currently spoken words are highlighted in bold. The text is organized into lines that appear with a smooth fade effect."
    
    # Create video (replace with your audio file)
    renderer.create_video("output.wav", text, "typewriter_demo.mp4") 