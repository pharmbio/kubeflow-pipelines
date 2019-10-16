import json, os

eval_passed = "false"
scores = "/home/evaluation_results/"
files = [s for s in os.listdir(scores) if s[-5:] == ".json"]
for score in files:
    with open(scores + score, "r") as class_score:
        if float(json.load(class_score).get("weighted avg", {}).get("f1-score", 0.0)) > 0.8:
            eval_passed = "true"

print(eval_passed)