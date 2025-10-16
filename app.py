import streamlit as st
import pandas as pd
import pymysql

#  Database Connection 
def create_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='1234',
            database='police_db',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

#  Fetch Data From Database 
def fetch_data(query):
    connection = create_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                df = pd.DataFrame(result)
                return df
        finally:
            connection.close()
    else:
        return pd.DataFrame()

#  Load all data for Input Form prediction 
def load_all_data():
    query = "SELECT * FROM police_logs;"
    return fetch_data(query)

#  Streamlit Setup 
st.set_page_config(page_title="Securecheck Police Dashboard", layout="wide")

#  Sidebar Menu 
st.sidebar.markdown('<p style="font-size:24px; font-weight:700; color:#2E86C1;">Menu</p>', unsafe_allow_html=True)
menu = st.sidebar.radio('Select Menu', ['Insight', 'Input Form'], label_visibility="collapsed")

#  INSIGHT SECTION 
if menu == 'Insight':
    st.header("🚦 Data Insights")

    #  Question categories 
    questions = {
        "Vehicle-Based": [
            "What are the top 10 vehicle_Number involved in drug-related stops?",
            "Which vehicles were most frequently searched?"
        ],
        "Demographic-Based": [
            "Which driver age group had the highest arrest rate?",
            "What is the gender distribution of drivers stopped in each country?",
            "Which race and gender combination has the highest search rate?"
        ],
        "Time & Duration Based": [
            "What time of day sees the most traffic stops?",
            "What is the average stop duration for different violations?",
            "Are stops during the night more likely to lead to arrests?"
        ],
        "Violation-Based": [
            "Which violations are most associated with searches or arrests?",
            "Which violations are most common among younger drivers (<25)?",
            "Is there a violation that rarely results in search or arrest?"
        ],
        "Location-Based": [
            "Which countries report the highest rate of drug-related stops?",
            "What is the arrest rate by country and violation?",
            "Which country has the most stops with search conducted?"
        ],
        "Complex": [
            "Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)",
            "Driver Violation Trends Based on Age and Race (Join with Subquery)",
            "Time Period Analysis of Stops (Joining with Date Functions)",
            "Violations with High Search and Arrest Rates (Window Function)",
            "Driver Demographics by Country (Age, Gender, and Race)",
            "Top 5 Violations with Highest Arrest Rates"
        ]
    }

    # Select question
    category = st.selectbox("Select a Category", list(questions.keys()))
    selected_question = st.selectbox("Select a Question", questions[category])

    # Run button
    if st.button("Run"):
        st.write(f"### 🔍 Query Result for: {selected_question}")

        # Complete SQL dictionary with percentages 
        sql_queries = {
            # Vehicle-Based
            "What are the top 10 vehicle_Number involved in drug-related stops?":
                "SELECT vehicle_number, COUNT(*) AS stop_count FROM police_logs WHERE drugs_related_stop = TRUE GROUP BY vehicle_number ORDER BY stop_count DESC LIMIT 10;",
            "Which vehicles were most frequently searched?":
                "SELECT vehicle_number, COUNT(*) AS search_count FROM police_logs WHERE search_conducted = TRUE GROUP BY vehicle_number ORDER BY search_count DESC LIMIT 10;",

            # Demographic-Based
            "Which driver age group had the highest arrest rate?":
                "SELECT driver_age, ROUND(COUNT(CASE WHEN stop_outcome = 'Arrest' THEN 1 END) * 100.0 / COUNT(*), 2) AS arrest_rate_percent FROM police_logs GROUP BY driver_age ORDER BY arrest_rate_percent DESC LIMIT 10;",
            "What is the gender distribution of drivers stopped in each country?":
                "SELECT country_name, driver_gender, COUNT(*) AS count, ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY country_name), 2) AS percentage FROM police_logs GROUP BY country_name, driver_gender;",
            "Which race and gender combination has the highest search rate?":
                "SELECT driver_race, driver_gender, ROUND(AVG(search_conducted)*100,2) AS search_rate_percent FROM police_logs GROUP BY driver_race, driver_gender ORDER BY search_rate_percent DESC LIMIT 10;",

            # Time & Duration Based
            "What time of day sees the most traffic stops?":
                "SELECT HOUR(stop_time) AS hour, COUNT(*) AS total_stops FROM police_logs GROUP BY hour ORDER BY total_stops DESC;",
            "What is the average stop duration for different violations?":
                "SELECT violation, AVG(CASE WHEN stop_duration='0-15 Min' THEN 10 WHEN stop_duration='16-30 Min' THEN 23 ELSE 35 END) AS avg_duration_min FROM police_logs GROUP BY violation;",
            "Are stops during the night more likely to lead to arrests?":
                "SELECT CASE WHEN HOUR(stop_time) >= 20 OR HOUR(stop_time) < 6 THEN 'Night' ELSE 'Day' END AS period, COUNT(*) AS total_stops, ROUND(SUM(CASE WHEN stop_outcome='Arrest' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS arrest_rate_percent FROM police_logs GROUP BY period;",

            # Violation-Based
            "Which violations are most associated with searches or arrests?":
                "SELECT violation, ROUND(AVG(search_conducted)*100,2) AS search_rate_percent, ROUND(AVG(stop_outcome='Arrest')*100,2) AS arrest_rate_percent FROM police_logs GROUP BY violation ORDER BY (search_rate_percent + arrest_rate_percent) DESC LIMIT 10;",
            "Which violations are most common among younger drivers (<25)?":
                "SELECT violation, COUNT(*) AS count FROM police_logs WHERE driver_age < 25 GROUP BY violation ORDER BY count DESC LIMIT 10;",
            "Is there a violation that rarely results in search or arrest?":
                "SELECT violation, ROUND(AVG(search_conducted)*100,2) AS search_rate_percent, ROUND(AVG(stop_outcome='Arrest')*100,2) AS arrest_rate_percent FROM police_logs GROUP BY violation ORDER BY (search_rate_percent + arrest_rate_percent) ASC LIMIT 5;",

            # Location-Based
            "Which countries report the highest rate of drug-related stops?":
                "SELECT country_name, ROUND(AVG(drugs_related_stop)*100,2) AS drug_stop_rate_percent FROM police_logs GROUP BY country_name ORDER BY drug_stop_rate_percent DESC LIMIT 5;",
            "What is the arrest rate by country and violation?":
                "SELECT country_name, violation, ROUND(AVG(stop_outcome='Arrest')*100,2) AS arrest_rate_percent FROM police_logs GROUP BY country_name, violation ORDER BY arrest_rate_percent DESC;",
            "Which country has the most stops with search conducted?":
                "SELECT country_name, COUNT(*) AS search_count FROM police_logs WHERE search_conducted = TRUE GROUP BY country_name ORDER BY search_count DESC LIMIT 5;",

            # Complex
            "Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)":
                "SELECT country_name, YEAR(stop_date) AS year, COUNT(*) AS total_stops, ROUND(SUM(stop_outcome='Arrest')*100.0/COUNT(*),2) AS total_arrests_percent FROM police_logs GROUP BY country_name, YEAR(stop_date) ORDER BY country_name, year;",
            "Driver Violation Trends Based on Age and Race (Join with Subquery)":
                "SELECT driver_race, driver_age, violation, COUNT(*) AS total FROM police_logs GROUP BY driver_race, driver_age, violation ORDER BY total DESC LIMIT 10;",
            "Time Period Analysis of Stops (Joining with Date Functions)":
                "SELECT YEAR(stop_date) AS year, MONTH(stop_date) AS month, HOUR(stop_time) AS hour, COUNT(*) AS total_stops FROM police_logs GROUP BY year, month, hour ORDER BY year, month, hour;",
            "Violations with High Search and Arrest Rates (Window Function)":
                "SELECT violation, ROUND(AVG(search_conducted)*100,2) AS search_rate_percent, ROUND(AVG(stop_outcome='Arrest')*100,2) AS arrest_rate_percent FROM police_logs GROUP BY violation HAVING search_rate_percent > 30 OR arrest_rate_percent > 20 ORDER BY (search_rate_percent + arrest_rate_percent) DESC;",
            "Driver Demographics by Country (Age, Gender, and Race)":
                "SELECT country_name, driver_gender, driver_race, AVG(driver_age) AS avg_age, COUNT(*) AS total_drivers FROM police_logs GROUP BY country_name, driver_gender, driver_race;",
            "Top 5 Violations with Highest Arrest Rates":
                "SELECT violation, ROUND(AVG(stop_outcome='Arrest')*100,2) AS arrest_rate_percent FROM police_logs GROUP BY violation ORDER BY arrest_rate_percent DESC LIMIT 5;"
        }

        query = sql_queries.get(selected_question)
        if query:
            df = fetch_data(query)
            if not df.empty:
                st.dataframe(df)
            else:
                st.info("No data found for this query.")

