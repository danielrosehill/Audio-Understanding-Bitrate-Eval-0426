"""Generate summary plots from results/all.csv.

Writes PNG files to plots/:
    wer_by_bitrate.png        # line chart: WER vs bitrate, one line per model
    latency_by_model.png      # bar chart: avg latency per model
    accuracy_vs_latency.png   # scatter: the "which model" trade-off chart
    wer_distribution.png      # box plot: WER distribution per model (reliability)
    wer_heatmap.png           # heatmap: model × bitrate → WER

Usage:
    python3 scripts/plot_results.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV = REPO_ROOT / "results" / "all.csv"
OUT = REPO_ROOT / "plots"


def short_name(model_id: str) -> str:
    """Shorten model ID for chart labels."""
    s = model_id.split("/")[-1]
    s = s.replace("-preview", "").replace("-001", "")
    s = s.replace("gemini-", "G-").replace("gpt-", "GPT-")
    s = s.replace("voxtral-small-24b-2507", "Voxtral 24B")
    s = s.replace("mimo-v2-omni", "MiMo V2")
    return s


def style() -> None:
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.grid": True,
        "grid.alpha": 0.25,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 11,
    })


def plot_wer_by_bitrate(df: pd.DataFrame) -> None:
    pivot = df.groupby(["model", "bitrate_kbps"])["wer"].mean().unstack()
    fig, ax = plt.subplots(figsize=(11, 7))
    cmap = plt.get_cmap("tab20")
    for i, (model, row) in enumerate(pivot.iterrows()):
        ax.plot(row.index, row.values, marker="o", linewidth=2,
                color=cmap(i), label=short_name(model))
    ax.set_xlabel("MP3 bitrate (kbps)")
    ax.set_ylabel("Word Error Rate (lower is better)")
    ax.set_title("WER vs. MP3 Bitrate — averaged across 4 dictation samples")
    ax.set_xticks([16, 24, 32, 48, 64])
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    fig.savefig(OUT / "wer_by_bitrate.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_latency_by_model(df: pd.DataFrame) -> None:
    means = df.groupby("model")["elapsed_s"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.get_cmap("viridis")(np.linspace(0.15, 0.85, len(means)))
    ax.barh([short_name(m) for m in means.index], means.values, color=colors)
    for i, v in enumerate(means.values):
        ax.text(v + 0.1, i, f"{v:.2f}s", va="center", fontsize=9)
    ax.set_xlabel("Average latency (seconds, wall-clock API round-trip)")
    ax.set_title("Latency by Model — averaged across all bitrates and samples")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(OUT / "latency_by_model.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_accuracy_vs_latency(df: pd.DataFrame) -> None:
    agg = df.groupby("model").agg(wer=("wer", "mean"), latency=("elapsed_s", "mean")).reset_index()
    fig, ax = plt.subplots(figsize=(10, 7))
    cmap = plt.get_cmap("tab20")
    for i, row in agg.iterrows():
        ax.scatter(row["latency"], row["wer"], s=180, color=cmap(i),
                   edgecolor="black", linewidth=0.8, zorder=3)
        ax.annotate(short_name(row["model"]),
                    (row["latency"], row["wer"]),
                    xytext=(7, 4), textcoords="offset points", fontsize=9)
    ax.set_xlabel("Average latency (s) — lower is better")
    ax.set_ylabel("Average WER — lower is better")
    ax.set_title("Accuracy vs. Latency — the dictation model trade-off\n(bottom-left is the sweet spot)")
    ax.axhline(0.05, color="red", linestyle="--", alpha=0.3, linewidth=1)
    ax.text(ax.get_xlim()[1] * 0.98, 0.05, " 5% WER", color="red",
            alpha=0.5, fontsize=8, va="bottom", ha="right")
    fig.tight_layout()
    fig.savefig(OUT / "accuracy_vs_latency.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_wer_distribution(df: pd.DataFrame) -> None:
    order = df.groupby("model")["wer"].median().sort_values().index
    fig, ax = plt.subplots(figsize=(11, 6))
    data = [df[df["model"] == m]["wer"].values for m in order]
    bp = ax.boxplot(data, labels=[short_name(m) for m in order],
                    patch_artist=True, widths=0.6, vert=True)
    cmap = plt.get_cmap("viridis")(np.linspace(0.15, 0.85, len(order)))
    for patch, color in zip(bp["boxes"], cmap):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    for med in bp["medians"]:
        med.set_color("black")
    ax.set_ylabel("WER distribution across 20 calls (4 samples × 5 bitrates)")
    ax.set_title("WER Reliability by Model — wide boxes = inconsistent behavior")
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    ax.set_ylim(bottom=-0.02)
    fig.tight_layout()
    fig.savefig(OUT / "wer_distribution.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_wer_heatmap(df: pd.DataFrame) -> None:
    pivot = df.groupby(["model", "bitrate_kbps"])["wer"].mean().unstack()
    pivot = pivot.loc[pivot.mean(axis=1).sort_values().index]

    fig, ax = plt.subplots(figsize=(9, 7))
    im = ax.imshow(pivot.values, cmap="RdYlGn_r", aspect="auto", vmin=0, vmax=0.5)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([f"{b} kbps" for b in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([short_name(m) for m in pivot.index])
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            v = pivot.values[i, j]
            txt = ax.text(j, i, f"{v:.3f}", ha="center", va="center",
                          color="white", fontsize=9, fontweight="bold")
            txt.set_path_effects([
                path_effects.Stroke(linewidth=2, foreground="black"),
                path_effects.Normal(),
            ])
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Average WER", rotation=270, labelpad=15)
    ax.set_title("WER Heatmap — Model × Bitrate\n(green = accurate, red = poor)")
    fig.tight_layout()
    fig.savefig(OUT / "wer_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    style()
    df = pd.read_csv(CSV)
    df = df[df["wer"].notna()]  # drop rows with API errors (no WER)

    plot_wer_by_bitrate(df)
    plot_latency_by_model(df)
    plot_accuracy_vs_latency(df)
    plot_wer_distribution(df)
    plot_wer_heatmap(df)

    print(f"Wrote 5 plots to {OUT}/")


if __name__ == "__main__":
    main()
