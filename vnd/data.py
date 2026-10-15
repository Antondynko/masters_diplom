from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Dataset:
    c: list[list[float]]
    d: list[list[float]]
    n: int
    m: int
    path: str
    median: int


def load_dataset(path: str, n: int, m: int, median: int | None = None) -> Dataset:
    p = Path(path)
    if median is None:
        parts = p.stem.split("_")
        if len(parts) < 3:
            raise ValueError(f"Невозможно извлечь количество предприятий (медиану) из имени файла: {p.name}. "
                             f"Передай медиану явно.")
        median = int(parts[2])

    c = [[0.0 for _ in range(m)] for _ in range(n)]
    d = [[0.0 for _ in range(m)] for _ in range(n)]

    with p.open("r") as f:
        for idx, line in enumerate(f):
            if idx < 3:
                continue
            parts = line.split()
            if not parts:
                continue
            i, j, cost, pref = (int(parts[0]), int(parts[1]), float(parts[2]), float(parts[3]))
            c[i][j] = cost
            d[i][j] = pref

    return Dataset(c=c, d=d, n=n, m=m, path=str(p), median=median)
