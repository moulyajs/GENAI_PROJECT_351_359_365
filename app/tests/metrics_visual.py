from pathlib import Path
from typing import Dict, List
import matplotlib.pyplot as plt

# Bar chart to compare attack success between no defense and with defense
def _save_attack_comparison_chart(metrics: Dict, output_dir: Path) -> Path:
    labels = ["Without Defense", "With Defense"]
    values = [
        int(metrics.get("successful_attacks_no_defense", 0)),
        int(metrics.get("successful_attacks_defense", 0)),
    ]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color=["#DC2626", "#16A34A"])
    plt.ylabel("Successful Attacks")
    plt.title("Attack Success Comparison")
    plt.grid(axis="y", linestyle="--", alpha=0.35)

    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            value + 0.05,
            str(value),
            ha="center",
            va="bottom",
            fontsize=10,
        )

    output_file = output_dir / "attack_success_comparison.png"
    plt.tight_layout()
    plt.savefig(output_file, dpi=160)
    plt.close()
    return output_file

# Confusion matrix to visualize the performance of the safety model
def _save_confusion_matrix(results: List[Dict], output_dir: Path) -> Path:
    # Positive class is "malicious", and prediction positive means "blocked".
    tp = fn = fp = tn = 0

    for row in results:
        actual_malicious = bool(row.get("is_malicious", False))
        predicted_blocked = bool(row.get("final_decision", False))

        if actual_malicious and predicted_blocked:
            tp += 1
        elif actual_malicious and not predicted_blocked:
            fn += 1
        elif not actual_malicious and predicted_blocked:
            fp += 1
        else:
            tn += 1

    matrix = [[tp, fn], [fp, tn]]

    plt.figure(figsize=(6, 5))
    plt.imshow(matrix, cmap="Blues")
    plt.title("Confusion Matrix (Safety Decision)")
    plt.colorbar()
    plt.xticks([0, 1], ["Pred: Blocked", "Pred: Allowed"])
    plt.yticks([0, 1], ["Actual: Malicious", "Actual: Benign"])

    for i in range(2):
        for j in range(2):
            plt.text(j, i, str(matrix[i][j]), ha="center", va="center", color="black", fontsize=12)

    plt.tight_layout()
    output_file = output_dir / "confusion_matrix.png"
    plt.savefig(output_file, dpi=160)
    plt.close()
    return output_file

# Save all metric visualizations to the output directory
def save_metric_visuals(metrics: Dict, results: List[Dict], output_dir: str = ".") -> List[str]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    attack_chart = _save_attack_comparison_chart(metrics, directory)
    confusion_chart = _save_confusion_matrix(results, directory)

    return [str(attack_chart), str(confusion_chart)]
