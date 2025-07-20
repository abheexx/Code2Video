"""
Code2Vid - Demo Script
Demonstrates how to use the Code2Vid system with a simple example.
"""

import os
import json
from pathlib import Path

def demo_explanation_only():
    """Demo the code explanation feature (no API keys required for setup)."""
    print("🎬 Code2Vid Demo - Explanation Only")
    print("=" * 50)
    
    # Example code
    example_code = """
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

# Test the algorithm
numbers = [3, 6, 8, 10, 1, 2, 1]
sorted_nums = quicksort(numbers)
print(f"Original: {numbers}")
print(f"Sorted: {sorted_nums}")
"""
    
    print("📝 Example Code:")
    print(example_code)
    
    print("\n🔧 To generate an explanation, you would:")
    print("1. Set your OpenAI API key:")
    print("   export OPENAI_API_KEY='your-key-here'")
    print("2. Run the explanation:")
    print("   from explain_code import CodeExplainer")
    print("   explainer = CodeExplainer()")
    print("   explanation = explainer.explain_code(example_code)")
    
    print("\n📊 Expected Output Structure:")
    expected_output = {
        "title": "Understanding QuickSort Algorithm",
        "overview": "A divide-and-conquer sorting algorithm that efficiently sorts arrays",
        "step_by_step": [
            "First, we check if the array has 1 or fewer elements",
            "We select a pivot element from the middle of the array",
            "We partition the array into three parts: less than, equal to, and greater than pivot",
            "We recursively sort the left and right partitions",
            "Finally, we combine the sorted partitions with the pivot"
        ],
        "key_takeaways": [
            "QuickSort uses divide-and-conquer strategy",
            "Average time complexity is O(n log n)",
            "Pivot selection affects performance"
        ],
        "narration_script": "Welcome to our explanation of the QuickSort algorithm! This is a powerful divide-and-conquer sorting algorithm that efficiently sorts arrays by partitioning them around a pivot element..."
    }
    
    print(json.dumps(expected_output, indent=2))
    
    return example_code

def demo_tts():
    """Demo the text-to-speech feature."""
    print("\n🔊 Text-to-Speech Demo")
    print("=" * 30)
    
    print("Available TTS Engines:")
    print("1. ElevenLabs (High Quality)")
    print("   - Requires API key")
    print("   - Natural-sounding voices")
    print("   - Multiple voice options")
    
    print("\n2. pyttsx3 (Free)")
    print("   - No API key required")
    print("   - System voices")
    print("   - Lower quality but functional")
    
    print("\n🔧 To use TTS:")
    print("from text_to_speech import TextToSpeech")
    print("tts = TextToSpeech(engine='pyttsx3')  # or 'elevenlabs'")
    print("audio_path = tts.generate_speech('Your text here')")

def demo_video_rendering():
    """Demo the video rendering feature."""
    print("\n🎥 Video Rendering Demo")
    print("=" * 30)
    
    print("Video Features:")
    print("✅ Syntax highlighting for code")
    print("✅ Dark theme with professional styling")
    print("✅ Synchronized audio and video")
    print("✅ Multiple video styles (simple/animated)")
    print("✅ Customizable resolution and FPS")
    
    print("\n🔧 To create a video:")
    print("from video_renderer import VideoRenderer")
    print("renderer = VideoRenderer()")
    print("video_path = renderer.create_video(code, audio_path, explanation)")

def demo_web_interface():
    """Demo the web interface."""
    print("\n🌐 Web Interface Demo")
    print("=" * 30)
    
    print("Streamlit Features:")
    print("✅ Beautiful, modern UI")
    print("✅ Real-time code preview")
    print("✅ Multiple example code snippets")
    print("✅ Configurable settings")
    print("✅ Download functionality")
    
    print("\n🔧 To run the web interface:")
    print("streamlit run app.py")
    print("Then open http://localhost:8501 in your browser")

def demo_complete_pipeline():
    """Demo the complete pipeline."""
    print("\n🚀 Complete Pipeline Demo")
    print("=" * 40)
    
    print("Full Code2Vid Pipeline:")
    print("1. 📝 Code Input → User provides code snippet")
    print("2. 🤖 AI Explanation → GPT-4 generates explanation")
    print("3. 🔊 Text-to-Speech → Convert explanation to audio")
    print("4. 🎥 Video Rendering → Create final video with code overlay")
    print("5. 📤 Output → Download video, audio, and explanation files")
    
    print("\n🔧 Complete usage example:")
    print("from code2vid import Code2Vid")
    print("code2vid = Code2Vid(openai_api_key='your-key')")
    print("result = code2vid.create_video(")
    print("    code='your code here',")
    print("    language='Python',")
    print("    difficulty_level='beginner',")
    print("    voice='default',")
    print("    video_style='simple'")
    print(")")

def main():
    """Run the complete demo."""
    print("🎬 Welcome to Code2Vid!")
    print("Turn code snippets into narrated explainer videos with AI")
    print("=" * 60)
    
    # Run all demos
    demo_explanation_only()
    demo_tts()
    demo_video_rendering()
    demo_web_interface()
    demo_complete_pipeline()
    
    print("\n" + "=" * 60)
    print("🎉 Demo Complete!")
    print("\n📋 Next Steps:")
    print("1. Set up your API keys:")
    print("   export OPENAI_API_KEY='your-openai-key'")
    print("   export ELEVENLABS_API_KEY='your-elevenlabs-key'  # Optional")
    print("\n2. Try the web interface:")
    print("   streamlit run app.py")
    print("\n3. Or use the command line:")
    print("   python3 code2vid.py")
    print("\n4. Check the README.md for detailed documentation")
    
    print("\n💡 Tips:")
    print("- Start with simple code snippets (under 50 lines)")
    print("- Use 'beginner' difficulty for clearer explanations")
    print("- Try both 'simple' and 'animated' video styles")
    print("- ElevenLabs provides better audio quality than pyttsx3")
    
    print("\n🔗 Project Structure:")
    print("Code2Vid/")
    print("├── explain_code.py      # AI code explanation")
    print("├── text_to_speech.py    # TTS functionality")
    print("├── video_renderer.py    # Video creation")
    print("├── code2vid.py         # Main orchestrator")
    print("├── app.py              # Web interface")
    print("├── requirements.txt    # Dependencies")
    print("├── README.md          # Documentation")
    print("└── demo.py            # This demo script")

if __name__ == "__main__":
    main() 