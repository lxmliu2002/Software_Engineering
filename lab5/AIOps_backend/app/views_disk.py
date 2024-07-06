import pandas as pd
import numpy as np
import warnings
from scipy.stats import entropy
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.base import BaseEstimator, ClassifierMixin, clone
import pickle
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings
from django.http import JsonResponse
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.metrics import mean_absolute_error, mean_squared_error
from uuid import uuid4

warnings.filterwarnings("ignore")


def fill_miss_date(df: pd.DataFrame, id_col):
    date_df: pd.DataFrame = df.groupby(id_col)["date"].agg(["min", "max"]).reset_index()
    date_df = pd.concat(
        [date_df[[id_col, "min"]], pd.DataFrame(date_df[[id_col, "max"]].values, columns=[id_col, "min"])]
    )
    date_df.columns = [id_col, "date"]
    date_df = date_df.set_index("date")
    date_df["tmp"] = 1
    date_df = (
        date_df.groupby(id_col)
        .resample("1D", closed="left")["tmp"]
        .count()
        .reset_index()
    )
    del date_df["tmp"]
    return date_df


def get_rolling_mean(grp, freq):
    return grp.rolling(freq).mean()


def get_rolling_std(grp, freq):
    return grp.rolling(freq).std()


def gen_feat(df, num_cols, cate_cols):
    fm = fill_miss_date(df, "serial_number")
    df = fm.merge(df, on=["serial_number", "date"], how="left")
    df.sort_values(["serial_number", "date"], inplace=True)
    rolling_periods = [3, 5, 7]
    diff_periods = [2, 4, 6]

    for j in zip(rolling_periods, diff_periods):
        print(f"start gen feats, window size:diff-{j[1]}, rolling-{j[0]}")

        tmp_diff = df.groupby("serial_number")[num_cols].diff(j[1])
        tmp_diff.columns = [f"diff_{t}_{j[1]}" for t in num_cols]

        tmp_mean = df.groupby("serial_number")[num_cols].apply(get_rolling_mean, j[0])
        tmp_mean.columns = [f"mean_{t}_{j[1]}" for t in num_cols]

        tmp_std = df.groupby("serial_number")[num_cols].apply(get_rolling_std, j[0])
        tmp_std.columns = [f"std_{t}_{j[1]}" for t in num_cols]

        df = pd.concat([df, tmp_diff, tmp_mean, tmp_std], axis=1)

    tmp_nunique = df.groupby("serial_number")[cate_cols].apply(get_rolling_std, 7)
    tmp_nunique.columns = [f"nunique_{t}_7" for t in cate_cols]
    df = pd.concat([df, tmp_nunique], axis=1)

    for i in rolling_periods:
        print(f"start gen shift feats, window size: {i}")

        tmp_shift = df.groupby("serial_number")[cate_cols].shift(i)
        tmp_shift.columns = [f"shift_{t}_{i}" for t in cate_cols]

        df = pd.concat([df, tmp_shift], axis=1)

    df = df[df["model"].notnull()]
    return df


