#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LSTM Price Prediction Model for Forex Trading Bot
"""

import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential, load_model, save_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.preprocessing import MinMaxScaler
import os
import logging

logger = logging.getLogger(__name__)

class PricePredictionModel:
    """LSTM model for predicting price movements"""
    
    def __init__(self, sequence_length=60, prediction_horizon=5):
        """
        Initialize the price prediction model
        
        Args:
            sequence_length: Number of past time steps to use as input
            prediction_horizon: Number of future time steps to predict
        """
        self.sequence_length = sequence_length
        self.prediction_horizon = prediction_horizon
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
        
        # Create models directory if it doesn't exist
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
    
    def _prepare_data(self, df):
        """
        Prepare data for LSTM model
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            X: Input sequences
            y: Target values
        """
        # Select features
        data = df[['open', 'high', 'low', 'close', 'volume']].values
        
        # Normalize data
        scaled_data = self.scaler.fit_transform(data)
        
        # Create sequences
        X, y = [], []
        for i in range(self.sequence_length, len(scaled_data) - self.prediction_horizon):
            X.append(scaled_data[i - self.sequence_length:i])
            # Predict the close price N steps ahead
            future_close = scaled_data[i + self.prediction_horizon - 1, 3]  # 3 is the index of close price
            y.append(future_close)
            
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape):
        """
        Build the LSTM model architecture
        
        Args:
            input_shape: Shape of input data (sequence_length, features)
        """
        model = Sequential()
        
        # First LSTM layer with dropout
        model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
        model.add(Dropout(0.2))
        
        # Second LSTM layer with dropout
        model.add(LSTM(units=50, return_sequences=False))
        model.add(Dropout(0.2))
        
        # Output layer
        model.add(Dense(1))
        
        # Compile model
        model.compile(optimizer='adam', loss='mean_squared_error')
        
        self.model = model
        return model
    
    def train(self, df, epochs=50, batch_size=32, validation_split=0.2):
        """
        Train the LSTM model
        
        Args:
            df: DataFrame with OHLCV data
            epochs: Number of training epochs
            batch_size: Batch size
            validation_split: Fraction of data to use for validation
            
        Returns:
            Training history
        """
        X, y = self._prepare_data(df)
        
        # Build model if not already built
        if self.model is None:
            self.build_model((X.shape[1], X.shape[2]))
        
        # Setup callbacks
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
            ModelCheckpoint(os.path.join(self.model_dir, 'lstm_price_predictor.h5'), 
                            save_best_only=True)
        ]
        
        # Train the model
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=callbacks,
            verbose=1
        )
        
        logger.info("Model training completed")
        return history
    
    def predict(self, df):
        """
        Make price predictions
        
        Args:
            df: DataFrame with OHLCV data (should have at least sequence_length rows)
            
        Returns:
            Predicted price and direction probability
        """
        if self.model is None:
            model_path = os.path.join(self.model_dir, 'lstm_price_predictor.h5')
            if os.path.exists(model_path):
                self.model = load_model(model_path)
            else:
                logger.error("No trained model found. Please train the model first.")
                return None
        
        # Prepare the most recent data for prediction
        data = df[['open', 'high', 'low', 'close', 'volume']].tail(self.sequence_length).values
        
        # Scale the data
        scaled_data = self.scaler.transform(data)
        
        # Create sequence
        X = np.array([scaled_data])
        
        # Make prediction
        scaled_prediction = self.model.predict(X)
        
        # Get the last actual close price for reference
        current_close = df['close'].iloc[-1]
        
        # Inverse transform to get actual price
        # Create a dummy array with same shape as original data
        dummy = np.zeros((1, 5))
        # Put the predicted value in the close price position
        dummy[0, 3] = scaled_prediction[0, 0]
        # Inverse transform
        prediction_array = self.scaler.inverse_transform(dummy)
        predicted_close = prediction_array[0, 3]
        
        # Calculate direction probability (simple approach)
        direction = "UP" if predicted_close > current_close else "DOWN"
        confidence = abs(predicted_close - current_close) / current_close * 100
        
        result = {
            "current_price": current_close,
            "predicted_price": predicted_close,
            "direction": direction,
            "confidence": confidence,
            "horizon": f"{self.prediction_horizon} candles ahead"
        }
        
        return result
    
    def save(self, filename='lstm_price_predictor.h5'):
        """Save the model to disk"""
        if self.model is not None:
            save_model(self.model, os.path.join(self.model_dir, filename))
            logger.info(f"Model saved to {filename}")
        else:
            logger.error("No model to save")
    
    def load(self, filename='lstm_price_predictor.h5'):
        """Load the model from disk"""
        path = os.path.join(self.model_dir, filename)
        if os.path.exists(path):
            self.model = load_model(path)
            logger.info(f"Model loaded from {filename}")
            return True
        else:
            logger.error(f"Model file {filename} not found")
            return False

# Create singleton instance
price_predictor = PricePredictionModel()
