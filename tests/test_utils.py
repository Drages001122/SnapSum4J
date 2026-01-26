import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import get_resource_path


class TestGetResourcePath:
    def test_get_resource_path_normal_case(self):
        result = get_resource_path("models/test.txt")
        assert "models" in result
        assert "test.txt" in result

    def test_get_resource_path_with_subdirectory(self):
        result = get_resource_path("src/utils.py")
        assert "src" in result
        assert "utils.py" in result

    def test_get_resource_path_empty_string(self):
        result = get_resource_path("")
        assert result.endswith(os.sep) or result == "."

    def test_get_resource_path_with_absolute_path(self):
        test_path = "models/PP-OCRv5_server_det"
        result = get_resource_path(test_path)
        assert test_path in result

    def test_get_resource_path_with_special_chars(self):
        test_path = "models/test_file-123.txt"
        result = get_resource_path(test_path)
        assert "test_file-123.txt" in result

    def test_get_resource_path_consistency(self):
        path1 = get_resource_path("test/path")
        path2 = get_resource_path("test/path")
        assert path1 == path2

    def test_get_resource_path_with_nested_directories(self):
        test_path = "models/PP-OCRv5_server_det/config.json"
        result = get_resource_path(test_path)
        assert "PP-OCRv5_server_det" in result
        assert "config.json" in result
