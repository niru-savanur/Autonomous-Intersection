from mesa.visualization.modules import TextElement


class ThroughputCounter(TextElement):
    def render(self, model):
        ratio = model.get_agent_rate()
        return F"Throughput: {ratio} cars per minute"
