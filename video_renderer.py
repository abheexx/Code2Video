"""
Code2Vid - Video Renderer Module
Builds videos with code overlay and synchronized narration.
"""

import os
import json
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import tempfile
import re

try:
    from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, ColorClip, TextClip, ImageClip, ImageSequenceClip  # type: ignore
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Import typewriter renderer
try:
    from typewriter_avatar_renderer import TypewriterAvatarRenderer
    TYPEWRITER_AVAILABLE = True
except ImportError:
    TYPEWRITER_AVAILABLE = False


class CodeHighlighter:
    """Handles syntax highlighting for code in videos."""
    
    def __init__(self):
        """Initialize the code highlighter."""
        self.colors = {
            'keyword': '#FF6B6B',      # Red for keywords
            'string': '#4ECDC4',       # Teal for strings
            'comment': '#95A5A6',      # Gray for comments
            'function': '#F39C12',     # Orange for functions
            'number': '#9B59B6',       # Purple for numbers
            'operator': '#E74C3C',     # Red for operators
            'default': '#2C3E50'       # Dark blue for default text
        }
        
        # Python keywords
        self.python_keywords = {
            'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except',
            'finally', 'with', 'as', 'import', 'from', 'return', 'yield', 'break',
            'continue', 'pass', 'raise', 'assert', 'del', 'global', 'nonlocal',
            'lambda', 'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is'
        }
    
    def highlight_code(self, code: str, language: str = 'python') -> List[Dict[str, Any]]:
        """
        Parse code and return highlighted tokens.
        
        Args:
            code: Source code to highlight
            language: Programming language
            
        Returns:
            List of tokens with color information
        """
        if language.lower() == 'python':
            return self._highlight_python(code)
        else:
            return self._highlight_generic(code)
    
    def _highlight_python(self, code: str) -> List[Dict[str, Any]]:
        """Highlight Python code."""
        tokens = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines):
            # Split line into tokens
            parts = re.split(r'(\s+|[^\w\s])', line)
            
            for part in parts:
                if not part:
                    continue
                    
                token_type = 'default'
                
                # Determine token type
                if part.strip() in self.python_keywords:
                    token_type = 'keyword'
                elif part.startswith('#') or part.startswith('"""') or part.startswith("'''"):
                    token_type = 'comment'
                elif part.startswith('"') or part.startswith("'"):
                    token_type = 'string'
                elif part.replace('.', '').replace('_', '').isdigit():
                    token_type = 'number'
                elif part in '+-*/=<>!&|^~':
                    token_type = 'operator'
                elif part.strip() and part[0].isalpha() and '(' in part:
                    token_type = 'function'
                
                tokens.append({
                    'text': part,
                    'type': token_type,
                    'color': self.colors[token_type],
                    'line': line_num
                })
        
        return tokens


