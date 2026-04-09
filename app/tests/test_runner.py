import os
import json
import statistics

from app.main import run_pipeline
from app.tests.metrics import evaluate_iar, evaluate_hf, evaluate_gcs

def run_tests():
    dataset_path = os.path.join(os.path.dirname(__file__), "test_cases.json")
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}.")
        return

    with open(dataset_path, "r") as f:
        tests = json.load(f)

    total_malicious = 0
    successful_attacks_defense = 0
    successful_attacks_no_defense = 0

    iar_scores = []
    hf_scores = []
    gcs_scores = []
    
    print("Starting Multi-modal Evaluation Pipeline...\n")

    for idx, test in enumerate(tests):
        prompt = test["prompt"]
        is_malicious = test.get("is_malicious", False)
        mode = test.get("mode", "text")

        print(f"[{idx+1}/{len(tests)}] Evaluating prompt ({mode}): {str(prompt)[:60]}...")
        
        final_decision, meta_reason, _, _, answer = run_pipeline(prompt)
        
        # Metrics logic
        if is_malicious:
            total_malicious += 1
            if not final_decision:
                successful_attacks_defense += 1
            successful_attacks_no_defense += 1

        actual_text = answer or ""
        
        print(f"   -> Blocked: {final_decision} | Reason: {meta_reason}")
        
        iar_scores.append(evaluate_iar(prompt, actual_text))
        
        if not final_decision: 
            hf_scores.append(evaluate_hf(prompt, actual_text))
            gcs_scores.append(evaluate_gcs(prompt, actual_text))

    der = 0.0
    if successful_attacks_no_defense > 0:
        der = ((successful_attacks_no_defense - successful_attacks_defense) / successful_attacks_no_defense) * 100

    avg_iar = (sum(iar_scores) / len(iar_scores)) * 100 if iar_scores else 0.0
    avg_hf = (sum(hf_scores) / len(hf_scores)) * 100 if hf_scores else 0.0
    avg_gcs = statistics.mean(gcs_scores) if gcs_scores else 0.0

    sqti = ((der/100) + (avg_iar/100) - (avg_hf/100) + (avg_gcs/10)) / 4 * 100

    print("\n" + "=" * 60)
    print("EVALUATION METRICS REPORT".center(60))
    print("=" * 60)

    print(f"{'Total Malicious Items Tested':40}: {total_malicious}")
    print(f"{'Attacks Successful (No Defense)':40}: {successful_attacks_no_defense}")
    print(f"{'Attacks Successful (With Defense)':40}: {successful_attacks_defense}")

    print("-" * 60)
    print("Validation Metrics".center(60))
    print("-" * 60)

    print(f"{'1. Defense Effectiveness Rate (DER)':40}: {der:>8.2f}%")
    print(f"{'2. Instruction Adherence Rate (IAR)':40}: {avg_iar:>8.2f}%")
    print(f"{'3. Hallucination Frequency (HF)':40}: {avg_hf:>8.2f}%")
    print(f"{'4. Generation Coherence Score (GCS)':40}: {avg_gcs:>8.2f} / 10")
    print(f"{'5. Safety-Quality Trade-off (SQTI)':40}: {sqti:>8.2f}%")

    print("=" * 60)

if __name__ == "__main__":
    run_tests()