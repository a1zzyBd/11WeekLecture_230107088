import ctypes
import multiprocessing as mp
from multiprocessing import shared_memory
from harness import run_benchmark, emit_verify_tag

STUDENT_ID = 230107088
M = 16_000_000
STRIDES = (1, 2, 4, 8, 16, 32)

def fs_worker(shm_name, slot_idx, iters):
    shm = shared_memory.SharedMemory(name=shm_name)
    arr = (ctypes.c_uint64 * 512).from_buffer(shm.buf)
    acc = arr[slot_idx]
    for i in range(iters):
        acc = (acc * 6364136223846793005 + (i | 1)) & 0xFFFFFFFFFFFFFFFF
        arr[slot_idx] = acc
    del arr
    shm.close()

def trial(p, stride):
    shm = shared_memory.SharedMemory(create=True, size=4096)
    try:
        processes = []
        for k in range(p):
            count = M // p + (k < M % p)
            proc = mp.Process(target=fs_worker, args=(shm.name, k * stride, count))
            processes.append(proc)
            proc.start()
        for proc in processes:
            proc.join()
            if proc.exitcode != 0:
                raise RuntimeError(f'Worker failed: {proc.exitcode}')
    finally:
        shm.close()
        shm.unlink()

def main():
    logical = mp.cpu_count()
    physical = min(int(input(f'Enter physical CPU cores (logical={logical}): ')), logical)
    if physical < 1 or physical * max(STRIDES) > 512:
        raise ValueError('Physical core count incompatible with 4096-byte buffer')
    print('PHASE 1 - FALSE SHARING')
    sweep = {}
    for stride in STRIDES:
        stats = run_benchmark(lambda: trial(physical, stride))
        sweep[stride] = stats.median_ms
        print(f'stride={stride:2} bytes={stride*8:3} median={stats.median_ms:.2f} ms IQR={stats.iqr_ms:.2f} throughput={M/stats.median_ms/1000:.3f} Mops/s')
    counts = sorted(set([1] + [2**k for k in range(1, logical.bit_length()) if 2**k <= logical] + [logical]))
    for stride in (1, 16):
        baseline = None
        print(f'\nScaling stride={stride}')
        for p in counts:
            if p * stride >= 512: continue
            stats = run_benchmark(lambda: trial(p, stride))
            if baseline is None: baseline = stats.median_ms
            speedup = baseline / stats.median_ms
            efficiency = speedup / p
            e = ((1/speedup)-(1/p))/(1-(1/p)) if p > 1 else 0
            print(f'p={p:2} T={stats.median_ms:.2f}ms S={speedup:.3f} E={efficiency:.3f} e={e:.4f}')
    print(emit_verify_tag('PHASE1', STUDENT_ID, sweep[1], sweep[16]))

if __name__ == '__main__':
    mp.freeze_support()
    main()
