import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    import requests
    return mo, np, plt, requests


@app.cell
def _():
    # единый стиль графиков: те же цвета и шрифты, что в lab01_style.ipynb
    import matplotlib as mpl

    C_DATA = "#1F4E8C"     # настоящие данные
    C_THEORY = "#E85D04"   # теоретическая кривая
    C_ACCENT = "#9B5DE5"   # генератор
    C_MUTED = "#8A94A6"    # вспомогательные линии
    C_PALETTE = [C_DATA, C_THEORY, C_ACCENT, C_MUTED, "#2A9D8F", "#C9184A"]

    mpl.rcParams.update({
        "figure.figsize": (9, 5.2),
        "figure.dpi": 110,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans"],
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 12,
        "axes.edgecolor": "#B9C0CC",
        "axes.linewidth": 1.0,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": "#D9DEE7",
        "grid.linewidth": 0.8,
        "grid.alpha": 0.7,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "xtick.color": "#4A5568",
        "ytick.color": "#4A5568",
        "lines.linewidth": 2.0,
        "legend.frameon": False,
        "legend.fontsize": 10,
        "axes.prop_cycle": mpl.cycler(color=C_PALETTE),
    })
    return C_ACCENT, C_DATA, C_MUTED, C_THEORY


@app.cell
def _(np):
    # Генератор из ноутбука lab01_fireballs.ipynb (раздел 6)
    # шаг 1: свой датчик равномерных чисел от 0 до 1 (линейный конгруэнтный метод)
    def lcg(n, seed=1):
        a = 6364136223846793005
        c = 1442695040888963407
        m = 2 ** 64
        x = seed
        numbers = []
        for i in range(n):
            x = (a * x + c) % m
            numbers.append(x / m)
        return np.array(numbers)

    # шаг 2: превращаем равномерные числа в интервалы между болидами
    def generate_intervals(n, mean_days, seed=1):
        u = lcg(n, seed)
        return -mean_days * np.log(1 - u)

    return (generate_intervals,)


@app.cell
def _(np, requests):
    # настоящие интервалы между болидами из каталога NASA, как в основном отчете
    # (болиды с 1994 года, дата конца зафиксирована)
    URL = "https://ssd-api.jpl.nasa.gov/fireball.api?date-max=2026-10-31"
    try:
        answer = requests.get(URL, timeout=30).json()
        column = answer["fields"].index("date")
        dates = np.sort(np.array([row[column] for row in answer["data"]], dtype="datetime64[s]"))
        dates = dates[dates >= np.datetime64("1994-01-01")]
        real_intervals = np.diff(dates).astype(float) / 86400
    except Exception:
        # без интернета страница работает, просто без сравнения с настоящими данными
        real_intervals = None
    return (real_intervals,)


@app.cell
def _(mo):
    mo.md(
        """
        # Генератор интервалов между болидами

        Болиды падают независимо друг от друга, поэтому время между соседними
        болидами распределено экспоненциально. Генератор из нашего отчета выдает
        такие интервалы. Здесь можно менять его настройки и сравнивать результат
        с теорией и с настоящими данными NASA.
        """
    )
    return


@app.cell
def _(mo):
    mean_days = mo.ui.slider(
        8, 30, value=11, step=1,
        label="Среднее время между болидами, дней",
        show_value=True,
    )
    n_events = mo.ui.slider(
        50, 5000, value=1000, step=50,
        label="Сколько болидов сгенерировать",
        show_value=True,
    )
    seed = mo.ui.slider(
        1, 100, value=7, step=1,
        label="Зерно датчика (другая случайная выборка)",
        show_value=True,
    )
    show_real = mo.ui.checkbox(value=True, label="показывать настоящие данные NASA")
    mo.vstack([
        mo.hstack([mean_days, n_events], justify="space-between"),
        mo.hstack([seed, show_real], justify="space-between"),
    ])
    return mean_days, n_events, seed, show_real


@app.cell
def _(generate_intervals, mean_days, n_events, np, seed):
    intervals = generate_intervals(int(n_events.value), float(mean_days.value), seed=int(seed.value))
    moments = np.cumsum(intervals)   # моменты падений, дней от начала наблюдения
    return intervals, moments


@app.cell
def _(intervals, mean_days, mo, np, real_intervals):
    # главные числа карточками: генератор, теория и настоящие данные
    cards = [
        mo.stat(
            value=f"{np.mean(intervals):.2f} дн.",
            label="Среднее у генератора",
            caption=f"по теории {float(mean_days.value):.2f} дн.",
            bordered=True,
        ),
        mo.stat(
            value=f"{np.std(intervals, ddof=1):.2f} дн.",
            label="Стандартное отклонение у генератора",
            caption=f"по теории {float(mean_days.value):.2f} дн., равно среднему",
            bordered=True,
        ),
        mo.stat(
            value=f"{np.max(intervals):.0f} дн.",
            label="Самый длинный интервал",
            caption="редкие долгие перерывы тоже бывают",
            bordered=True,
        ),
    ]
    if real_intervals is not None:
        cards.append(
            mo.stat(
                value=f"{np.mean(real_intervals):.2f} дн.",
                label="Среднее в данных NASA",
                caption=f"{len(real_intervals)} интервалов с 1994 года",
                bordered=True,
            )
        )
    mo.hstack(cards, widths="equal")
    return


