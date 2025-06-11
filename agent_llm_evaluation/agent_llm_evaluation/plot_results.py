from __future__ import annotations
import json
from pathlib import Path
from typing import List, Tuple

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import wilcoxon

try:
    import pandas as pd
except ImportError:  # pretty-print is optional
    pd = None


def load_scores(jsonl_path: str | Path) -> List[Tuple[int, int]]:
    """Return a list of (lora_score, silica_score) tuples (ints ∈ 1–5)."""
    pairs: List[Tuple[int, int]] = []
    with Path(jsonl_path).expanduser().open("r", encoding="utf-8") as fh:
        for raw in fh:
            if not raw.strip():
                continue
            try:
                rec = json.loads(raw)
                pairs.append(
                    (int(rec["lora"]["final_score"]),
                     int(rec["silica"]["final_score"]))
                )
            except (KeyError, ValueError, TypeError, json.JSONDecodeError):
                continue
    return pairs


def confusion_matrix(pairs: List[Tuple[int, int]]) -> np.ndarray:
    mat = np.zeros((5, 5), dtype=int)
    for lora, silica in pairs:
        if 1 <= lora <= 5 and 1 <= silica <= 5:
            mat[lora - 1, silica - 1] += 1
    return mat


def plot_confusion_matrix(mat: np.ndarray,
                          total: int,
                          title: str = "LoRA vs Silica (normalised)") -> None:
    """Heat-map of normalised frequencies (rows = LoRA, cols = Silica)."""
    norm = mat / total
    fig, ax = plt.subplots(figsize=(6, 5))
    cax = ax.imshow(norm, aspect="equal")
    fig.colorbar(cax, ax=ax, label="Proportion")

    ax.set_xticks(range(5));  ax.set_yticks(range(5))
    ax.set_xticklabels(range(1, 6));  ax.set_yticklabels(range(1, 6))
    ax.set_xlabel("Silica score");  ax.set_ylabel("LoRA score")
    ax.set_title(title)

    for i in range(5):
        for j in range(5):
            pct = norm[i, j] * 100
            ax.text(j, i, f"{pct:.1f}%", ha="center", va="center",
                    fontsize=9,
                    color="white" if norm[i, j] > 0.25 else "black")

    plt.tight_layout()
    plt.show()


def plot_diff_hist(diffs: List[int], total: int, avg: float,
                   title: str = "LoRA – Silica diff (normalised)") -> None:
    buckets = {d: 0 for d in range(-4, 5)}
    for d in diffs:
        if -4 <= d <= 4:
            buckets[d] += 1

    xs, counts = zip(*sorted(buckets.items()))
    freqs = [c / total for c in counts]

    plt.figure(figsize=(8, 4))
    bars = plt.bar(xs, freqs, width=0.7, alpha=0.8)

    for bar, freq in zip(bars, freqs):
        if freq:
            plt.text(bar.get_x() + bar.get_width() / 2,
                     bar.get_height() + 0.005,
                     f"{freq*100:.1f}%",
                     ha="center", va="bottom", fontsize=9)

    plt.axvline(avg, color="red", linestyle="--", linewidth=1.8)
    plt.text(avg, plt.ylim()[1] * 0.95, f"μ = {avg:.2f}",
             rotation=90, ha="right", va="top",
             color="red", fontsize=10)

    plt.title(title, fontsize=14)
    plt.xlabel("Score difference");  plt.ylabel("Proportion of samples")
    plt.xticks(xs)
    plt.tight_layout()
    plt.show()


def wilcoxon_one_sided(pairs: List[Tuple[int, int]]) -> tuple[float, float]:
    lora, silica = zip(*pairs)
    return wilcoxon(lora, silica, alternative="greater")  # H₁: LoRA > Silica


def show_matrix(mat: np.ndarray, total: int) -> None:
    norm = mat / total
    if pd is not None:
        df = pd.DataFrame(norm,
                          index=[f"LoRA {i}" for i in range(1, 6)],
                          columns=[f"Silica {j}" for j in range(1, 6)])
        print("\nNormalised matrix (rows = LoRA, cols = Silica, values = %):")
        with pd.option_context("display.float_format",
                               lambda v: f"{v*100:5.1f}%"):
            print(df.to_string())
    else:
        print("\nNormalised matrix (rows = LoRA, cols = Silica):")
        for i, row in enumerate(norm, 1):
            pct_row = "  ".join(f"{v*100:5.1f}%" for v in row)
            print(f"LoRA {i}: {pct_row}")


def main(jsonl_path: str | Path = "results.jsonl") -> None:
    pairs = load_scores(jsonl_path)
    if not pairs:
        raise ValueError("No valid samples found.")
    total = len(pairs)

    # Confusion matrix (normalised)
    mat = confusion_matrix(pairs)
    show_matrix(mat, total)
    plot_confusion_matrix(mat, total)

    # Histogram (normalised)
    diffs = [l - s for l, s in pairs]
    avg_diff = float(np.mean(diffs))
    plot_diff_hist(diffs, total, avg_diff)

    # Means & lift
    lora_scores, silica_scores = zip(*pairs)
    mu_lora   = float(np.mean(lora_scores))
    mu_silica = float(np.mean(silica_scores))
    mu_delta  = mu_lora - mu_silica
    lift      = mu_delta / mu_silica

    print(f"\nAverages  →  LoRA = {mu_lora:.3f},  Silica = {mu_silica:.3f}")
    print(f"Δ (LoRA – Silica) = {mu_delta:.3f}")
    print(f"Lift (Δ / μ_base) = {lift:.3%}")

    # Wilcoxon
    W, p = wilcoxon_one_sided(pairs)
    print(f"\nOne-sided paired Wilcoxon signed-rank test "
          f"(H₁: LoRA > Silica)\nW = {W:.4f},  p = {p:.4g}")
    if p < 0.05:
        print("Result: **statistically significant** at α = 0.05.")
    else:
        print("Result: not statistically significant at α = 0.05.")


JSONL_PATH = r"lora_vs_silica_quality_eval_agent.jsonl"

if __name__ == "__main__":
    main(JSONL_PATH)
