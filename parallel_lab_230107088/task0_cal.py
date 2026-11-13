import multiprocessing as mp
import time
from harness import emit_verify_tag

STUDENT_ID = 230107088
CALLS = 1_000_000

def main():
    print('PHASE 0 - HARDWARE AND TIMER')
    print('Logical cores:', mp.cpu_count())
    start = time.perf_counter_ns()
    for _ in range(CALLS):
        time.perf_counter_ns()
    elapsed_ns = time.perf_counter_ns() - start
    avg_ns = elapsed_ns / CALLS
    print(f'Average timer call latency: {avg_ns:.4f} ns')
    print(emit_verify_tag('PHASE0', STUDENT_ID, avg_ns, elapsed_ns / 1e6))

if __name__ == '__main__':
    main()