def train_and_save_model(data_path, model_name):
    df_data = pd.read_csv(data_path)

    # 指定需要使用的SMART属性编号
    features = [5, 9, 187, 188, 193, 194, 197, 198, 241, 242]
    features_specified = ["smart_{0}_raw".format(feature) for feature in features]

    # 处理日期和缺失值
    df_data["date"] = pd.to_datetime(df_data["date"])
    df_data.fillna(0, inplace=True)

    # 计算每个硬盘距离发生故障的天数，将20天以后记为100天
    df_data["days_to_failure"] = (
        df_data.groupby("serial_number")["date"].transform("max") - df_data["date"]
    ).dt.days
    df_data["days_to_failure"] = df_data["days_to_failure"].apply(
        lambda x: 100 if x > 20 or x < 0 else x
    )

    # 生成特征
    df_data = gen_feat(df_data, features_specified, [])

    # 确保days_to_failure列存在
    if "days_to_failure" not in df_data.columns:
        raise KeyError(
            "Column 'days_to_failure' not found in DataFrame after feature generation."
        )

    # 提取自变量和因变量
    X_data = df_data.drop(
        columns=["serial_number", "model", "failure", "date", "days_to_failure"]
    )
    Y_data = df_data["days_to_failure"]

    # 划分训练集和验证集
    X_train, X_val, Y_train, Y_val = train_test_split(
        X_data, Y_data, test_size=0.2, random_state=0
    )

    # 初始化XGBoost回归模型
    xgb_model = xgb.XGBRegressor(objective="reg:linear", eval_metric="rmse")

    # 定义超参数网格
    param_grid = {
        "n_estimators": [100, 200],
        "max_depth": [3, 6, 9],
        "learning_rate": [0.01, 0.1, 0.2],
    }

    # 使用网格搜索和交叉验证来优化模型超参数
    grid_search = GridSearchCV(
        estimator=xgb_model,
        param_grid=param_grid,
        scoring="neg_mean_squared_error",
        cv=3,
    )
    grid_search.fit(X_train, Y_train)

    # 最佳模型
    best_model = grid_search.best_estimator_
    print(f"Best parameters found: {grid_search.best_params_}")

    # 保存训练好的模型
    best_model.save_model(os.path.join(settings.MEDIA_ROOT, model_name))

    # 验证模型并输出评估指标
    Y_val_pred = best_model.predict(X_val)
    mse = mean_squared_error(Y_val, Y_val_pred)
    mae = mean_absolute_error(Y_val, Y_val_pred)
    print(f"The Mean Squared Error is {mse}")
    print(f"The Mean Absolute Error is {mae}")

@csrf_exempt
def train_days_after(request):
    """_summary_

    Args:
        request (_type_): HTTP请求
        ```json
        {
            "file_name": "days.csv"
        }
        ```

    Returns:
        ```json
        {
            "code": 0,
            "msg": "success",
            "data": {
                "model_name": "xgb_model_54cfbaa6-1ddc-4458-9979-036e00902d55.json"
            }
        }
        ```
    """
    reqBody = json.loads(request.body.decode())
    file_name = reqBody.get('file_name', None)
    model_name = f"xgb_model_{uuid4()}.json"
    train_and_save_model(os.path.join(settings.MEDIA_ROOT, file_name), model_name)
    return JsonResponse({'code': 0, 'msg': 'success', 'data': {"model_name": model_name}})


def load_model(model_name):
    model = xgb.XGBRegressor()
    model.load_model(model_name)
    return model


def predict_failure_days(model, test_data_path):
    test_data = pd.read_csv(test_data_path)
    features = [5, 9, 187, 188, 193, 194, 197, 198, 241, 242]
    features_specified = ["smart_{0}_raw".format(feature) for feature in features]

    test_data["date"] = pd.to_datetime(test_data["date"])
    test_data.fillna(0, inplace=True)
    test_data = gen_feat(test_data, features_specified, [])

    last_day_df = (
        test_data.groupby("serial_number")
        .apply(lambda df: df.iloc[-1])
        .reset_index(drop=True)
    )

    drop_columns = ["serial_number", "model", "failure", "date"]
    drop_columns = [col for col in drop_columns if col in last_day_df.columns]

    X_test = last_day_df.drop(columns=drop_columns)

    Y_pred = model.predict(X_test)
    Y_pred_rounded = np.round(Y_pred)
    last_day_df["predicted_days_to_failure"] = Y_pred_rounded

    return last_day_df[["serial_number", "date", "predicted_days_to_failure"]]

