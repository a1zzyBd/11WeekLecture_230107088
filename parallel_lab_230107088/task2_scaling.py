import math
import multiprocessing as mp
import time
from harness import emit_verify_tag

STUDENT_ID = 230107088
STRONG_N = 1_200_000
WEAK_N0 = 200_000

def stage_a(n):
    total = 0.0
    for i in range(max(1, n // 20)):
        x = (i + 1) * 0.00001
        for _ in range(10):
            x = math.sin(x) + math.sqrt(abs(x) + 1)
        total += x
    return total

def stage_b(args):
    start, end = args
    total = 0.0
    for i in range(start, end):
        x = (i % 1000 + 1) * 0.001
        for _ in range(30):
            x = math.sin(x) * 0.5 + math.sqrt(abs(x) + 1) * 0.5
        total += x
    return total

def trial(pool, n, p):
    t0 = time.perf_counter()
    stage_a(n)
    ta = time.perf_counter() - t0
    chunks = [(i*n//p, (i+1)*n//p) for i in range(p)]
    sum(pool.map(stage_b, chunks))
    return time.perf_counter()-t0, ta

def main():
    logical = mp.cpu_count()
    physical = int(input(f'Physical cores (logical={logical}): '))
    strong = {}
    weak = {}
    print('PHASE 2 - STRONG AND WEAK SCALING')
    for p in range(1, logical + 1):
        with mp.Pool(p) as pool:
            trial(pool, 1000, p)  # warmup
            strong[p] = trial(pool, STRONG_N, p)
            weak[p] = trial(pool, p*WEAK_N0, p)
        ts, ta = strong[p]
        tw, taw = weak[p]
        ss = strong[1][0] / ts
        ew = weak[1][0] / tw
        gust = p - (taw/tw)*(p-1)
        print(f'p={p:2} strong={ts:.3f}s S={ss:.3f} E={ss/p:.3f} weak={tw:.3f}s Eweak={ew:.3f} Gustafson={gust:.3f}')
    s = strong[1][1] / strong[1][0]
    print(f'Amdahl upper bound: {1/s:.3f}')
    if physical < logical:
        before = strong[1][0]/strong[physical][0]
        after = strong[1][0]/strong[physical+1][0]
        print(f'Marginal speedup p={physical} to {physical+1}: {after-before:.4f}')
    p = logical
    print(emit_verify_tag('PHASE2', STUDENT_ID, strong[1][0]/strong[p][0], p-(weak[p][1]/weak[p][0])*(p-1)))

if __name__ == '__main__':
    mp.freeze_support()
    main()
