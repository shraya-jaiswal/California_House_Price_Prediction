from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pandas as pd
import joblib

print("Loading datasets")
data=fetch_california_housing()

X=pd.DataFrame(data.data, columns=data.feature_name)
y=data.target
print(f"Total records:{X.shape[0]}")

X_train, X_test, y_train, y_test= train_test_split(X)