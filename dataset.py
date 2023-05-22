import time

import numpy as np
import torch

from swc_tool_lib import *

class ConnParmDataset(Dataset):
    def __init__(self, device):
        df_data = pd.read_excel(ConnParam_path)  # 假设输出变量在第一列
        # scaler = MinMaxScaler()
        # norm_data = (scaler.fit_transform(df_data))  # norm_data的类型为 numpy.ndarray
        norm_data = np.asarray(df_data[0:10005])
        # index = np.where(norm_data[1:, 0:1] == 1)
        # print(len(index[0]) / len(norm_data))
        # time.sleep(5)
        ###### posi_norm_data = norm_data[index[0]]
        # print(posi_norm_data)
        # print(len(posi_norm_data))
        # print("_-------------")
        # print(round((len(norm_data) / len(posi_norm_data))))
        ###### copy_times = round((len(norm_data) / len(posi_norm_data)))
        ###### posi_norm_data = np.tile(posi_norm_data, (copy_times, 1))
        # print(posi_norm_data)
        # print(len(posi_norm_data))
        ###### norm_data = np.vstack((norm_data, posi_norm_data))
        # norm_data.to(device)

        self.data = torch.from_numpy(norm_data[1:, 1:]).to(torch.float32).to(device)
        self.label = torch.from_numpy(norm_data[1:, 0:1]).to(torch.float32).squeeze(-1).to(device)

    def __getitem__(self, index):
        return self.data[index], self.label[index]  # 以元组的形式返回

    def __len__(self):
        return len(self.data)

def LoadData(device, batch_size = 1):
    custom_dataset = ConnParmDataset(device)

    train_size = int(len(custom_dataset) * 0.8)
    validate_size = int(len(custom_dataset) * 0.1)
    test_size = len(custom_dataset) - validate_size - train_size
    train_dataset, validate_dataset, test_dataset = torch.utils.data.random_split(custom_dataset,
                                                                                  [train_size, validate_size,
                                                                                   test_size])
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    # train_loader = DataLoader(custom_dataset, batch_size=batch_size, shuffle=True)
    validate_loader = DataLoader(validate_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=True)

    return train_loader, validate_loader, test_loader
    # return train_loader, test_loader

def LoadData_svm(device, batch_size = 1):
    custom_dataset = ConnParmDataset(device)

    train_size = int(len(custom_dataset) * 0.8)
    validate_size = int(len(custom_dataset) * 0.1)
    test_size = len(custom_dataset) - validate_size - train_size
    train_dataset, validate_dataset, test_dataset = torch.utils.data.random_split(custom_dataset,
                                                                                  [train_size, validate_size,
                                                                                   test_size])
    # train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    # # train_loader = DataLoader(custom_dataset, batch_size=batch_size, shuffle=True)
    # validate_loader = DataLoader(validate_dataset, batch_size=batch_size, shuffle=True)
    # test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=True)

    return train_dataset, validate_dataset, test_dataset
    # return train_loader, test_loader


if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print('Using {} device'.format(device))

