from typing import Union
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_score
import streamlit as st
import numpy as np
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
)
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
from xgboost.sklearn import XGBClassifier
from  features.util_build_features import SplitDataset
"""from  models.model_utils import (
    create_cross_validation_df,
    cross_validation_scores,
    get_df_trueStatus_probabilityDefault_threshStatus_loanAmount,
)"""
from  visualization.graphs_test import (
    cross_validation_graph,
)


def make_tests_view(
    model_name_short: str,
    model_name_generic: str,
):
    def view(
        clf_xgbt_model: Union[XGBClassifier, LogisticRegression],
        split_dataset: SplitDataset,
        currency: str,
        prob_thresh_selected,
        predicted_default_status,
    ):
        st.header(f"Model Evaluation - {model_name_generic}")

        st.subheader("Cross Validation")

        st.write("Shows how our model will perform as new loans come in.")
        st.write(
            "If evaluation metric for test and train set improve as models \
            train on each fold suggests performance will be stable."
        )

        st.write(f'{model_name_short} cross validation test:')

        stcol_seed, stcol_eval_metric = st.columns(2)

        with stcol_seed:
            cv_seed = int(
                st.number_input(
                    label="Random State Seed for Cross Validation:",
                    value=123235,
                    key=f"cv_seed_{model_name_short}",
                )
            )

        with stcol_eval_metric:
            eval_metric = st.selectbox(
                label="Select evaluation metric",
                options=[
                    "auc",
                    "aucpr",
                    "rmse",
                    "mae",
                    "logloss",
                    "error",
                    "merror",
                    "mlogloss",
                ],
                key=f"eval_metric_{model_name_short}",
            )

        stcol_trees, stcol_eval_nfold, stcol_earlystoppingrounds = st.columns(
            3
        )

        with stcol_trees:
            trees = int(
                st.number_input(
                    label="Number of trees",
                    value=5,
                    key=f"trees_{model_name_short}",
                )
            )

        with stcol_eval_nfold:
            nfolds = int(
                st.number_input(
                    label="Number of folds",
                    value=5,
                    key=f"nfolds_{model_name_short}",
                )
            )

        with stcol_earlystoppingrounds:
            early_stopping_rounds = int(
                st.number_input(
                    label="Early stopping rounds",
                    value=10,
                    key=f"early_stopping_rounds_{model_name_short}",
                )
            )

        DTrain, cv_df = create_cross_validation_df(
            split_dataset.X_test,
            split_dataset.y_test,
            eval_metric,
            cv_seed,
            trees,
            nfolds,
            early_stopping_rounds,
        )

        st.write(cv_df)

        scoring_options = [
            "roc_auc",
            "accuracy",
            "precision",
            "recall",
            "f1",
            "jaccard",
        ]

        overfit_test = st.radio(
            label="Overfit test:",
            options=("No", "Yes"),
            key=f"overfit_test_{model_name_short}",
        )

        if overfit_test == "Yes":
            st.write("Overfit test:")
            iterations = int(
                st.number_input(
                    label="Number of folds (iterations)",
                    value=500,
                    key=f"iterations_{model_name_short}",
                )
            )

            DTrain, cv_df_it = create_cross_validation_df(
                split_dataset.X_test,
                split_dataset.y_test,
                eval_metric,
                cv_seed,
                iterations,
                nfolds,
                iterations,
            )

            fig_it = cross_validation_graph(cv_df_it, eval_metric, iterations)
            st.pyplot(fig_it)

        st.write("Sklearn cross validation test:")
        stcol_scoringmetric, st_nfold = st.columns(2)

        with stcol_scoringmetric:
            score_metric = st.selectbox(
                label="Select score",
                options=scoring_options,
                key=f"stcol_scoringmetric_{model_name_short}",
            )

        with st_nfold:
            nfolds_score = int(
                st.number_input(
                    label="Number of folds",
                    value=5,
                    key=f"st_nfold_{model_name_short}",
                )
            )

        cv_scores = cross_validation_scores(
            clf_xgbt_model,
            split_dataset.X_test,
            split_dataset.y_test,
            nfolds_score,
            score_metric,
            cv_seed,
        )

        stcol_vals, stcol_mean, st_std = st.columns(3)

        with stcol_vals:
            st.markdown(f"{score_metric} scores:")
            st.write(
                pd.DataFrame(
                    cv_scores,
                    columns=[score_metric],
                )
            )

        with stcol_mean:
            st.metric(
                label=f"Average {score_metric} score ",
                value="{:.4f}".format(cv_scores.mean()),
                delta=None,
                delta_color="normal",
            )

        with st_std:
            st.metric(
                label=f"{score_metric} standard deviation (+/-)",
                value="{:.4f}".format(cv_scores.std()),
                delta=None,
                delta_color="normal",
            )

        st.subheader("Classification Report")

        target_names = ["Non-Default", "Default"]

        classification_report_dict = classification_report(
            split_dataset.y_test,
            predicted_default_status,
            target_names=target_names,
            output_dict=True,
        )

        (
            stcol_defaultpres,
            stcol_defaultrecall,
            stcol_defaultf1score,
            stcol_f1score,
        ) = st.columns(4)
        with stcol_defaultpres:
            st.metric(
                label="Default Precision",
                value="{:.0%}".format(
                    classification_report_dict["Default"]["precision"]
                ),
                delta=None,
                delta_color="normal",
            )

        with stcol_defaultrecall:
            st.metric(
                label="Default Recall",
                value="{:.0%}".format(
                    classification_report_dict["Default"]["recall"]
                ),
                delta=None,
                delta_color="normal",
            )

        with stcol_defaultf1score:
            st.metric(
                label="Default F1 Score",
                value="{:.2f}".format(
                    classification_report_dict["Default"]["f1-score"]
                ),
                delta=None,
                delta_color="normal",
            )

        with stcol_f1score:
            st.metric(
                label="Macro avg F1 Score (Model F1 Score):",
                value="{:.2f}".format(
                    classification_report_dict["macro avg"]["f1-score"]
                ),
                delta=None,
                delta_color="normal",
            )

        with st.expander("Classification Report Dictionary:"):
            st.write(classification_report_dict)

        st.markdown(
            f'Default precision: {"{:.0%}".format(classification_report_dict["Default"]["precision"])} of loans predicted as default were actually default.'
        )

        st.markdown(
            f'Default recall: {"{:.0%}".format(classification_report_dict["Default"]["recall"])} of true defaults predicted correctly.'
        )

        f1_gap = 1 - classification_report_dict["Default"]["f1-score"]
        st.markdown(
            f'Default F1 score: {"{:.2f}".format(classification_report_dict["Default"]["f1-score"])}\
                is {"{:.2f}".format(f1_gap)} away from perfect precision and recall (no false positive rate).'
        )

        st.markdown(
            f'macro avg F1 score: {"{:.2f}".format(classification_report_dict["macro avg"]["f1-score"])} is the models F1 score.'
        )

        st.subheader("Confusion Matrix")
        confuctiomatrix_dict = confusion_matrix(
            split_dataset.y_test, predicted_default_status
        )

        tn, fp, fn, tp = confusion_matrix(
            split_dataset.y_test, predicted_default_status
        ).ravel()

        with st.expander(
            "Confusion matrix (column name = classification model prediction, row name = true status, values = number of loans"
        ):
            st.write(confuctiomatrix_dict)

        st.markdown(
            f'{tp} ,\
            {"{:.0%}".format(tp / len(predicted_default_status))} \
                true positives (defaults correctly predicted as defaults).'
        )

        st.markdown(
            f'{fp} ,\
            {"{:.0%}".format(fp / len(predicted_default_status))} \
                false positives (non-defaults incorrectly predicted as defaults).'
        )

        st.markdown(
            f'{fn} ,\
            {"{:.0%}".format(fn / len(predicted_default_status))} \
                false negatives (defaults incorrectly predicted as non-defaults).'
        )

        st.markdown(
            f'{tn} ,\
            {"{:.0%}".format(tn / len(predicted_default_status))} \
                true negatives (non-defaults correctly predicted as non-defaults).'
        )

        st.subheader("Bad Rate")

        df_trueStatus_probabilityDefault_threshStatus_loanAmount = (
            get_df_trueStatus_probabilityDefault_threshStatus_loanAmount(
                clf_xgbt_model,
                split_dataset.X_test,
                split_dataset.y_test,
                prob_thresh_selected,
                "loan_amnt",
            )
        )

        with st.expander(
            "Loan Status, Probability of Default, & Loan Amount DataFrame"
        ):
            st.write(df_trueStatus_probabilityDefault_threshStatus_loanAmount)

        accepted_loans = (
            df_trueStatus_probabilityDefault_threshStatus_loanAmount[
                df_trueStatus_probabilityDefault_threshStatus_loanAmount[
                    "PREDICT_DEFAULT_STATUS"
                ]
                == 0
            ]
        )

        bad_rate = (
            np.sum(accepted_loans["loan_status"])
            / accepted_loans["loan_status"].count()
        )

        with st.expander("Loan Amount Summary Statistics"):
            st.write(
                df_trueStatus_probabilityDefault_threshStatus_loanAmount[
                    "loan_amnt"
                ].describe()
            )

        avg_loan = np.mean(
            df_trueStatus_probabilityDefault_threshStatus_loanAmount[
                "loan_amnt"
            ]
        )

        crosstab_df = pd.crosstab(
            df_trueStatus_probabilityDefault_threshStatus_loanAmount[
                "loan_status"
            ],  # row label
            df_trueStatus_probabilityDefault_threshStatus_loanAmount[
                "PREDICT_DEFAULT_STATUS"
            ],
        ).apply(
            lambda x: x * avg_loan, axis=0
        )  # column label

        with st.expander(
            "Cross tabulation (column name = classification model prediction, row name = true status, values = number of loans * average loan value"
        ):
            st.write(crosstab_df)

        st.write(
            f'Bad rate: {"{:.2%}".format(bad_rate)} of all the loans the model accepted (classified as non-default) from the test set were actually defaults.'
        )

        st.write(
            f'Estimated value of the bad rate is {currency} {"{:,.2f}".format(crosstab_df[0][1])}.'
        )

        st.write(
            f'Total estimated value of actual non-default loans is {currency} {"{:,.2f}".format(crosstab_df[0][0]+crosstab_df[0][1])}'
        )

        st.write(
            f'Estimated value of loans incorrectly predicted as default is {currency} {"{:,.2f}".format(crosstab_df[1][0])}'
        )

        st.write(
            f'Estimated value of loans correctly predicted as defaults is {currency} {"{:,.2f}".format(crosstab_df[1][1])}'
        )

        return df_trueStatus_probabilityDefault_threshStatus_loanAmount

    return view


def cross_validation_scores(model, X, y, nfold, score, seed):
    # return cv scores of metric
    return cross_val_score(
        model,
        np.ascontiguousarray(X),
        np.ravel(np.ascontiguousarray(y)),
        cv=StratifiedKFold(n_splits=nfold, shuffle=True, random_state=seed),
        scoring=score,
    )


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
