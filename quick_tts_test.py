#!/usr/bin/env python3
"""
Quick TTS test to generate audio for typewriter video testing
"""

import os
import sys
from text_to_speech import TextToSpeech

def generate_test_audio():
    """Generate test audio for typewriter video"""
    
    # Test text for typewriter demonstration
    test_text = """Hello! This is a demonstration of the typewriter-style narration system. Each character appears in perfect sync with the audio, and the currently spoken words are highlighted in bold. The text is organized into exactly three lines that appear with smooth fade effects. When the first three lines are complete, the next line appears automatically. This creates a professional, engaging video experience that keeps viewers focused on the content."""
    
    try:
        # Initialize TTS system with pyttsx3
        tts = TextToSpeech(engine="pyttsx3")
        
        print("🎤 Generating test audio for typewriter video...")
        print(f"📝 Text length: {len(test_text)} characters")
        
        # Generate audio
        audio_file = tts.generate_speech(test_text, "output.wav")
        
        print(f"✅ Audio generated: {audio_file}")
        print(f"📁 File size: {os.path.getsize(audio_file) / 1024:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating audio: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎵 Quick TTS Test for Typewriter Video")
    print("=" * 40)
    
    if generate_test_audio():
        print("\n🎉 Audio ready! Now you can test the typewriter video system.")
        print("💡 Run: python3 test_typewriter.py")
    else:
        print("\n💡 Audio generation failed. Check TTS system setup.") 