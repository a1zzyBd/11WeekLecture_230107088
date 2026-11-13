import math
import multiprocessing as mp
import time
from harness import emit_verify_tag

STUDENT_ID = 230107088
N = 8000

def work(i):
    k = 1 + (i//40)**2
    x = 0.1
    for _ in range(k):
        x = math.sin(x) + math.cos(x)*0.1 + math.sqrt(abs(x)+1)*0.01
    return x

def worker(worker_id, p, strategy, chunk, counter, runtimes):
    start = time.perf_counter()
    if strategy == 'block':
        indices = range(worker_id*N//p, (worker_id+1)*N//p)
        for i in indices: work(i)
    elif strategy == 'cyclic':
        for i in range(worker_id, N, p): work(i)
    else:
        while True:
            with counter.get_lock():
                first = counter.value
                counter.value += chunk
            if first >= N: break
            for i in range(first, min(first+chunk, N)): work(i)
    runtimes[worker_id] = time.perf_counter()-start

def trial(p, strategy, chunk=1):
    counter = mp.Value('i', 0)
    runtimes = mp.Array('d', p)
    processes = [mp.Process(target=worker, args=(i,p,strategy,chunk,counter,runtimes)) for i in range(p)]
    t0 = time.perf_counter()
    for proc in processes: proc.start()
    for proc in processes:
        proc.join()
        if proc.exitcode: raise RuntimeError(f'Worker exit code {proc.exitcode}')
    wall = time.perf_counter()-t0
    active = list(runtimes)
    imbalance = max(active)/(sum(active)/p)
    return wall, imbalance

def main():
    physical = int(input(f'Physical CPU cores (logical={mp.cpu_count()}): '))
    print('PHASE 4 - SCHEDULING')
    results = {}
    for name, chunk in [('block',0),('cyclic',0),('dynamic',1),('dynamic',8),('dynamic',64),('dynamic',512)]:
        wall, imbalance = trial(physical,name,chunk)
        results[(name,chunk)] = wall
        print(f'{name:8} chunk={chunk:3} wall={wall:.3f}s lambda={imbalance:.3f}')
    best = min((c for c in (1,8,64,512)), key=lambda c: results[('dynamic',c)])
    print('Best dynamic chunk:',best)
    print(emit_verify_tag('PHASE4',STUDENT_ID,results[('block',0)],results[('dynamic',best)]))

if __name__ == '__main__':
    mp.freeze_support()
    main()
