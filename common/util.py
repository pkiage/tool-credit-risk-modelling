# DATA MANIPULATION & ANALYSIS

import pickle
import streamlit as st

# Arrays
import numpy as np

# DataFrames and Series
import pandas as pd

# Returns the indices of the maximum values along an axis
from numpy import argmax

# MODELLING

# Logistic regression
from sklearn.linear_model import LogisticRegression

from sklearn.model_selection import StratifiedKFold

# XGBoosted Decision Trees
import xgboost as xgb


# REPORTING, EVALUATION, AND INTERPRETATION

# Classification report
from sklearn.metrics import classification_report

# Reciever Operator Curve
from sklearn.metrics import roc_curve


# Evaluate a score by cross-validation
from sklearn.model_selection import cross_val_score


# # Functions


def drop_columns(df, columns):
    return df.drop(columns, axis=1)


def remove_less_than_0_columns(df, column):
    df[column].dropna()
    return df.loc[(df[column] != 0).any(1)]


def boolean_int_condition_label(df, label_column_name, condition):
    df[label_column_name] = condition
    y = df[label_column_name].astype(int)
    df = drop_columns(df, label_column_name)
    return y, df


@st.cache(suppress_st_warning=True)
def undersample_training_data(
    df: pd.DataFrame, column_name: str, split_dataset
):
    count_nondefault, count_default = split_dataset.X_y_train[
        column_name
    ].value_counts()

    nondefaults = df[df[column_name] == 0]  # 0

    defaults = df[df[column_name] == 1]

    under_sample = min(count_nondefault, count_default)

    nondefaults_under = nondefaults.sample(under_sample)

    defaults_under = defaults.sample(under_sample)

    X_y_train_under = pd.concat(
        [
            nondefaults_under.reset_index(drop=True),
            defaults_under.reset_index(drop=True),
        ],
        axis=0,
    )

    X_train_under = X_y_train_under.drop([column_name], axis=1)  # remove label

    y_train_under = X_y_train_under[column_name]  # label only

    class_balance_default = X_y_train_under[column_name].value_counts()

    return [
        X_train_under,
        y_train_under,
        X_y_train_under,
        class_balance_default,
    ]


def create_coeffient_feature_dictionary_logistic_model(
    logistic_model, training_data
):
    return {
        feat: coef
        for coef, feat in zip(
            logistic_model.coef_[0, :], training_data.columns
        )
    }


@st.cache(suppress_st_warning=True)
def test_variables_logistic(X_train, y_train):
    # Create and fit the logistic regression model
    return LogisticRegression(solver="lbfgs").fit(X_train, np.ravel(y_train))


@st.cache(suppress_st_warning=True)
def print_coeff_logistic(clf_logistic_model, split_dataset):
    # Dictionary of features and their coefficients
    return create_coeffient_feature_dictionary_logistic_model(
        clf_logistic_model, split_dataset.X_train
    )


@st.cache(suppress_st_warning=True, hash_funcs={
    xgb.XGBClassifier: pickle.dumps
})
def test_variables_gbt(X_train, y_train):
    # Using hyperparameters learning_rate and max_depth
    return xgb.XGBClassifier(
        learning_rate=0.1,
        max_depth=7,
        use_label_encoder=False,
        eval_metric="logloss",
    ).fit(X_train, np.ravel(y_train), eval_metric="logloss")


# In[398]:


def get_df_trueStatus_probabilityDefault_threshStatus_loanAmount(
    model, X, y, threshold, loan_amount_col_name
):
    true_status = y.to_frame()

    loan_amount = X[loan_amount_col_name]

    clf_prediction_prob = model.predict_proba(np.ascontiguousarray(X))

    clf_prediction_prob_df = pd.DataFrame(
        clf_prediction_prob[:, 1], columns=["PROB_DEFAULT"]
    )

    clf_thresh_predicted_default_status = (
        clf_prediction_prob_df["PROB_DEFAULT"]
        .apply(lambda x: 1 if x > threshold else 0)
        .rename("PREDICT_DEFAULT_STATUS")
    )

    return pd.concat(
        [
            true_status.reset_index(drop=True),
            clf_prediction_prob_df.reset_index(drop=True),
            clf_thresh_predicted_default_status.reset_index(drop=True),
            loan_amount.reset_index(drop=True),
        ],
        axis=1,
    )


def find_best_threshold_J_statistic(y, clf_prediction_prob_df):
    fpr, tpr, thresholds = roc_curve(y, clf_prediction_prob_df)
    # get the best threshold
    # Youden’s J statistic tpr-fpr
    # Argmax to get the index in
    # thresholds
    return thresholds[argmax(tpr - fpr)]


# In[399]:


# Function that makes dataframe with probability of default, predicted default status based on threshold
# and actual default status


def model_probability_values_df(model, X):
    return pd.DataFrame(model.predict_proba(X)[:, 1], columns=["PROB_DEFAULT"])


def apply_threshold_to_probability_values(probability_values, threshold):
    return (
        probability_values["PROB_DEFAULT"]
        .apply(lambda x: 1 if x > threshold else 0)
        .rename("PREDICT_DEFAULT_STATUS")
    )


@st.cache(suppress_st_warning=True)
def find_best_threshold_J_statistic(y, clf_prediction_prob_df):
    fpr, tpr, thresholds = roc_curve(y, clf_prediction_prob_df)
    # get the best threshold
    J = tpr - fpr  # Youden’s J statistic
    ix = argmax(J)
    return thresholds[ix]


# In[401]:


