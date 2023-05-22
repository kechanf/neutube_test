from swc_tool_lib import *

debug_mode = 0

class ConnNet(nn.Module):
    # def __init__(self):
    #     super(ConnNet, self).__init__()
    #     self.fc1 = nn.Linear(2, 4)
    #     self.fc2 = nn.Linear(4, 2)
    def __init__(self):
        super(ConnNet, self).__init__()
        N_HIDDEN = 10

        self.net_bn = torch.nn.Sequential(
            torch.nn.BatchNorm1d(4),
            torch.nn.Linear(4, N_HIDDEN),
            torch.nn.BatchNorm1d(N_HIDDEN),
            torch.nn.ReLU(),
            torch.nn.Linear(N_HIDDEN, N_HIDDEN),
            torch.nn.BatchNorm1d(N_HIDDEN),
            torch.nn.ReLU(),
            torch.nn.Linear(N_HIDDEN, 1),
            torch.nn.Sigmoid(),
        )


    def forward(self, x):
        x = self.net_bn(x)
        return x

    # def predict(self, x):
    #     # Apply softmax to output
    #     pred = F.softmax(self.forward(x))
    #     ans = []
    #     for t in pred:
    #         if t[0] > t[1]:
    #             ans.append(0)
    #         else:
    #             ans.append(1)
    #     return torch.tensor(ans)


if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device {device}")

    # train_loader, validate_loader, test_loader = LoadData()
    train_loader, val_loader, test_loader = LoadData(device, 64)

    # model = ConnNet().to(device)
    model = ConnNet().to(device)
    learning_rate = 1e-5
    # batch_size = 64
    epochs = 500

    # loss_fn = nn.CrossEntropyLoss()
    loss_fn = nn.MSELoss(reduction='mean')
    optimizer = torch.optim.Adamax(model.parameters(), lr = learning_rate)  # Adam梯度优化器
    # optimizer = torch.optim.SGD(model.parameters(), lr = learning_rate)


    def nntrain_loop(dataloader, model, loss_fn, optimizer):
        size = len(dataloader.dataset)
        losses = []
        for batch, (X, y) in enumerate(dataloader):
            # Compute prediction and loss
            pred = model.forward(X)
            # print(X)
            # print(pred)
            # print(y)
            # print("------------")
            # print(f"pred {pred}")
            # print(f"y {y}")
            loss = loss_fn(pred, y)
            # print(f"loss {loss}")

            losses.append(loss.item())

            # Backpropagation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if batch % 1000 == 0:
                loss, current = loss.item(), batch * len(X)
                print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")


    def nntest_loop(dataloader, model, loss_fn):
        size = len(dataloader.dataset)
        test_loss, correct, TP, FN = 0, 0, 0, 0

        with torch.no_grad():
            for X, y in dataloader:
                pred = model(X)
                # print(f"pred = {pred}")
                # print(f"pred.argmax(1) = {pred.argmax(1)}")
                # print(f"y = {y}")
                # print("--------------------------")
                test_loss += loss_fn(pred, y).item()
                for i in range(len(pred)):
                    if(math.fabs(pred[i] - y[i]) < 0.4):
                        correct = correct + 1
                # correct += (pred.argmax(1) == y).type(torch.float).sum().item()
                # if(y == 1 and pred.argmax(1) == 1):
                #     TP = TP + 1
                # if(y == 1 and pred.argmax(1) == 0):
                #     FN = FN + 1

        test_loss /= size
        correct /= size
        print(f"Test Error: \n Accuracy: {(100 * correct):>0.1f}%, Avg loss: {test_loss:>8f}")
        # print(f"TP = {TP}, FN = {FN}, recall = {TP / (TP + FN)}  \n")

    for t in range(epochs):
        print(f"Epoch {t + 1}\n-------------------------------")
        nntrain_loop(train_loader, model, loss_fn, optimizer)
        nntest_loop(test_loader, model, loss_fn)
    print("Done!")

    torch.save(model.state_dict(), nn_model_path)
    print(f"Saved PyTorch Model State to {nn_model_path}")

