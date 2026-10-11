"""
Demographic Distribution Analysis Pipeline
==========================================
Author: Raghavendra (imrpittala)
Project: SCT_DS_1 - SkillCraft Technology Data Science Internship
Objective: In-depth analysis and visualization of continuous (Age, Population,
           Life Expectancy) and categorical (Region, Income Group) demographic variables.
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def set_visual_style():
    """Configures professional publication-quality styling for matplotlib and seaborn."""
    sns.set_theme(style="whitegrid", palette="deep")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial"],
        "axes.edgecolor": "#cccccc",
        "axes.linewidth": 1.0,
        "grid.color": "#e0e0e0",
        "grid.linestyle": "--",
        "grid.alpha": 0.7,
        "figure.titlesize": 16,
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    })


def load_data(filepath: str) -> pd.DataFrame:
    """Loads demographic dataset from CSV and validates essential columns."""
    logger.info(f"Loading demographic dataset from {filepath}")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at {filepath}")
    
    df = pd.read_csv(filepath)
    logger.info(f"Loaded {df.shape[0]} records across {df.shape[1]} attributes.")
    return df


def compute_distribution_metrics(series: pd.Series) -> dict:
    """Calculates comprehensive parametric and non-parametric statistical metrics."""
    cleaned = series.dropna()
    mean_val = float(cleaned.mean())
    median_val = float(cleaned.median())
    std_val = float(cleaned.std())
    skew_val = float(cleaned.skew())
    kurt_val = float(cleaned.kurtosis())
    q25, q75 = float(cleaned.quantile(0.25)), float(cleaned.quantile(0.75))
    
    return {
        "mean": mean_val,
        "median": median_val,
        "std": std_val,
        "iqr": q75 - q25,
        "skewness": skew_val,
        "kurtosis": kurt_val,
        "min": float(cleaned.min()),
        "max": float(cleaned.max())
    }


def plot_continuous_demographics(df: pd.DataFrame, ax1: plt.Axes, ax2: plt.Axes):
    """
    Plots continuous demographic distributions:
    1. Median Age distribution histogram with KDE, mean, and median annotations.
    2. Life Expectancy vs Median Age with Population size weighting.
    """
    age_metrics = compute_distribution_metrics(df["Median_Age"])
    
    # 1. Annotated Histogram + KDE for Median Age
    sns.histplot(
        data=df,
        x="Median_Age",
        kde=True,
        color="#1f77b4",
        bins=15,
        ax=ax1,
        edgecolor="white",
        alpha=0.65,
        line_kws={"linewidth": 2.5, "color": "#0d47a1"}
    )
    
    ax1.axvline(
        age_metrics["mean"],
        color="#d32f2f",
        linestyle="--",
        linewidth=2,
        label=f"Mean: {age_metrics['mean']:.1f} yrs"
    )
    ax1.axvline(
        age_metrics["median"],
        color="#388e3c",
        linestyle="-.",
        linewidth=2,
        label=f"Median: {age_metrics['median']:.1f} yrs"
    )
    
    stats_text = (
        f"Std Dev: {age_metrics['std']:.1f}\n"
        f"Skewness: {age_metrics['skewness']:.2f}\n"
        f"IQR: {age_metrics['iqr']:.1f}"
    )
    ax1.text(
        0.05, 0.90, stats_text,
        transform=ax1.transAxes,
        fontsize=9.5,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffffff", edgecolor="#bbbbbb", alpha=0.9)
    )
    
    ax1.set_title("Global Median Age Distribution (Continuous)", weight="bold", pad=12)
    ax1.set_xlabel("Median Age (Years)")
    ax1.set_ylabel("Frequency (Count of Nations)")
    ax1.legend(loc="upper right", frameon=True)

    # 2. Continuous Scatter: Life Expectancy vs Median Age by Region
    sns.scatterplot(
        data=df,
        x="Median_Age",
        y="Life_Expectancy",
        hue="Region",
        size="Total_Population",
        sizes=(40, 400),
        alpha=0.85,
        palette="tab10",
        ax=ax2
    )
    
    # Regression trendline
    sns.regplot(
        data=df,
        x="Median_Age",
        y="Life_Expectancy",
        scatter=False,
        ax=ax2,
        color="#455a64",
        line_kws={"linestyle": ":", "linewidth": 2}
    )
    
    ax2.set_title("Longevity Correlation: Life Expectancy vs Median Age", weight="bold", pad=12)
    ax2.set_xlabel("Median Age (Years)")
    ax2.set_ylabel("Life Expectancy (Years)")
    ax2.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0, frameon=True, fontsize=8.5)


def plot_categorical_demographics(df: pd.DataFrame, ax3: plt.Axes, ax4: plt.Axes):
    """
    Plots categorical demographic distributions:
    1. Country distribution across Geographic Regions (Horizontal Bar Chart).
    2. Income Group distribution with gender ratio analysis.
    """
    # 1. Geographic Regions Count & Percentage
    region_counts = df["Region"].value_counts()
    total_countries = len(df)
    palette_reg = sns.color_palette("mako", len(region_counts))
    
    bars = ax3.barh(region_counts.index, region_counts.values, color=palette_reg, edgecolor="black", alpha=0.85)
    for bar in bars:
        width = bar.get_width()
        pct = (width / total_countries) * 100
        ax3.text(
            width + 0.5,
            bar.get_y() + bar.get_height() / 2,
            f"{int(width)} ({pct:.1f}%)",
            va="center",
            ha="left",
            fontsize=9.5,
            fontweight="semibold"
        )
        
    ax3.set_xlim(0, max(region_counts.values) * 1.25)
    ax3.set_title("Sample Distribution by World Region (Categorical)", weight="bold", pad=12)
    ax3.set_xlabel("Number of Countries")
    ax3.invert_yaxis()

    # 2. Income Group Distribution (Ordered Categories)
    income_order = ["Low income", "Lower middle income", "Upper middle income", "High income"]
    income_counts = df["Income_Group"].value_counts().reindex(income_order).fillna(0)
    
    palette_inc = ["#e57373", "#ffb74d", "#81c784", "#64b5f6"]
    bars_inc = ax4.bar(
        income_counts.index,
        income_counts.values,
        color=palette_inc,
        edgecolor="#333333",
        linewidth=1.2,
        alpha=0.9
    )
    
    for bar in bars_inc:
        height = bar.get_height()
        pct = (height / total_countries) * 100
        ax4.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.4,
            f"{int(height)}\n({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold"
        )
        
    ax4.set_ylim(0, max(income_counts.values) * 1.25)
    ax4.set_title("Country Distribution by Income Classification", weight="bold", pad=12)
    ax4.set_xlabel("World Bank Income Tier")
    ax4.set_ylabel("Number of Countries")
    ax4.tick_params(axis="x", rotation=12)


def generate_executive_report(df: pd.DataFrame, output_image_path: str):
    """
    Assembles a comprehensive 4-panel executive visual report
    and exports high-resolution output (300 DPI).
    """
    logger.info("Generating multi-panel executive visualization...")
    set_visual_style()
    
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    plt.subplots_adjust(hspace=0.35, wspace=0.32)
    
    # Header title
    fig.suptitle(
        "Global Demographic & Population Distribution Analysis Dashboard\n"
        "SkillCraft Technology Data Science Internship | Task 1 (SCT_DS_1)",
        fontsize=18,
        fontweight="bold",
        y=0.98
    )
    
    # Generate subplots
    plot_continuous_demographics(df, axes[0, 0], axes[0, 1])
    plot_categorical_demographics(df, axes[1, 0], axes[1, 1])
    
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    plt.savefig(output_image_path, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info(f"Executive visual report exported successfully to: {output_image_path}")


def export_statistical_summary(df: pd.DataFrame, output_json_path: str):
    """Computes and dumps key statistical highlights into JSON."""
    summary = {
        "dataset_metrics": {
            "total_countries_analyzed": int(len(df)),
            "global_population_sum": int(df["Total_Population"].sum()),
            "median_age_metrics": compute_distribution_metrics(df["Median_Age"]),
            "life_expectancy_metrics": compute_distribution_metrics(df["Life_Expectancy"]),
            "urbanization_metrics": compute_distribution_metrics(df["Urban_Population_Pct"])
        },
        "regional_breakdown": df.groupby("Region")["Total_Population"].agg(["count", "sum"]).to_dict(),
        "income_group_counts": df["Income_Group"].value_counts().to_dict()
    }
    
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    logger.info(f"Statistical summary exported to: {output_json_path}")


def main():
    """Main execution function for demographic pipeline."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "dataset.csv")
    report_img_path = os.path.join(base_dir, "reports", "visual_insights.png")
    report_json_path = os.path.join(base_dir, "reports", "demographic_summary.json")
    
    logger.info("Initializing SCT_DS_1 Demographic Analysis Pipeline...")
    df = load_data(data_path)
    
    # Generate figures and metrics
    generate_executive_report(df, report_img_path)
    export_statistical_summary(df, report_json_path)
    logger.info("Pipeline execution completed successfully.")


if __name__ == "__main__":
    main()
