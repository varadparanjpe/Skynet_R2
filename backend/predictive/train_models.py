import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Set random seed for reproducibility
np.random.seed(42)

def generate_mock_historical_data(num_samples=5000):
    """
    Generate synthetic logistics data that mirrors the new ShipmentContext.
    """
    distances = np.random.uniform(50, 2000, num_samples)
    weather_risks = np.random.beta(2, 5, num_samples) # Skewed towards low risk
    traffic_risks = np.random.beta(2, 5, num_samples)
    carrier_reliabilities = np.random.beta(8, 2, num_samples) # Skewed towards high reliability
    queue_times = np.random.exponential(30, num_samples) # Average 30 mins wait
    priorities = np.random.randint(1, 6, num_samples)
    
    df = pd.DataFrame({
        'distance_remaining_km': distances,
        'weather_risk': weather_risks,
        'traffic_risk': traffic_risks,
        'port_hub_queue_time_mins': queue_times,
        'carrier_reliability': carrier_reliabilities,
        'shipment_priority': priorities
    })
    
    # Heuristics for targets to give models something logical to learn
    # ETA calculation (regression)
    base_speed_kmh = 80.0
    effective_speed = base_speed_kmh * (1 - (df['traffic_risk'] * 0.5) - (df['weather_risk'] * 0.3))
    df['actual_eta_mins'] = (df['distance_remaining_km'] / effective_speed) * 60 + df['port_hub_queue_time_mins']
    # Add noise to ETA
    df['actual_eta_mins'] += np.random.normal(0, 15, num_samples)
    
    # Delay probability generation (classification target -> thresholded for actual delay)
    delay_score = (
        (df['weather_risk'] * 0.4) + 
        (df['traffic_risk'] * 0.3) + 
        (df['port_hub_queue_time_mins'] / 100 * 0.2) + 
        ((1 - df['carrier_reliability']) * 0.3)
    )
    df['is_delayed'] = (delay_score + np.random.normal(0, 0.1, num_samples) > 0.6).astype(int)
    
    return df

def train_delay_model(df):
    features = ['distance_remaining_km', 'weather_risk', 'traffic_risk', 'port_hub_queue_time_mins', 'carrier_reliability', 'shipment_priority']
    X = df[features]
    y = df['is_delayed']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42))
    ])
    
    pipeline.fit(X_train, y_train)
    accuracy = pipeline.score(X_test, y_test)
    print(f"Delay Model Accuracy: {accuracy:.2f}")
    
    os.makedirs('backend/predictive/models', exist_ok=True)
    joblib.dump(pipeline, 'backend/predictive/models/delay_model.pkl')
    print("Saved delay_model.pkl")

def train_eta_model(df):
    features = ['distance_remaining_km', 'weather_risk', 'traffic_risk', 'port_hub_queue_time_mins', 'carrier_reliability', 'shipment_priority']
    X = df[features]
    y = df['actual_eta_mins']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42))
    ])
    
    pipeline.fit(X_train, y_train)
    score = pipeline.score(X_test, y_test)
    print(f"ETA Model R^2 Score: {score:.2f}")
    
    os.makedirs('backend/predictive/models', exist_ok=True)
    joblib.dump(pipeline, 'backend/predictive/models/eta_model.pkl')
    print("Saved eta_model.pkl")

if __name__ == "__main__":
    print("Generating simulated historical logistics data...")
    historical_data = generate_mock_historical_data(10000)
    
    print("\nTraining Delay Prediction Model (Random Forest Classifier)...")
    train_delay_model(historical_data)
    
    print("\nTraining ETA Prediction Model (Random Forest Regressor)...")
    train_eta_model(historical_data)
    
    print("\nPredictive Intelligence Layer ready.")
