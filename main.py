import streamlit as st

EOL = "Estimates of Location"
EOV = "Estimates of Variability"
DIST = "Exploring the Data Distribution"
THEO = "Central Limit"
PERM = "Permutation"
# TEST = "Statistical Test (Intro)"
TS = "Timeseries"
CLUSTER = "Cluster"

if __name__ == '__main__':
    section = st.sidebar.radio("Section", [EOL, EOV, DIST, THEO, PERM, TS,CLUSTER])

    if section == EOL:
        from estimates_of_location import render
    elif section == EOV:
        from estimates_of_variability import render
    elif section == DIST:
        from data_distribution import render
    elif section == THEO:
        from theorem import render
    elif section == PERM:
        from perm import render
    elif section == TS:
        from ts import render
    elif section == CLUSTER:
        from cluster import render

    render()
