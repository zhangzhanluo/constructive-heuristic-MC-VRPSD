from section_2_3_problem import MCVRPSDInstance


def s_split(instance: MCVRPSDInstance, r: list):
    """
    使用s_split对路线进行切分。

    :param instance: 案例
    :param r: 路径
    :return:
    """
    print(r)
    Q = 1e10
    Z = [Q for _ in range(len(r))]
    Z[0] = 0
    B = [0 for _ in range(len(r))]
    for i in range(len(r) - 1):
        for j in range(i + 1, len(r)):
            # i所指向的位置是上一次结束的位置，路径中不应包括进去，应补0；j+1则代表末尾点是包含在路径里面的
            if j == len(r):
                current_r = [0] + r[i + 1: j + 1]  # 当j指向最后一位时，由于最后一位一定是0因此路径不再补充0
            else:
                current_r = [0] + r[i + 1: j + 1] + [0]
            current_total_expected_cost = instance.calculate_total_expected_length(current_r)
            if current_total_expected_cost <= instance.L:
                if Z[j] > Z[i] + current_total_expected_cost:
                    Z[j] = Z[i] + current_total_expected_cost
                    B[j] = i
            else:
                break
    i = len(r) - 1
    R = [[0] + r[B[i] + 1:]]
    i = B[i]
    while i != 0:
        R.append([0] + r[B[i] + 1:i + 1] + [0])
        i = B[i]
    print(R)
    return R


def NN(instance: MCVRPSDInstance, save_pic=True):
    r = [0]
    rest_customers = list(range(1, instance.n_customers + 1))
    while rest_customers:
        large_number = 1e10
        n = -1
        last_customer = r[-1]
        for customer in rest_customers:
            if customer not in r and customer != last_customer:
                if instance.distances[customer][last_customer] < large_number:
                    n = customer
                    large_number = instance.distances[customer][last_customer]
        r.append(n)
        rest_customers.remove(n)
        if save_pic:
            instance.draw_routes([r], description='NN Algorithm {}\nPlanned Cost: {}'.format(
                len(r), instance.calculate_planned_length(r)),
                                 show_pic=False, save_pic_suffix='NN Algorithm {}'.format(len(r)))
    r.append(0)
    if save_pic:
        instance.draw_routes([r], description='NN Algorithm {}\nPlanned Cost: {}'.format(
            len(r), instance.calculate_planned_length(r)),
                             show_pic=False, save_pic_suffix='NN Algorithm {}'.format(len(r)))
    return r


def NI(instance: MCVRPSDInstance, save_pic=True):
    farthest_customer = instance.distances[0].index(max(instance.distances[0]))
    r = [0, farthest_customer, 0]
    if save_pic:
        instance.draw_routes([r], description='NI Algorithm {}\nPlanned Cost: {}'.format(
            len(r), instance.calculate_planned_length(r)),
                             show_pic=False, save_pic_suffix='NI Algorithm {}'.format(len(r)))
    rest_customers = list(range(1, instance.n_customers + 1))
    rest_customers.remove(farthest_customer)
    while rest_customers:
        new_lengths = []
        new_lengths_insertion = []
        for customer in rest_customers:
            all_possible_insertion = []
            for i in range(1, len(r)):
                new_r = r.copy()
                new_r.insert(i, customer)
                all_possible_insertion.append(instance.calculate_planned_length(new_r))
            new_lengths.append(min(all_possible_insertion))
            new_lengths_insertion.append(all_possible_insertion.index(min(all_possible_insertion)) + 1)
        best_customer = rest_customers[new_lengths.index(min(new_lengths))]
        best_insertion_position = new_lengths_insertion[new_lengths.index(min(new_lengths))]
        r.insert(best_insertion_position, best_customer)
        rest_customers.remove(best_customer)
        if save_pic:
            instance.draw_routes([r], description='NI Algorithm {}\nPlanned Cost: {}'.format(
                len(r), instance.calculate_planned_length(r)),
                                 show_pic=False, save_pic_suffix='NI Algorithm {}'.format(len(r)))
    return r


if __name__ == '__main__':
    mcvrpsd = MCVRPSDInstance(n_customers=20, random_seed=0)
    r_nn = NN(mcvrpsd)
    R_nn_split = s_split(mcvrpsd, r_nn)
    mcvrpsd.draw_routes(R_nn_split,
                        description='NN Algorithm S-Split\nPlanned Cost: {}\nTotal Expected Cost: {}'.format(
                            mcvrpsd.calculate_routes_planned_length(R_nn_split),
                            mcvrpsd.calculate_routes_total_expected_length(R_nn_split)),
                        show_pic=False, save_pic_suffix='NN Algorithm S-Split')

    r_ni = NI(mcvrpsd)
    R_ni_split = s_split(mcvrpsd, r_ni)
    mcvrpsd.draw_routes(R_ni_split,
                        description='NI Algorithm S-Split\nPlanned Cost: {}\nTotal Expected Cost: {}'.format(
                            mcvrpsd.calculate_routes_planned_length(R_ni_split),
                            mcvrpsd.calculate_routes_total_expected_length(R_ni_split)),
                        show_pic=False, save_pic_suffix='NI Algorithm S-Split')
