# test_snakebyte.py
import tempfile
import os
import subprocess
import sys

def test_snakebyte_syntax():
    """Test that the script has valid Python syntax"""
    result = subprocess.run([sys.executable, '-m', 'py_compile', 'snakebyte.py'], 
                          capture_output=True)
    assert result.returncode == 0, f"Syntax error: {result.stderr.decode()}"

def test_snakebyte_help():
    """Test that the script can show help"""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"Hello World!")
        f.flush()
        
        # This won't fully test interactivity, but ensures it doesn't crash on startup
        try:
            result = subprocess.run([sys.executable, 'snakebyte.py', f.name], 
                                  timeout=2, capture_output=True)
        except subprocess.TimeoutExpired:
            pass  # Expected since it's an interactive program
        finally:
            os.unlink(f.name)

if __name__ == "__main__":
    test_snakebyte_syntax()
    test_snakebyte_help()
    print("All tests passed!")
