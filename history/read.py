import os
import zipfile
import datetime
import calendar

def get_search_range(line):
    """从log.txt的一行中提取搜索范围"""
    search_range_str = line.split(" ")[2]
    log_type = "search"
    index = -1
    if search_range_str == "the":
        search_range_str = line.split("the result of ")[1].split(" is")[0]
        if line.split("is ")[1] == "empty":
            log_type = "empty"
        elif line.split("is ")[1] == "not complete":
            log_type = "not complete"
    
    if log_type == "search":
        start_str = search_range_str.split(":")[0]
        end_str = search_range_str.split(":")[1]
        try:
            start = datetime.datetime.strptime(start_str, "%Y-%m-%d-%H")
            end = datetime.datetime.strptime(end_str, "%Y-%m-%d-%H")
        except:
            start = datetime.datetime.strptime(start_str, "%Y-%m-%d-%H-%M")
            end = datetime.datetime.strptime(end_str, "%Y-%m-%d-%H-%M")
    else:
        try:
            start = datetime.datetime.strptime(search_range_str, "%Y-%m-%d-%H")
            end = start + datetime.timedelta(hours=1)
        except:
            start = datetime.datetime.strptime(search_range_str, "%Y-%m-%d")
            end = start + datetime.timedelta(days=1)

    if log_type == "search":
        index = int(line.split(" ")[3].split("&")[0])

    return log_type, start, end, index

def read_log_lines_from_zip(zip_path):
    """从指定的ZIP文件中读取weibo-search\\log.txt的内容"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # 检查ZIP文件中是否存在weibo-search\\log.txt
        
        begin_year = int(zip_path.split("_")[1][0:4])
        begin_month = int(zip_path.split("_")[1][4:6])
        end_year = int(zip_path.split("_")[2][0:4])
        end_month = int(zip_path.split("_")[2][4:6]) 
        begin_date = datetime.datetime(begin_year, begin_month, 1)
        end_date = datetime.datetime(end_year, end_month, calendar.monthrange(end_year, end_month)[1])
        end_date = end_date + datetime.timedelta(days=1)
        with zip_ref.open('weibo-search/log.txt') as log_file:
            for l in log_file:
                line = l.decode('utf-8').strip() 
                _, start, end, _ = get_search_range(line)
                if (start >= begin_date and start < end_date) or (end >= begin_date and end < end_date):
                    yield line


def process_directory(directory_path):
    """遍历指定目录下的所有ZIP文件，并读取其中的log.txt"""
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.zip'):
                zip_path = os.path.join(root, file)
                log_content = read_log_lines_from_zip(zip_path)
                if log_content:
                    yield log_content

if __name__ == "__main__":
    ranges = dict()

    # 读取当前目录下的所有ZIP文件
    for log_content in process_directory('.'):
        for line in log_content:
            log_type, start, end, index = get_search_range(line)
            match log_type:
                case "search":
                    if (start, end) in ranges:
                        ranges[(start, end)].add(index)
                    else:
                        ranges[(start, end)] = {index}
                case "empty":
                    if start == end:
                        end = end + datetime.timedelta(days=1)
                    if (start, end) in ranges:
                        ranges[(start, end)].add(-1)
                    else:
                        ranges[(start, end)] = {-1}
    
    max_index = 0
    for key in ranges:
        max_index = max(max_index, max(ranges[key]))
        for i in range(1, 51):
            if i not in ranges[key] and i + 1 in ranges[key]:
                print(f"缺页：{key[0]} {key[1]} {i}")
    print(f"最大页码：{max_index}")

    ranges = list(ranges.keys())
    ranges.sort()

    
    # 判断是否有缺漏
    lack_days = set()
    lack_hours = set()
    for i in range(1, len(ranges)):
        if ranges[i][0] > ranges[i - 1][1]:
            print(f"缺漏：{ranges[i - 1][1]} {ranges[i][0]}")
            for j in range((ranges[i][0] - ranges[i - 1][1]).days):
                lack_days.add(ranges[i - 1][1] + datetime.timedelta(days=j))
            if ranges[i][0] - ranges[i - 1][1] < datetime.timedelta(days=1):
                for j in range((ranges[i][0] - ranges[i - 1][1]).seconds // 3600):
                    lack_hours.add(ranges[i - 1][1] + datetime.timedelta(hours=j))
    
    lack_days = list(lack_days)
    lack_days = sorted(lack_days)
    with open("lack_days.txt", "w") as f:
        for day in lack_days:
            f.write(day.strftime("%Y-%m-%d") + "\n")

    lack_hours = list(lack_hours)
    lack_hours = sorted(lack_hours)
    with open("lack_hours.txt", "w") as f:
        for hour in lack_hours:
            f.write(hour.strftime("%Y-%m-%d-%H") + "\n")