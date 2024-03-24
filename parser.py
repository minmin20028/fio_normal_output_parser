import re
import pandas as pd

def parse_fio_output(output):
    result = {}

    # write IOPS 추출
    iops_match = re.search(r'IOPS=(\d+\.?\d*)', output)
    if iops_match:
        result['write IOPS(k)'] = float(iops_match.group(1))

    # clat avg, stdev, max, min 추출
    clat_attributes = re.findall(r'clat \(usec\): min=(\d+\.?\d*\S*), max=(\d+\.?\d*\S*), avg=(\d+\.?\d*\S*), stdev=(\d+\.?\d*\S*)', output)
    #print(clat_attributes)

    result['min(usec)'] = float(clat_attributes[0][0])
    if clat_attributes[0][1][-1] == 'k':
        result['max(usec)'] = float(clat_attributes[0][1][:-1]) * 1000
    else:
        result['max(usec)'] = float(clat_attributes[0][1])
    result['avg(usec)'] = float(clat_attributes[0][2])
    result['stdev(usec)'] = float(clat_attributes[0][3])

    # clat percentiles 추출
    percentile_matches = re.findall(r'(\d+.\d+)th=\[\s*(\d+)\s*\]', output)
    #print(percentile_matches)

    for percentile_match in percentile_matches:
        percentile = percentile_match[0]
        latency = int(percentile_match[1])
        result[percentile+'th(usec)'] = latency

    return result

def parse_fio_files(file_paths):
    parsed_results = {}
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            fio_output = file.read()

            # Extract prefix from filename
            prefix = file_path.split('_output_')[0]
            if prefix not in parsed_results:
                parsed_results[prefix] = []

            parsed_results[prefix].append(parse_fio_output(fio_output))
    return parsed_results

# 파일 경로 설정
file_paths = ["write100_fio_output_1.txt", "write100_fio_output_2.txt", 
              "write50_fio_output_1.txt", "write50_fio_output_2.txt"]

# 파일 파싱
parsed_results = parse_fio_files(file_paths)

# 데이터프레임 생성 및 결과 내보내기
with pd.ExcelWriter('fio_results.xlsx') as writer:
    for prefix, results in parsed_results.items():
        df = pd.DataFrame(results)
        df = df.transpose()
        df.to_excel(writer, sheet_name=prefix)
