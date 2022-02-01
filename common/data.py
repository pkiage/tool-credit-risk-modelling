from typing import List, Union, cast
from dataclasses import dataclass
from sklearn.model_selection import train_test_split
import pandas as pd

from common.util import drop_columns


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
