import pandas as pd
import numpy as np
import seaborn as sns
import scipy.stats as stats

import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn import preprocessing
from sklearn.linear_model import LinearRegression, LassoCV, RidgeCV
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt

def std_scale(x):
    scaler = preprocessing.StandardScaler()
    x_scaled = scaler.fit_transform(x)
    return x_scaled

def minmax_scale(x):
    min_max_scaler = preprocessing.MinMaxScaler()
    x_minmax = min_max_scaler.fit_transform(x)
    return x_minmax

def quantile(x):
    x = minmax_scale(x)
    quantile_transformer = preprocessing.QuantileTransformer(output_distribution='normal')
    x_quantile = quantile_transformer.fit_transform(x)
    return x_quantile

def yeo(x):
    x = minmax_scale(x)
    pt = preprocessing.PowerTransformer(method='yeo-johnson', standardize=True)
    x_yeo = pt.fit_transform(x)
    return x_yeo

def diagnostic_plot(x, y):
    y = y.to_numpy()
    rows = len(x.columns)
    plt.figure(figsize=(20, 5*rows))
    for i, c in enumerate(x.columns):
        x_col = x[c].to_numpy().reshape(-1,1)

        rgr = LinearRegression()
        rgr.fit(x_col,y)
        pred = rgr.predict(x_col)

        plt.subplot(rows, 3, (3*i)+1)
        plt.scatter(x_col,y)
        plt.plot(x_col, pred, color='blue',linewidth=1)
        plt.title(f"{c}: Regression fit")
        plt.xlabel("x")
        plt.ylabel("y")

        plt.subplot(rows, 3, (3*i)+2)
        res = y - pred
        plt.scatter(pred, res)
        plt.title(f"{c}: Residual plot")
        plt.xlabel("prediction")
        plt.ylabel("residuals")

        plt.subplot(rows, 3, (3*i)+3)
        #Generates a probability plot of sample data against the quantiles of a
        # specified theoretical distribution
        stats.probplot(res, dist="norm", plot=plt)
        plt.title(f"{c}: Normal Q-Q plot")

def split_and_validate(X, y, cols=None):
    '''
    For a set of features and target X, y, perform a 80/20 train/val split,
    fit and validate a linear regression model, and report results
    '''

    if ~isinstance(X, pd.core.frame.DataFrame):
        X = pd.DataFrame(X, columns=cols)

    # perform train/val split
    X_train, X_val, y_train, y_val = \
        train_test_split(X, y, test_size=0.2, random_state=42)

    # fit linear regression to training data
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)

    # score fit model on validation data
    val_score = lr_model.score(X_val, y_val)

    # report results
    print('\nValidation R^2 score was:', val_score)
    print('Feature coefficient results: \n')
    for feature, coef in zip(X.columns, lr_model.coef_):
        print(f'{feature} : {coef:.2f}')
    return val_score

def calc_mae(y_true, y_pred):
    return np.mean(np.abs(y_pred - y_true))

def kfold_val(X, y, splits=5, rand=42):
    lr = LinearRegression()
    kf = KFold(n_splits=splits, shuffle=True, random_state = rand)
    scores = cross_val_score(lr, X, y, cv=kf, scoring='r2')
    mean_r2 = np.mean(scores)
    var = f'Simple mean cv r^2: {mean_r2:.3f} +- {np.std(scores):.3f}'
    return (mean_r2, scores, var)

def lasso_cv(X, y, alphas=200):
    alphavec = 10**np.linspace(-2,2,alphas)
    model = LassoCV(alphas = alphavec, cv=5)
    model.fit(X, y)
    pred = model.predict(X)
    r2 = r2_score(y, pred)
    mae = calc_mae(y, pred)
    coeffs = list(zip(X.columns, model.coef_))
    return (r2, mae, coeffs)

def ridge_cv(X, y, alphas=200):
    alphavec = 10**np.linspace(-2,2,alphas)
    model = RidgeCV(alphas = alphavec, cv=5)
    model.fit(X, y)
    pred = model.predict(X)
    r2 = r2_score(y, pred)
    mae = calc_mae(y, pred)
    coeffs = list(zip(X.columns, model.coef_))
    return (r2, mae, coeffs)

def drop_infl(X, y, cv_score, lasso_score, ridge_score, threshold = -0.5, \
                models=['cv', 'lasso', 'ridge']):

    cv_score = cv_score.round(6)
    lasso_score = lasso_score.round(6)
    ridge_score = ridge_score.round(6)
    print(f'Current number of features: {len(X.columns)}')


    for c in X.columns:
        deltas = ['','','']
        X_drop = X.drop(columns=c)
        if 'cv' in models:
            drop_score_cv = kfold_val(X_drop, y)[0].round(6)
            deltas[0] = (drop_score_cv - cv_score).round(6)

        if 'lasso' in models:
            drop_score_lasso = lasso_cv(X_drop, y, 40)[0].round(6)
            deltas[1] = (drop_score_lasso - lasso_score).round(6)

        if 'ridge' in models:
            drop_score_ridge = ridge_cv(X_drop, y, 40)[0].round(6)
            deltas[2] = (drop_score_ridge - ridge_score).round(6)


        delta_mean = np.mean([d for d in deltas if d != '']).round(6)
        if delta_mean > threshold:
            print(f'Drop {c} -> CV: {deltas[0]}, L: {deltas[1]}, R: {deltas[2]}, mean: {delta_mean}')

def add_infl(df, y, cv_score, lasso_score, ridge_score, x_dropped, \
            threshold = 0.1, models=['cv', 'lasso', 'ridge']):

    cv_score = cv_score.round(6)
    lasso_score = lasso_score.round(6)
    ridge_score = ridge_score.round(6)
    for a in x_dropped:
        deltas = ['','','']
        x_drop = x_dropped[:]
        x_drop.remove(a)
        X_add = df.drop(columns=['achievement', *x_drop])
        if 'cv' in models:
            add_score_cv = kfold_val(X_add, y)[0].round(6)
            deltas[0] = (add_score_cv - cv_score).round(6)

        if 'lasso' in models:
            add_score_lasso = lasso_cv(X_add, y, 40)[0].round(6)
            deltas[1] = (add_score_lasso - lasso_score).round(6)

        if 'ridge' in models:
            add_score_ridge = ridge_cv(X_add, y, 40)[0].round(6)
            deltas[2] = (add_score_ridge - ridge_score).round(6)

        delta_mean = np.mean([d for d in deltas if d !='']).round(6)
        if delta_mean > threshold:
            print(f'Add {a} -> CV: {deltas[0]}, L: {deltas[1]}, R: {deltas[2]}, mean: {delta_mean}')
