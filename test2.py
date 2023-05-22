import sklearn.datasets
import torch
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# np.random.seed(0)
ConnParam_path = 'E://KaifengChen//neuTube_plus//dataset//result//256//ConnParam.xlsx'
df_data = pd.read_excel(ConnParam_path)  # 假设输出变量在第一列
scaler = MinMaxScaler()
norm_data = (scaler.fit_transform(df_data))  # norm_data的类型为 numpy.ndarray
# X = torch.from_numpy(norm_data[1:100, 1:]).to(torch.float32)
# y = torch.from_numpy(norm_data[1:100, 0:1]).to(torch.long).squeeze(-1)
X, y = sklearn.datasets.make_moons(200, noise=0.2)
# plt.scatter(X[:, 0], X[:, 1], s=40, c=y, cmap=plt.cm.binary)
X = torch.from_numpy(X).type(torch.FloatTensor)
y = torch.from_numpy(y).type(torch.LongTensor)




import torch.nn as nn
import torch.nn.functional as F


# our class must extend nn.Module
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        # Our network consists of 3 layers. 1 input, 1 hidden and 1 output layer
        # This applies Linear transformation to input data.
        self.fc1 = nn.Linear(2, 8)

        # This applies linear transformation to produce output data
        self.fc2 = nn.Linear(8, 2)

    # This must be implemented
    def forward(self, x):
        # Output of the first layer
        x = self.fc1(x)
        # Activation function is Relu. Feel free to experiment with this
        x = F.tanh(x)
        # This produces output
        x = self.fc2(x)
        return x

    # This function takes an input and predicts the class, (0 or 1)
    def predict(self, x):
        # Apply softmax to output
        pred = F.softmax(self.forward(x))
        ans = []
        for t in pred:
            if t[0] > t[1]:
                ans.append(0)
            else:
                ans.append(1)
        return torch.tensor(ans)


# Initialize the model
model = Net()
# Define loss criterion
criterion = nn.CrossEntropyLoss()
# Define the optimizer
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

# Number of epochs
epochs = 10000
# List to store losses
losses = []
for i in range(epochs):
    # Precit the output for Given input
    y_pred = model.forward(X)
    print(f"y = {y}")
    print(f"y_pred = {y_pred}")
    # Compute Cross entropy loss
    loss = criterion(y_pred, y)
    # Add loss to the list
    losses.append(loss.item())
    # Clear the previous gradients
    optimizer.zero_grad()
    # Compute gradients
    loss.backward()
    # Adjust weights
    optimizer.step()
    print(i)

from sklearn.metrics import accuracy_score

print(accuracy_score(model.predict(X), y))


def predict(x):
    x = torch.from_numpy(x).type(torch.FloatTensor)
    ans = model.predict(x)
    return ans.numpy()


# Helper function to plot a decision boundary.
# If you don't fully understand this function don't worry, it just generates the contour plot below.
def plot_decision_boundary(pred_func, X, y):
    # Set min and max values and give it some padding
    x_min, x_max = X[:, 0].min() - .5, X[:, 0].max() + .5
    y_min, y_max = X[:, 1].min() - .5, X[:, 1].max() + .5
    h = 0.01
    # Generate a grid of points with distance h between them
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    # Predict the function value for the whole gid
    Z = pred_func(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    # Plot the contour and training examples
    plt.contourf(xx, yy, Z, cmap=plt.cm.Spectral)
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap=plt.cm.binary)


# plot_decision_boundary(lambda x: predict(x), X.numpy(), y.numpy())
# plt.show()