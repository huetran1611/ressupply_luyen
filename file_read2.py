import Function2 as Function
import Data2 as Data
solution = [[], []]

def tranfer(arr, k):
    solution[0].append([])
    solution[0][k].append([0, []])
    for i in range(len(arr)):
        solution[0][k][0][1].append(arr[i])
    for i in range(1, len(arr) - 1):
        solution[0][k].append([arr[i], []])
    return solution

def add(solution, package, location):
    for i in range(len(solution[0])):
        if package in solution[0][i][0][1]:
            solution[0][i][0][1].remove(package)
    for j in range(len(solution[0])):
        for i in range(1, len(solution[0][j])):
            if solution[0][j][i][0] == location:
                solution[0][j][i][1].append(package)
    add = False
    for i in range(len(solution[1])):
        for j in range(len(solution[1][i])):
            if solution[1][i][j][0] == location:
                solution[1][i][j][1].append(package)
                add = True
    if not add:
        solution[1].append([[location, [package]]])
    return solution

# a = tranfer([
#             0,
#             1,2,3,4,
#             0
#         ], 0)
# a = tranfer([
#             0,
#             5,6,7,8,
#             0
#         ], 1)
# # print(a)
# a = add(a, 2,2)
# a = add (a,3,2)
# a = add (a,4,4)
# a = add (a,7,7)
# a = add (a,8,7)

solution = [
            [
                [[0, [1]], 
                 [1, []], 
                 [2, [2,3]],
                 [0,[]], 
                 [3, []], 
                 [4, [4]]
                 ], 
                 [[0, [5,6]], 
                  [5, [0]],
                  [6, []], 
                   [7, [7,8]],
                   [8, []]
                ]
                ], 
                [
                    [
                        [2, [2,3]]
                    ], 
                    [
                        [4, [4]],
                        [7,[7,8]]
                    ]
                ]
            ]


Data.read_data("test_data\example.txt")

#a = add(a, 6, 6)

print(solution)
print(Function.fitness(solution))



