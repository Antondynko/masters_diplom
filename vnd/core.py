import time

from vnd.follower import follower
from vnd.leader import leader, leader_simplified
from vnd.local_search import local_search, improve
from vnd.neighborhoods import generate_y_start


def solve(y_start, c, d, V, n, p, mode="full", verbose=True, tracer=None):
    """
    Полный цикл поиска: Local_Search + Improve, пока есть улучшение.
    :param y_start: стартовое размещение или None (генерировать)
    :param c: матрица затрат
    :param d: матрица предпочтений
    :param V: порог
    :param n: размер множества предприятий
    :param p: количество открываемых предприятий
    :param mode: "full" (VND.py логика) или "simplified" (VND_siplified.py логика)
    :param verbose: печатать ли промежуточные результаты
    :param tracer: необязательный vnd.trace.Tracer для записи хода поиска - нужен для визуализации
    :return: (y_final, rho_final, elapsed)
    """
    leader_fn = leader if mode == "full" else leader_simplified

    def _log(*args):
        if verbose:
            print(*args)

    start = time.time()

    y = generate_y_start(n, p) if y_start is None else list(y_start)
    _log(y)
    rho_ij, rho = leader_fn(follower(y, d), c, V)
    _log(rho_ij)
    if tracer is not None:
        tracer.start(y, rho)

    current = y

    while True:
        r = local_search(current, d, c, V, leader_fn, verbose=verbose, tracer=tracer)
        _log(r)
        r_rho_ij, r_rho = leader_fn(follower(r, d), c, V)
        _log(r_rho)

        s = improve(r, d, c, V, leader_fn, verbose=verbose, tracer=tracer)
        _log(s)
        s_rho_ij, s_rho = leader_fn(follower(s, d), c, V)
        _log(s_rho)

        for row in s_rho_ij:
            _log(row)

        if s_rho > r_rho:
            current = s
            continue
        else:
            break

    end = time.time()
    elapsed = end - start
    return current, s_rho, elapsed
