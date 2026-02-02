import time
import matplotlib.pyplot as plt
from observability.tracer import TraceRun


def render_chart(df, chart_type="bar", trace: TraceRun | None = None):
    """
    Convention:
    - Colonne 0 = X (catégories)
    - Colonne 1 = Y (valeurs numériques)
    """

    start = time.time()
    fig, ax = plt.subplots(figsize=(7, 4))

    x = df.iloc[:, 0]
    y = df.iloc[:, 1] if df.shape[1] > 1 else None

    if chart_type == "bar":
        ax.bar(range(len(x)), y)
        ax.set_xticks(range(len(x)))
        ax.set_xticklabels(x, rotation=45, ha="right")
        ax.set_ylabel(df.columns[1])

    elif chart_type == "hist":
        ax.hist(y.dropna(), bins=10)
        ax.set_xlabel(df.columns[1])
        ax.set_ylabel("Frequency")

    elif chart_type == "pie":
        ax.pie(y, labels=x, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")

    ax.set_title("Visualisation des résultats")
    plt.tight_layout()

    if trace:
        trace.log(
            "chart_generation",
            {
                "type": chart_type,
                "rows": len(df),
                "duration_ms": int((time.time() - start) * 1000)
            }
        )

    return fig
