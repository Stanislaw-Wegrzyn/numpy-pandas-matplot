import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

s = 'https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data'

df = pd.read_csv(s,
                 header=None,
                 encoding='utf-8')



y = df.iloc[0:100, 4].values
y = np.where(y == 'Iris-setosa', -1, 1)

X = df.iloc[0:100, [0, 2]].values



# from perceptron import Perceptron
# ppn = Perceptron(eta=0.1, n_iter=10)
#
# ppn.fit(X, y)
#
# plt.plot(range(1, len(ppn.errors_) + 1), ppn.errors_, marker='o')
# plt.title('Perceptron')
# plt.xlabel('Epochs')
# plt.ylabel('Number of updates')
#
# # plt.savefig('images/02_07.png', dpi=300)
# plt.show()


from adeline import AdalineGD

ada1 = AdalineGD(n_iter=200, eta=0.0004).fit(X, y)
plt.plot(range(1, len(ada1.cost_) + 1), np.log10(ada1.cost_), marker='o')
plt.xlabel('Epochs')
plt.ylabel('log(Sum-squared-error)')
plt.title('Adaline - Learning rate 0.01')


plt.show()

