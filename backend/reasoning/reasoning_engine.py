
class ReasoningEngine:

    def analyze(self, shipment):

        evidence = []

        if shipment["hub_congestion"] > 0.8:
            evidence.append("hub congestion")

        if shipment["traffic_level"] > 0.7:
            evidence.append("traffic spike")

        root = evidence[0] if evidence else "unknown"

        return {
            "root_cause": root,
            "confidence": 0.8,
            "evidence": evidence
        }
