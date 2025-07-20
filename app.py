"""
Code2Vid - Streamlit Web Interface
A beautiful web interface for creating narrated code explanation videos.
"""

import streamlit as st
import os
import json
from pathlib import Path
import tempfile
from typing import Dict, Any

from code2vid import Code2Vid


def main():
    """Main Streamlit application."""
    
    # Page configuration
    st.set_page_config(
        page_title="Code2Vid - AI Code Explanation Videos",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .code-input {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        border: 2px solid #e9ecef;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🎬 Code2Vid</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Turn code snippets into narrated explainer videos with AI</p>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Keys
        st.subheader("API Keys")
        openai_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Required for GPT-4 code explanation generation"
        )
        
        elevenlabs_api_key = st.text_input(
            "ElevenLabs API Key",
            type="password",
            help="Required for high-quality text-to-speech"
        )
        
        # Video settings
        st.subheader("Video Settings")
        language = st.selectbox(
            "Programming Language",
            ["Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", "TypeScript"],
            index=0
        )
        
        difficulty_level = st.selectbox(
            "Target Audience",
            ["beginner", "intermediate", "advanced"],
            index=0
        )
        
        tts_engine = st.selectbox(
            "TTS Engine",
            ["elevenlabs", "pyttsx3"],
            index=0,
            help="ElevenLabs provides higher quality, pyttsx3 is free but may not work on all macOS systems"
        )
        
        voice = st.selectbox(
            "Voice",
            ["default", "male", "female", "british", "deep"],
            index=0
        )
        
        video_style = st.selectbox(
            "Video Style",
            ["animated", "typewriter", "simple"],
            index=0,
            help="Animated: Interactive with avatar and code highlighting, Typewriter: Perfect audio sync with character-by-character animation, Simple: static code display"
        )
        
        # Example code snippets
        st.subheader("📚 Examples")
        example_choice = st.selectbox(
            "Load Example",
            ["None", "Fibonacci Function", "Bubble Sort", "Class Example", "Quick Sort", "Binary Search"],
            index=0
        )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💻 Code Input")
        
        # Load example code if selected
        example_code = ""
        if example_choice != "None":
            example_code = get_example_code(example_choice)
        
        # Code input
        code_input = st.text_area(
            "Paste your code here:",
            value=example_code,
            height=400,
            placeholder="def hello_world():\n    print('Hello, World!')\n\nhello_world()",
            help="Enter the code you want to explain in a video"
        )
        
        # Generate button
        if st.button("🎬 Generate Video", type="primary", use_container_width=True):
            if not code_input.strip():
                st.error("Please enter some code to explain.")
            elif not openai_api_key:
                st.error("OpenAI API key is required for code explanation generation.")
            else:
                generate_video(code_input, language, difficulty_level, tts_engine, voice, video_style, openai_api_key, elevenlabs_api_key)
    
    with col2:
        st.header("📊 Preview")
        
        if code_input.strip():
            # Show code statistics
            lines = len(code_input.split('\n'))
            chars = len(code_input)
            st.metric("Lines of Code", lines)
            st.metric("Characters", chars)
            
            # Show syntax highlighting preview
            st.subheader("Code Preview")
            st.code(code_input, language=language.lower())
            
            # Estimate video duration
            if code_input.strip():
                estimated_duration = estimate_video_duration(code_input)
                st.metric("Estimated Duration", f"{estimated_duration:.1f}s")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>Built with ❤️ using Streamlit, OpenAI GPT-4, and ElevenLabs</p>
        <p>Create engaging educational content from your code snippets!</p>
    </div>
    """, unsafe_allow_html=True)


def get_example_code(example_name: str) -> str:
    """Get example code based on selection."""
    examples = {
        "Fibonacci Function": """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
""",
        
        "Bubble Sort": """
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
        
        "Class Example": """
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
""",
        
        "Quick Sort": """
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

# Test
numbers = [3, 6, 8, 10, 1, 2, 1]
sorted_nums = quicksort(numbers)
print(f"Original: {numbers}")
print(f"Sorted: {sorted_nums}")
""",
        
        "Binary Search": """
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# Test
sorted_array = [1, 3, 5, 7, 9, 11, 13, 15]
target = 7
result = binary_search(sorted_array, target)
print(f"Array: {sorted_array}")
print(f"Target: {target}")
print(f"Found at index: {result}")
"""
    }
    
    return examples.get(example_name, "")


