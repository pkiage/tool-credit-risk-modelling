import plotly.express as px


def plot_logistic_coeff_barh(df):
    fig = px.bar(data_frame=df, x="Value",
                 y="Coefficient", orientation="h")

    fig.update_layout(
        title="Logistic Regression Coefficients",
        xaxis_title="Value",
        yaxis_title="Coefficient",)
    return fig
