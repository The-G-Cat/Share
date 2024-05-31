import numpy as np
import itertools
from multiprocessing import Pool
from openpyxl import load_workbook

def read_data(filename):
	data=[]
	datas=[]
	tdata=[]
	wb = load_workbook(filename, data_only=True)
	twb = list(wb)
	del twb[0]
	for sheet in twb:
		rows = list(sheet.rows)
		del rows[0]
		del rows[0]
		temp=rows[0][1].value
		for row in rows:
			if row[1].value==temp:
				tdata.append((float(format(row[5].value,'.3f')),row[1].value,float(format(row[6].value,'.3f')),row[2].value))
			else:
				temp=row[1].value
				datas.append(tdata)
				tdata=[]
				tdata.append((float(format(row[5].value,'.3f')),float(format(row[6].value,'.3f')),row[4].value,row[2].value))
		data.append(datas)
		datas=[]
	wb.close()
	return data


def calculate_t(values, params):
	i, m, j, k = params
	try:
		t_values = [float(a)**i * float(b)**m / (float(c)**j * float(d)**k) for a, b, c, d in values]
	except ZeroDivisionError:
		return float('inf'), 0  # Avoid division by zero errors 
	variance = np.var(t_values)
	mean = np.mean(t_values)
	return variance, mean

def find_good_params(args):
	sublist, variance_threshold = args
	good_results = []
	for i, m, j, k in itertools.product([x * 0.1 for x in range(0, 31)], repeat=4):
		if i != 0 and m != 0 and j != 0 and k != 0:
			variance, mean = calculate_t(sublist, (i, m, j, k))
			if variance < variance_threshold and mean > 0.5:
				good_results.append(((i, m, j, k), variance, mean))
	return good_results

def process_data(data, pool,variance_threshold):
	tasks = [(sublist, variance_threshold) for sublist in itertools.chain.from_iterable(data)]
	results = pool.map(find_good_params, tasks)
	
	# Analyze the results
	all_params = [param for sublist in results for param, _, _ in sublist]
	try:
		common_params = max(set(all_params), key=all_params.count)
		common_results = [[(param, var, mean) for (param, var, mean) in sublist if param == common_params] for sublist in results]
		return common_params, common_results  # Most common parameter set
	except:
		print(variance_threshold,"FAILED!")
		variance_threshold+=0.001
		return process_data(data,pool,variance_threshold)

if __name__ == '__main__':
	data=read_data("元数据.xlsx")
	
	with Pool() as pool:
		common_params, results = process_data(data, pool,0.0001)
	
	print("Common Parameters:", common_params)
	for result_set in results:
		for result in result_set:
			print("Sublist result:", result)