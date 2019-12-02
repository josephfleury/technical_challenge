def solver(problem):
    colors = problem.get("colors")
    customers = problem.get("customers")
    demands = problem.get("demands")

    mattes = []
    glossy = {}
    for c in range(customers):
        length = demands[c][0]
        demand = demands[c][1:]
        mattes.append([])
        for i in range(length):
            (color, matte) = (demand[2 * i], demand[2 * i + 1])
            if matte == 1:
                glossy[c] = color - 1
            else:
                mattes[c].append(color - 1)
    solved, solution = start(colors, customers, mattes, glossy)
    if solved:
        return " ".join(map(str, solution))
    else:
        return "IMPOSSIBLE"


def check(solution, customers, mattes, glossy):
    for customer in range(customers):
        good = False
        for i in range(len(solution)):
            if solution[i] == 0 and i in mattes[customer]:
                good = True
            if solution[i] == 1 and glossy.get(customer) == i:
                good = True
        if not good:
            return False
    return True


def start(colors, customers, mattes, glossy):
    solution = [0] * colors
    if check(solution, customers, mattes, glossy):
        return True, solution
    result = None
    solved = False
    for i in range(len(solution)):
        if solution[i] == 0:
            solved_i, result_i = reduce(solution, i, customers, mattes, glossy)
            if solved_i:
                if not solved:
                    solved = True
                    result = result_i
                if sum(result_i) < sum(result):
                    result = result_i
    return solved, result


def reduce(solution_on_stack, change, customers, mattes, glossy):
    solution = list(solution_on_stack)
    solution[change] = 1
    if check(solution, customers, mattes, glossy):
        return True, solution
    if sum(solution) == len(solution):
        return False, None
    result = None
    solved = False
    for i in range(len(solution)):
        if solution[i] == 0:
            solved_i, result_i = reduce(solution, i, customers, mattes, glossy)
            if solved_i:
                if not solved:
                    solved = True
                    result = result_i
                if sum(result_i) < sum(result):
                    result = result_i
    return solved, result
