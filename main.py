import streamlit as st

EOL = "Estimates of Location"
EOV = "Estimates of Variability"

if __name__ == '__main__':
    section = st.sidebar.radio("Section", [EOL, EOV])

    if section == EOL:
        from estimates_of_location import render
    elif section == EOV:
        from estimates_of_variability import render

    render()
