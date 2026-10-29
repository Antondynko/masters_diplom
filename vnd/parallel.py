import os
import random
import statistics
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass

from vnd.core import solve
from vnd.neighborhoods import generate_y_start


@dataclass(frozen=True)
class Run:
    index: int
    y_start: list[int]
    y: list[int]
    objective: float
    elapsed: float


@dataclass(frozen=True)
class MultistartResult:
    best: Run
    runs: list[Run]
    elapsed: float
    workers: int

    @property
    def objectives(self):
        return [r.objective for r in self.runs]

    def summary(self):
        """
        :return: словарь со статистикой по стартам (лучшее, худшее, среднее, разброс)
        """
        objs = self.objectives
        return {
            "starts": len(objs),
            "best": max(objs),
            "worst": min(objs),
            "mean": statistics.fmean(objs),
            "stdev": statistics.stdev(objs) if len(objs) > 1 else 0.0,
        }


# Данные задачи в процессе-воркере: передаются один раз через initializer,
# чтобы не сериализовать матрицы c и d для каждого старта.
_ctx = None


def _init_worker(c, d, V, n, p, mode):
    global _ctx
    _ctx = (c, d, V, n, p, mode)


def _run_one(index, y_start):
    c, d, V, n, p, mode = _ctx
    y, objective, elapsed = solve(y_start, c, d, V, n, p, mode=mode, verbose=False)
    return Run(index=index, y_start=y_start, y=y, objective=objective, elapsed=elapsed)


def solve_multistart(c, d, V, n, p, starts, workers=None, seed=None, mode="full", on_run=None):
    """
    Мультистарт: независимые запуски solve из разных случайных стартов, параллельно по процессам.
    :param c: матрица затрат
    :param d: матрица предпочтений
    :param V: порог
    :param n: размер множества предприятий
    :param p: количество открываемых предприятий
    :param starts: число стартов
    :param workers: число процессов (по умолчанию os.cpu_count()); 1 - без пула, в текущем процессе
    :param seed: зерно генератора стартов; при одном seed результат не зависит от workers
    :param mode: "full" или "simplified"
    :param on_run: необязательный callback(Run), вызывается по завершении каждого старта
    :return: MultistartResult
    """
    if starts < 1:
        raise ValueError("Число стартов должно быть не меньше 1")
    if workers is None:
        workers = os.cpu_count() or 1
    workers = max(1, min(workers, starts))

    # Старты генерируются заранее в главном процессе - так воспроизводимость
    # не зависит от того, какой воркер возьмёт задачу.
    rng = random.Random(seed)
    y_starts = [generate_y_start(n, p, rng) for _ in range(starts)]

    start = time.time()
    runs = []
    if workers == 1:
        _init_worker(c, d, V, n, p, mode)
        for k, y0 in enumerate(y_starts):
            run = _run_one(k, y0)
            runs.append(run)
            if on_run is not None:
                on_run(run)
    else:
        with ProcessPoolExecutor(
            max_workers=workers,
            initializer=_init_worker,
            initargs=(c, d, V, n, p, mode),
        ) as pool:
            futures = [pool.submit(_run_one, k, y0) for k, y0 in enumerate(y_starts)]
            for fut in as_completed(futures):
                run = fut.result()
                runs.append(run)
                if on_run is not None:
                    on_run(run)
    elapsed = time.time() - start

    runs.sort(key=lambda r: r.index)
    # При равенстве целевой функции выигрывает старт с меньшим номером - детерминированно.
    best = max(runs, key=lambda r: (r.objective, -r.index))
    return MultistartResult(best=best, runs=runs, elapsed=elapsed, workers=workers)
