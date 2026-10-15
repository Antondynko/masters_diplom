import time

from vnd.follower import Folower
from vnd.leader import Leader, Leader_simplified
from vnd.local_search import Local_Search, Improve
from vnd.neighborhoods import Generate_y_start


def solve(y_start, c, d, V, n, p, mode="full", verbose=True):
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
    :return: (y_final, rho_final, elapsed)
    """
    leader_fn = Leader if mode == "full" else Leader_simplified

    def _log(*args):
        if verbose:
            print(*args)

    start = time.time()

    y = Generate_y_start(n, p) if y_start is None else list(y_start)
    _log(y)
    rho_ij, rho = leader_fn(Folower(y, d), c, V)
    _log(rho_ij)

    current = y

    while True:
        r = Local_Search(current, d, c, V, leader_fn, verbose=verbose)
        _log(r)
        r_rho_ij, r_rho = leader_fn(Folower(r, d), c, V)
        _log(r_rho)

        s = Improve(r, d, c, V, leader_fn, verbose=verbose)
        _log(s)
        s_rho_ij, s_rho = leader_fn(Folower(s, d), c, V)
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
