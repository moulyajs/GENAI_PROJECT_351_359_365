import os
import json
import argparse
from datetime import datetime
from pathlib import Path

from app.main import run_pipeline
from app.tests.metrics import compute_metrics
from app.tests.metrics_visual import save_metric_visuals

def main():
    parser = argparse.ArgumentParser(description="Multi-modal AI Safety Test Runner")
    parser.add_argument("--input", type=str, required=True, help="Path to the test JSON file")
    args = parser.parse_args()

    input_path = args.input
    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        return

    with open(input_path, "r") as f:
        tests = json.load(f)

    results = []
    print(f"Starting Multi-modal Evaluation on {len(tests)} test cases...\n")

    skipped = 0
    for idx, test in enumerate(tests):
        prompt = test["prompt"]
        is_malicious = test.get("is_malicious", False)
        mode = test.get("mode", "text")

        print(f"[{idx+1}/{len(tests)}] Evaluating {mode} prompt: {str(prompt)[:60]}...")

        if mode in ["image", "document"]:
            file_path = os.path.join(os.getcwd(), prompt)

            if not os.path.exists(file_path):
                print(f"\t--- File not found: {file_path}. Skipping...\n")
                skipped += 1
                continue

            prompt = file_path

        try:
            final_decision, meta_reason, _, _, answer = run_pipeline(prompt)

            results.append({
                "prompt": prompt,
                "is_malicious": is_malicious,
                "final_decision": final_decision,
                "response": answer
            })

            print(f"   -> Blocked: {final_decision} | Reason: {str(meta_reason)[:50]}...")

        except Exception as e:
            print(f"\t--- Error processing test case: {e}. Skipping...\n")
            skipped += 1
            continue

    # Compute metrics
    metrics = compute_metrics(results)

    # Print Report
    print("\n" + "=" * 60)
    print("EVALUATION METRICS REPORT".center(60))
    print("=" * 60)

    print(f"{'Total Malicious Items Tested':40}: {metrics['total_malicious']}")
    print(f"{'Attacks Successful (No Defense)':40}: {metrics['successful_attacks_no_defense']}")
    print(f"{'Attacks Successful (With Defense)':40}: {metrics['successful_attacks_defense']}")
    print(f"{'Total Test Cases':40}: {len(tests)}")
    print(f"{'Skipped Test Cases':40}: {skipped}")

    print("-" * 60)
    print("Validation Metrics".center(60))
    print("-" * 60)

    print(f"{'1. Defense Effectiveness Rate (DER)':40}: {metrics['der']:>8.2f}%")
    print(f"{'2. Instruction Adherence Rate (IAR)':40}: {metrics['iar']:>8.2f}%")
    print(f"{'3. Hallucination Frequency (HF)':40}: {metrics['hf']:>8.2f}%")
    print(f"{'4. Generation Coherence Score (GCS)':40}: {metrics['gcs']:>8.2f} / 10")
    print(f"{'5. Safety-Quality Trade-off (SQTI)':40}: {metrics['sqti']:>8.2f}%")

    # Store each test run output in root/test_<timestamp>
    root_dir = Path(__file__).resolve().parents[2]
    timestamp = datetime.now().strftime("%d-%m-%y__%H-%M")
    run_output_dir = root_dir / f"test_{timestamp}"
    run_output_dir.mkdir(parents=True, exist_ok=True)

    # Save results JSON in the run output folder
    input_stem = Path(input_path).stem
    report_file = run_output_dir / f"{input_stem}_results.json"
    with open(report_file, "w") as f:
        json.dump({
            "metrics": metrics,
            "skipped": skipped,
            "total_tests": len(tests),
            "individual_results": results
        }, f, indent=4)

    visual_files = save_metric_visuals(metrics, results, output_dir=str(run_output_dir))
    print(f"\nRun output folder: {run_output_dir}")
    print(f"Results saved at: {report_file}")
    print("\nSaved metric visualizations:")
    for file_path in visual_files:
        print(f" - {file_path}")

    print("=" * 60)

if __name__ == "__main__":
    main()