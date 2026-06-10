"""Power BI–inspired chart theme: clean, minimal, consistent palette."""

from matplotlib.ticker import FuncFormatter

# Core palette (Microsoft Power BI–style)
C = {
    "primary": "#118DFF",
    "secondary": "#12239E",
    "success": "#1AAB40",
    "warning": "#FF8C00",
    "danger": "#D64550",
    "purple": "#7B61FF",
    "teal": "#0D9D9A",
    "neutral": "#605E5C",
    "grid": "#E8E8E8",
    "bg": "#FFFFFF",
}

PAYMENT_COLORS = {
    "UPI": C["primary"],
    "Credit Card": C["secondary"],
    "Debit Card": C["success"],
    "NetBanking": C["warning"],
    "Wallet": C["danger"],
}

STATUS_COLORS = {
    "success": C["success"],
    "failed": C["danger"],
    "declined": C["warning"],
    "disputed": C["purple"],
}

RISK_BUCKET_COLORS = {
    "Low": C["success"],
    "Med": C["warning"],
    "High": C["danger"],
    "Critical": "#8B1A1A",
}

MERCHANT_RISK_COLORS = {
    "Low Risk": C["success"],
    "Medium Risk": C["warning"],
    "High Risk": C["danger"],
    "No Activity": C["neutral"],
}


def apply_theme():
    import matplotlib.pyplot as plt

    try:
        from IPython.core.getipython import get_ipython

        ip = get_ipython()
        if ip is not None:
            ip.run_line_magic("matplotlib", "inline")
    except Exception:
        pass

    plt.rcParams.update(
        {
            "figure.facecolor": C["bg"],
            "figure.dpi": 100,
            "savefig.dpi": 150,
            "axes.facecolor": C["bg"],
            "axes.edgecolor": "#D1D1D1",
            "axes.labelcolor": "#252423",
            "axes.titleweight": "600",
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "text.color": "#252423",
            "xtick.color": C["neutral"],
            "ytick.color": C["neutral"],
            "font.size": 10,
            "grid.color": C["grid"],
            "grid.linewidth": 0.7,
            "legend.frameon": False,
            "legend.fontsize": 9,
        }
    )
    plt.style.use("seaborn-v0_8-whitegrid")


def style_axes(ax, *, grid_axis="y"):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, axis=grid_axis, color=C["grid"], linewidth=0.7, alpha=0.9)
    if grid_axis == "y":
        ax.grid(False, axis="x")


def inr_cr(x, _):
    if abs(x) >= 1e7:
        return f"₹{x / 1e7:.1f}Cr"
    if abs(x) >= 1e5:
        return f"₹{x / 1e5:.0f}L"
    return f"₹{x:,.0f}"


def inr_compact(x, _):
    if abs(x) >= 1e7:
        return f"₹{x / 1e7:.2f}Cr"
    if abs(x) >= 1e5:
        return f"₹{x / 1e5:.1f}L"
    return f"₹{x:,.0f}"


INR_CR = FuncFormatter(inr_cr)
INR_COMPACT = FuncFormatter(inr_compact)