import random
import time
import numpy as np

def construct(probs, eps):
    idx_upper = [-1 for i in xrange(len(probs))]
    large = []
    small = []
    aver = 1.0 / len(probs)
    thres = [aver for i in xrange(len(probs))]
    for i, p in enumerate(probs):
        if p > aver:
            large.append((p, i))
        else:
            small.append((p, i))

    head_large = 0
    head_small = 0
    while head_small < len(small):
        p, i = small[head_small]
        q, j = large[head_large]
        idx_upper[i] = j
        thres[i] = p
        head_small += 1
        if q - (aver - p) > aver + eps:
            large[head_large] = (q - (aver - p), j)
        elif q - (aver - p) < aver - eps:
            small.append((q - (aver - p), j))
            head_large += 1
        else:
            head_large += 1

    return thres, idx_upper


class AliasSampler(object):
    def __init__(self, probs, eps=1e-12):
        self.probs = probs
        self.thres, self.idx_upper = construct(self.probs, eps)
        self.aver = 1.0 / len(probs)

    def draw(self):
        x = random.randint(0, len(self.probs) - 1)
        y = random.random() * self.aver
        return x if y < self.thres[x] else self.idx_upper[x]

    def draw_batch(self, batch_size):
        x_batch = np.random.randint(len(self.probs), size=batch_size)
        y_batch = np.random.rand(batch_size) * self.aver
        return [x if y < self.thres[x] else self.idx_upper[x] for x, y in zip(x_batch, y_batch)]


if __name__ == '__main__':
    AS = AliasSampler([0.3, 0.2, 0.2, 0.01, 0.14, 0.14, 0.01])
    cnt = [0 for _ in range(7)]
    tot = 1000000
    for i in range(tot):
        cnt[AS.draw()] += 1
    print [1.0 * x / tot for x in cnt]
    
    start_time = time.time()
    gen_batch_1 = [AS.draw() for _ in range(tot * 10)]
    print time.time() - start_time
    start_time = time.time()
    gen_batch_2 = AS.draw_batch(tot * 10)
    print time.time() - start_time
    cnt = [0 for _ in range(7)]
    for item in gen_batch_2:
        cnt[item] += 1
    print cnt
