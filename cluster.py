from bq import run_sql

import streamlit as st
import pydeck as pdk


@st.cache(allow_output_mutation=True)
def get_map_points():
    df = run_sql("""
  select centroid_id, lon,lat FRom ml.predict(model `analytics-bootcamp-323516.week1.geo_clusters`,
  (select pickup_longitude lon, pickup_latitude  lat
from `analytics-bootcamp-323516.week1.trips_2015` TABLESAMPLE SYSTEM(1 PERCENT)
LIMIT
  10000))
    """)

    color_lookup = pdk.data_utils.assign_random_colors(df.centroid_id)
    # st.write(color_lookup.get(str(1)))
    df['color'] = df.centroid_id.apply(lambda row: color_lookup.get(str(row)))

    return df


def render():
    points = get_map_points()

    st.dataframe(points.head())
    # st.map(data=points, hue="centroid_id")

    # fig = sns.scatterplot(data=points, x="lon", y="lat", hue="centroid_id")

    st.pydeck_chart(
        pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9', initial_view_state=pdk.ViewState(
                latitude=40.04699,
                longitude=-72.69647,
                zoom=11,
                pitch=10,
            ), layers=[

                pdk.Layer(
                    'ScatterplotLayer',
                    data=points,
                    get_position='[lon, lat]',
                    get_fill_color='color',
                    get_line_color='[0, 0, 0]',
                    get_radius=st.slider("Pickup Points Size", 50, 100, 50, 5),
                ),
            ],
        ), use_container_width=True
    )
