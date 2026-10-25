"""
Карта пространства решений: все C(n, p) размещений проецируются на плоскость
по расстоянию Хэмминга (UMAP), поверх рисуется путь одного запуска VND.

Запуск из корня репозитория:
    .venv/bin/python -m viz.landscape --p 5 --seed 2
"""
import argparse
import random
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

from vnd.core import solve
from vnd.data import load_dataset
from vnd.follower import follower
from vnd.leader import leader
from vnd.trace import Tracer

CACHE_DIR = Path(__file__).parent / "cache"
OUTPUT_DIR = Path(__file__).parent / "output"


def enumerate_solutions(n, p):
    """
    :return: матрица (C(n,p), n) всех бинарных размещений с ровно p единицами
    """
    combos = list(combinations(range(n), p))
    Y = np.zeros((len(combos), n), dtype=np.uint8)
    for k, idx in enumerate(combos):
        Y[k, list(idx)] = 1
    return Y


def objectives(Y, c, d, V):
    """
    Векторизованный follower + leader: значение V - f для каждого размещения.
    Разрыв ничьих совпадает с follower(): берётся первое предприятие с минимальным d.
    """
    c = np.asarray(c)
    d = np.asarray(d)
    masked = np.where(Y[:, :, None] == 1, d[None, :, :], np.inf)
    assigned = masked.argmin(axis=1)
    f = c[assigned, np.arange(c.shape[1])].sum(axis=1)
    return V - f


def embed(Y, seed, cache_key):
    """
    UMAP-проекция по метрике Хэмминга. Результат кэшируется: проекция не зависит от запуска VND.
    """
    CACHE_DIR.mkdir(exist_ok=True)
    path = CACHE_DIR / f"umap_{cache_key}_seed{seed}.npy"
    if path.exists():
        return np.load(path)

    import umap
    xy = umap.UMAP(
        n_neighbors=30, min_dist=0.3, metric="hamming", random_state=seed
    ).fit_transform(Y)
    np.save(path, xy)
    return xy


def curve(a, b, bend=0.25, steps=16):
    """
    Квадратичная кривая Безье от a к b, изогнутая вбок — чтобы рёбра выглядели как сосуды.
    """
    a, b = np.asarray(a), np.asarray(b)
    mid = (a + b) / 2
    normal = np.array([b[1] - a[1], a[0] - b[0]])
    ctrl = mid + bend * normal
    t = np.linspace(0, 1, steps)[:, None]
    return (1 - t) ** 2 * a + 2 * (1 - t) * t * ctrl + t ** 2 * b


