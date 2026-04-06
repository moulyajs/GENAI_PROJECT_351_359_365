import json
from app.main import run_pipeline

def run_tests():
    with open("app/tests/test_cases.json") as f:
        tests = json.load(f)

    correct = 0

    for test in tests:
        prompt = test["text"]
        expected = test["expected"]

        final_decision, _, _ = run_pipeline(prompt)
        result = "BLOCK" if final_decision else "ALLOW"

        print("\n---------------------------")
        print("Prompt:", prompt)
        print("Expected:", expected)
        print("Got:", result)

        if result == expected:
            print("✅ PASS")
            correct += 1
        else:
            print("❌ FAIL")

    print("\n===========================")
    print(f"Accuracy: {correct}/{len(tests)}")


if __name__ == "__main__":
    run_tests()