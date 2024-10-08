"""
@author: raquebam
"""
import streamlit as st
from datetime import datetime
import pandas as pd
from libcomcat.search import search, get_event_by_id

def fetch_earthquake_data(starttime, endtime, min_latitude, max_latitude, min_longitude, max_longitude, min_mag, max_mag):
    event_data = []
    try:
        events = search(starttime=starttime, endtime=endtime,
                        maxlatitude=max_latitude, minlatitude=min_latitude,
                        maxlongitude=max_longitude, minlongitude=min_longitude,
                        minmagnitude=min_mag, maxmagnitude=max_mag,
                        producttype='focal-mechanism')

        for event in events:
            try:
                event_details = get_event_by_id(event.id)
                focal_mechanism_products = event_details.getProducts('focal-mechanism')

                if focal_mechanism_products:
                    focal_mechanism_product = focal_mechanism_products[0]

                    product_info = focal_mechanism_product._product
                    properties = product_info.get('properties', {})

                    strike1 = properties.get('nodal-plane-1-strike', 'N/A')
                    dip1 = properties.get('nodal-plane-1-dip', 'N/A')
                    rake1 = properties.get('nodal-plane-1-rake', 'N/A')

                    strike2 = properties.get('nodal-plane-2-strike', 'N/A')
                    dip2 = properties.get('nodal-plane-2-dip', 'N/A')
                    rake2 = properties.get('nodal-plane-2-rake', 'N/A')

                    event_info = {
                        'id': event.id,
                        'time': event.time,
                        'latitude': event.latitude,
                        'longitude': event.longitude,
                        'depth': event.depth,
                        'magnitude': event.magnitude,
                        'strike_1': strike1,
                        'dip_1': dip1,
                        'rake_1': rake1,
                        'strike_2': strike2,
                        'dip_2': dip2,
                        'rake_2': rake2
                    }

                    event_data.append(event_info)
                else:
                    st.write(f"Evento {event.id} no tiene un producto de tipo focal-mechanism")

            except Exception as e:
                st.error(f"Error al procesar evento {event.id}: {str(e)}")

    except Exception as e:
        st.error(f"Error al buscar eventos: {str(e)}")
        
    return event_data

def main():
    st.markdown("## Buscador de planos nodales de sismos usando el 'product type' de <u>mecanismos focales</u> en la página del NEIC", unsafe_allow_html=True)
    st.write("###### Para tensores de momento, visite la página: https://neic-mt.streamlit.app/")
    st.write("#### Parámetros de búsqueda")

    start_date = st.date_input("Fecha de inicio", value=datetime(2001, 9, 17))
    end_date = st.date_input("Fecha de fin", value=datetime(2001, 9, 17))

    min_latitude = st.number_input("Latitud mínima", value=0.0)
    max_latitude = st.number_input("Latitud máxima", value=0.0)
    min_longitude = st.number_input("Longitud mínima", value=-0.0)
    max_longitude = st.number_input("Longitud máxima", value=-0.0)
    min_mag = st.number_input("Magnitud mínima", value=1.0)
    max_mag = st.number_input("Magnitud máxima", value=0.0)

    if 'event_data' not in st.session_state:
        st.session_state.event_data = None

    if 'file_name' not in st.session_state:
        st.session_state.file_name = "sismos_mecanismos_focales"

    if st.button("Buscar", key='search_button'):
        starttime = datetime.combine(start_date, datetime.min.time())
        endtime = datetime.combine(end_date, datetime.max.time())

        st.session_state.event_data = fetch_earthquake_data(starttime, endtime, min_latitude, max_latitude, min_longitude, max_longitude, min_mag, max_mag)

    if st.session_state.event_data:
        events_df = pd.DataFrame(st.session_state.event_data)
        st.write(events_df)

        file_name = st.text_input("Nombre del archivo", value=st.session_state.file_name)

        st.session_state.file_name = file_name

        csv_data = events_df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="Descargar CSV",
            data=csv_data,
            file_name=f"{st.session_state.file_name}.csv",
            mime='text/csv',
            key='download_button'
        )

if __name__ == "__main__":
    main()
