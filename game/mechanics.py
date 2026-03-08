class GameMechanics:
    @staticmethod
    def calculate_round_results(passed_laws):
        if not passed_laws:
            return {"coalition": -10, "opposition": 10}
        
        total_impact = {"coalition": 0, "opposition": 0}
        for law in passed_laws:
            total_impact["coalition"] += law["impact"].get("coalition", 0)
            total_impact["opposition"] += law["impact"].get("opposition", 0)
            
        return total_impact

    @staticmethod
    def check_law_passed(votes, weights):
        total_yes_weight = sum(weights.get(p, 0) for p, voted_yes in votes.items() if voted_yes)
        return total_yes_weight >= 50.0
