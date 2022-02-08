import streamlit as st
import matplotlib.pyplot as plt


def download_importance_gbt(fig1, barxsize, barysize):
    if st.button(
        "Download Feature Importance Plot as png (Gradient Boosted Tree)"
    ):
        dpisize = max(barxsize, barysize)
        plt.savefig("bar.png", dpi=dpisize * 96, bbox_inches="tight")
        fig1.set_size_inches(barxsize, barysize)


def download_tree_gbt(treexsize, treeysize):
    if st.button("Download XGBoost Decision Tree Plot as png (Gradient Boosted Tree)"):
        dpisize = max(treexsize, treeysize)
        plt.savefig("tree.png", dpi=dpisize * 96, bbox_inches="tight")
