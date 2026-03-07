import math

class ETAModel:
    """
    A more realistic mock model representing an ETA predictor.
    In production, this would be an XGBoost or Random Forest model loaded from disk.
    """
    def __init__(self):
        # Base speed in km/h representing optimal conditions
        self.base_speed_kmh = 80.0

    def predict(self, features: list) -> float:
        """
        Predicts ETA in minutes based on distance and network conditions.
        features: [distance_km, traffic_level (0-1), hub_congestion (0-1)]
        """
        if not features or len(features) < 3:
            return 0.0

        distance = features[0]
        traffic_level = features[1]
        hub_congestion = features[2]

        # Heavy traffic penalizes speed severely
        effective_speed = self.base_speed_kmh * (1 - (traffic_level * 0.6))
        
        # Base travel time in hours converted to minutes
        base_time_mins = (distance / effective_speed) * 60

        # Hub congestion adds flat waiting time penalties (up to 3 hours)
        congestion_penalty_mins = (hub_congestion ** 2) * 180

        total_eta_mins = base_time_mins + congestion_penalty_mins
        
        return round(total_eta_mins, 2)
