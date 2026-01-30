"""Basic tests for MzymeD."""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestMzymeDStructure(unittest.TestCase):
    """Test MzymeD package structure."""
    
    def test_imports(self):
        """Test that main modules can be imported."""
        try:
            import mzymed
            self.assertTrue(hasattr(mzymed, '__version__'))
        except ImportError as e:
            self.fail(f"Failed to import mzymed: {e}")
    
    def test_file_structure(self):
        """Test that key files exist."""
        base_dir = os.path.join(os.path.dirname(__file__), '..')
        
        required_files = [
            'README.md',
            'requirements.txt',
            'setup.py',
            'app.py',
            'example_usage.py',
        ]
        
        for file in required_files:
            filepath = os.path.join(base_dir, file)
            self.assertTrue(os.path.exists(filepath), f"Missing required file: {file}")
    
    def test_package_structure(self):
        """Test that package structure is correct."""
        base_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
        
        required_dirs = [
            'mzymed',
            'mzymed/models',
            'mzymed/analysis',
            'mzymed/visualization',
        ]
        
        for dir_path in required_dirs:
            full_path = os.path.join(base_dir, dir_path)
            self.assertTrue(os.path.isdir(full_path), f"Missing required directory: {dir_path}")


if __name__ == '__main__':
    unittest.main()
