from vnd.follower import follower
from vnd.neighborhoods import swap, swap_2
from vnd.leader import leader, leader_simplified


def n(y, d, c, V, leader_fn=leader, tracer=None):
    """
    Выбрать лучшего соседа 1-swap (first-improvement).
    :param y: стартовое размещение
    :param d: матрица предпочтений
    :param c: матрица затрат
    :param V: порог
    :param leader_fn: функция leader
    :param tracer: необязательный vnd.trace.Tracer - нужен для визуализации
    :return: сосед с улучшением или y
    """
    neighbors = swap(y)
    _, delta_rho = leader_fn(follower(y, d), c, V)

    for v in neighbors:
        _, g = leader_fn(follower(v, d), c, V)
        if tracer is not None:
            tracer.evaluate(y, v, g, "swap1")
        if g > delta_rho:
            if tracer is not None:
                tracer.accept(y, v, g, "swap1")
            return v
    return y


def local_search(y, d, c, V, leader_fn=leader, max_iter=100, verbose=True, tracer=None):
    """
    Процедура локального спуска.
    :param y: размещение, от которого стартует спуск
    :param d: матрица предпочтений
    :param c: матрица затрат
    :param V: порог
    :param leader_fn: функция leader
    :param max_iter: ограничение итераций
    :param verbose: печатать предупреждения
    :param tracer: необязательный vnd.trace.Tracer
    :return: локальный оптимум
    """
    k = 0
    result = [0 for _ in range(len(y))]
    while True:
        k += 1
        _, delta_rho = leader_fn(follower(y, d), c, V)
        vector = n(y, d, c, V, leader_fn, tracer=tracer)
        _, f = leader_fn(follower(vector, d), c, V)
        if f <= delta_rho:
            result = vector
            break
        else:
            y = vector
        if k > max_iter:
            if verbose:
                print("Сработал ограничитель")
            break
    return result


def improve(y, d, c, V, leader_fn=leader, verbose=True, tracer=None):
    """
    Процедура последовательного просмотра окрестности 2-swap после локального спуска.
    :param y: размещение
    :param d: матрица предпочтений
    :param c: матрица затрат
    :param V: порог
    :param leader_fn: функция leader
    :param verbose: печатать статус
    :param tracer: необязательный vnd.trace.Tracer
    :return: улучшенное решение или y
    """
    neighbors = swap_2(y)
    _, rho = leader_fn(follower(y, d), c, V)

    for v in neighbors:
        _, rho_new = leader_fn(follower(v, d), c, V)
        if tracer is not None:
            tracer.evaluate(y, v, rho_new, "swap2")
        if rho_new > rho:
            if tracer is not None:
                tracer.accept(y, v, rho_new, "swap2")
            if verbose:
                print("Improvement happened")
            return v
    if verbose:
        print("No improvement")
    return y