@csrf_exempt
def predict_days_after(request):
    """_summary_

    Args:
        request (_type_): HTTP请求
        ```json
        {
            "file_name": "test_day.csv",
            "model_name": "xgb_model_54cfbaa6-1ddc-4458-9979-036e00902d55.json",
        }
        ```
    
    Returns:
        ```json
        {
            "code": 0,
            "msg": "success",
            "data": [
                {
                    "serial_number":"ZCH06DWE",
                    "date":1579478400000,
                    "predicted_days_to_failure":4.0
                }
                ...
            ]
        }
        ```
    """
    reqBody = json.loads(request.body.decode())
    file_name = reqBody.get('file_name', None)
    model_name = reqBody.get('model_name', None)

    model = load_model(os.path.join(settings.MEDIA_ROOT, model_name))
    res:pd.DataFrame = predict_failure_days(model, os.path.join(settings.MEDIA_ROOT, file_name))
    return JsonResponse({'code': 0, 'msg': 'success', 'data': res.to_json(orient='records')})

# 以下为判断是否故障的代码
class CustomStackingClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, base_models, meta_model):
        self.base_models = base_models
        self.meta_model = meta_model

    def fit(self, X, y):
        self.base_models_ = [clone(model) for model in self.base_models]
        self.meta_model_ = clone(self.meta_model)
        for model in self.base_models_:
            model.fit(X, y)
        meta_features = self.predict_meta_features(X)
        self.meta_model_.fit(meta_features, y)
        return self

    def predict_meta_features(self, X):
        meta_features = np.column_stack([model.predict(X) for model in self.base_models_])
        return meta_features

    def predict(self, X):
        meta_features = self.predict_meta_features(X)
        return self.meta_model_.predict(meta_features)

def process_detect_model(df_data, model, features):
    print(f"Processing model: {model}")
    
    df_data_model = df_data[df_data['model'] == model]
    
    if df_data_model.empty:
        print(f"No data for model: {model}")
        return None
    
    features_specified = ["smart_{0}_raw".format(feature) for feature in features]
    X_data = df_data_model[features_specified]
    Y_data = df_data_model['failure']

    imputer = SimpleImputer(strategy='mean')
    X_data = imputer.fit_transform(X_data)

    X_train, X_test, Y_train, Y_test = train_test_split(X_data, Y_data, test_size=0.2, random_state=0)
    
    print("valid hdds in train set:", len(Y_train) - np.sum(Y_train.values))
    print("failed hdds in train set:", np.sum(Y_train.values))
    print("valid hdds in test set:", len(Y_test) - np.sum(Y_test.values))
    print("failed hdds in test set:", np.sum(Y_test.values))
    
    xgb_model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    rf_model = RandomForestClassifier()

    param_grid_xgb = {
        'n_estimators': [100, 200],
        'max_depth': [3, 6, 9],
        'learning_rate': [0.01, 0.1, 0.2]
    }
    
    param_grid_rf = {
        'n_estimators': [100, 200],
        'max_depth': [10, 20, 30],
        'min_samples_split': [2, 5, 10]
    }

    grid_search_xgb = GridSearchCV(estimator=xgb_model, param_grid=param_grid_xgb, scoring='roc_auc', cv=3)
    grid_search_xgb.fit(X_train, Y_train)
    
    grid_search_rf = GridSearchCV(estimator=rf_model, param_grid=param_grid_rf, scoring='roc_auc', cv=3)
    grid_search_rf.fit(X_train, Y_train)
    
    best_xgb_model = grid_search_xgb.best_estimator_
    best_rf_model = grid_search_rf.best_estimator_
    
    print(f"Best parameters found for XGBoost: {grid_search_xgb.best_params_}")
    print(f"Best parameters found for RandomForest: {grid_search_rf.best_params_}")

    base_models = [best_xgb_model, best_rf_model]
    meta_model = LogisticRegression()
    stack_model = CustomStackingClassifier(base_models=base_models, meta_model=meta_model)
    stack_model.fit(X_train, Y_train)

    with open(os.path.join(settings.MEDIA_ROOT,f'stack_model_{model}.pkl'), 'wb') as f:
        pickle.dump(stack_model, f)
    with open(os.path.join(settings.MEDIA_ROOT,f'imputer_{model}.pkl'), 'wb') as f:
        pickle.dump(imputer, f)
    return f'stack_model_{model}.pkl', f'imputer_{model}.pkl'

