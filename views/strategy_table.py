from typing import OrderedDict
import plotly.express as px
import numpy as np
import streamlit as st
from common.util import create_strategyTable_df
from views.typing import ModelView


def strategy_table_view(
    currency: str, model_views: OrderedDict[str, ModelView]
):
    st.header("Strategy Table")

    for (model_name, model_view) in model_views.items():
        st.subheader(model_name)
        strat_df = create_strategyTable_df(
            0.05,
            1,
            20,
            model_view.trueStatus_probabilityDefault_threshStatus_loanAmount_df,
            "loan_status",
            currency,
        )

        columns = strat_df.columns

        with st.expander("Strategy Table:"):
            st.write(strat_df)

        for i in columns:
            strat_df[i] = strat_df[i].astype(np.float64)

        strat_df_boxPlot_data = strat_df.iloc[:, 0:3]

        plot = px.box(data_frame=strat_df_boxPlot_data)

        st.plotly_chart(plot)

        # Plot the strategy curve

        fig1 = px.line(
            strat_df_boxPlot_data,
            x="Acceptance Rate",
            y="Bad Rate",
            title="Acceptance and Bad Rates",
        )

        st.plotly_chart(fig1)

        fig2 = px.line(
            strat_df,
            x="Acceptance Rate",
            y=f"Estimated Value ({currency})",
            title=f"Estimated Value ({currency}) by Acceptance Rate",
        )

        st.plotly_chart(fig2)

        st.write("Row with the greatest estimated value:")

        max_estimated_value = np.max(
            strat_df[f"Estimated Value ({currency})"].astype(np.float64)
        )
        columns = strat_df.columns

        max_estimated_value = np.max(strat_df[f"Estimated Value ({currency})"])

        st.write(
            strat_df.loc[
                strat_df[f"Estimated Value ({currency})"]
                == max_estimated_value
            ]
        )

        loss_given_default = 1
        df_trueStatus_probabilityDefault_threshStatus_loanAmount = (
            model_view.trueStatus_probabilityDefault_threshStatus_loanAmount_df[
                "PROB_DEFAULT"
            ]
            * loss_given_default
            * model_view.trueStatus_probabilityDefault_threshStatus_loanAmount_df[
                "loan_amnt"
            ]
        )

        tot_exp_loss = round(
            np.sum(df_trueStatus_probabilityDefault_threshStatus_loanAmount),
            2,
        )

        st.metric(
            label=f"Total expected loss:",
            value=f"{currency} {tot_exp_loss:,.2f}",
            delta=None,
            delta_color="normal",
        )
