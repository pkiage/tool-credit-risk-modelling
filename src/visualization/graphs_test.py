from matplotlib import pyplot as plt

from sklearn.metrics import roc_curve

from typing import OrderedDict

from  models.util_model_class import ModelClass

from sklearn.calibration import calibration_curve


def cross_validation_graph(cv, eval_metric, trees):

    # Plot the test AUC scores for each iteration
    fig = plt.figure()
    plt.plot(cv[cv.columns[2]])
    plt.title(
        "Test {eval_metric} Score Over {it_numbr} Iterations".format(
            eval_metric=eval_metric, it_numbr=trees
        )
    )
    plt.xlabel("Iteration Number")
    plt.ylabel("Test {eval_metric} Score".format(eval_metric=eval_metric))
    return fig


def roc_auc_compare_n_models(y, model_views: OrderedDict[str, ModelClass]):
    colors = ["blue", "green"]
    fig = plt.figure()
    for color_idx, (model_name, model_view) in enumerate(model_views.items()):
        fpr, tpr, _thresholds = roc_curve(
            y, model_view.prediction_probability_df
        )
        plt.plot(fpr, tpr, color=colors[color_idx], label=f"{model_name}")
    plt.plot([0, 1], [0, 1], linestyle="--", label="Random Prediction")
    model_names = list(model_views.keys())
    if not model_names:
        model_name_str = "None"
    elif len(model_names) == 1:
        model_name_str = model_names[0]
    else:
        model_name_str = " and ".join(
            [", ".join(model_names[:-1]), model_names[-1]]
        )
    plt.title(f"ROC Chart for {model_name_str} on the Probability of Default")
    plt.xlabel("False Positive Rate (FP Rate)")
    plt.ylabel("True Positive Rate (TP Rate)")
    plt.legend()
    plt.grid(False)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    return fig


def calibration_curve_report_commented_n(
    y, model_views: OrderedDict[str, ModelClass], bins: int
):
    fig = plt.figure()
    for model_name, model_view in model_views.items():
        frac_of_pos, mean_pred_val = calibration_curve(
            y,
            model_view.prediction_probability_df,
            n_bins=bins,
            normalize=True,
        )
        plt.plot(mean_pred_val, frac_of_pos, "s-", label=f"{model_name}")

    # Create the calibration curve plot with the guideline
    plt.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")

    plt.ylabel("Fraction of positives")
    plt.xlabel("Average Predicted Probability")
    plt.title("Calibration Curve")
    plt.legend()
    plt.grid(False)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    return fig
