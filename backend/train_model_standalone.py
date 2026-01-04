"""
Standalone script to train XGBoost model
Can be run independently of the API server
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ml_training_data_service import ml_training_data_service
from app.services.ml_model_service import ml_model_service


def main():
    print("\n" + "="*60)
    print("XGBoost Model Training")
    print("="*60 + "\n")
    
    # Generate training data
    num_samples = 5000
    print(f"[1/3] Generating {num_samples} training samples...")
    training_data = ml_training_data_service.generate_synthetic_data(num_samples)
    print(f"✓ Generated {len(training_data)} balanced samples\n")
    
    # Train model
    print(f"[2/3] Training XGBoost model...")
    result = ml_model_service.train(training_data)
    
    if not result['success']:
        print(f"\n✗ Training failed: {result.get('error', 'Unknown error')}")
        return False
    
    # Save model
    print(f"\n[3/3] Saving model...")
    ml_model_service.save_model()
    
    # Display results
    metrics = result['metrics']
    print("\n" + "="*60)
    print("Training Complete! 🎉")
    print("="*60)
    print(f"\n📊 Performance Metrics:")
    print(f"  Accuracy:  {metrics['accuracy']:.2%}")
    print(f"  Precision: {metrics['precision']:.2%}")
    print(f"  Recall:    {metrics['recall']:.2%}")
    print(f"  F1 Score:  {metrics['f1_score']:.2%}")
    print(f"\n📈 Training Data:")
    print(f"  Train samples: {metrics['train_samples']}")
    print(f"  Test samples:  {metrics['test_samples']}")
    print(f"  Features:      {metrics['num_features']}")
    print(f"\n🔝 Top 5 Important Features:")
    for i, (feature, score) in enumerate(list(metrics['feature_importance'].items())[:5], 1):
        print(f"  {i}. {feature}: {score:.3f}")
    print("\n" + "="*60 + "\n")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
