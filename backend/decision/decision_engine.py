
class DecisionEngine:

    def decide(self, shipment):

        if shipment["delay_probability"] > 0.75:
            return "reroute"

        if shipment["hub_congestion"] > 0.8:
            return "prioritize"

        return "none"
