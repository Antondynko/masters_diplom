import argparse

from vnd.core import solve
from vnd.data import load_dataset


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
    args = parser.parse_args()

    ds = load_dataset(args.dataset, n=20, m=20)

    print(f"Dataset: {ds.path} (n={ds.n}, m={ds.m}, median={ds.median})")
    print(f"V={args.V}, p={args.p}, mode={'simplified' if args.simplified else 'full'}")
    print()

    y_final, rho_final, elapsed = solve(
        None, ds.c, ds.d, args.V, ds.n, args.p,
        mode="simplified" if args.simplified else "full",
        verbose=True,
    )
    print(f"Elapsed time: {elapsed:.3f}s")


if __name__ == "__main__":
    main()
