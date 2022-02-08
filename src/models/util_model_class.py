from dataclasses import dataclass
from typing import Union

import pandas as pd
from xgboost.sklearn import XGBClassifier
from sklearn.linear_model import LogisticRegression


@dataclass(frozen=True)
class ModelClass:
    model: Union[XGBClassifier, LogisticRegression]
    probability_threshold_selected: float
    predicted_default_status: pd.Series
    trueStatus_probabilityDefault_threshStatus_loanAmount_df: pd.DataFrame
    prediction_probability_df: pd.DataFrame
