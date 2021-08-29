import streamlit as st

EOL = "Estimates of Location"
EOV = "Estimates of Variability"
DIST = "Exploring the Data Distribution"
THEO = "Central Limit"
TEST = "Statistical Test (Intro)"

if __name__ == '__main__':
    section = st.sidebar.radio("Section", [EOL, EOV, DIST, THEO, TEST])

    if section == EOL:
        from estimates_of_location import render
    elif section == EOV:
        from estimates_of_variability import render
    elif section == DIST:
        from data_distribution import render
    elif section == THEO:
        from theorem import render
    elif section == TEST:
        from pair import render

    render()