class VideoRenderer:
    """Handles video rendering with code overlay and narration."""
    
    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 30):
        """
        Initialize the video renderer.
        
        Args:
            width: Video width in pixels
            height: Video height in pixels
            fps: Frames per second
        """
        if not MOVIEPY_AVAILABLE:
            raise ImportError("moviepy not available. Install with: pip install moviepy")
        
        self.width = width
        self.height = height
        self.fps = fps
        self.highlighter = CodeHighlighter()
        
        # Video styling - convert hex to RGB
        self.background_color = (30, 30, 30)  # Dark background (#1E1E1E)
        self.code_bg_color = (45, 45, 48)     # Slightly lighter for code area (#2D2D30)
        self.text_color = (255, 255, 255)     # White text (#FFFFFF)
        
    def create_video(self, code: str, audio_path: str, explanation: Dict[str, Any],
                    output_path: str = "code_explanation.mp4", animated: bool = True, narration_text: str = None) -> str:
        """
        Create a video with code overlay and narration.
        
        Args:
            code: Source code to display
            audio_path: Path to narration audio file
            explanation: Explanation dictionary from explain_code.py
            output_path: Path to save the video
            animated: Whether to create an animated video with avatar
            
        Returns:
            Path to the generated video
        """
        try:
            # Use avatar animated renderer with speech bubble
            if animated:
                try:
                    from avatar_renderer import AvatarVideoRenderer
                    avatar_renderer = AvatarVideoRenderer(1280, 720, 24)  # Lower resolution and FPS
                    return avatar_renderer.create_animated_video(
                        code=code,
                        audio_path=audio_path,
                        explanation=explanation,
                        output_path=output_path,
                        narration_text=narration_text
                    )
                except Exception as e:
                    print(f"Avatar animated rendering failed, falling back to static: {e}")
            
            # Load audio for static rendering
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            
            # Create background
            background = ColorClip(size=(self.width, self.height), 
                                 color=self.background_color, 
                                 duration=duration)
            
            # Create a high-quality video with clear text
            try:
                from PIL import Image, ImageDraw, ImageFont
                import numpy as np
                
                # Create a high-quality image with clear text
                img = Image.new('RGB', (self.width, self.height), color=self.background_color)
                draw = ImageDraw.Draw(img)
                
                # Try to load better fonts
                try:
                    # Try to use system fonts for better quality
                    font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
                    font_code = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 32)
                    font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
                except:
                    try:
                        # Fallback to other system fonts
                        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
                        font_code = ImageFont.truetype("/System/Library/Fonts/Monaco.ttc", 32)
                        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
                    except:
                        # Final fallback to default
                        font_large = ImageFont.load_default()
                        font_code = ImageFont.load_default()
                        font_small = ImageFont.load_default()
                
                # Draw title with better positioning and styling
                title_text = explanation.get('title', 'Code Explanation')
                # Center the title
                title_bbox = draw.textbbox((0, 0), title_text, font=font_large)
                title_width = title_bbox[2] - title_bbox[0]
                title_x = (self.width - title_width) // 2
                draw.text((title_x, 80), title_text, fill='white', font=font_large)
                
                # Draw code with better formatting and syntax highlighting
                code_lines = code.strip().split('\n')
                y_pos = 200
                line_height = 40
                
                # Limit to reasonable number of lines for readability
                max_lines = min(15, len(code_lines))
                
                for i, line in enumerate(code_lines[:max_lines]):
                    # Add line numbers for better readability
                    line_num = f"{i+1:2d} "
                    line_with_num = line_num + line
                    
                    # Draw line number in gray
                    draw.text((50, y_pos), line_num, fill='#888888', font=font_code)
                    
                    # Draw code line in white
                    draw.text((50 + len(line_num) * 12, y_pos), line, fill='white', font=font_code)
                    
                    y_pos += line_height
                
                # Add a subtle border around the code area
                border_color = (60, 60, 60)
                draw.rectangle([40, 180, self.width - 40, y_pos + 20], outline=border_color, width=2)
                
                # Add explanation text at the bottom if there's space
                if y_pos < self.height - 150:
                    explanation_text = explanation.get('overview', 'Code explanation generated by AI')
                    # Wrap text to fit width
                    words = explanation_text.split()
                    lines = []
                    current_line = ""
                    for word in words:
                        test_line = current_line + " " + word if current_line else word
                        bbox = draw.textbbox((0, 0), test_line, font=font_small)
                        if bbox[2] - bbox[0] < self.width - 100:
                            current_line = test_line
                        else:
                            if current_line:
                                lines.append(current_line)
                            current_line = word
                    if current_line:
                        lines.append(current_line)
                    
                    # Draw explanation lines
                    y_pos = self.height - 120
                    for line in lines[:3]:  # Limit to 3 lines
                        bbox = draw.textbbox((0, 0), line, font=font_small)
                        line_width = bbox[2] - bbox[0]
                        line_x = (self.width - line_width) // 2
                        draw.text((line_x, y_pos), line, fill='#CCCCCC', font=font_small)
                        y_pos += 30
                
                # Convert PIL image to numpy array
                img_array = np.array(img)
                
                # Create video clip from image
                image_clip = ImageClip(img_array, duration=duration)
                
                # Add audio
                final_video = image_clip.with_audio(audio)
                
            except Exception as img_error:
                # Fallback to just background with audio if image creation fails
                print(f"Image creation failed, using fallback: {img_error}")
                final_video = background.with_audio(audio)
            
            # Write video file
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Video rendering failed: {str(e)}")
    
    def _create_code_overlay(self, code: str, duration: float):
        """Create a text clip with highlighted code."""
        try:
            # Highlight the code
            tokens = self.highlighter.highlight_code(code)
            
            # Create formatted text with HTML-like tags for colors
            formatted_code = ""
            for token in tokens:
                color = token['color'].replace('#', '')
                formatted_code += f'<span color="#{color}">{token["text"]}</span>'
            
            # Create text clip with minimal parameters to avoid font issues
            code_clip = TextClip(
                text=formatted_code,
                color='white',
                bg_color='#2D2D30',  # Use hex string for TextClip
                method='label'
            ).with_position(('center', 200)).with_duration(duration)
            
            return code_clip
            
        except Exception as e:
            # Fallback to simple text if highlighting fails
            code_clip = TextClip(
                text=code,
                color='white',
                bg_color='#2D2D30',  # Use hex string for TextClip
                method='label'
            ).with_position(('center', 200)).with_duration(duration)
            
            return code_clip
    
    def _create_title_overlay(self, title: str, duration: float):
        """Create a title overlay."""
        title_clip = TextClip(
            text=title,
            color='white',
            bg_color='transparent',
            method='label'
        ).with_position(('center', 50)).with_duration(duration)
        
        return title_clip
    
    def create_typewriter_video(self, code: str, audio_path: str, 
                               explanation: Dict[str, Any],
                               output_path: str = "typewriter_video.mp4") -> str:
        """
        Create a typewriter-style video with perfect audio sync and character-by-character animation.
        
        Args:
            code: Source code to display
            audio_path: Path to narration audio file
            explanation: Explanation dictionary
            output_path: Path to save the video
            
        Returns:
            Path to the generated video
        """
        if not TYPEWRITER_AVAILABLE:
            raise ImportError("TypewriterAvatarRenderer not available")
        
        try:
            # Get narration text
            narration_text = explanation.get('narration', '')
            if not narration_text:
                # Fallback to explanation text
                narration_text = explanation.get('explanation', 'Code explanation video')
            
            # Create typewriter renderer
            renderer = TypewriterAvatarRenderer(1280, 720, 24)  # Lower resolution for performance
            
            # Create the video
            output_file = renderer.create_video(audio_path, narration_text, output_path)
            
            print(f"Typewriter video created: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"Typewriter video creation failed: {e}")
            # Fallback to regular animated video
            return self.create_animated_code_video(code, audio_path, explanation, output_path)

    def create_animated_code_video(self, code: str, audio_path: str, 
                                 explanation: Dict[str, Any],
                                 output_path: str = "animated_code.mp4") -> str:
        """
        Create an animated video that highlights code sections as they're explained.
        
        Args:
            code: Source code to display
            audio_path: Path to narration audio file
            explanation: Explanation dictionary
            output_path: Path to save the video
            
        Returns:
            Path to the generated video
        """
        try:
            # Load audio
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            
            # Create background
            background = ColorClip(size=(self.width, self.height), 
                                 color=self.background_color, 
                                 duration=duration)
            
            # Create a high-quality video with clear text
            try:
                from PIL import Image, ImageDraw, ImageFont
                import numpy as np
                
                # Create a high-quality image with clear text
                img = Image.new('RGB', (self.width, self.height), color=self.background_color)
                draw = ImageDraw.Draw(img)
                
                # Try to load better fonts
                try:
                    # Try to use system fonts for better quality
                    font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
                    font_code = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 32)
                    font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
                except:
                    try:
                        # Fallback to other system fonts
                        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
                        font_code = ImageFont.truetype("/System/Library/Fonts/Monaco.ttc", 32)
                        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
                    except:
                        # Final fallback to default
                        font_large = ImageFont.load_default()
                        font_code = ImageFont.load_default()
                        font_small = ImageFont.load_default()
                
                # Draw title with better positioning and styling
                title_text = explanation.get('title', 'Code Explanation')
                # Center the title
                title_bbox = draw.textbbox((0, 0), title_text, font=font_large)
                title_width = title_bbox[2] - title_bbox[0]
                title_x = (self.width - title_width) // 2
                draw.text((title_x, 80), title_text, fill='white', font=font_large)
                
                # Draw code with better formatting and syntax highlighting
                code_lines = code.strip().split('\n')
                y_pos = 200
                line_height = 40
                
                # Limit to reasonable number of lines for readability
                max_lines = min(15, len(code_lines))
                
                for i, line in enumerate(code_lines[:max_lines]):
                    # Add line numbers for better readability
                    line_num = f"{i+1:2d} "
                    line_with_num = line_num + line
                    
                    # Draw line number in gray
                    draw.text((50, y_pos), line_num, fill='#888888', font=font_code)
                    
                    # Draw code line in white
                    draw.text((50 + len(line_num) * 12, y_pos), line, fill='white', font=font_code)
                    
                    y_pos += line_height
                
                # Add a subtle border around the code area
                border_color = (60, 60, 60)
                draw.rectangle([40, 180, self.width - 40, y_pos + 20], outline=border_color, width=2)
                
                # Add explanation text at the bottom if there's space
                if y_pos < self.height - 150:
                    explanation_text = explanation.get('overview', 'Code explanation generated by AI')
                    # Wrap text to fit width
                    words = explanation_text.split()
                    lines = []
                    current_line = ""
                    for word in words:
                        test_line = current_line + " " + word if current_line else word
                        bbox = draw.textbbox((0, 0), test_line, font=font_small)
                        if bbox[2] - bbox[0] < self.width - 100:
                            current_line = test_line
                        else:
                            if current_line:
                                lines.append(current_line)
                            current_line = word
                    if current_line:
                        lines.append(current_line)
                    
                    # Draw explanation lines
                    y_pos = self.height - 120
                    for line in lines[:3]:  # Limit to 3 lines
                        bbox = draw.textbbox((0, 0), line, font=font_small)
                        line_width = bbox[2] - bbox[0]
                        line_x = (self.width - line_width) // 2
                        draw.text((line_x, y_pos), line, fill='#CCCCCC', font=font_small)
                        y_pos += 30
                
                # Convert PIL image to numpy array
                img_array = np.array(img)
                
                # Create video clip from image
                image_clip = ImageClip(img_array, duration=duration)
                
                # Add audio
                final_video = image_clip.with_audio(audio)
                
            except Exception as img_error:
                # Fallback to just background with audio if image creation fails
                print(f"Image creation failed, using fallback: {img_error}")
                final_video = background.with_audio(audio)
            
            # Write video file
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Animated video rendering failed: {str(e)}")
    
    def _split_code_into_sections(self, code: str, explanation: Dict[str, Any]) -> List[str]:
        """Split code into sections based on explanation steps."""
        lines = code.split('\n')
        step_by_step = explanation.get('step_by_step', [])
        
        if not step_by_step:
            # If no step-by-step explanation, split by function/class
            sections = []
            current_section = []
            
            for line in lines:
                if line.strip().startswith(('def ', 'class ')) and current_section:
                    sections.append('\n'.join(current_section))
                    current_section = []
                current_section.append(line)
            
            if current_section:
                sections.append('\n'.join(current_section))
            
            return sections if sections else [code]
        else:
            # Split based on number of explanation steps
            num_sections = len(step_by_step)
            lines_per_section = len(lines) // num_sections
            
            sections = []
            for i in range(num_sections):
                start_line = i * lines_per_section
                end_line = (i + 1) * lines_per_section if i < num_sections - 1 else len(lines)
                section = '\n'.join(lines[start_line:end_line])
                sections.append(section)
            
            return sections


