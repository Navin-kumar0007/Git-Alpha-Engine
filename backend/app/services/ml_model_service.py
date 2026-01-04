"""
ML Model Service - XGBoost Implementation
Trains and predicts stock signals using XGBoost
"""
from typing import List, Dict, Optional, Tuple
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pandas as pd
import joblib
import os
from datetime import datetime


class MLModelService:
    """Service for XGBoost model training and prediction"""
    
    def __init__(self, model_path: str = "ml_models/xgboost_signal_model.pkl"):
        self.model = None
        self.model_path = model_path
        self.feature_names = []
        self.metrics = {}
        self.training_history = []
        
        # XGBoost hyperparameters
        self.params = {
            'objective': 'binary:logistic',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 150,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42,
            'eval_metric': 'logloss'
        }
    
    def train(self, training_data: List[Dict]) -> Dict:
        """
        Train XGBoost model on labeled data
        
        Args:
            training_data: List of {features: Dict, label: int}
        
        Returns:
            Training metrics dict
        """
        if len(training_data) < 100:
            return {
                'success': False,
                'error': f'Insufficient training data: {len(training_data)} samples (need 100+)'
            }
        
        # Convert to pandas DataFrame
        features_list = [d['features'] for d in training_data]
        labels = [d['label'] for d in training_data]
        
        df = pd.DataFrame(features_list)
        self.feature_names = df.columns.tolist()
        
        # Split train/test (80/20)
        X_train, X_test, y_train, y_test = train_test_split(
            df, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        print(f"Training XGBoost model with {len(X_train)} samples...")
        print(f"Features: {len(self.feature_names)}")
        
        # Train XGBoost classifier
        self.model = xgb.XGBClassifier(**self.params)
        
        # Fit with eval set for early stopping
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Evaluate on test set
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)
        
        self.metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred, zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, zero_division=0)),
            'f1_score': float(f1_score(y_test, y_pred, zero_division=0)),
            'train_samples': int(len(X_train)),
            'test_samples': int(len(X_test)),
            'num_features': int(len(self.feature_names)),
            'timestamp': datetime.now().isoformat()
        }
        
        # Feature importance (convert numpy types to native Python)
        feature_importance = dict(zip(
            self.feature_names,
            [float(x) for x in self.model.feature_importances_]  # Convert numpy.float32 to float
        ))
        self.metrics['feature_importance'] = dict(
            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        # Save model
        self.save_model()
        
        # Store in history
        self.training_history.append(self.metrics)
        
        print(f"✓ Model trained successfully!")
        print(f"  Accuracy: {self.metrics['accuracy']:.2%}")
        print(f"  Precision: {self.metrics['precision']:.2%}")
        print(f"  Recall: {self.metrics['recall']:.2%}")
        
        return {
            'success': True,
            'metrics': self.metrics
        }
    
    def predict(self, features: Dict[str, float]) -> Dict:
        """
        Predict signal for given features
        
        Args:
            features: Dict of feature_name -> value
        
        Returns:
            {
                'signal': 'BUY' or 'HOLD/SELL',
                'confidence': 0-100,
                'probability': 0.0-1.0,
                'source': 'ML'
            }
        """
        # Load model if not in memory
        if self.model is None:
            if not self.load_model():
                return {
                    'signal': 'HOLD',
                    'confidence': 50,
                    'probability': 0.5,
                    'source': 'ML_NOT_TRAINED',
                    'error': 'Model not trained yet'
                }
        
        # Convert to DataFrame with correct feature order
        df = pd.DataFrame([features])[self.feature_names]
        
        # Predict probability (convert numpy types to native Python)
        proba = self.model.predict_proba(df)[0]
        buy_probability = float(proba[1])  # Probability of class 1 (BUY) - convert numpy.float32
        
        # Determine signal based on probability threshold
        if buy_probability > 0.6:  # 60% threshold for BUY
            signal = 'BUY'
            confidence = buy_probability * 100
        elif buy_probability < 0.4:  # Below 40% = SELL/HOLD
            signal = 'SELL'
            confidence = (1 - buy_probability) * 100
        else:
            signal = 'HOLD'
            confidence = 50
        
        return {
            'signal': signal,
            'confidence': round(confidence, 1),
            'probability': round(buy_probability, 3),
            'source': 'ML'
        }
    
    def save_model(self) -> bool:
        """Save model to disk"""
        try:
            # Create directory if doesn't exist
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            # Save model and metadata
            model_data = {
                'model': self.model,
                'feature_names': self.feature_names,
                'params': self.params,
                'metrics': self.metrics
            }
            
            joblib.dump(model_data, self.model_path)
            print(f"✓ Model saved to {self.model_path}")
            return True
        except Exception as e:
            print(f"✗ Failed to save model: {e}")
            return False
    
    def load_model(self) -> bool:
        """Load model from disk"""
        try:
            if not os.path.exists(self.model_path):
                print(f"✗ Model file not found: {self.model_path}")
                return False
            
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.feature_names = model_data['feature_names']
            self.params = model_data.get('params', self.params)
            self.metrics = model_data.get('metrics', {})
            
            print(f"✓ Model loaded from {self.model_path}")
            print(f"  Accuracy: {self.metrics.get('accuracy', 0):.2%}")
            return True
        except Exception as e:
            print(f"✗ Failed to load model: {e}")
            return False
    
    def get_metrics(self) -> Dict:
        """Get current model metrics"""
        return self.metrics
    
    def get_feature_importance(self, top_n: int = 10) -> Dict[str, float]:
        """Get top N most important features"""
        if not self.model or not self.feature_names:
            return {}
        
        importance = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        
        # Sort and return top N
        sorted_importance = sorted(
            importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        return dict(sorted_importance)


# Singleton instance
ml_model_service = MLModelService()
