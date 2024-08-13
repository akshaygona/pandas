import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.compose import make_column_transformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures

class UserPredictor:
    def __init__(self, degree=2):
        transf1 = make_column_transformer((StandardScaler(), ['past_purchase_amt', 'seconds', 'age']),(OneHotEncoder(), ['badge']),remainder='passthrough')
        self.pipeline = Pipeline([('preprocess', transf1),('polynomial_features', PolynomialFeatures(degree=degree)),('classifier', LogisticRegression())])

    def fit(self, train_users, train_logs, train_y):
        x = ['past_purchase_amt', 'seconds', 'badge', 'age']
        y = 'y'
        train_agg = train_logs.groupby('user_id')['seconds'].sum().reset_index()
        train_users = pd.merge(train_users, train_agg, on='user_id', how='left').fillna(0)
        x_train = train_users[x]
        self.pipeline.fit(x_train, train_y[y])

    def predict(self, test_users, test_logs):
        x = ['past_purchase_amt', 'seconds', 'badge', 'age']
        test_agg = test_logs.groupby('user_id')['seconds'].sum().reset_index()
        test_users = pd.merge(test_users, test_agg, on='user_id', how='left').fillna(0)
        x_test = test_users[x]
        return self.pipeline.predict(x_test)
