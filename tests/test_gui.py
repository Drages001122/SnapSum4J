import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gui import recognition_process


class TestRecognitionProcess:
    def test_recognition_process_success(self):
        mock_result = Mock()
        mock_result.rec_texts = ["12.5", "34.2", "56.7"]
        
        mock_ocr_result = [mock_result]
        
        with patch('src.gui.global_ocr') as mock_global_ocr:
            mock_global_ocr.predict.return_value = mock_ocr_result
            
            result = recognition_process("test_image.png")
            
            assert result["success"] is True
            assert result["numbers"] == ["12.5", "34.2", "56.7"]
            assert result["total"] == 103.4
            assert "elapsed_time" in result

    def test_recognition_process_with_integer_numbers(self):
        mock_result = Mock()
        mock_result.rec_texts = ["10", "20", "30"]
        
        mock_ocr_result = [mock_result]
        
        with patch('src.gui.global_ocr') as mock_global_ocr:
            mock_global_ocr.predict.return_value = mock_ocr_result
            
            result = recognition_process("test_image.png")
            
            assert result["success"] is True
            assert result["numbers"] == ["10", "20", "30"]
            assert result["total"] == 60.0

    def test_recognition_process_with_mixed_numbers(self):
        mock_result = Mock()
        mock_result.rec_texts = ["10", "20.5", "30", "40.75"]
        
        mock_ocr_result = [mock_result]
        
        with patch('src.gui.global_ocr') as mock_global_ocr:
            mock_global_ocr.predict.return_value = mock_ocr_result
            
            result = recognition_process("test_image.png")
            
            assert result["success"] is True
            assert result["numbers"] == ["10", "20.5", "30", "40.75"]
            assert result["total"] == 101.25

    def test_recognition_process_with_non_numeric_text(self):
        mock_result = Mock()
        mock_result.rec_texts = ["hello", "world", "test"]
        
        mock_ocr_result = [mock_result]
        
        with patch('src.gui.global_ocr') as mock_global_ocr:
            mock_global_ocr.predict.return_value = mock_ocr_result
            
            result = recognition_process("test_image.png")
            
            assert result["success"] is True
            assert result["numbers"] == []
            assert result["total"] == 0.0

    def test_recognition_process_with_mixed_content(self):
        mock_result = Mock()
        mock_result.rec_texts = ["10", "hello", "20.5", "world", "30"]
        
        mock_ocr_result = [mock_result]
        
        with patch('src.gui.global_ocr') as mock_global_ocr:
            mock_global_ocr.predict.return_value = mock_ocr_result
            
            result = recognition_process("test_image.png")
            
            assert result["success"] is True
            assert result["numbers"] == ["10", "20.5", "30"]
            assert result["total"] == 60.5

    def test_recognition_process_with_dict_result(self):
        mock_result = {"rec_texts": ["15.5", "25.5"]}
        
        mock_ocr_result = [mock_result]
        
        with patch('src.gui.global_ocr') as mock_global_ocr:
            mock_global_ocr.predict.return_value = mock_ocr_result
            
            result = recognition_process("test_image.png")
            
            assert result["success"] is True
            assert result["numbers"] == ["15.5", "25.5"]
            assert result["total"] == 41.0

    def test_recognition_process_exception(self):
        with patch('src.gui.global_ocr') as mock_global_ocr:
            mock_global_ocr.predict.side_effect = Exception("OCR error")
            
            result = recognition_process("test_image.png")
            
            assert result["success"] is False
            assert "error" in result
            assert "OCR error" in result["error"]

    def test_recognition_process_empty_result(self):
        mock_ocr_result = []
        
        with patch('src.gui.global_ocr') as mock_global_ocr:
            mock_global_ocr.predict.return_value = mock_ocr_result
            
            result = recognition_process("test_image.png")
            
            assert result["success"] is True
            assert result["numbers"] == []
            assert result["total"] == 0.0

    def test_recognition_process_with_negative_numbers(self):
        mock_result = Mock()
        mock_result.rec_texts = ["-10", "20", "-30.5"]
        
        mock_ocr_result = [mock_result]
        
        with patch('src.gui.global_ocr') as mock_global_ocr:
            mock_global_ocr.predict.return_value = mock_ocr_result
            
            result = recognition_process("test_image.png")
            
            assert result["success"] is True
            assert result["numbers"] == ["20"]
            assert result["total"] == 20.0

    def test_recognition_process_with_decimal_numbers(self):
        mock_result = Mock()
        mock_result.rec_texts = ["0.1", "0.2", "0.3"]
        
        mock_ocr_result = [mock_result]
        
        with patch('src.gui.global_ocr') as mock_global_ocr:
            mock_global_ocr.predict.return_value = mock_ocr_result
            
            result = recognition_process("test_image.png")
            
            assert result["success"] is True
            assert result["numbers"] == ["0.1", "0.2", "0.3"]
            assert abs(result["total"] - 0.6) < 0.0001

    def test_recognition_process_with_large_numbers(self):
        mock_result = Mock()
        mock_result.rec_texts = ["1000.5", "2000.25", "3000.75"]
        
        mock_ocr_result = [mock_result]
        
        with patch('src.gui.global_ocr') as mock_global_ocr:
            mock_global_ocr.predict.return_value = mock_ocr_result
            
            result = recognition_process("test_image.png")
            
            assert result["success"] is True
            assert result["numbers"] == ["1000.5", "2000.25", "3000.75"]
            assert result["total"] == 6001.5

    def test_recognition_process_elapsed_time(self):
        mock_result = Mock()
        mock_result.rec_texts = ["10", "20"]
        
        mock_ocr_result = [mock_result]
        
        with patch('src.gui.global_ocr') as mock_global_ocr:
            mock_global_ocr.predict.return_value = mock_ocr_result
            
            result = recognition_process("test_image.png")
            
            assert result["success"] is True
            assert "elapsed_time" in result
            assert result["elapsed_time"] >= 0
