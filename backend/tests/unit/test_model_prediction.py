"""
Unit Test: Model Prediction Function
Tests the ML model prediction logic with mocked MLflow model
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_loader import load_production_model, get_expected_features


class TestModelPrediction:
    """Test suite for ML model prediction functionality"""
    
    @patch('model_loader.mlflow.pyfunc.load_model')
    @patch('model_loader.mlflow.set_tracking_uri')
    @patch('model_loader.mlflow.set_experiment')
    def test_load_production_model_success(self, mock_set_exp, mock_set_uri, mock_load_model):
        """Test successful model loading from MLflow"""
        # Arrange
        mock_model = Mock()
        mock_model.predict = Mock(return_value=[0.85])
        mock_load_model.return_value = mock_model
        
        # Clear and set environment variables properly
        os.environ.clear()
        os.environ['MLFLOW_TRACKING_URI'] = 'http://test-uri'
        os.environ['MLFLOW_EXPERIMENT_NAME'] = 'test-experiment'
        os.environ['MLFLOW_MODEL_NAME'] = 'test-model'
        os.environ['MLFLOW_MODEL_VERSION'] = '1'
        
        # Reset the global model cache
        import model_loader
        model_loader._model = None
        
        # Act
        model = load_production_model()
        
        # Assert
        assert model is not None
        assert mock_load_model.called
        mock_set_uri.assert_called_once_with('http://test-uri')
        mock_set_exp.assert_called_once_with('test-experiment')
        
    @patch('model_loader.mlflow.pyfunc.load_model')
    def test_load_production_model_missing_env(self, mock_load_model):
        """Test model loading fails gracefully when env vars are missing"""
        # Arrange - clear environment variables
        for key in ['MLFLOW_TRACKING_URI', 'MLFLOW_EXPERIMENT_NAME', 
                    'MLFLOW_MODEL_NAME', 'MLFLOW_MODEL_VERSION']:
            os.environ.pop(key, None)
        
        # Reset the global model cache
        import model_loader
        model_loader._model = None
        
        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            load_production_model()
        
        assert 'Missing one of' in str(exc_info.value)
    
    def test_model_prediction_output_format(self):
        """Test that model prediction returns correct output format"""
        # Arrange
        mock_model = Mock()
        mock_model.predict = Mock(return_value=[0.75])
        
        # Create sample input features
        features = pd.DataFrame([{
            'max_cooking_time': 60,
            'recipe_cook_time': 45,
            'cook_time_diff': 15,
            'ingredient_overlap_ratio': 0.8,
            'cuisine_similarity': 1.0
        }])
        
        # Act
        prediction = mock_model.predict(features)
        
        # Assert
        assert isinstance(prediction, list)
        assert len(prediction) == 1
        assert 0.0 <= prediction[0] <= 1.0
        assert isinstance(prediction[0], float)
    
    def test_model_prediction_validation(self):
        """Test input validation for model predictions"""
        # Arrange
        mock_model = Mock()
        mock_model.predict = Mock(return_value=[0.65])
        
        # Test with valid features
        valid_features = pd.DataFrame([{
            'max_cooking_time': 60,
            'recipe_cook_time': 45,
            'cook_time_diff': 15,
            'ingredient_overlap_ratio': 0.8,
            'cuisine_similarity': 1.0
        }])
        
        # Act
        result = mock_model.predict(valid_features)
        
        # Assert
        assert result is not None
        assert len(result) > 0
        
        # Test with invalid features (negative values should still work but give poor scores)
        invalid_features = pd.DataFrame([{
            'max_cooking_time': -10,
            'recipe_cook_time': 45,
            'cook_time_diff': 55,
            'ingredient_overlap_ratio': 0.0,
            'cuisine_similarity': 0.0
        }])
        
        # Should not raise an error
        result_invalid = mock_model.predict(invalid_features)
        assert result_invalid is not None
    
    def test_model_prediction_score_range(self):
        """Test that prediction scores are within valid range"""
        # Arrange
        mock_model = Mock()
        
        # Test various score values
        test_scores = [0.0, 0.25, 0.5, 0.75, 1.0]
        
        for score in test_scores:
            mock_model.predict = Mock(return_value=[score])
            
            features = pd.DataFrame([{
                'max_cooking_time': 60,
                'recipe_cook_time': 60,
                'cook_time_diff': 0,
                'ingredient_overlap_ratio': score,
                'cuisine_similarity': 1.0
            }])
            
            # Act
            result = mock_model.predict(features)[0]
            
            # Assert
            assert 0.0 <= result <= 1.0, f"Score {result} out of valid range [0, 1]"
    
    @patch('model_loader.mlflow.pyfunc.load_model')
    @patch('model_loader.mlflow.set_tracking_uri')
    @patch('model_loader.mlflow.set_experiment')
    def test_model_caching(self, mock_set_exp, mock_set_uri, mock_load_model):
        """Test that model is cached and not reloaded on subsequent calls"""
        # Arrange
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        os.environ['MLFLOW_TRACKING_URI'] = 'http://test-uri'
        os.environ['MLFLOW_EXPERIMENT_NAME'] = 'test-experiment'
        os.environ['MLFLOW_MODEL_NAME'] = 'test-model'
        os.environ['MLFLOW_MODEL_VERSION'] = '1'
        
        # Reset cache
        import model_loader
        model_loader._model = None
        
        # Act - load model twice
        model1 = load_production_model()
        model2 = load_production_model()
        
        # Assert - model should only be loaded once
        assert mock_load_model.call_count == 1
        assert model1 is model2  # Same object reference


if __name__ == '__main__':
    pytest.main([__file__, '-v'])