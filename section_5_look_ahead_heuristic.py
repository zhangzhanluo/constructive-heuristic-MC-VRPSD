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
    i = len(r)-1
    R = [[0]+r[B[i]+1:]]
    i = B[i]
    while i != 0:
        R.append([0]+r[B[i]+1:i+1]+[0])
        i = B[i]
    print(R)
    return R


if __name__ == '__main__':
    pass