@app.cell
def _(
    C_ACCENT,
    C_DATA,
    C_MUTED,
    C_THEORY,
    intervals,
    mean_days,
    np,
    plt,
    real_intervals,
    show_real,
):
    # оси закреплены: при движении ползунка видно как меняется само распределение
    X_MAX = 120
    bins = np.arange(0, X_MAX + 3, 3)
    mu = float(mean_days.value)

    fig, ax = plt.subplots()
    ax.hist(
        intervals, bins=bins, density=True,
        color=C_ACCENT, alpha=0.6, edgecolor="white", linewidth=0.5,
        label="генератор",
    )
    if show_real.value and real_intervals is not None:
        ax.hist(
            real_intervals, bins=bins, density=True,
            histtype="step", color=C_DATA, linewidth=2,
            label="настоящие данные NASA",
        )
    x_grid = np.linspace(0, X_MAX, 400)
    ax.plot(x_grid, np.exp(-x_grid / mu) / mu, color=C_THEORY, linewidth=2.5, label="теория")
    ax.axvline(mu, color=C_MUTED, linestyle="--", linewidth=1.5, label=f"среднее по теории, {mu:.0f} дн.")
    ax.set_xlim(0, X_MAX)
    ax.set_ylim(0, 0.13)
    ax.set_title("Интервалы между болидами: генератор, теория и данные")
    ax.set_xlabel("интервал между болидами, дни")
    ax.set_ylabel("плотность, 1/день")
    ax.legend()
    fig
    return


@app.cell
def _(mean_days, mo, real_intervals):
    if real_intervals is not None:
        about_real = (
            "Настоящие данные NASA (синяя линия) не меняются, у них среднее около 11 дней, "
            "поэтому генератор совпадает с ними когда ползунок стоит на 11."
        )
    else:
        about_real = (
            "Настоящие данные NASA сейчас не загрузились (каталог не ответил), "
            "поэтому на графике только генератор и теория. Если перезапустить страницу позже, появится синяя линия с данными."
        )
    mo.md(
        f"""
        Оси на графике не двигаются. Если увеличивать среднее время, фиолетовые
        столбики и оранжевая кривая становятся ниже и растягиваются вправо:
        коротких интервалов становится меньше, длинных больше. {about_real}
        Сейчас среднее {float(mean_days.value):.0f} дн.
        """
    )
    return


@app.cell
def _(C_ACCENT, moments, np, plt):
    # лента времени: показываем первые два года, иначе отдельные болиды сливаются
    DAYS = 730
    shown = moments[moments <= DAYS]

    fig_time, ax_time = plt.subplots(figsize=(9, 2.2))
    ax_time.vlines(shown, 0, 1, color=C_ACCENT, linewidth=1.6)
    ax_time.set_xlim(0, DAYS)
    ax_time.set_ylim(0, 1)
    ax_time.set_xticks([0, 182, 365, 547, 730])
    ax_time.set_xticklabels(["0", "полгода", "1 год", "полтора года", "2 года"])
    ax_time.set_yticks([])
    ax_time.grid(False)
    ax_time.set_title("Лента времени: когда падали болиды в первые два года")
    ax_time.set_xlabel("время от начала наблюдения")
    fig_time
    return (shown,)


@app.cell
def _(mo, moments, shown):
    mo.md(
        f"""
        Каждая черточка это один болид. За первые два года их упало **{len(shown)}**.
        Видно что они идут неравномерно: то несколько подряд, то долгий перерыв.
        Так и должно быть у случайного потока. Все {len(moments)} сгенерированных
        болидов заняли бы **{float(moments[-1]) / 365:.0f} лет** наблюдений.
        """
    )
    return


@app.cell
def _(C_ACCENT, C_THEORY, mean_days, moments, np, plt):
    # вторая проверка: число болидов за месяц должно быть распределено по Пуассону
    from math import exp, factorial

    MONTH = 30.44
    per_month = np.bincount((moments // MONTH).astype(int))[:-1]   # последний месяц неполный
    lam_month = MONTH / float(mean_days.value)
    k = np.arange(0, 16)
    share = np.array([(per_month == j).mean() for j in k]) if len(per_month) else np.zeros(len(k))
    poisson = np.array([lam_month ** int(j) * exp(-lam_month) / factorial(int(j)) for j in k])

    fig_month, ax_month = plt.subplots(figsize=(9, 4))
    ax_month.bar(k, share, color=C_ACCENT, alpha=0.6, label="генератор")
    ax_month.plot(k, poisson, "o-", color=C_THEORY, label="распределение Пуассона")
    ax_month.set_xticks(k)
    ax_month.set_ylim(0, 0.65)
    ax_month.set_title("Сколько болидов за месяц дает генератор")
    ax_month.set_xlabel("число болидов за месяц, шт")
    ax_month.set_ylabel("доля месяцев")
    ax_month.legend()
    fig_month
    return


@app.cell
def _(mo):
    mo.md(
        """
        Если интервалы экспоненциальные, то число болидов за месяц должно быть
        распределено по Пуассону. Столбики генератора ложатся на оранжевые точки.
        Чем больше болидов сгенерировать (второй ползунок), тем точнее совпадение.

        ---
        Генератор тот же что в разделе 6 отчета `lab01_fireballs.ipynb`: свой датчик
        равномерных чисел (линейный конгруэнтный метод) и метод обратной функции.
        Готовый датчик из numpy не используется.
        """
    )
    return


if __name__ == "__main__":
    app.run()
