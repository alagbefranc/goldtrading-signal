#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ML-based Signal Validator for Forex Trading Bot
Uses machine learning to validate and enhance trading signals
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib
import os
import logging
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)

class SignalValidator:
    """Machine learning model for validating trading signals"""
    
    def __init__(self):
        """Initialize the signal validator"""
        self.model = None
        self.scaler = StandardScaler()
        self.model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
        
        # Create models directory if it doesn't exist
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
            
        # Try to load pre-trained model if available
        model_path = os.path.join(self.model_dir, 'signal_validator.joblib')
        if os.path.exists(model_path):
            self.load_model(model_path)
        else:
            # Create a basic pre-trained model if none exists
            self._create_basic_model()
    
    def _extract_features(self, data: pd.DataFrame, order_blocks: List[Dict], fvgs: List[Dict]) -> np.ndarray:
        """
        Extract features from price data and detected patterns
        
        Args:
            data: OHLCV DataFrame
            order_blocks: List of detected order blocks
            fvgs: List of detected fair value gaps
            
        Returns:
            Feature array for ML model
        """
        features = []
        
        # Price action features
        close = data['close'].values
        high = data['high'].values
        low = data['low'].values
        volume = data['volume'].values
        
        # Basic features
        current_price = close[-1]
        price_change = close[-1] - close[-2]
        price_change_pct = price_change / close[-2] * 100
        
        # Volatility features
        recent_volatility = np.std(close[-5:]) / np.mean(close[-5:]) * 100
        longer_volatility = np.std(close[-20:]) / np.mean(close[-20:]) * 100
        
        # Volume features
        volume_change = volume[-1] / np.mean(volume[-5:])
        
        # Order block features
        bullish_ob_count = sum(1 for ob in order_blocks if ob['type'] == 'bullish')
        bearish_ob_count = sum(1 for ob in order_blocks if ob['type'] == 'bearish')
        recent_ob_distance = 0
        if order_blocks:
            if order_blocks[-1]['type'] == 'bullish':
                recent_ob_distance = (current_price - order_blocks[-1]['low']) / current_price * 100
            else:
                recent_ob_distance = (order_blocks[-1]['high'] - current_price) / current_price * 100
        
        # Fair value gap features
        bullish_fvg_count = sum(1 for fvg in fvgs if fvg['type'] == 'bullish')
        bearish_fvg_count = sum(1 for fvg in fvgs if fvg['type'] == 'bearish')
        recent_fvg_size = 0
        if fvgs:
            recent_fvg_size = fvgs[-1]['size']
            
        # Combine all features
        features = [
            price_change_pct,
            recent_volatility,
            longer_volatility,
            volume_change,
            bullish_ob_count,
            bearish_ob_count,
            recent_ob_distance,
            bullish_fvg_count,
            bearish_fvg_count,
            recent_fvg_size
        ]
        
        return np.array(features).reshape(1, -1)
    
    def build_model(self):
        """Build the machine learning model"""
        # Create model pipeline with preprocessing
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        
        self.model = pipeline
        return self.model
    
    def train(self, training_data: List[Dict], labels: List[int]):
        """
        Train the model with historical signals and their outcomes
        
        Args:
            training_data: List of dictionaries with 'data', 'order_blocks', and 'fvgs'
            labels: 1 for successful signals, 0 for unsuccessful ones
        
        Returns:
            Dictionary with training metrics
        """
        # Extract features from training data
        X = np.vstack([
            self._extract_features(item['data'], item['order_blocks'], item['fvgs']) 
            for item in training_data
        ])
        y = np.array(labels)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Build model if not exists
        if self.model is None:
            self.build_model()
        
        # Grid search for best parameters
        param_grid = {
            'classifier__n_estimators': [50, 100, 200],
            'classifier__max_depth': [None, 10, 20, 30],
            'classifier__min_samples_split': [2, 5, 10]
        }
        
        grid_search = GridSearchCV(
            self.model,
            param_grid,
            cv=5,
            scoring='f1',
            n_jobs=-1
        )
        
        # Train the model
        grid_search.fit(X_train, y_train)
        self.model = grid_search.best_estimator_
        
        # Evaluate on test set
        y_pred = self.model.predict(X_test)
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'best_params': grid_search.best_params_
        }
        
        # Save the model
        self.save_model()
        
        logger.info(f"Model trained with metrics: {metrics}")
        return metrics
    
    def validate_signal(self, 
                        data: pd.DataFrame,
                        order_blocks: List[Dict],
                        fvgs: List[Dict],
                        signal_type: str) -> Dict:
        """
        Validate a trading signal using the ML model
        
        Args:
            data: OHLCV DataFrame
            order_blocks: Detected order blocks
            fvgs: Detected fair value gaps
            signal_type: 'BUY' or 'SELL'
            
        Returns:
            Dictionary with validation results
        """
        if self.model is None:
            logger.warning("Model not trained yet, loading default if available")
            if not self.load_model():
                logger.error("No model available for signal validation")
                return {
                    "valid": True,  # Default to True if no model available
                    "confidence": 0.5,
                    "reason": "No trained model available for validation"
                }
        
        # Extract features
        features = self._extract_features(data, order_blocks, fvgs)
        
        # Get prediction probability
        try:
            probability = self.model.predict_proba(features)[0]
            # Index 1 is probability of class 1 (successful signal)
            confidence = probability[1] if len(probability) > 1 else 0.5
            
            # Determine if signal is valid based on confidence threshold
            valid = confidence >= 0.6
            
            # Determine if signal type is consistent with features
            consistent_direction = True
            if signal_type == 'BUY' and len(fvgs) > 0:
                # For BUY signals, we should have more bullish FVGs
                bullish_count = sum(1 for fvg in fvgs if fvg['type'] == 'bullish')
                bearish_count = len(fvgs) - bullish_count
                consistent_direction = bullish_count >= bearish_count
            elif signal_type == 'SELL' and len(fvgs) > 0:
                # For SELL signals, we should have more bearish FVGs
                bearish_count = sum(1 for fvg in fvgs if fvg['type'] == 'bearish')
                bullish_count = len(fvgs) - bearish_count
                consistent_direction = bearish_count >= bullish_count
            
            # Generate reason based on consistency and confidence
            if not valid:
                reason = "Low confidence in signal success based on historical patterns"
            elif not consistent_direction:
                reason = f"Signal direction ({signal_type}) inconsistent with detected patterns"
                valid = False  # Override validation if direction is inconsistent
            else:
                reason = "Signal validated based on pattern recognition"
            
            return {
                "valid": valid,
                "confidence": float(confidence),
                "reason": reason
            }
            
        except Exception as e:
            logger.error(f"Error validating signal: {e}")
            return {
                "valid": True,  # Default to True on error
                "confidence": 0.5,
                "reason": f"Error during validation: {str(e)}"
            }
    
    def save_model(self, filename='signal_validator.joblib'):
        """Save the model to disk"""
        if self.model is not None:
            path = os.path.join(self.model_dir, filename)
            joblib.dump(self.model, path)
            logger.info(f"Model saved to {path}")
            return True
        else:
            logger.error("No model to save")
            return False
    
    def _create_basic_model(self):
        """Create a basic pre-trained model with reasonable defaults"""
        logger.info("Creating a basic pre-trained model for signal validation")
        try:
            # Create a simple gradient boosting model with sensible defaults for forex trading
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=3,
                min_samples_split=5,
                random_state=42
            )
            
            # Create some synthetic data for initial training
            # This isn't ideal, but it allows the model to work immediately
            # Later, it will be replaced by real trading data
            
            # Features: [price_change_pct, volatility, range_size, 
            #           bullish_blocks, bearish_blocks, bullish_fvgs, bearish_fvgs]
            X_synthetic = np.array([
                # Synthetic BUY signals - good patterns
                [0.05, 0.02, 0.8, 3, 1, 2, 0],   # Strong bullish
                [0.03, 0.01, 0.7, 2, 1, 2, 1],   # Moderate bullish
                [0.02, 0.02, 0.5, 2, 0, 1, 0],   # Mild bullish
                
                # Synthetic BUY signals - bad patterns
                [0.01, 0.05, 0.3, 1, 3, 0, 2],   # Not good for BUY
                [0.005, 0.04, 0.2, 0, 2, 0, 2],  # Bad for BUY
                
                # Synthetic SELL signals - good patterns
                [-0.05, 0.02, 0.8, 1, 3, 0, 2],  # Strong bearish
                [-0.03, 0.01, 0.7, 1, 2, 1, 2],  # Moderate bearish
                [-0.02, 0.02, 0.5, 0, 2, 0, 1],  # Mild bearish
                
                # Synthetic SELL signals - bad patterns
                [-0.01, 0.05, 0.3, 3, 1, 2, 0],  # Not good for SELL
                [-0.005, 0.04, 0.2, 2, 0, 2, 0]  # Bad for SELL
            ])
            
            # Labels: 1 = successful trade, 0 = unsuccessful trade
            y_synthetic = np.array([1, 1, 1, 0, 0, 1, 1, 1, 0, 0])
            
            # Fit the model on synthetic data
            self.model.fit(X_synthetic, y_synthetic)
            
            # Save this model as baseline
            path = os.path.join(self.model_dir, 'signal_validator.joblib')
            joblib.dump(self.model, path)
            logger.info("Basic pre-trained model created and saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating basic model: {e}")
            self.model = None
            return False
    
    def load_model(self, filename='signal_validator.joblib'):
        """Load the model from disk"""
        try:
            path = os.path.join(self.model_dir, filename)
            if os.path.exists(path):
                self.model = joblib.load(path)
                logger.info(f"Model loaded from {path}")
                return True
            else:
                logger.warning(f"Model file {path} not found")
                return False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

# Create singleton instance
signal_validator = SignalValidator()
