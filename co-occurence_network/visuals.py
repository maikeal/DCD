import matplotlib.pyplot as plt
import numpy as np

X = [2015, 2016, 2017, 2018, 2019]



'''
Y_nb_overall = [77.57547463429816, 79.87861811391222, 81.87052598817304, 84.93619670090258, 87.31714908185496]
Y_nb_already_political = [91.55326137963398, 91.96254389387437, 92.18897637795276, 92.69333333333333, 91.88372093023256]
Y_nb_non_political = [70.64027939464493, 71.86124773492105, 71.79329437096278, 74.06576980568012, 78.08090310442145]

fig, nb_ax = plt.subplots()

nb_ax.plot(X, Y_nb_overall, label="Overall")
nb_ax.plot(X, Y_nb_already_political, label="Already Political")
nb_ax.plot(X, Y_nb_non_political, label="Non-Political")
nb_ax.legend()
nb_ax.set_title('Naive Bayes Classifier Performance')
nb_ax.set_xlabel('Year')
nb_ax.set_ylabel('Accuracy (%)')
nb_ax.set_xticks(X)
nb_ax.set_yticks(np.arange(75, 102.5, 2.5))

plt.show()
'''
'''
X_including_2020 = [2015, 2016, 2017, 2018, 2019, 2020]

Y_percentage_of_political_bios = 100 * np.array([2131, 2563, 3175, 3750, 4300]) / 6426
Y_percentage_of_political_bios_conservative = 100 * np.array([1277 + 96, 1506 + 118, 1783 + 139, 2122 + 184, 2399+258]) / 6426
Y_percentage_of_political_bios_liberal = 100 * np.array([84 + 674, 88 + 851, 99 + 1144, 90+1354, 91+1552]) / 6426

Y_percentage_of_non_political_bios = 100 * np.array([4295, 3863, 3251, 2767, 2126]) / 6426
Y_percentage_of_non_political_bios_conservative = 100 * np.array([1277 + 96, 1506 + 118, 1783 + 139, 2122 + 184, 2399+258]) / 6426
Y_percentage_of_non_political_bios_liberal = 100 * np.array([84 + 674, 88 + 851, 99 + 1144, 90+1354, 91+1552]) / 6426

fig, ax = plt.subplots()
ax.plot(X, Y_percentage_of_political_bios, color='green', label="Clearly Political Bios")
ax.plot([2019, 2020], [Y_percentage_of_political_bios[-1], 100], color='green', linestyle = '--')
ax.plot(X, Y_percentage_of_political_bios_conservative, color='red', label="Clearly Political Conservative Bios")
ax.plot([2019, 2020], [Y_percentage_of_political_bios_conservative[-1], 100*3237/6426], color='red', linestyle = '--')
ax.plot(X, Y_percentage_of_political_bios_liberal, color='blue', label="Clearly Political Liberal Bios")
ax.plot([2019, 2020], [Y_percentage_of_political_bios_liberal[-1], 100*3189/6426], color='blue', linestyle = '--')
ax.legend()
ax.set_title('Percentage of Bios in Dataset Containing Political Keywords')
ax.set_xlabel('Year')
ax.set_ylabel('% of Bios with Political Keywords')
ax.set_xticks(X_including_2020)
ax.set_yticks(range(0, 101, 10))
plt.show()
'''
'''
Y_svm_overall = [77.37501385655692, 78.79392528544507, 80.47888260724974, 83.4718989025607, 85.97716439419133]
Y_svm_already_political = [88.09766022380468, 86.30377524143987, 88.07201800450113, 87.82552083333334, 88.28353837141182]
Y_svm_non_political = [76.06369743717343, 77.70870337477798, 79.16233090530697, 82.57849031396127, 85.43888433141919]

fig, (nb_ax, svm_ax) = plt.subplots(1,2)

fig.suptitle('Classifier Performance Over Time')

nb_ax.plot(X, Y_nb_overall, label="Overall")
nb_ax.plot(X, Y_nb_already_political, label="Already Political")
nb_ax.plot(X, Y_nb_non_political, label="Non-Political")
nb_ax.legend()
nb_ax.set_title('Naive Bayes')
nb_ax.set_xlabel('Year')
nb_ax.set_ylabel('Accuracy (%)')
nb_ax.set_xticks(X)
nb_ax.set_yticks(np.arange(75, 102.5, 2.5))


svm_ax.plot(X, Y_svm_overall, label="Overall")
svm_ax.plot(X, Y_svm_already_political, label="Already Political")
svm_ax.plot(X, Y_svm_non_political, label="Non-Political")
svm_ax.legend()
svm_ax.set_title('Support Vector Machine')
svm_ax.set_xlabel('Year')
svm_ax.set_ylabel('Accuracy (%)')
svm_ax.set_xticks(X)
svm_ax.set_yticks(np.arange(75, 102.5, 2.5))

for ax in fig.get_axes():
	ax.label_outer()

plt.show()
'''