"""
ML Training API Endpoints
Admin endpoints for model training and metrics
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

from app.api.auth import get_current_user
from app.models import User
from app.services.ml_training_data_service import ml_training_data_service
from app.services.ml_model_service import ml_model_service


router = APIRouter(prefix="/api/ml-training", tags=["ML Training"])


class TrainResponse(BaseModel):
    success: bool
    message: str
    metrics: Optional[Dict] = None
    error: Optional[str] = None


@router.post("/train", response_model=TrainResponse)
async def train_model(
    num_samples: int = 5000,
    current_user: User = Depends(get_current_user)
):
    """
    Train XGBoost model with synthetic data
    
    Args:
        num_samples: Number of training samples to generate (default: 5000)
    
    Returns:
        Training results and metrics
    """
    try:
        print(f"\n{'='*60}")
        print(f"Starting ML Model Training")
        print(f"{'='*60}")
        
        # Generate training data
        print(f"\n[1/3] Generating {num_samples} training samples...")
        training_data = ml_training_data_service.generate_synthetic_data(num_samples)
        print(f"✓ Generated {len(training_data)} balanced samples")
        
        # Train model
        print(f"\n[2/3] Training XGBoost model...")
        result = ml_model_service.train(training_data)
        
        if not result['success']:
            return TrainResponse(
                success=False,
                message="Training failed",
                error=result.get('error', 'Unknown error')
            )
        
        # Save model
        print(f"\n[3/3] Saving model...")
        ml_model_service.save_model()
        
        print(f"\n{'='*60}")
        print(f"Training Complete!")
        print(f"{'='*60}\n")
        
        return TrainResponse(
            success=True,
            message=f"Model trained successfully with {len(training_data)} samples",
            metrics=result['metrics']
        )
        
    except Exception as e:
        print(f"\n✗ Training error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Training failed: {str(e)}"
        )


@router.get("/metrics")
async def get_model_metrics(current_user: User = Depends(get_current_user)):
    """
    Get current model performance metrics
    
    Returns:
        Model accuracy, precision, recall, feature importance
    """
    try:
        # Try to load model if not in memory
        if ml_model_service.model is None:
            ml_model_service.load_model()
        
        metrics = ml_model_service.get_metrics()
        
        if not metrics:
            return {
                "trained": False,
                "message": "Model not trained yet. Use POST /api/ml-training/train to train."
            }
        
        return {
            "trained": True,
            "metrics": metrics,
            "feature_importance": ml_model_service.get_feature_importance(10)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metrics: {str(e)}"
        )


@router.get("/status")
async def get_model_status(current_user: User = Depends(get_current_user)):
    """
    Get model training status
    
    Returns:
        Whether model is trained, timestamp, sample count
    """
    try:
        metrics = ml_model_service.get_metrics()
        
        return {
            "is_trained": ml_model_service.model is not None or ml_model_service.load_model(),
            "last_trained": metrics.get('timestamp', 'Never'),
            "accuracy": metrics.get('accuracy', 0),
            "train_samples": metrics.get('train_samples', 0),
            "num_features": metrics.get('num_features', 0)
        }
        
    except Exception as e:
        return {
            "is_trained": False,
            "error": str(e)
        }