def main():
    """Example usage of the VideoRenderer module."""
    
    # Example code and explanation
    example_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
"""
    
    example_explanation = {
        "title": "Understanding the Fibonacci Function",
        "overview": "A recursive function that calculates Fibonacci numbers",
        "step_by_step": [
            "First, we define a function that takes a parameter n",
            "We check if n is 0 or 1, returning n directly",
            "Otherwise, we recursively call the function twice",
            "Finally, we test the function with a loop"
        ],
        "key_takeaways": [
            "Recursion can solve mathematical problems elegantly",
            "Base cases are crucial for recursive functions"
        ],
        "narration_script": "Welcome to our code explanation! Today we're looking at a simple Python function that calculates the Fibonacci sequence. This function uses recursion to solve a classic mathematical problem."
    }
    
    try:
        # Check if we have an audio file to work with
        audio_path = "narration.wav"
        if not os.path.exists(audio_path):
            print("No audio file found. Please run text_to_speech.py first to generate narration.")
            return
        
        # Create video renderer
        renderer = VideoRenderer()
        
        # Create simple video
        print("Creating video with code overlay...")
        video_path = renderer.create_video(example_code, audio_path, example_explanation, "code_video.mp4")
        print(f"Video saved to: {video_path}")
        
        # Create animated video
        print("Creating animated video...")
        animated_path = renderer.create_animated_code_video(example_code, audio_path, example_explanation, "animated_video.mp4")
        print(f"Animated video saved to: {animated_path}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 