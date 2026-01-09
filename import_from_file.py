def from_str_to_float(string):
    for i in range(len(string)):
        string[i] = float(string[i])

    return string

# WARNING!
n = 20
m = 20
# WARNING!

c = [[0 for j in range(m)] for i in range(n)]
d = [[0 for j in range(m)] for i in range(n)]

string_array = []

with open('20_20_15.txt', 'r') as file:

    k = 0
    for line in file:
        if k < 3:
            k += 1
            continue

        string = line.split()
        string_array.append(from_str_to_float(string))


for i in range(len(string_array)):
    ind_i = int(string_array[i][0])
    ind_j = int(string_array[i][1])

    c[ind_i][ind_j] = string_array[i][2]
    d[ind_i][ind_j] = string_array[i][3]

#print(648.042789316054 + 521.9224224961249 + 595.3707846609672 + 305.4702479550933 + 650.8442135518653 + 434.5125888332025 + 454.62308824316784 + 480.76230927779363 + 718.995388315976 + 494.62272430863345 + 473.97754685519686 + 134.11108653600246 + 843.3868462376041 + 641.3265751713176 + 390.9976265917679 + 376.39671112137194 + 640.9479286539071 + 643.0537447515269 + 518.9644485754043 + 396.62397345465945)
