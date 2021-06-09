from section_4_SCW_heuristic import MCVRPSDInstance, SCW
from section_5_look_ahead_heuristic import s_split


def stochastic_2_opt(instance: MCVRPSDInstance, R: list):
    """
    At every iteration, routes r and r0 from the MC-VRPSD solution (R) are merged into a single
    tour, and all possible arc exchanges in the resulting route are explored. To avoid excessive computations,
    every exchange is first evaluated solely on the basis of the deterministic part of the overall cost,
    which can be done in constant time as in the classical 2-Opt procedure. If the exchange is promising, meaning
    that the planned cost of the MC-VRPSD solution improves, the move is then evaluated in terms
    of the whole overall cost using s-split. The tour partitioning process generates a temporary set of
    feasible routes T serving the customers originally visited by r and r0. If the expected cost of the new set T
    is lower than the sum of those of the two original routes r and r0, the move improves the current
    MC-VRPSD solution because the expected cost of the other routes (i.e., Rn8r1 r09) remains unchanged.
    In such case, we deem the move successful, and the MC-VRPSD solution is updated. Finally,
    the procedure is restarted from the top following a first improvement configuration. The S2-Opt procedure
    repeats until it cannot find any more improvements.
    :param instance: 实例
    :param R: 路线集
    :return: 优化后的路线集
    """
    for r in R:
        for r_apo in R:
            if r == r_apo:
                continue
            r_apo_2 = r[:-1] + r_apo[1:]
            for i in range(1, len(r_apo_2) - 2):
                for j in range(i + 2, len(r_apo_2)):
                    r_apo_3 = r_apo_2[:i] + list(reversed(r_apo_2[i:j])) + r_apo_2[j:]
                    # 这里是可以优化的，只需要计算变化的边之差就好，但目前的本身也不算麻烦
                    if instance.calculate_planned_length(r_apo_3) < instance.calculate_planned_length(r_apo_2):
                        R_apo_3 = s_split(instance, r_apo_3)
                        if instance.calculate_routes_total_expected_length(
                                R_apo_3) < instance.calculate_total_expected_length(
                            r) + instance.calculate_total_expected_length(r_apo):
                            R.remove(r)
                            R.remove(r_apo)
                            R.extend(R_apo_3)
                            R = stochastic_2_opt(instance, R)
                            return R
    return R


if __name__ == '__main__':
    mcvrpsd = MCVRPSDInstance(n_customers=20, random_seed=0)
    init_R = SCW(mcvrpsd)
    optimized_R = stochastic_2_opt(instance=mcvrpsd, R=init_R.copy())
    mcvrpsd.draw_routes(optimized_R,
                        description='2-Opt optimizes results from SCW\nPlanned Cost: {}\nTotal Expected Cost: {}'.format(
                            mcvrpsd.calculate_routes_planned_length(optimized_R),
                            mcvrpsd.calculate_routes_total_expected_length(optimized_R)),
                        save_pic_suffix='SCW-2-opt')
