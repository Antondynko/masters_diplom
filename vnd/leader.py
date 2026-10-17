CONST = 90000000


def leader(x, c, V):
    """
    Функция считающая радиус пороговой устойчивости по решению нижнего уровня (full).
    :param x: матрица назначений клиентов
    :param c: матрица производственно-транспортных затрат
    :param V: порог
    :return: матрица радиусов пороговой устойчивости и значение целевой функции
    """
    n = len(c)
    m = len(c[0])
    f = 0
    C = 0

    for i in range(n):
        for j in range(m):
            if x[i][j] == 0:
                continue
            f += c[i][j]
            C += x[i][j]

    delta_rho = (V - f) / C

    rho = [row[:] for row in x]
    for i in range(n):
        for j in range(m):
            if rho[i][j] == 0:
                continue
            rho[i][j] *= delta_rho

    return rho, V - f


def leader_simplified(x, c, V):
    """
    Упрощённая модель Leader: весь остаток V-f ставится в позицию глобального min c
    среди назначенных клиентов.
    :param x: матрица назначений клиентов
    :param c: матрица производственно-транспортных затрат
    :param V: порог
    :return: матрица радиусов пороговой устойчивости и значение целевой функции
    """
    n = len(c)
    m = len(c[0])
    f = 0

    for i in range(n):
        for j in range(m):
            if x[i][j] == 0:
                continue
            f += c[i][j]

    rho = [[0 for _ in range(m)] for _ in range(n)]

    c_d = [[0 for _ in range(m)] for _ in range(n)]
    for i in range(n):
        for j in range(m):
            if x[i][j] == 0:
                continue
            c_d[i][j] = c[i][j]

    c_d_min_val = CONST
    for i in range(n):
        for j in range(m):
            if c_d[i][j] != 0 and c_d[i][j] < c_d_min_val:
                c_d_min_val = c_d[i][j]

    min_idx = None
    for r_idx, row in enumerate(c_d):
        if c_d_min_val in row:
            c_idx = row.index(c_d_min_val)
            min_idx = (r_idx, c_idx)
            break

    if min_idx is not None:
        rho[min_idx[0]][min_idx[1]] = V - f

    return rho, V - f
