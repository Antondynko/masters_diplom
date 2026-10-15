def Folower(y, d):
    """
    Решает задачу нижнего уровня.
    :param y: размещение (решение верхнего уровня)
    :param d: матрица предпочтений клиентов
    :return: матрица назначений клиентов
    """
    n = len(d)
    m = len(d[0])
    x = [[0 for _ in range(m)] for _ in range(n)]

    for i in range(m):
        indx = 0
        best = 2147483647
        for j in range(n):
            if d[j][i] < best and y[j] == 1:
                indx = j
                best = d[j][i]
        x[indx][i] = 1
    return x
