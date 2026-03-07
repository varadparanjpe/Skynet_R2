class DelayModel:
    """
    A more realistic mock model representing a Delay Probability classifier.
    In production, this would be a Logistic Regression or Neural Net loaded from disk.
    """
    def predict(self, shipment: dict) -> float:
        """
        Predicts the probability of a delay (0.0 to 1.0) based on weighted features.
        """
        # Weighted importance of different features
        weights = {
            "traffic_level": 0.35,
            "hub_congestion": 0.40,
            "warehouse_load": 0.15,
            # Inverse relationship: low reliability increases delay probability
            "carrier_reliability": -0.40,
            "dependency_score": 0.10
        }

        # Calculate raw score sum
        score = (
            (shipment.get("traffic_level", 0) * weights["traffic_level"]) +
            (shipment.get("hub_congestion", 0) * weights["hub_congestion"]) +
            (shipment.get("warehouse_load", 0) * weights["warehouse_load"]) +
            ((1.0 - shipment.get("carrier_reliability", 1.0)) * abs(weights["carrier_reliability"])) +
            (shipment.get("dependency_score", 0) * weights["dependency_score"])
        )

        # Apply a sigmoid-like squashing function to constrain between 0 and 1
        probability = 1 / (1 + (2.71828 ** (-10 * (score - 0.5))))
        
        return round(probability, 3)
