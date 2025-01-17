from read import process_directory, get_search_range
import matplotlib.pyplot as plt
import datetime
import calendar
import matplotlib
import matplotlib.dates as mdates
from bisect import bisect_left, bisect_right
import numpy as np

matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号

def iter_month(begin_date, end_date):
    while begin_date < end_date:
        yield begin_date, begin_date + datetime.timedelta(days=calendar.monthrange(begin_date.year, begin_date.month)[1])
        begin_date = begin_date + datetime.timedelta(days=calendar.monthrange(begin_date.year, begin_date.month)[1])

def iter_day(begin_date, end_date):
    while begin_date < end_date:
        yield begin_date, begin_date + datetime.timedelta(days=1)
        begin_date = begin_date + datetime.timedelta(days=1)

translate = {
    "search": "搜索条数", 
    "empty": "空页数", 
    "not complete": "未完全搜索数",
    "search avg": "页平均条数",
    "search max": "页平均最大条数",
    "search prop": "每页条数比例",
}

if __name__ == "__main__":
    statlog = dict({"search": dict(), "empty": dict(), "not complete": dict()})
    for log_content in process_directory('.'):
        for line in log_content:
            log_type, start, end, index = get_search_range(line)
            if start == end:
                continue
            match log_type:
                case "search":
                    count = int(line.split(" ")[4])
                    if (start, end) in statlog["search"]:
                        statlog["search"][(start, end)].add((index, count))
                    else:
                        statlog["search"][(start, end)] = {(index, count)}

                    if count == 0:
                        if (start, end) in statlog["empty"]:
                            statlog["empty"][(start, end)].add(index)
                        else:
                            statlog["empty"][(start, end)] = {index}
                case "empty":
                    if start == end:
                        end = end + datetime.timedelta(days=1)
                    if (start, end) in statlog["empty"]:
                        statlog["empty"][(start, end)].add(index)
                    else:
                        statlog["empty"][(start, end)] = {index}
                case "not complete":
                    if (start, end) in statlog["not complete"]:
                        statlog["not complete"][(start, end)].add((index))
                    else:
                        statlog["not complete"][(start, end)] = {index}

    sum_statlog = dict({"search": dict(), "search avg": dict(), "search max": dict(), "search prop": dict(), "empty": dict(), "not complete": dict()})
    for key in statlog["search"]:
        scale = (key[1] - key[0]).total_seconds()
        sum_statlog["search"][key] = sum([x[1] for x in statlog["search"][key]])
        sum_statlog["search avg"][key] = sum_statlog["search"][key] / len(statlog["search"][key])
        sum_statlog["search max"][key] = max([x[1] for x in statlog["search"][key]])
        sum_statlog["search prop"][key] = sum_statlog["search avg"][key] / sum_statlog["search max"][key] if sum_statlog["search max"][key] != 0 else 0
    for key in statlog["empty"]:
        sum_statlog["empty"][key] = len(set(statlog["empty"][key]))
    for key in statlog["not complete"]:
        sum_statlog["not complete"][key] = len(set(statlog["not complete"][key]))

    # 时间加权平均

    time_points = set()
    for domain in statlog:
        for key in statlog[domain]:
            time_points.add(key[0])
            time_points.add(key[1])
    time_points = list(time_points)
    time_points.sort()

    time_statlog = dict()
    for domain in sum_statlog:
        time_statlog[domain] = dict()
    for tp in time_points:
        for domain in time_statlog:
            time_statlog[domain][tp] = []
    for domain in sum_statlog:
        for key in sum_statlog[domain]:
            begin_tp = bisect_right(time_points, key[0]) - 1
            end_tp = bisect_left(time_points, key[1])
            scale = (key[1] - key[0]).total_seconds()
            for i in range(begin_tp, end_tp):
                tp_scale = (time_points[i + 1] - time_points[i]).total_seconds()
                if domain in ["search", "empty", "not complete"]:
                    time_statlog[domain][time_points[i]].append(sum_statlog[domain][key] * tp_scale / scale)
                else:
                    time_statlog[domain][time_points[i]].append(sum_statlog[domain][key])

    for domain in time_statlog:
        for i in range(len(time_points) - 1):
            if len(time_statlog[domain][time_points[i]]) != 0:
                time_statlog[domain][time_points[i]] = sum(time_statlog[domain][time_points[i]]) / len(time_statlog[domain][time_points[i]])
            else:
                time_statlog[domain][time_points[i]] = 0
        time_statlog[domain][time_points[-1]] = 0


    result_freq = dict()
    for domain in time_statlog:
        result_freq[domain] = dict()
    for begin_date, end_date in iter_month(datetime.datetime(2014, 1, 1), datetime.datetime(2025, 1, 1)):
        for domain in time_statlog:
            if (begin_date, end_date) not in result_freq[domain]:
                result_freq[domain][(begin_date, end_date)] = 0
                
            begin_tp = bisect_right(time_points, begin_date) - 1
            end_tp = bisect_left(time_points, end_date)

            for i in range(begin_tp, end_tp):
                if domain in ["search", "empty", "not complete"]:
                    tp_prop = 1
                    if time_points[i] < begin_date:
                        tp_prop = 1 - (time_points[i + 1] - begin_date).total_seconds() / (time_points[i + 1] - time_points[i]).total_seconds()
                    elif time_points[i + 1] > end_date:
                        tp_prop = 1 - (end_date - time_points[i]).total_seconds() / (time_points[i + 1] - time_points[i]).total_seconds()
                    result_freq[domain][(begin_date, end_date)] += time_statlog[domain][time_points[i]] * tp_prop
                else:
                    prop = (min(time_points[i + 1], end_date) - max(time_points[i], begin_date)).total_seconds() / (end_date - begin_date).total_seconds()
                    result_freq[domain][(begin_date, end_date)] += time_statlog[domain][time_points[i]] * prop

    # 绘制每月平均频率
    for domain in result_freq:
        fig, ax = plt.subplots()
        dates = [x[0] for x in sorted(result_freq[domain].keys())]
        values = [result_freq[domain][x] for x in sorted(result_freq[domain].keys())]
        ax.plot(dates, values, label=translate[domain], color=(0.2, 0.2, 0.2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        plt.xlabel('年')
        plt.ylabel(f"{translate[domain]}")
        plt.title(f'每月{translate[domain]}')
        plt.savefig(f"output/{domain}_monthly_avg_freq.png")
        plt.close(fig)

    # 计算域的相关性系数
    domains = list(result_freq.keys())
    corr_coef = dict()
    corr_18_coef = dict()
    for i in range(len(domains)):
        for j in range(i+1, len(domains)):
            # 提取两个域的值序列
            dates_i = [x[0] for x in sorted(result_freq[domains[i]].keys())]
            values_i = [result_freq[domains[i]][x] for x in sorted(result_freq[domains[i]].keys())]
            values_j = [result_freq[domains[j]].get(x, 0) for x in sorted(result_freq[domains[i]].keys())]

            # 计算皮尔逊相关系数
            corr_coef[(domains[i], domains[j])] = np.corrcoef(values_i, values_j)[0, 1]
            print(f"Correlation between {domains[i]} and {domains[j]}: {corr_coef[(domains[i], domains[j])]}")

            dates_18_i = [x[0] for x in sorted(result_freq[domains[i]].keys()) if x[0] >= datetime.datetime(2018, 1, 1)]
            values_18_i = [result_freq[domains[i]][x] for x in sorted(result_freq[domains[i]].keys()) if x[0] >= datetime.datetime(2018, 1, 1)]
            values_18_j = [result_freq[domains[j]].get(x, 0) for x in sorted(result_freq[domains[i]].keys()) if x[0] >= datetime.datetime(2018, 1, 1)]

            # 计算皮尔逊相关系数
            corr_18_coef[(domains[i], domains[j])] = np.corrcoef(values_18_i, values_18_j)[0, 1]
            print(f"Correlation between {domains[i]} and {domains[j]} after 2018: {corr_18_coef[(domains[i], domains[j])]}")

    # 绘制两个指定的域
    task = {("empty", "not complete"): "频次", ("search avg", "search max"): "平均条数"}
    for key in task:
        fig, ax = plt.subplots()
        dates = [x[0] for x in sorted(result_freq[key[0]].keys())]
        values_i = [result_freq[key[0]][x] for x in sorted(result_freq[key[0]].keys())]
        values_j = [result_freq[key[1]].get(x, 0) for x in sorted(result_freq[key[0]].keys())]
        ax.plot(dates, values_i, label=translate[key[0]], color='r')
        ax.plot(dates, values_j, label=translate[key[1]], color='b')
        ax.legend()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        plt.xlabel('年')
        plt.ylabel(f"{task[key]}")
        plt.title(f"相关性系数：{corr_coef[key]:.2f}")
        plt.savefig(f"output/{key[0]}_{key[1]}_monthly_avg_freq.png")
        plt.close(fig)

    # 计算绘制域每年相关性系数
    for i in range(len(domains)):
        for j in range(i+1, len(domains)):
            corr_coef_year = dict()
            for year in range(2014, 2025):
                begin_date = datetime.datetime(year, 1, 1)
                end_date = datetime.datetime(year + 1, 1, 1)
                dates_i = [x[0] for x in sorted(result_freq[domains[i]].keys()) if x[0] >= begin_date and x[0] < end_date]
                values_i = [result_freq[domains[i]][x] for x in sorted(result_freq[domains[i]].keys()) if x[0] >= begin_date and x[0] < end_date]
                values_j = [result_freq[domains[j]].get(x, 0) for x in sorted(result_freq[domains[i]].keys()) if x[0] >= begin_date and x[0] < end_date]

                # 计算皮尔逊相关系数
                corr_coef_year[year] = np.corrcoef(values_i, values_j)[0, 1]
            fig, ax = plt.subplots()
            dates = list(corr_coef_year.keys())
            values = list(corr_coef_year.values())
            ax.plot(dates, values, color=(0.2, 0.2, 0.2))
            # 标注数值
            for a, b in zip(dates, values):
                plt.text(a, b, f"{b:.2f}", ha='center', va='bottom', fontsize=10)
            plt.xlabel('年')
            plt.ylabel(f"相关性系数")
            plt.title(f"{translate[domains[i]]}与{translate[domains[j]]}每年相关性系数")
            plt.savefig(f"output/{domains[i]}_{domains[j]}_yearly_corr_coef.png")
            
