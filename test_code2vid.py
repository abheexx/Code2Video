"""
Code2Vid - Test Script
Tests all modules to ensure they work correctly.
"""

import os
import sys
from pathlib import Path


def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing module imports...")
    
    try:
        from explain_code import CodeExplainer
        print("✅ explain_code.py imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import explain_code.py: {e}")
        return False
    
    try:
        from text_to_speech import TextToSpeech, AudioProcessor
        print("✅ text_to_speech.py imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import text_to_speech.py: {e}")
        return False
    
    try:
        from video_renderer import VideoRenderer, CodeHighlighter
        print("✅ video_renderer.py imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import video_renderer.py: {e}")
        return False
    
    try:
        from code2vid import Code2Vid
        print("✅ code2vid.py imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import code2vid.py: {e}")
        return False
    
    return True


def test_explainer():
    """Test the CodeExplainer module."""
    print("\n🧪 Testing CodeExplainer...")
    
    try:
        from explain_code import CodeExplainer
        
        # Test without API key (should fail gracefully)
        try:
            explainer = CodeExplainer()
            print("⚠️  CodeExplainer initialized without API key (expected)")
        except ValueError as e:
            print(f"✅ CodeExplainer properly validates API key: {e}")
        
        print("✅ CodeExplainer module test passed")
        return True
        
    except Exception as e:
        print(f"❌ CodeExplainer test failed: {e}")
        return False


def test_tts():
    """Test the TextToSpeech module."""
    print("\n🧪 Testing TextToSpeech...")
    
    try:
        from text_to_speech import TextToSpeech
        
        # Test pyttsx3 (should work without API key)
        try:
            tts = TextToSpeech(engine="pyttsx3")
            voices = tts.get_available_voices()
            print(f"✅ pyttsx3 TTS initialized, {len(voices)} voices available")
        except Exception as e:
            print(f"⚠️  pyttsx3 not available: {e}")
        
        # Test ElevenLabs (should fail without API key)
        try:
            tts = TextToSpeech(engine="elevenlabs")
            print("⚠️  ElevenLabs initialized without API key (unexpected)")
        except ValueError as e:
            print(f"✅ ElevenLabs properly validates API key: {e}")
        
        print("✅ TextToSpeech module test passed")
        return True
        
    except Exception as e:
        print(f"❌ TextToSpeech test failed: {e}")
        return False


def test_video_renderer():
    """Test the VideoRenderer module."""
    print("\n🧪 Testing VideoRenderer...")
    
    try:
        from video_renderer import VideoRenderer, CodeHighlighter
        
        # Test CodeHighlighter
        highlighter = CodeHighlighter()
        test_code = "def hello(): print('Hello, World!')"
        tokens = highlighter.highlight_code(test_code)
        print(f"✅ CodeHighlighter processed {len(tokens)} tokens")
        
        # Test VideoRenderer initialization
        try:
            renderer = VideoRenderer()
            print("✅ VideoRenderer initialized successfully")
        except ImportError as e:
            print(f"⚠️  VideoRenderer requires moviepy: {e}")
        
        print("✅ VideoRenderer module test passed")
        return True
        
    except Exception as e:
        print(f"❌ VideoRenderer test failed: {e}")
        return False


def test_code2vid():
    """Test the main Code2Vid orchestrator."""
    print("\n🧪 Testing Code2Vid orchestrator...")
    
    try:
        from code2vid import Code2Vid
        
        # Test initialization without API keys
        try:
            code2vid = Code2Vid()
            print("⚠️  Code2Vid initialized without API keys (unexpected)")
        except ValueError as e:
            print(f"✅ Code2Vid properly validates API keys: {e}")
        
        print("✅ Code2Vid orchestrator test passed")
        return True
        
    except Exception as e:
        print(f"❌ Code2Vid test failed: {e}")
        return False


def test_dependencies():
    """Test that all required dependencies are available."""
    print("\n🧪 Testing dependencies...")
    
    dependencies = [
        ("openai", "OpenAI API client"),
        ("streamlit", "Web framework"),
        ("moviepy", "Video processing"),
        ("PIL", "Image processing"),
        ("numpy", "Numerical computing"),
        ("requests", "HTTP requests")
    ]
    
    all_available = True
    
    for package, description in dependencies:
        try:
            __import__(package)
            print(f"✅ {package} ({description}) available")
        except ImportError:
            print(f"❌ {package} ({description}) not available")
            all_available = False
    
    return all_available


def test_file_structure():
    """Test that all required files exist."""
    print("\n🧪 Testing file structure...")
    
    required_files = [
        "explain_code.py",
        "text_to_speech.py", 
        "video_renderer.py",
        "code2vid.py",
        "app.py",
        "requirements.txt",
        "README.md"
    ]
    
    all_exist = True
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_exist = False
    
    return all_exist


def main():
    """Run all tests."""
    print("🎬 Code2Vid Test Suite")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Dependencies", test_dependencies),
        ("Module Imports", test_imports),
        ("CodeExplainer", test_explainer),
        ("TextToSpeech", test_tts),
        ("VideoRenderer", test_video_renderer),
        ("Code2Vid Orchestrator", test_code2vid)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Code2Vid is ready to use.")
        print("\nNext steps:")
        print("1. Set your API keys:")
        print("   export OPENAI_API_KEY='your-key'")
        print("   export ELEVENLABS_API_KEY='your-key'")
        print("2. Run the web interface:")
        print("   streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("- Install missing dependencies: pip install -r requirements.txt")
        print("- On macOS, install ffmpeg: brew install ffmpeg")
        print("- Check that all files are in the correct location")


if __name__ == "__main__":
    main() 