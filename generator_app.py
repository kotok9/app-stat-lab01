import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    return mo, np, plt


@app.cell
def _():
    # --- единый стиль графиков: те же настройки, что в lab01_style.ipynb--
    import matplotlib as mpl

    C_DATA = "#1F4E8C"
    C_THEORY = "#E85D04"
    C_ACCENT = "#9B5DE5"
    C_MUTED = "#8A94A6"
    C_PALETTE = [C_DATA, C_THEORY, C_ACCENT, C_MUTED, "#2A9D8F", "#C9184A"]

    # Блок Б: полотно
    mpl.rcParams.update({
        "figure.figsize": (9, 5),
        "figure.dpi": 110,
    })
    # Блок В: шрифты
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans"],
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 12,
    })
    # Блок Г: рамки и сетка
    mpl.rcParams.update({
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": "#D9DEE7",
        "grid.linewidth": 0.8,
    })
    # Блок Д: деления осей
    mpl.rcParams.update({
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    })
    # Блок Е: линии, легенда, порядок цветов
    mpl.rcParams.update({
        "legend.frameon": False,
        "legend.fontsize": 10,
        "lines.linewidth": 2.0,
        "axes.prop_cycle": mpl.cycler(color=C_PALETTE),
    })
    return C_ACCENT, C_DATA, C_MUTED, C_THEORY


@app.cell
def _(np):
    # Заглушка генератора: подменим на настоящий датчик из ноутбука по болидам
    def generate_intervals(n, mean_days, seed=0):
        rng = np.random.default_rng(seed)
        return rng.exponential(mean_days, size=n)

    return (generate_intervals,)


@app.cell
def _(mo):
    mo.md(
        """
        # Генератор интервалов между болидами

        Модель: падения болидов образуют пуассоновский поток, интервалы между
        соседними событиями распределены показательно (экспоненциально).
        Двигайте ползунки: графики и числа пересчитываются сразу.
        """
    )
    return


@app.cell
def _(mo):
    mean_days = mo.ui.slider(
        1, 30, value=11, step=1,
        label="Среднее время между болидами, дней",
        show_value=True,
    )
    n_events = mo.ui.slider(
        50, 5000, value=1000, step=50,
        label="Сколько болидов сгенерировать",
        show_value=True,
    )
    mo.hstack([mean_days, n_events], justify="space-between")
    return mean_days, n_events


@app.cell
def _(generate_intervals, mean_days, n_events, np):
    intervals = generate_intervals(int(n_events.value), float(mean_days.value), seed=7)
    moments = np.cumsum(intervals)  # моменты падений, дней от начала наблюдения
    return intervals, moments


@app.cell
def _(C_ACCENT, C_DATA, C_THEORY, intervals, mean_days, np, plt):
    mu_th = float(mean_days.value)
    x_max = float(np.quantile(intervals, 0.995)) * 1.05
    fig, ax = plt.subplots()
    ax.hist(
        intervals, bins=40, range=(0, x_max), density=True,
        color=C_DATA, alpha=0.6, edgecolor="white", linewidth=0.5,
        label="сгенерированные интервалы",
    )
    x_grid = np.linspace(0.0, x_max, 300)
    ax.plot(
        x_grid, np.exp(-x_grid / mu_th) / mu_th,
        color=C_THEORY, linewidth=2.5, label="теоретическая плотность",
    )
    ax.axvline(
        mu_th, color=C_ACCENT, linestyle="--", linewidth=2,
        label=f"теоретическое среднее = {mu_th:.0f} дн.",
    )
    ax.set_title("Гистограмма интервалов и теоретическая плотность")
    ax.set_xlabel("интервал между падениями, дней")
    ax.set_ylabel("плотность, 1/день")
    ax.legend()
    fig
    return


@app.cell
def _(intervals, mean_days, mo, np):
    mu_stat = float(mean_days.value)
    sample_mean = float(np.mean(intervals))
    sample_std = float(np.std(intervals, ddof=1))
    mo.md(
        f"**Сгенерированные интервалы:** среднее **{sample_mean:.2f} дн.**, "
        f"стандартное отклонение **{sample_std:.2f} дн.**"
        "\n\n"
        f"**Теория (показательное распределение):** среднее **{mu_stat:.2f} дн.**, "
        f"стандартное отклонение **{mu_stat:.2f} дн.** — у него σ = μ"
        "\n\n"
        "Чем больше n (второй ползунок), тем ближе выборочные числа к теоретическим: "
        "это и есть совпадение метрик генератора и распределения."
    )
    return


@app.cell
def _(C_DATA, moments, plt):
    fig_time, ax_time = plt.subplots(figsize=(9, 2.6))
    ax_time.eventplot(
        moments, lineoffsets=0, linelengths=0.8,
        colors=C_DATA, linewidths=1.2,
    )
    ax_time.set_title("Лента времени: моменты падения болидов")
    ax_time.set_xlabel("время, дней")
    ax_time.set_yticks([])
    fig_time
    return


@app.cell
def _(moments, mo):
    mo.md(
        f"Лента тянется **{float(moments[-1]):.0f} дней** — столько «длилось» наблюдение, "
        f"пока не упали все {len(moments)} сгенерированных болидов."
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ---
        Сейчас работает заглушка `generate_intervals` (numpy, показательное
        распределение). Она подменяется настоящим датчиком из ноутбука
        по болидам; имя функции и параметры остаются теми же.
        """
    )
    return


if __name__ == "__main__":
    app.run()
