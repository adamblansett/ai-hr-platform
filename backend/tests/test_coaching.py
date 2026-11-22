import unittest
import statistics

class TestCoachingAndCalibration(unittest.TestCase):
    def test_calibration_bias_detection(self):
        def analyze_ratings(ratings: list[int]):
            total = len(ratings)
            distribution = {str(i): ratings.count(i) for i in range(1, 6)}
            mean_val = round(statistics.mean(ratings), 2)
            biases = []

            if (distribution.get("3", 0) / total) >= 0.55:
                biases.append("CENTRAL_TENDENCY_BIAS")

            high_ratings = distribution.get("4", 0) + distribution.get("5", 0)
            if mean_val >= 4.0 or (high_ratings / total) >= 0.65:
                biases.append("LENIENCY_BIAS")

            if mean_val <= 2.5:
                biases.append("HARSHNESS_BIAS")

            return mean_val, biases

        # Central tendency bias test (15 out of 20 rated 3)
        mean, biases = analyze_ratings([3] * 15 + [4] * 3 + [2] * 2)
        self.assertIn("CENTRAL_TENDENCY_BIAS", biases)

        # Leniency bias test
        mean, biases = analyze_ratings([4] * 10 + [5] * 8 + [3] * 2)
        self.assertIn("LENIENCY_BIAS", biases)

        # Harshness bias test
        mean, biases = analyze_ratings([1] * 8 + [2] * 10 + [3] * 2)
        self.assertIn("HARSHNESS_BIAS", biases)

    def test_1on1_agenda_talking_point_selection(self):
        def select_prompts(focus_area: str):
            if focus_area == "CAREER_GROWTH":
                return "What skills or competencies would you like to develop in the next 6 months?"
            elif focus_area == "PERFORMANCE_INTERVENTION":
                return "What specific support or unblocking do you need from me as your manager?"
            return "What was the most rewarding project or milestone you shipped this month?"

        self.assertIn("skills", select_prompts("CAREER_GROWTH"))
        self.assertIn("unblocking", select_prompts("PERFORMANCE_INTERVENTION"))
        self.assertIn("rewarding", select_prompts("GENERAL_PROGRESS"))

if __name__ == "__main__":
    unittest.main()
