import os
import math
import random
from functools import reduce
import scipy.stats as stats
import networkx as nx
from matplotlib import pyplot as plt


class MCVRPSDInstance:
    def __init__(self, n_customers=50, cv=0.1, product_mean_distribution='uniform', random_seed=None):
        """
        构建MCVRPSD实例。

        :param n_customers: 顾客数量
        :param cv: 方差因子，取0.1或0.3
        :param product_mean_distribution: 顾客单个产品的需求均值，10-30均匀分布（uniform）还是0-1分布（01）
        :param random_seed: 随机种子，控制案例生成中均值和地理位置的随机性
        """
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

        self.random_seed = random_seed
        self.name = 'Customers {} - CV {} - Random_Seed {}'.format(self.n_customers, self.cv, self.random_seed)
        self.further_init()

    @staticmethod
    def euclidean_distance(position_1, position_2):
        return round(math.sqrt(sum([(position_1[i] - position_2[i]) ** 2 for i in range(len(position_1))])), 2)

    def further_init(self):
        """
        进一步的初始化。

        :return: 无
        """
        random.seed(self.random_seed)
        self.depot_customers_position = [(random.uniform(0, self.distributed_space[0]),
                                          random.uniform(0, self.distributed_space[0])) for _ in
                                         range(self.n_customers + 1)]
        self.distances = [
            [self.euclidean_distance(self.depot_customers_position[i], self.depot_customers_position[j])
             for i in range(self.n_customers + 1)]
            for j in range(self.n_customers + 1)
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

    def calculate_routes_planned_length(self, R):
        """
        计算routes 总计划长度

        :param R: 路线的集合
        :return: 路线总计划长度
        """
        return round(sum([self.calculate_planned_length(r) for r in R]), 2)

    def calculate_customers_failure_probability(self, r):
        """
        第2个客户失败的概率等于从第0个客户到当前才失败的概率+从第1个客户到当前就失败的概率。
        第3个客户失败的概率等于从第0个客户到当前才失败的概率+从第1个客户到当前才失败的概率+从第2个客户到当前就失败的概率。
        所以理论上，这并不是一个递增的过程！

        :param r: 路径
        :return: 每个顾客失败的概率
        """
        Pr = [0 for _ in range(len(r) - 1)]  # 记录第j个点失败的概率
        Pr[0] = 1  # 边界条件，对于depot处就更新概率为1（失败的具体影响就是更新该点）
        for i in range(1, len(Pr)):  # i -> 第i个顾客， 具体对应的编号为r[i]，在0-index的情况下，要用r[i]-1
            pr_j = []  # 记录从第j个点更新后到当前失败的概率
            for j in range(i):  # 从depot开始，到达i-1客户，求不同点更新对应的情况
                if j == i - 1:  # 上面提到了，对于第i个客户前面一个客户更新，是不一样的，这里区别主要还是无法计算公式的第一项（不存在随机性了）
                    pr_j_1 = 1  # 第一部分概率，即到了i-1也不发生失败的概率，由于上一次才更新，因此这部分不存在随机性
                    # 到了第i个客户，累积的容量仍能满足要求的概率
                    customer_v_i_products_success_rate = [
                        stats.norm.cdf(
                            (self.products_capacity[p] - self.customers_products_demand_mean[r[i] - 1][p]) / (
                                    self.cv * self.customers_products_demand_mean[r[i] - 1][p])
                        ) for p in range(self.n_products)]
                    customer_v_i_success_rate = reduce(lambda x, y: x * y, customer_v_i_products_success_rate)
                    pr_j.append(pr_j_1 - customer_v_i_success_rate)
                else:
                    pr_j_m = []  # [第一部分概率，即到了i-1也不发生失败的概率；第二部分概率，到了第i次，仍然不会发生失败的概率]（第j次更新的前提下）
                    for m in [i, i + 1]:
                        # 先求每种产品累积的期望需求
                        m_accumulate_demand = [sum(
                            [self.customers_products_demand_mean[r[k] - 1][p] for k in range(j + 1, m)]) for p in
                            range(self.n_products)]
                        # 再求每种产品累积的随机性（标准差）
                        m_accumulate_std = [
                            math.sqrt(sum([(self.customers_products_demand_mean[r[k] - 1][p] * self.cv) ** 2
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
            Pr[i] = sum([pr_j[j] * Pr[j] for j in range(i)])  # 全概率公式
        return Pr[1:]

    def calculate_total_expected_length(self, r):
        """
        计算总期望路径（成本），等于计划成本加失败补救成本。

        :param r: 路径
        :return:总期望长度
        """
        Pr = self.calculate_customers_failure_probability(r)
        # 由于Pr[0]代表第0个客户的概率，但是r[0]代表depot，因此两者的index错一位
        return round(self.calculate_planned_length(r) + sum(
            [self.distances[r[i + 1]][0] * 2 * Pr[i] for i in range(0, len(r) - 2)]), 2)

    def calculate_routes_total_expected_length(self, R):
        """
        计算路线集合的总期望长度（成本）

        :param R: 路线集合
        :return: 路线集合的总期望长度（成本）
        """
        return round(sum([self.calculate_total_expected_length(r) for r in R]), 3)

    def check_distance_constrain(self, r):
        """
        检查路径的期望总长度是否小于L。

        :param r: 路径
        :return: 是否满足路径约束
        """
        return self.calculate_total_expected_length(r) <= self.L

    def draw_routes(self, R, description=None, show_pic=True, save_pic_suffix=None):
        """
        对结果进行可视化。

        :param R: 路线或路线的集合
        :param description: 一些描述性的文字，会被打印在左上角
        :param show_pic: show
        :param save_pic_suffix: 保存图片名城的后缀，None的话不会保存图片
        :return: 无
        """
        if R[0] is int:
            R = [R]
        g = nx.DiGraph()
        g.add_nodes_from(range(self.n_customers + 1))
        for node in g.nodes:
            if node == 0:
                g.nodes[node]['label'] = 'depot'
                g.nodes[node]['demand'] = self.products_capacity
            else:
                g.nodes[node]['label'] = str(node)
                g.nodes[node]['demand'] = self.customers_products_demand_mean[node - 1]
        for r in R:
            for i in range(len(r) - 1):
                g.add_edge(r[i], r[i + 1], weight=self.distances[r[i]][r[i + 1]])
        pos = {i: self.depot_customers_position[i] for i in g.nodes}
        plt.figure(figsize=[7, 7])
        nx.draw(g, pos, with_labels=True, font_color='w')
        plt.text(1, 0, 'https://github.com/zhangzhanluo/constructive-heuristic-MC-VRPSD', ha='right', va='bottom',
                 fontsize=6, transform=plt.gca().transAxes)
        plt.text(0.01, 0.99, self.name, ha='left', va='top', fontsize=8, transform=plt.gca().transAxes)
        if description is not None:
            plt.text(0.01, 0.95, description, ha='left', va='top', fontsize=8, transform=plt.gca().transAxes)
        if save_pic_suffix is not None:
            pic_path = '01_Results/Pics/'
            if not os.path.exists(pic_path):
                os.makedirs(pic_path)
            plt.savefig(
                pic_path + '{} - {}.png'.format(self.name, save_pic_suffix if save_pic_suffix is not None else ''),
                dpi=300)
        if show_pic:
            plt.show()
        else:
            plt.close()


if __name__ == '__main__':
    instance = MCVRPSDInstance(n_customers=20, random_seed=0)
    print(instance.calculate_customers_failure_probability([0, 2, 4, 0]))
    print(instance.calculate_total_expected_length([0, 2, 4, 0]))
    instance.draw_routes([[0, 1, 0], [0, 3, 4, 5, 6, 0]], save_pic_suffix='test', description='test')

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
