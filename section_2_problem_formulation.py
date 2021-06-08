import math
import random
from functools import reduce
import numpy as np
import scipy.stats as stats


class MCVRPSDInstance:
    def __init__(self, n_customers=50, cv=0.1, product_mean_distribution='uniform', random_seed=None):
        self.n_customers = n_customers
        self.n_products = 3

        # 距离相关设定
        self.distributed_space = (100, 100)
        self.depot_customers_position = []
        self.depot_position = None
        self.distances = None
        self.customers_depot_distance = None
        self.L = None

        # 容量相关的设定
        self.product_mean_distribution = product_mean_distribution
        self.cv = cv
        self.customers_products_demand_mean = None
        self.products_capacity = None
        self.tightness_ratio = 10

        # 长度相关的设定
        self.random_seed = random_seed
        self.further_init()

    @staticmethod
    def euclidean_distance(position_1, position_2):
        return round(math.sqrt(sum([(position_1[i] - position_2[i]) ** 2 for i in range(len(position_1))])), 2)

    def further_init(self):
        random.seed(self.random_seed)
        self.depot_customers_position = [(random.uniform(0, self.distributed_space[0]),
                                          random.uniform(0, self.distributed_space[0])) for _ in
                                         range(self.n_customers + 1)]
        self.distances = [
            [self.euclidean_distance(self.depot_customers_position[i], self.depot_customers_position[j])
             for i in range(self.n_customers)]
            for j in range(self.n_customers)
        ]
        customers_distance = [x[1:] for x in self.distances[1:]]
        self.L = round(random.uniform(3, 4) * max([max(x) for x in customers_distance]), 2)

        self.customers_products_demand_mean = []
        for _ in range(self.n_customers):
            products_demand = []
            for _ in range(self.n_products):
                mean = random.uniform(10, 30) if self.product_mean_distribution == 'uniform' else random.choice(
                    [10, 30])
                products_demand.append(mean)
            self.customers_products_demand_mean.append(products_demand)
        self.products_capacity = [sum([self.customers_products_demand_mean[i][j] for i in range(self.n_customers)]) / 10
                                  for j in range(self.n_products)]
        random.seed(None)

    def calculate_planned_length(self, r):
        """
        计算计划长度。

        :param r: 路径
        :return: 计划路径长度
        """
        return sum([self.distances[r[i]][r[i + 1]] for i in range(len(r) - 1)])

    def calculate_failure_probability(self, r):
        """
        第2个客户失败的概率等于从第0个客户到当前才失败的概率+从第1个客户到当前就失败的概率。
        第3个客户失败的概率等于从第0个客户到当前才失败的概率+从第1个客户到当前才失败的概率+从第2个客户到当前就失败的概率。
        所以理论上，这并不是一个递增的过程！

        :param r: 路径
        :return: 每个点失败的概率
        """
        Pr = [0 for _ in range(len(r) - 1)]  # 记录第j个点失败的概率
        Pr[0] = 1  # 边界条件，对于depot处就更新概率为1（失败的具体影响就是更新改点）
        for i in range(1, len(Pr)):  # i -> 第i个顾客， 具体对应的编号为r[i]
            pr_j = []  # 记录从第j个点更新后到当前失败的概率
            for j in range(i):  # 从depot开始，到达i-1客户，求不同点更新对应的情况
                if j == i - 1:  # 上面提到了，对于第i个客户前面一个客户更新，是不一样的，这里去区别主要还是无法公式的第一项（不存在随机性了）
                    pr_j_1 = 1  # 第一部分概率，即到了i-1也不发生失败的概率，由于上一次才更新，因此这部分不存在随机性
                    # 到了第i个客户，累积的容量仍能满足要求的概率
                    customer_v_i_products_success_rate = [
                        stats.norm.cdf((self.products_capacity[p] - self.customers_products_demand_mean[r[i]][p]) / (
                                self.cv * self.customers_products_demand_mean[r[i]][p])
                                       ) for p in range(self.n_products)]
                    customer_v_i_success_rate = reduce(lambda x, y: x * y, customer_v_i_products_success_rate)
                    pr_j.append(pr_j_1 - customer_v_i_success_rate)
                else:
                    pr_j_m = []  # [第一部分概率，即到了i-1也不发生失败的概率，第二部分概率，到了第i次，仍然不会发生失败的概率]（第j次更新的前提下）
                    for m in [i, i + 1]:
                        # 先求每种产品累积的期望需求
                        m_accumulate_demand = [sum(
                            [self.customers_products_demand_mean[r[k]][p] for k in range(j + 1, m)]) for p in
                            range(self.n_products)]
                        # 再求每种产品累积的随机性（标准差）
                        m_accumulate_std = [math.sqrt(sum([(self.customers_products_demand_mean[r[k]][p] * self.cv) ** 2
                                                           for k in range(j + 1, m)]))
                                            for p in range(self.n_products)]
                        # 再求累积下来的成功率
                        m_accumulate_success_rate = [
                            stats.norm.cdf((self.products_capacity[p] - m_accumulate_demand[p]) / (
                                m_accumulate_std[p])
                                           ) for p in range(self.n_products)]
                        # 三种产品累积的成功率
                        pr_j_m.append(reduce(lambda x, y: x * y, m_accumulate_success_rate))
                        # 到了i仍然不发生失败的概率-到了i-1不发生失败的概率 = 到了i发生失败的概率（第j次更新的前提下）
                    pr_j.append(pr_j_m[0] - pr_j_m[1])
            Pr[i] = sum([pr_j[j] * Pr[j] for j in range(i)])
        return Pr[1:]


if __name__ == '__main__':
    instance = MCVRPSDInstance(n_customers=25, random_seed=None)
    print(instance.calculate_failure_probability([0, 2, 4, 0]))

    # 检验结果
    # 对于第一个客户(2号）而言，三种产品满足要求的概率分别是
    c1_p0 = stats.norm.cdf((instance.products_capacity[0] - instance.customers_products_demand_mean[2][0]) /
                           (instance.customers_products_demand_mean[2][0] * instance.cv))
    c1_p1 = stats.norm.cdf((instance.products_capacity[1] - instance.customers_products_demand_mean[2][1]) /
                           (instance.customers_products_demand_mean[2][1] * instance.cv))
    c1_p2 = stats.norm.cdf((instance.products_capacity[2] - instance.customers_products_demand_mean[2][2]) /
                           (instance.customers_products_demand_mean[2][2] * instance.cv))
    # 第一个顾客不满足要求的概率是
    pr_1 = 1 - c1_p0 * c1_p2 * c1_p1
