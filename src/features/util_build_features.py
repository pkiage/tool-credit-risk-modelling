import streamlit as st

from typing import List, Union, cast

from dataclasses import dataclass

from sklearn.model_selection import train_test_split

import pandas as pd


@dataclass
class SplitDataset:
    X_test: pd.DataFrame
    X_train: pd.DataFrame
    y_test: pd.Series
    y_train: pd.Series

    @property
    def X_y_test(self) -> pd.DataFrame:
        return pd.concat(
            cast(
                List[Union[pd.DataFrame, pd.Series]],
                [
                    self.X_test.reset_index(drop=True),
                    self.y_test.reset_index(drop=True),
                ],
            ),
            axis=1,
        )

    @property
    def X_y_train(self) -> pd.DataFrame:
        return pd.concat(
            cast(
                List[Union[pd.DataFrame, pd.Series]],
                [
                    self.X_train.reset_index(drop=True),
                    self.y_train.reset_index(drop=True),
                ],
            ),
            axis=1,
        )


@dataclass
class Dataset:
    df: pd.DataFrame
    random_state: int
    test_size: int

    @property
    def y_value(self) -> pd.DataFrame:
        return self.df["loan_status"]

    @property
    def x_values(self) -> pd.DataFrame:
        return cast(
            pd.DataFrame,
            drop_columns(
                self.df,
                [
                    "loan_status",
                    "loan_grade_A",
                    "loan_grade_B",
                    "loan_grade_C",
                    "loan_grade_D",
                    "loan_grade_E",
                    "loan_grade_F",
                    "loan_grade_G",
                ],
            ),
        )

    @property
    def x_values_column_names(self):
        return self.x_values.columns.tolist()

    def x_values_filtered_columns(self, columns: List[str]) -> pd.DataFrame:
        return self.df.filter(columns)

    def train_test_split(
        self, selected_x_values: pd.DataFrame
    ) -> SplitDataset:
        X_train, X_test, y_train, y_test = train_test_split(
            selected_x_values,
            self.y_value,
            test_size=self.test_size / 100,  # since up was given as pct
            random_state=self.random_state,
        )

        return SplitDataset(
            X_train=cast(pd.DataFrame, X_train),
            X_test=cast(pd.DataFrame, X_test),
            y_train=cast(pd.Series, y_train),
            y_test=cast(pd.Series, y_test),
        )


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


def select_predictors(dataset):
    st.header("Predictors")

    possible_columns = dataset.x_values_column_names

    selected_columns = st.sidebar.multiselect(
        label="Select Predictors",
        options=possible_columns,
        default=possible_columns,
    )
    return dataset.x_values_filtered_columns(selected_columns)


def import_data():
    if "input_data_frame" not in st.session_state:
        st.session_state.input_data_frame = pd.read_csv(
            r"./data/processed/cr_loan_w2.csv"
        )
    if "dataset" not in st.session_state:
        df = cast(pd.DataFrame, st.session_state.input_data_frame)
        dataset = Dataset(
            df=df,
            random_state=123235,
            test_size=40,
        )
        st.session_state.dataset = dataset
    else:
        dataset = st.session_state.dataset

    return dataset
