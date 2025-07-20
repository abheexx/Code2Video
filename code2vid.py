"""
Code2Vid - Main Orchestrator
Combines all modules to create narrated explainer videos from code snippets.
"""

import os
import json
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

from explain_code import CodeExplainer
from text_to_speech import TextToSpeech, AudioProcessor
from video_renderer import VideoRenderer


class Code2Vid:
    """Main class that orchestrates the entire video creation process."""
    
    def __init__(self, openai_api_key: Optional[str] = None, 
                 elevenlabs_api_key: Optional[str] = None,
                 tts_engine: str = "elevenlabs"):
        """
        Initialize Code2Vid with API keys and settings.
        
        Args:
            openai_api_key: OpenAI API key for GPT-4
            elevenlabs_api_key: ElevenLabs API key for TTS
            tts_engine: TTS engine to use ('elevenlabs' or 'pyttsx3')
        """
        self.explainer = CodeExplainer(api_key=openai_api_key)
        self.tts = TextToSpeech(engine=tts_engine, api_key=elevenlabs_api_key)
        self.renderer = VideoRenderer()
        self.audio_processor = AudioProcessor()
        
        # Create output directory
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def create_video(self, code: str, language: str = "Python", 
                    difficulty_level: str = "beginner",
                    voice: str = "default", 
                    video_style: str = "simple",
                    output_name: Optional[str] = None) -> Dict[str, str]:
        """
        Create a complete narrated video from code.
        
        Args:
            code: Source code to explain
            language: Programming language
            difficulty_level: Target audience level
            voice: TTS voice to use
            video_style: Video style ('simple' or 'animated')
            output_name: Base name for output files (without extension)
            
        Returns:
            Dictionary with paths to generated files
        """
        
        if not output_name:
            output_name = f"code_explanation_{language.lower()}"
        
        try:
            print("🎬 Starting Code2Vid pipeline...")
            
            # Step 1: Generate explanation
            print("📝 Generating code explanation...")
            explanation = self.explainer.explain_code(code, language, difficulty_level)
            
            # Save explanation
            explanation_path = self.output_dir / f"{output_name}_explanation.json"
            self.explainer.save_explanation(explanation, str(explanation_path))
            print(f"✅ Explanation saved to: {explanation_path}")
            
            # Step 2: Generate speech
            print("🔊 Converting explanation to speech...")
            narration_script = explanation.get('narration_script', '')
            audio_path = self.output_dir / f"{output_name}_narration.wav"
            
            self.tts.generate_speech(narration_script, str(audio_path), voice)
            print(f"✅ Audio saved to: {audio_path}")
            
            # Step 3: Create video
            print("🎥 Rendering video...")
            video_path = self.output_dir / f"{output_name}_{video_style}.mp4"
            
            # Handle different video styles
            if video_style == "typewriter":
                # Use typewriter renderer for perfect audio sync
                self.renderer.create_typewriter_video(
                    code, str(audio_path), explanation, str(video_path)
                )
            else:
                # Use regular renderer
                self.renderer.create_video(
                    code, str(audio_path), explanation, str(video_path), 
                    animated=(video_style == "animated"),
                    narration_text=narration_script
                )
            
            print(f"✅ Video saved to: {video_path}")
            
            # Return all generated file paths
            return {
                "explanation": str(explanation_path),
                "audio": str(audio_path),
                "video": str(video_path),
                "title": explanation.get('title', 'Code Explanation'),
                "duration": self.tts.estimate_duration(narration_script)
            }
            
        except Exception as e:
            raise Exception(f"Video creation failed: {str(e)}")
    
    def create_batch_videos(self, code_snippets: Dict[str, str], 
                          language: str = "Python",
                          difficulty_level: str = "beginner") -> Dict[str, Dict[str, str]]:
        """
        Create videos for multiple code snippets.
        
        Args:
            code_snippets: Dictionary mapping snippet names to code
            language: Programming language
            difficulty_level: Target audience level
            
        Returns:
            Dictionary mapping snippet names to their output files
        """
        results = {}
        
        for name, code in code_snippets.items():
            print(f"\n🎬 Processing: {name}")
            try:
                result = self.create_video(
                    code, language, difficulty_level, output_name=name
                )
                results[name] = result
                print(f"✅ Completed: {name}")
            except Exception as e:
                print(f"❌ Failed: {name} - {e}")
                results[name] = {"error": str(e)}
        
        return results
    
    def get_available_voices(self) -> list:
        """Get list of available TTS voices."""
        return self.tts.get_available_voices()
    
    def preview_explanation(self, code: str, language: str = "Python", 
                          difficulty_level: str = "beginner") -> Dict[str, Any]:
        """
        Generate and return explanation without creating audio/video.
        
        Args:
            code: Source code to explain
            language: Programming language
            difficulty_level: Target audience level
            
        Returns:
            Explanation dictionary
        """
        return self.explainer.explain_code(code, language, difficulty_level)


def main():
    """Example usage of the Code2Vid pipeline."""
    
    # Example code snippets
    code_snippets = {
        "fibonacci": """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
""",
        
        "bubble_sort": """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# Example usage
numbers = [64, 34, 25, 12, 22, 11, 90]
sorted_numbers = bubble_sort(numbers.copy())
print(f"Original: {numbers}")
print(f"Sorted: {sorted_numbers}")
""",
        
        "class_example": """
class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def get_history(self):
        return self.history

# Usage
calc = Calculator()
print(calc.add(5, 3))
print(calc.add(10, 20))
print("History:", calc.get_history())
"""
    }
    
    try:
        # Initialize Code2Vid
        print("🚀 Initializing Code2Vid...")
        code2vid = Code2Vid()
        
        # Show available voices
        voices = code2vid.get_available_voices()
        print(f"Available voices: {voices}")
        
        # Create a single video
        print("\n🎬 Creating single video...")
        result = code2vid.create_video(
            code_snippets["fibonacci"],
            language="Python",
            difficulty_level="beginner",
            voice="default",
            video_style="simple",
            output_name="fibonacci_demo"
        )
        
        print(f"\n✅ Video created successfully!")
        print(f"Title: {result['title']}")
        print(f"Duration: {result['duration']:.2f} seconds")
        print(f"Files created:")
        for file_type, path in result.items():
            if file_type not in ['title', 'duration']:
                print(f"  {file_type}: {path}")
        
        # Create batch videos
        print("\n🎬 Creating batch videos...")
        batch_results = code2vid.create_batch_videos(
            code_snippets,
            language="Python",
            difficulty_level="beginner"
        )
        
        print(f"\n✅ Batch processing completed!")
        for name, result in batch_results.items():
            if "error" not in result:
                print(f"  {name}: {result['video']}")
            else:
                print(f"  {name}: ❌ {result['error']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 