def estimate_video_duration(code: str) -> float:
    """Estimate video duration based on code complexity."""
    lines = len(code.split('\n'))
    chars = len(code)
    
    # Rough estimation: 2-3 seconds per line + base time
    base_time = 5.0  # Base time for intro/outro
    time_per_line = 2.5
    estimated_time = base_time + (lines * time_per_line)
    
    return min(estimated_time, 300)  # Cap at 5 minutes


def generate_video(code: str, language: str, difficulty_level: str, 
                  tts_engine: str, voice: str, video_style: str,
                  openai_api_key: str, elevenlabs_api_key: str):
    """Generate the video using Code2Vid."""
    
    # Create progress container
    progress_container = st.container()
    result_container = st.container()
    
    with progress_container:
        st.info("🚀 Starting video generation...")
        
        try:
            # Initialize Code2Vid
            with st.spinner("Initializing Code2Vid..."):
                code2vid = Code2Vid(
                    openai_api_key=openai_api_key,
                    elevenlabs_api_key=elevenlabs_api_key,
                    tts_engine=tts_engine
                )
            
            # Generate video
            with st.spinner("Generating explanation..."):
                result = code2vid.create_video(
                    code=code,
                    language=language,
                    difficulty_level=difficulty_level,
                    voice=voice,
                    video_style=video_style,
                    output_name="streamlit_generated"
                )
            
            # Show results
            with result_container:
                st.success("✅ Video generated successfully!")
                
                # Display results in columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Title", result['title'])
                    st.metric("Duration", f"{result['duration']:.1f}s")
                
                with col2:
                    # Show explanation preview
                    if os.path.exists(result['explanation']):
                        with open(result['explanation'], 'r') as f:
                            explanation_data = json.load(f)
                        
                        st.subheader("📝 Explanation Preview")
                        st.write(f"**Overview:** {explanation_data.get('overview', 'N/A')}")
                        
                        if 'key_takeaways' in explanation_data:
                            st.write("**Key Takeaways:**")
                            for takeaway in explanation_data['key_takeaways']:
                                st.write(f"• {takeaway}")
                
                with col3:
                    # Download buttons
                    st.subheader("📥 Download Files")
                    
                    # Video download
                    if os.path.exists(result['video']):
                        with open(result['video'], 'rb') as f:
                            st.download_button(
                                label="📹 Download Video",
                                data=f.read(),
                                file_name=f"{result['title'].replace(' ', '_')}.mp4",
                                mime="video/mp4",
                                use_container_width=True
                            )
                    
                    # Audio download
                    if os.path.exists(result['audio']):
                        with open(result['audio'], 'rb') as f:
                            st.download_button(
                                label="🔊 Download Audio",
                                data=f.read(),
                                file_name=f"{result['title'].replace(' ', '_')}.wav",
                                mime="audio/wav",
                                use_container_width=True
                            )
                    
                    # Explanation download
                    if os.path.exists(result['explanation']):
                        with open(result['explanation'], 'r') as f:
                            st.download_button(
                                label="📄 Download Explanation",
                                data=f.read(),
                                file_name=f"{result['title'].replace(' ', '_')}_explanation.json",
                                mime="application/json",
                                use_container_width=True
                            )
                
                # Show video preview (if possible)
                if os.path.exists(result['video']):
                    st.subheader("🎬 Video Preview")
                    st.video(result['video'])
                
        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ Error generating video: {error_msg}")
            
            # Provide helpful suggestions based on error type
            if "pyttsx3" in error_msg.lower() and "objc" in error_msg.lower():
                st.error("💡 **Solution**: Switch to 'ElevenLabs' TTS engine in the sidebar. pyttsx3 doesn't work well on some macOS systems.")
            elif "openai" in error_msg.lower():
                st.error("💡 **Solution**: Please add your OpenAI API key in the sidebar.")
            elif "elevenlabs" in error_msg.lower():
                st.error("💡 **Solution**: Add your ElevenLabs API key or switch to 'pyttsx3' TTS engine.")
            else:
                st.error("Please check your API keys and try again.")


if __name__ == "__main__":
    main() 