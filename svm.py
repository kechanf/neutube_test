from swc_tool_lib import *
# from sklearn.model_selection import train_test_split#划分数据集与测试集
# from sklearn import svm#导入算法模块
# from sklearn.metrics import accuracy_score#导入评分模块
# from sklearn.preprocessing import MinMaxScaler


ConnParam_path = 'D://KaifengChen//neuTube_plus//dataset//result//256//ConnParam.xlsx'
df_data = pd.read_excel(ConnParam_path)  # 假设输出变量在第一列
df_data = df_data[1:]

scaler = MinMaxScaler()
norm_data = (scaler.fit_transform(df_data))
# print(type(norm_data))
# norm_data = np.array(df_data)
# print(type(norm_data))
X = norm_data[0:, 1:]
y = norm_data[0:, 0:1]

X_train,X_test,y_train,y_test=train_test_split(X, y, test_size=0.2, random_state=1)
# print(y_train)

svm_model=svm.SVC(C=1, kernel="rbf")#参数部分会在下面进行讲解
svm_model.fit(X_train, y_train.ravel())
print("train_acc：" + str(accuracy_score(y_train, svm_model.predict(X_train))))
print("test_acc：" + str(accuracy_score(y_test, svm_model.predict(X_test))))
print(f"train_recall = {recall_score(svm_model.predict(X_train), y_train)}")
print(X_train)
print(f"test_recall = {recall_score(svm_model.predict(X_test), y_test)}")

joblib.dump(svm_model, svm_model_path)