# INPUT FORM SECTION 
elif menu == 'Input Form':
    st.header("🚔 SecureCheck Police Dashboard - Input Form")

    # Load all data for predictions
    data = load_all_data()
    if data.empty:
        st.warning("No data available in the database for predictions.")
    else:
        # User inputs
        driver_gender = st.selectbox("Driver Gender", ["Male", "Female"])
        driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=25)
        driver_race = st.selectbox("Driver Race", ["Asian", "Black", "White", "Hispanic", "Other"])
        search_conducted = st.selectbox("Was a Search Conducted?", [0, 1])
        search_type = st.selectbox("Search Type",["Vehicle Search","Frisk","None"]) 
        drugs_related_stop = st.selectbox("Was it Drug Related?", [0, 1])
        stop_duration = st.selectbox("Stop Duration", ["0-15 Min", "16-30 Min", "30+ Min"])
        vehicle_number = st.text_input("Vehicle Number", "")
        stop_date = st.date_input("Stop Date")
        stop_time = st.time_input("Stop Time")

        submitted = st.button("🔍 Predict Stop Outcome & Violation")

        if submitted:
            filtered_data = data[
                (data['driver_gender'] == driver_gender) &
                (data['driver_age'] == driver_age) &
                (data['search_conducted'] == int(search_conducted)) &
                (data['stop_duration'] == stop_duration) &
                (data['drugs_related_stop'] == int(drugs_related_stop))
            ]

            if not filtered_data.empty:
                predicted_outcome = filtered_data['stop_outcome'].mode()[0]
                predicted_violation = filtered_data['violation'].mode()[0]
            else:
                predicted_outcome = "Warning"
                predicted_violation = "Speeding"

            search_text = "A search was conducted" if int(search_conducted) else "No search was conducted"
            drug_text = "was drug-related" if int(drugs_related_stop) else "was not drug-related"

            st.markdown(f"""
            ### 💡 Prediction Summary  
            **Predicted Violation:** {predicted_violation}  
            **Predicted Stop Outcome:** {predicted_outcome}  

            A {driver_age}-year-old {driver_gender.lower()} driver of race {driver_race} was stopped at **{stop_time.strftime('%I:%M %p')}** on **{stop_date}**.  
            {search_text}, and the stop {drug_text}.  
            Stop duration: **{stop_duration}**.  
            Vehicle number: **{vehicle_number}**.
            """)

