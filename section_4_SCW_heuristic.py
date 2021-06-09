from section_2_3_problem import MCVRPSDInstance


def SCW(instance: MCVRPSDInstance):
    """
    Similarly to the classical savings algorithm, the SCW heuristic starts from a trivial
    solution comprised of n round trips from the depot to each customer. Then it tries at each iteration to
    merge two routes by their extreme vertices (those connected to the depot), aiming to generate the largest
    possible savings in the overall cost.

    :param instance: 案例
    :return: 规划的路线的集合
    """
    R = []
    for customer in range(1, instance.n_customers + 1):
        R.append([0, customer, 0])
    R_version = 0
    instance.draw_routes(R, description='Planned Cost: {}\nTotal Expected Cost: {}'.format(
        instance.calculate_routes_planned_length(R), instance.calculate_routes_total_expected_length(R)),
                         show_pic=False, save_pic_suffix='SCW {}'.format(R_version))
    R_version += 1
    while True:
        saving_list = []
        route_records = []
        combination_list = []
        for r in R:
            u_e = r[1:]  # e: end
            e_u = list(reversed(u_e))
            s_v = r[:-1]  # s: start
            v_s = list(reversed(s_v))
            for r_apo in R:
                if r == r_apo:
                    continue
                u_e_apo = r_apo[1:]
                e_u_apo = list(reversed(u_e_apo))
                s_v_apo = r_apo[:-1]
                v_s_apo = list(reversed(s_v_apo))
                all_possible_combination_pairs = [[e_u + u_e_apo, e_u_apo + u_e],
                                                  [e_u + v_s_apo, s_v_apo + u_e],
                                                  [s_v + u_e_apo, e_u_apo + v_s],
                                                  [s_v + v_s_apo, s_v_apo + v_s]]
                original_cost = instance.calculate_total_expected_length(
                    r) + instance.calculate_planned_length(r_apo)
                for combination_pair in all_possible_combination_pairs:
                    combination_pairs_total_cost = [
                        instance.calculate_total_expected_length(combination_pair[0]),
                        instance.calculate_total_expected_length(combination_pair[1])]
                    min_merging_cost = min(combination_pairs_total_cost)
                    if min_merging_cost < instance.L:
                        saving_list.append(original_cost - min_merging_cost)
                        route_records.append([r, r_apo])
                        combination_list.append(combination_pair[combination_pairs_total_cost.index(min_merging_cost)])
        s_max = max(saving_list)
        if s_max < 0 or len(saving_list) == 0:
            return R
        else:
            best_merge_index = saving_list.index(s_max)
            R.remove(route_records[best_merge_index][0])
            R.remove(route_records[best_merge_index][1])
            R.append(combination_list[best_merge_index])
            instance.draw_routes(R, description='Planned Cost: {}\nTotal Expected Cost: {}'.format(
                instance.calculate_routes_planned_length(R), instance.calculate_routes_total_expected_length(R)),
                                 show_pic=False, save_pic_suffix='SCW {}'.format(R_version))
            R_version += 1


if __name__ == '__main__':
    mcvrpsd_instance = MCVRPSDInstance(n_customers=20, random_seed=0)
    print(SCW(mcvrpsd_instance))
