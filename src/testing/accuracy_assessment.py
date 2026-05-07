import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

from src.utils.logger import AppLogger
from src.config.constants import (
    MEAN,
    STD,
    MIN,
    MAX,
    ACCURACY_SCORE,
    CV,
    RANGE,
    ERROR_RATE,
    TABLE,
    MOST_RELIABLE,
    RANKING,
)


class AccuracyAssessment:

    def __init__(self):
        self.logger = AppLogger("AccuracyAssessment")

    # =========================================================
    # MAIN COMPARISON ENGINE (OOP VERSION)
    # =========================================================
    def compare_ammeters(self, results):
        """
        Compare normalized ammeter results and generate metrics:
        mean, std, min, max, coefficient of variation, range, error rate, accuracy score
        """

        self.logger.info("Starting ammeter comparison")

        metrics = {}

        for r in results:

            ammeter = r.ammeter
            self.logger.info(f"Processing {ammeter}")

            samples = np.array(r.samples, dtype=float)

            if samples.size == 0:
                self.logger.warning(f"{ammeter} has no samples")
                continue

            mean = float(np.mean(samples))
            std = float(np.std(samples, ddof=1)) if len(samples) > 1 else 0.0
            min_v = float(np.min(samples))
            max_v = float(np.max(samples))

            cv = std / (mean + 1e-9)
            value_range = max_v - min_v
            error_rate = r.errors / max(len(samples), 1)

            accuracy_score = 1 / (
                (std + 1e-6) *
                (1 + cv) *
                (1 + error_rate) *
                (1 + value_range * 0.01)
            )

            self.logger.debug(
                f"{ammeter} -> mean={mean:.2f}, std={std:.2f}, score={accuracy_score:.6f}"
            )

            metrics[ammeter] = {
                MEAN: mean,
                STD: std,
                MIN: min_v,
                MAX: max_v,
                CV: cv,
                RANGE: value_range,
                ERROR_RATE: error_rate,
                ACCURACY_SCORE: accuracy_score
            }

        if not metrics:
            self.logger.error("No metrics generated")
            return {
                TABLE: pd.DataFrame(),
                MOST_RELIABLE: None,
                RANKING: {}
            }

        df = pd.DataFrame(metrics).T
        df = df.sort_values(ACCURACY_SCORE, ascending=False)

        most_reliable = df.index[0]
        ranking = df[ACCURACY_SCORE].to_dict()

        self.logger.info(f"Most reliable ammeter: {most_reliable}")

        return {
            TABLE: df,
            MOST_RELIABLE: most_reliable,
            RANKING: ranking
        }

    # =========================================================
    # VISUALIZATION
    # =========================================================
    def plot_comparison(self, df):
        """
        Plot the accuracy scores for all ammeters
        """

        self.logger.info("Generating comparison plot")

        if df is None or df.empty:
            self.logger.warning("Empty dataframe - no plot generated")
            return None

        fig, ax = plt.subplots(figsize=(6, 4))
        df = df.sort_values(ACCURACY_SCORE, ascending=True)
        ax.bar(df.index, df[ACCURACY_SCORE])
        ax.set_title("Ammeter Accuracy Comparison")
        ax.set_xlabel("Ammeter")
        ax.set_ylabel("Accuracy Score")
        fig.tight_layout()

        self.logger.info("Plot generated successfully")
        return fig

    # =========================================================
    # SAVE RAW SIGNAL PLOTS
    # =========================================================
    def save_raw_plots(self, results, save_dir="results"):
        """
        Save raw sample plots for all ammeters
        """

        self.logger.info(f"Saving raw plots to {save_dir}")
        os.makedirs(save_dir, exist_ok=True)

        # Use .samples since results are NormalizedAmmeterResult
        valid_results = [
            r for r in results
            if r.ammeter and len(r.samples) > 0
        ]

        if not valid_results:
            self.logger.warning("No valid results to plot")
            return

        for r in valid_results:
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.plot(r.samples, marker="o", linewidth=1)
            ax.set_title(f"{r.ammeter} - Current Measurements")
            ax.set_xlabel("Sample")
            ax.set_ylabel("Value")
            fig.tight_layout()

            file_path = os.path.join(save_dir, f"{r.ammeter}_plot.png")
            fig.savefig(file_path, dpi=120)
            plt.close(fig)
            self.logger.info(f"Saved plot: {file_path}")