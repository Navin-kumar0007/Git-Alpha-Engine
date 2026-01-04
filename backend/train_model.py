"""
Train the XGBoost model with synthetic data
Run this script after starting the backend server
"""
import requests
import json

# Configuration
API_URL = "http://127.0.0.1:8000"
# You'll need to replace this with a valid token from your logged-in session
TOKEN = "your-bearer-token-here"

def train_model(num_samples=5000):
    """Trigger model training"""
    print(f"\n{'='*60}")
    print(f"Training XGBoost Model")
    print(f"{'='*60}\n")
    
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    
    print(f"POST {API_URL}/api/ml-training/train?num_samples={num_samples}")
    print("Sending request...")
    
    try:
        response = requests.post(
            f"{API_URL}/api/ml-training/train",
            params={"num_samples": num_samples},
            headers=headers,
            timeout=120  # 2 minutes timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n✓ Training successful!")
            print(f"\nMetrics:")
            print(json.dumps(data['metrics'], indent=2))
        else:
            print(f"\n✗ Training failed:")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\n✗ Request timed out (training takes 2-5 minutes)")
    except Exception as e:
        print(f"\n✗ Error: {e}")

def get_model_status():
    """Check if model is trained"""
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    
    try:
        response = requests.get(
            f"{API_URL}/api/ml-training/status",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\nModel Status:")
            print(json.dumps(data, indent=2))
        else:
            print(f"✗ Failed to get status: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("\nXGBoost Model Training Script")
    print("=" * 60)
    print("\nIMPORTANT: Update TOKEN variable with your auth token")
    print("You can get it from browser DevTools > Application > Local Storage")
    print("\nOr train directly via API:")
    print(f"  POST {API_URL}/api/ml-training/train")
    print("\n" + "=" * 60)
    
    # Uncomment to run:
    # train_model(5000)
    # get_model_status()
