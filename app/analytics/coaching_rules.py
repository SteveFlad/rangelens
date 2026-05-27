from app.analytics.dispersion import DispersionSummary


def coaching_insights(summary: DispersionSummary) -> list[str]:
    insights = []
    if summary.shot_count == 0:
        return ["No shots captured yet."]
    if summary.dominant_miss == "right":
        insights.append("Miss tendency is right. Check face control and alignment.")
    elif summary.dominant_miss == "left":
        insights.append("Miss tendency is left. Check face closure through impact.")
    else:
        insights.append("Start line is relatively centered.")
    if summary.max_radius > 20:
        insights.append("Dispersion is wide. Focus on repeatable tempo and contact.")
    else:
        insights.append("Dispersion is reasonably tight for this sample size.")
    return insights
