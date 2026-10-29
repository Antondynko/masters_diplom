import argparse
import random

from vnd.core import solve
from vnd.data import load_dataset
from vnd.parallel import solve_multistart


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Двухуровневая задача размещения: локальный спуск + 2-swap."
    )
    parser.add_argument(
        "--dataset",
        default="datasets/20_20_15.txt",
        help="Путь к .txt-датасету (по умолчанию datasets/20_20_15.txt)",
    )
    parser.add_argument("--V", type=int, default=47000, help="Порог (по умолчанию 47000)")
    parser.add_argument("--p", type=int, default=15, help="Количество предприятий (по умолчанию 15)")
    parser.add_argument(
        "--simplified",
        action="store_true",
        help="Использовать упрощённую модель Leader (VND_siplified.py логика)",
    )
    parser.add_argument(
        "--starts",
        type=int,
        default=1,
        help="Число стартов мультистарта (по умолчанию 1 - одиночный запуск с подробным выводом)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Число процессов для мультистарта (по умолчанию - число ядер)",
    )
    parser.add_argument("--seed", type=int, default=None, help="Зерно генератора стартов")
    args = parser.parse_args()

    ds = load_dataset(args.dataset, n=20, m=20)
    mode = "simplified" if args.simplified else "full"

    print(f"Dataset: {ds.path} (n={ds.n}, m={ds.m}, median={ds.median})")
    print(f"V={args.V}, p={args.p}, mode={mode}")
    print()

    if args.starts == 1:
        if args.seed is not None:
            random.seed(args.seed)
        y_final, rho_final, elapsed = solve(
            None, ds.c, ds.d, args.V, ds.n, args.p,
            mode=mode,
            verbose=True,
        )
        print(f"Elapsed time: {elapsed:.3f}s")
        return

    def _report(run):
        print(f"Старт {run.index:>3}: {run.objective:.3f} ({run.elapsed:.3f}s)")

    result = solve_multistart(
        ds.c, ds.d, args.V, ds.n, args.p,
        starts=args.starts, workers=args.workers, seed=args.seed, mode=mode,
        on_run=_report,
    )
    s = result.summary()
    print()
    print(f"Стартов: {s['starts']}, процессов: {result.workers}")
    print(f"Лучшее: {s['best']:.3f} (старт {result.best.index})")
    print(f"Худшее: {s['worst']:.3f}")
    print(f"Среднее: {s['mean']:.3f} ± {s['stdev']:.3f}")
    print(f"y: {result.best.y}")
    print(f"Elapsed time: {result.elapsed:.3f}s")


if __name__ == "__main__":
    main()