def create_cross_validation_df(
    X, y, eval_metric, seed, trees, n_folds, early_stopping_rounds
):
    # Test data x and y
    DTrain = xgb.DMatrix(X, label=y)

    # auc or logloss
    params = {
        "eval_metric": eval_metric,
        "objective": "binary:logistic",  # logistic say 0 or 1 for loan status
        "seed": seed,
    }

    # Create the data frame of cross validations
    cv_df = xgb.cv(
        params,
        DTrain,
        num_boost_round=trees,
        nfold=n_folds,
        early_stopping_rounds=early_stopping_rounds,
        shuffle=True,
    )

    return [DTrain, cv_df]


# In[450]:


def cross_validation_scores(model, X, y, nfold, score, seed):
    # return cv scores of metric
    return cross_val_score(
        model,
        np.ascontiguousarray(X),
        np.ravel(np.ascontiguousarray(y)),
        cv=StratifiedKFold(n_splits=nfold, shuffle=True, random_state=seed),
        scoring=score,
    )


def default_status_per_threshold(threshold_list, prob_default):
    threshold_default_status_list = []
    for threshold in threshold_list:
        threshold_default_status = prob_default.apply(
            lambda x: 1 if x > threshold else 0
        )
        threshold_default_status_list.append(threshold_default_status)
    return threshold_default_status_list


def classification_report_per_threshold(
    threshold_list, threshold_default_status_list, y_test
):
    target_names = ["Non-Default", "Default"]
    classification_report_list = []
    for threshold_default_status in threshold_default_status_list:
        thresh_classification_report = classification_report(
            y_test,
            threshold_default_status,
            target_names=target_names,
            output_dict=True,
            zero_division=0,
        )
        classification_report_list.append(thresh_classification_report)
    # Return threshold classification report dict
    return dict(zip(threshold_list, classification_report_list))


def thresh_classification_report_recall_accuracy(
    thresh_classification_report_dict,
):
    thresh_def_recalls_list = []
    thresh_nondef_recalls_list = []
    thresh_accs_list = []
    for x in [*thresh_classification_report_dict]:
        thresh_def_recall = thresh_classification_report_dict[x]["Default"][
            "recall"
        ]
        thresh_def_recalls_list.append(thresh_def_recall)
        thresh_nondef_recall = thresh_classification_report_dict[x][
            "Non-Default"
        ]["recall"]
        thresh_nondef_recalls_list.append(thresh_nondef_recall)
        thresh_accs = thresh_classification_report_dict[x]["accuracy"]
        thresh_accs_list.append(thresh_accs)
    return [
        thresh_def_recalls_list,
        thresh_nondef_recalls_list,
        thresh_accs_list,
    ]


def create_accept_rate_list(start, end, samples):
    return np.linspace(start, end, samples, endpoint=True)


def create_strategyTable_df(
    start, end, samples, actual_probability_predicted_acc_rate, true, currency
):
    accept_rates = create_accept_rate_list(start, end, samples)
    thresholds_strat = []
    bad_rates_start = []
    Avg_Loan_Amnt = actual_probability_predicted_acc_rate[true].mean()
    num_accepted_loans_start = []

    for rate in accept_rates:
        # Calculate the threshold for the acceptance rate
        thresh = np.quantile(
            actual_probability_predicted_acc_rate["PROB_DEFAULT"], rate
        ).round(3)
        # Add the threshold value to the list of thresholds
        thresholds_strat.append(
            np.quantile(
                actual_probability_predicted_acc_rate["PROB_DEFAULT"], rate
            ).round(3)
        )

        # Reassign the loan_status value using the threshold
        actual_probability_predicted_acc_rate[
            "PREDICT_DEFAULT_STATUS"
        ] = actual_probability_predicted_acc_rate["PROB_DEFAULT"].apply(
            lambda x: 1 if x > thresh else 0
        )

        # Create a set of accepted loans using this acceptance rate
        accepted_loans = actual_probability_predicted_acc_rate[
            actual_probability_predicted_acc_rate["PREDICT_DEFAULT_STATUS"]
            == 0
        ]
        # Calculate and append the bad rate using the acceptance rate
        bad_rates_start.append(
            np.sum((accepted_loans[true]) / len(accepted_loans[true])).round(3)
        )
        # Accepted loans
        num_accepted_loans_start.append(len(accepted_loans))

    # Calculate estimated value
    money_accepted_loans = [
        accepted_loans * Avg_Loan_Amnt
        for accepted_loans in num_accepted_loans_start
    ]

    money_bad_accepted_loans = [
        2 * money_accepted_loan * bad_rate
        for money_accepted_loan, bad_rate in zip(
            money_accepted_loans, bad_rates_start
        )
    ]

    zip_object = zip(money_accepted_loans, money_bad_accepted_loans)
    estimated_value = [
        money_accepted_loan - money_bad_accepted_loan
        for money_accepted_loan, money_bad_accepted_loan in zip_object
    ]

    accept_rates = ["{:.2f}".format(elem) for elem in accept_rates]

    thresholds_strat = ["{:.2f}".format(elem) for elem in thresholds_strat]

    bad_rates_start = ["{:.2f}".format(elem) for elem in bad_rates_start]

    estimated_value = ["{:.2f}".format(elem) for elem in estimated_value]

    return (
        pd.DataFrame(
            zip(
                accept_rates,
                thresholds_strat,
                bad_rates_start,
                num_accepted_loans_start,
                estimated_value,
            ),
            columns=[
                "Acceptance Rate",
                "Threshold",
                "Bad Rate",
                "Num Accepted Loans",
                f"Estimated Value ({currency})",
            ],
        )
        .sort_values(by="Acceptance Rate", axis=0, ascending=False)
        .reset_index(drop=True)
    )
