import math
import random


class MCVRPSDInstance:
    def __init__(self, n_customs=50, product_mean=10, random_seed=None):
        self.n_customs = n_customs
        self.n_products = 3

        # 距离相关设定
        self.distributed_space = (100, 100)
        self.customs_position = None
        self.depot_position = None
        self.customs_distance = None
        self.customs_depot_distance = None

        # 容量相关的设定
        self.product_mean = product_mean
        self.cv = 0.1 if product_mean == 10 else 0.3
        self.customs_products_demand = None
        self.products_capacity = None
        self.tightness_ratio = 10

        # 长度相关的设定
        self.L_beta = None
        self.random_seed = random_seed
        self.further_init()

    @staticmethod
    def euclidean_distance(position_1, position_2):
        return math.sqrt(sum([(position_1[i] - position_2[i]) ** 2 for i in range(len(position_1))]))

    def further_init(self):
        random.seed(self.random_seed)
        self.customs_position = [(random.uniform(0, self.distributed_space[0]),
                                  random.uniform(0, self.distributed_space[0])) for _ in range(self.n_customs)]
        self.customs_distance = [
            [self.euclidean_distance(self.customs_position[i], self.customs_position[j]) for i in range(self.n_customs)]
            for j in range(self.n_customs)
        ]
        self.depot_position = (random.uniform(0, self.distributed_space[0]),
                               random.uniform(0, self.distributed_space[0]))
        self.customs_depot_distance = [self.euclidean_distance(self.customs_position[i], self.depot_position) for i
                                       in range(self.n_customs)]

        self.customs_products_demand = [
            [random.normalvariate(self.product_mean, self.cv * self.product_mean) for _ in
             range(self.n_products)] for _ in range(self.n_customs)]
        self.L_beta = random.uniform(3, 4)


if __name__ == '__main__':
    pass
