import streamlit as st
import read_data 
from PIL import Image
from read_pandas import read_my_csv, make_plot, seconds_to_mmss


st.write("# EKG APP")
st.write("## Versuchsperson auswählen")

# Session State wird leer angelegt, solange er noch nicht existiert
if 'current_user' not in st.session_state:
    st.session_state.current_user = 'None'


st.write("Der Name ist: ", st.session_state.current_user) 


# Legen Sie eine neue Liste mit den Personennamen an indem Sie ihre Funktionen aufrufen
person_data = read_data.load_person_data()
person_list = read_data.get_person_list()

# Nutzen Sie ihre neue Liste anstelle der hard-gecodeten Lösung
col1, col2 = st.columns(2)
with col1:
    st.session_state.current_user = st.selectbox(
        'Versuchsperson',
        options = person_list, key="sbVersuchsperson")

# Anlegen des Session State. Bild, wenn es kein Bild gibt
if 'picture_path' not in st.session_state:
        st.session_state.picture_path = 'data/pictures/none.jpg'

# Suche den Pfad zum Bild, aber nur wenn der Name bekannt ist
if st.session_state.current_user in person_list:
        st.session_state.picture_path = read_data.find_person_data_by_name(st.session_state.current_user)["picture_path"]

# Öffne das Bild und Zeige es an
with col2: 
    image = Image.open(st.session_state.picture_path)
    st.image(image, caption=st.session_state.current_user)




st.title("Training Session Overview")
st.write("This plot shows your **Power Output** and **Heart Rate** over time.")

# Input max HR
max_hr = st.number_input("Gib deine maximale Herzfrequenz (max HR) ein:", min_value=100, max_value=220, value=190)

# Read data
df = read_my_csv()

# Create plot with max_hr for zones
fig, df_plot = make_plot(df, max_hr)

# Display plot
st.plotly_chart(fig, use_container_width=True)

# Show raw data if checked
if st.checkbox("Show raw data"):
    st.dataframe(df.head(2000))

# Show stats below plot
st.write(f"Mittelwert der Leistung: {df['PowerOriginal'].mean():.2f} W")
st.write(f"Maximalwert der Leistung: {df['PowerOriginal'].max():.2f} W")

# Calculate and display time spent in zones and average power per zone
time_per_zone = df_plot["HR_Zone"].value_counts().sort_index()
time_per_zone_mmss = time_per_zone.apply(seconds_to_mmss)

power_per_zone = df_plot.groupby("HR_Zone")["PowerOriginal"].mean()





st.write("Zeit in den HR-Zonen (mm:ss):")
st.write(time_per_zone_mmss)

st.write("Durchschnittliche Leistung pro HR-Zone (W):")
st.write(power_per_zone)