@csrf_exempt
def train_fault_detect(request):
    """_summary_

    Args:
        request (_type_): 
        ```json
        {
            "file_name": "dataset_2020.csv"
        }
        ```

    Returns:
        ```json
        {
            "code": 0,
            "msg": "success",
            "data": {
                "model":[
                    "ST12000NM0007"
                ]
            }
        }
    """
    reqBody = json.loads(request.body.decode())
    file_name = reqBody.get('file_name', None)
    df_data = pd.read_csv(os.path.join(settings.MEDIA_ROOT, file_name))
    top_1_models = df_data['model'].value_counts().index[:1]
    features = [5, 9, 187, 188, 193, 194, 197, 198, 241, 242]
    res = []
    for model in top_1_models:
        sname, iname = process_detect_model(df_data, model, features)
        res.append({'model': model, 'stack_file_name': sname, 'imputer_file_name': iname})
    return JsonResponse({'code': 0, 'msg': 'success', 'data': res})


def load_imputer(model):
    with open(os.path.join(settings.MEDIA_ROOT, f'imputer_{model}.pkl'), 'rb') as f:
        return pickle.load(f)

def detect_load_model(model):
    with open(os.path.join(settings.MEDIA_ROOT,f'stack_model_{model}.pkl'), 'rb') as f:
        return pickle.load(f)

def evaluate_model(df_test_model, features_specified, model):
    X_test = df_test_model[features_specified]
    Y_test = df_test_model['failure']

    imputer = load_imputer(model)
    X_test = imputer.transform(X_test)

    stack_model = detect_load_model(model)
    Y_pred = stack_model.predict(X_test)

    acc = accuracy_score(Y_test, Y_pred)
    prec = precision_score(Y_test, Y_pred)
    rec = recall_score(Y_test, Y_pred)
    f1 = f1_score(Y_test, Y_pred)
    roc_auc = roc_auc_score(Y_test, Y_pred)
    
    print(f"Model: {model}")
    print(f"The accuracy is {acc}")
    print(f"The precision is {prec}")
    print(f"The recall is {rec}")
    print(f"The F1-Score is {f1}")
    print(f"The ROC AUC Score is {roc_auc}")
    print("\n")
    
    return pd.DataFrame({'model': model, 'actual': Y_test, 'predicted': Y_pred})

def process_test_data(test_data_path) -> pd.DataFrame:
    test_data = pd.read_csv(test_data_path)
    top_1_models = test_data['model'].value_counts().index[:1]
    features = [5, 9, 187, 188, 193, 194, 197, 198, 241, 242]
    results = []

    for model in top_1_models:
        print(f"Processing model: {model}")
        df_test_model = test_data[test_data['model'] == model]
        
        if df_test_model.empty:
            print(f"No data for model: {model}")
            continue

        features_specified = ["smart_{0}_raw".format(feature) for feature in features]
        result = evaluate_model(df_test_model, features_specified, model)
        results.append(result)

    results_df = pd.concat(results, ignore_index=True)
    return results_df

@csrf_exempt
def fault_detect(request):
    """_summary_

    Args:
        request (_type_): HTTP请求
        ```json
        {
            "file_name": "test1.csv",
        }
        ```
    
    Returns:
        ```json
        {
            "code": 0,
            "msg": "success",
            "data": [
                ["ST12000NM0007",1,1],
                ["ST12000NM0007",1,0],
                ...
            ]
        }
        ```
    """
    reqBody = json.loads(request.body.decode())
    file_name = reqBody.get('file_name', None)
    
    res = process_test_data(os.path.join(settings.MEDIA_ROOT,file_name))
    return JsonResponse({'code': 0, 'msg': 'success', 'data': res.to_json(orient='values')})
