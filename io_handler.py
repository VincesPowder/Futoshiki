from forward_chaining import ForwardChaining, format_solution

def solve_forward_chaining(kb_gen):
    solver = ForwardChaining(
        kb_gen.N, kb_gen.raw_grid, kb_gen.raw_horiz, kb_gen.raw_vert
    )
    data = solver.solve()
    if data['success']:
        print(format_solution(kb_gen.N, data['result'],
                              kb_gen.raw_horiz, kb_gen.raw_vert))
    return data