def plot(xy, values, index, tracer, out_path, title):
    fig, ax = plt.subplots(figsize=(12, 12), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Фон: все решения, цвет — значение целевой функции
    order = np.argsort(values)
    sc = ax.scatter(
        xy[order, 0], xy[order, 1], c=values[order], cmap="YlGn",
        s=4, alpha=0.6, linewidths=0, zorder=1,
    )

    capillaries, arteries, jumps = [], [], []
    for e in tracer.events:
        if e.kind == "start":
            continue
        seg = curve(xy[index[e.parent]], xy[index[e.child]], bend=0.15 if e.move == "swap1" else 0.35)
        if e.kind == "evaluate":
            capillaries.append((seg, e.move))
        elif e.move == "swap1":
            arteries.append(seg)
        else:
            jumps.append(seg)

    # Капилляры: все просмотренные соседи
    ax.add_collection(LineCollection(
        [s for s, m in capillaries if m == "swap1"], colors="#e88", linewidths=0.4, alpha=0.5, zorder=2,
    ))
    ax.add_collection(LineCollection(
        [s for s, m in capillaries if m == "swap2"], colors="#89c", linewidths=0.25, alpha=0.35, zorder=2,
    ))
    # Артерии: принятые ходы локального спуска и прыжки 2-swap
    ax.add_collection(LineCollection(arteries, colors="#a00", linewidths=2.8, zorder=4, capstyle="round"))
    ax.add_collection(LineCollection(jumps, colors="#036", linewidths=2.8, linestyles=(0, (4, 2)), zorder=4))

    start = next(e for e in tracer.events if e.kind == "start")
    accepted = [e for e in tracer.events if e.kind == "accept"]
    final = accepted[-1].child if accepted else start.child
    best = int(np.argmax(values))

    for e in accepted:
        p = xy[index[e.child]]
        ax.scatter(*p, s=18, color="#a00" if e.move == "swap1" else "#036", zorder=5)
    ax.scatter(*xy[index[start.child]], s=140, marker="o", facecolor="white", edgecolor="black", lw=2, zorder=6,
               label=f"старт  {start.value:,.0f}")
    ax.scatter(*xy[index[final]], s=220, marker="*", color="#a00", edgecolor="black", zorder=7,
               label=f"итог VND  {values[index[final]]:,.0f}")
    ax.scatter(*xy[best], s=220, marker="*", color="gold", edgecolor="black", zorder=7,
               label=f"глобальный оптимум  {values[best]:,.0f}")

    ax.plot([], [], color="#a00", lw=2.8, label="ход локального спуска (1-swap)")
    ax.plot([], [], color="#036", lw=2.8, ls=(0, (4, 2)), label="прыжок improve (2-swap)")
    ax.plot([], [], color="#e88", lw=1, label="просмотренные 1-swap соседи")
    ax.plot([], [], color="#89c", lw=1, label="просмотренные 2-swap соседи")
    ax.legend(loc="lower left", frameon=False, fontsize=9)

    cb = fig.colorbar(sc, ax=ax, shrink=0.4, pad=0.01)
    cb.set_label("V − f")
    ax.set_title(title, fontsize=12)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    print(f"Сохранено: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Карта пространства решений и путь VND.")
    parser.add_argument("--dataset", default="datasets/20_20_15.txt")
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--m", type=int, default=20)
    parser.add_argument("--V", type=int, default=47000)
    parser.add_argument("--p", type=int, default=15)
    parser.add_argument("--seed", type=int, default=1, help="Сид стартового решения")
    parser.add_argument("--umap-seed", type=int, default=42)
    parser.add_argument(
        "--out", default=None,
        help="Путь к PNG (по умолчанию viz/output/landscape_{датасет}_p{p}_seed{seed}.png)",
    )
    args = parser.parse_args()
    out = args.out or OUTPUT_DIR / f"landscape_{Path(args.dataset).stem}_p{args.p}_seed{args.seed}.png"

    ds = load_dataset(args.dataset, n=args.n, m=args.m)
    Y = enumerate_solutions(ds.n, args.p)
    values = objectives(Y, ds.c, ds.d, args.V)
    index = {tuple(int(b) for b in row): k for k, row in enumerate(Y)}

    # Сверка векторизованной функции с исходным follower/leader
    for k in random.Random(0).sample(range(len(Y)), 20):
        _, ref = leader(follower(list(Y[k]), ds.d), ds.c, args.V)
        assert np.isclose(ref, values[k]), (k, ref, values[k])

    print(f"Решений: {len(Y)}, V−f от {values.min():,.0f} до {values.max():,.0f}")
    xy = embed(Y, args.umap_seed, f"{Path(args.dataset).stem}_p{args.p}")

    random.seed(args.seed)
    tracer = Tracer()
    solve(None, ds.c, ds.d, args.V, ds.n, args.p, verbose=False, tracer=tracer)
    n_eval = sum(e.kind == "evaluate" for e in tracer.events)
    n_acc = sum(e.kind == "accept" for e in tracer.events)
    print(f"Просмотрено соседей: {n_eval}, принято ходов: {n_acc}")

    plot(xy, values, index, tracer, out,
         f"{Path(args.dataset).name}, V={args.V}, p={args.p}, seed={args.seed}")


if __name__ == "__main__":
    main()
