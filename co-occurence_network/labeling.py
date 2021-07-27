import pandas
import csv
import readchar
import sys
from sklearn import metrics

def test():

	true_conservatives, false_liberals = 0, 0
	false_conservatives, true_liberals = 0, 0
	total_correct, total_incorrect = 0, 0

	df = pandas.read_csv('labeling.csv', names=['user_id_str', 'bio', 'pred_ideology'])
	curr_row = 0
	num_rows = len(df.index)

	ground_truth = []

	print("Use the left arrow key to classify  as 'liberal',  the right arrow key to classify as 'conservative', or the down arrow key to classify as 'neither/neutral':")
	for index, row in df.iterrows():
		curr_row += 1
		print(f"{curr_row} / {num_rows}")
		print(row['bio'])
		human_label = 0
		key = readchar.readkey()
		if key == "\x1b\x5b\x44": # left arrow key
			print("human label: liberal")
			human_label = -1
		elif key == "\x1b\x5b\x43": # right arrow key
			print("human label: conservative")
			human_label = 1
		elif key == "\x1b\x5b\x42": # down arrow key
			print("human label: neither/neutral")
			human_label = 0
		elif key == "\x1b" or key == "\x03":
			sys.exit(0)
		ground_truth.append(human_label)

		if human_label == row['pred_ideology']:
			print("[PASS] LABEL IS CORRECT")
			total_correct += 1
			if human_label == 1:
				true_conservatives += 1
			elif human_label == -1:
				true_liberals += 1
		else:
			print("[FAIL] LABEL IS INCORRECT")
			total_incorrect += 1
			if human_label == 1:
				false_liberals += 1
			elif human_label == -1:
				false_conservatives += 1
		print('-'*10)

	df['actual_ideology'] = ground_truth
	df.to_csv('ground_truth.csv')

	print("\nREPORT:\n")
	total = total_correct + total_incorrect
	matrix = [
	   [f"n={total}",  "Predicted Conservatives", "Predicted Liberals"],
	   ["Actual Conservatives", f"{true_conservatives}", f"{false_liberals}"],
	   ["Actual Liberals",  f"{false_conservatives}", f"{true_liberals}"]
	]

	s = [[str(e) for e in row] for row in matrix]
	lens = [max(map(len, col)) for col in zip(*s)]
	fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
	table = [fmt.format(*row) for row in s]
	print('\n'.join(table))

	accuracy = 100 * total_correct / total
	print(f"\nACCURACY: {accuracy} % ({total_correct} / {total})\n")

def read_ground_truth():
	ground_truth_df = pandas.read_csv('ground_truth.csv', names=['user_id_str', 'bio', 'pred_ideology', 'actual_ideology'])
	pred_ideology = ground_truth_df[['pred_ideology']].to_numpy()
	actual_ideology = ground_truth_df[['actual_ideology']].to_numpy()
	print(metrics.classification_report(actual_ideology, pred_ideology))
	print(metrics.confusion_matrix(y_true=actual_ideology, y_pred=pred_ideology, labels=['-1', '0', '1']))


if '-t' in sys.argv:
	test()
if '-r' in sys.argv:
	read_ground_truth()
#read_ground_truth()
