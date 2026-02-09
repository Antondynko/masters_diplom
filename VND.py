import import_from_file
import random
import time

# _____________________________ DATA BASE _____________________________
# _____________________________ Warning! _____________________________

V = 47000
#V = 2000
p = 15
#p = 3
n = import_from_file.n
#n = 5
m = import_from_file.m
#m = 3
c = import_from_file.c
#c = [[200, 380, 480], [700, 910, 550], [630, 560, 290], [450, 740, 670], [930, 400, 920]]
d = import_from_file.d
#d = [[14, 12, 10], [19, 9, 17], [8, 13, 15], [16, 11, 18], [20, 25, 21]]


# _____________________________ Function list _____________________________
def Swap(y):
    """
    :param y: вектор размещения
    :return: окретсность 1-swap
    """
    indx_1 = []
    indx_0 = []
    swap = []

    for i in range(len(y)):
        if y[i] == 1:
            indx_1.append(i)
        else:
            indx_0.append(i)

    for i in indx_1:
        for j in indx_0:
            vector = []
            for k in range(len(y)):
                vector.append(y[k])
            vector[i] = 0
            vector[j] = 1
            swap.append(vector)

    return swap


def Generate_y_start(n, p):
    """
    :param n: мощность множетсва I
    :param p: количество открываемых предприятий (медиана)
    :return: какое-то размещение, которое может быть решением задачи
    """
    y_start = [0 for i in range(n)]
    indexes = [i for i in range(n)]

    indexes_one = random.sample(indexes, p)

    for i in indexes_one:
        y_start[i] = 1

    return y_start


def Folower(y, d):
    """
    Решает задачу нижнего уровня
    :param y: размещение (решение верхнего уровня)
    :param d: матрица предпочтений клиентов
    :return: матрица назначений клиентов
    """
    n = len(d)
    m = len(d[0])
    x = [[0 for i in range(m)] for j in range(n)]

    for i in range(m):
        indx = 0
        min = 2147483647
        for j in range(n):
            if d[j][i] < min and y[j] == 1:
                indx = j
                min = d[j][i]

        x[indx][i] = 1
    return x


def Leader(x, c, V):
    """
    Функция считающая радиус пороговой устойчивости по решению нижнего уровня
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
            else:
                f += c[i][j]

    for i in range(n):
        for j in range(m):
            if x[i][j] == 0:
                continue
            C += x[i][j]

    delta_rho = (V - f) / C

    rho = x
    for i in range(n):
        for j in range(m):
            if rho[i][j] == 0:
                continue
            rho[i][j] *= delta_rho

    return rho, V - f


def N(y):
    """
    Процедура локального спуска
    :param y: стартовое размещение
    :return: локальный оптимум
    """
    swap = Swap(y)
    rho, delta_rho = Leader(Folower(y, d), c, V)

    for v in swap:
        _, g = Leader(Folower(v, d), c, V)
        if g > delta_rho:
            return v

    return y


def Local_Search(y):
    """
    Процедура локального спуска
    :param y: размещение, от которого стартует спуск
    :return: локальный оптимум
    """
    k = 0
    result = [0 for i in range(len(y))]
    while True:
        k += 1
        _, delta_rho = Leader(Folower(y, d), c, V)
        vector = N(y)
        o, f = Leader(Folower(vector, d), c, V)
        if f <= delta_rho:
            result = vector
            break
        else:
            y = vector
        if k > 100:
            print("Сработал ограничитель")
            break
    return result


def Pairs(array):
    """
    Вспомогательная функция, которая нужна для реализации окрестности 2-swap(y)
    :param array: массив
    :return: массив различных пар из элементов данного массива
    """
    pairs = []
    n = len(array)

    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((array[i], array[j]))

    return pairs


def Swap_2(y):
    """
    Окрестность более высокого ранга
    :param y: размещение
    :return: множество (массив) размещений из окрестности 2-swap(y)
    """
    indx_1 = []
    indx_0 = []
    swap_2 = []

    for i in range(len(y)):
        if y[i] == 1:
            indx_1.append(i)
        else:
            indx_0.append(i)

    p_1 = Pairs(indx_1)
    p_0 = Pairs(indx_0)

    for i in p_1:
        for j in p_0:
            vector = []
            for k in range(len(y)):
                vector.append(y[k])
            vector[j[0]] = 1
            vector[j[1]] = 1
            vector[i[0]] = 0
            vector[i[1]] = 0
            swap_2.append(vector)

    return swap_2


def Improve(y):
    """
    Процедура последовтельного просмотра окрестностей высокого ранга после локального спуска
    :param y: размещнение
    :return: возможно оптимальное решение
    """

    swap_2 = Swap_2(y)
    _, rho = Leader(Folower(y, d), c, V)

    for v in swap_2:
        o, rho_new = Leader(Folower(v, d), c, V)
        if rho_new > rho:
            print("Improvement happened")
            return v
    print("No improvement")
    return y


# _____________________________ Time _____________________________
start = time.time()

# _____________________________ Step 0 _____________________________
y = Generate_y_start(n, p)

print(y)
rho_ij, rho = Leader(Folower(y, d), c, V)
print(rho_ij)

solve = y

while True:
    # p = N(y)
    # print(p)
    # print(Leader(Folower(p, d), c, V))

    # _____________________________ Step 1 _____________________________

    r = Local_Search(solve)
    print(r)
    r_rho_ij, r_rho = Leader(Folower(r, d), c, V)
    print(r_rho)

    # _____________________________ Step 2 _____________________________

    s = Improve(r)
    print(s)
    s_rho_ij, s_rho = Leader(Folower(s, d), c, V)
    print(s_rho)


    for v in range(len(s_rho_ij)):
        print(s_rho_ij[v])

    if s_rho > r_rho:
        solve = s
        continue
    else:
        break

end = time.time()
time = end - start
print("Elapsed time:", time)

# _____________________________ Info _____________________________
# Treaning data:
# n = 5
# m = 3
# p = 2
# c =[[200, 380, 480], [700, 910, 550], [630, 560, 290], [450, 740, 670], [930, 400, 920]]
# d = [[14, 12, 10], [19, 9, 17], [8, 13, 15], [16, 11, 18], [20, 25, 21]]
# x = [
