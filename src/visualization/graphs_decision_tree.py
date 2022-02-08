
import xgboost as xgb

import streamlit as st

import matplotlib.pyplot as plt

from xgboost import plot_tree


def plot_importance_gbt(clf_xgbt_model, barxsize, barysize):
    axobject1 = xgb.plot_importance(clf_xgbt_model, importance_type="weight")
    fig1 = axobject1.figure
    st.write("Feature Importance Plot (Gradient Boosted Tree)")
    fig1.set_size_inches(barxsize, barysize)
    return fig1


def plot_tree_gbt(treexsize, treeysize, clf_xgbt_model):
    plot_tree(clf_xgbt_model)
    fig2 = plt.gcf()
    fig2.set_size_inches(treexsize, treeysize)
    return fig2
