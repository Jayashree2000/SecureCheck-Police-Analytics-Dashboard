# 🚔 SecureCheck Police Analytics Dashboard

**SecureCheck** is an interactive Streamlit application powered by **MySQL**, designed to help law enforcement and analysts visualize and understand traffic stop data.

---

## 🧩 Features

✅ **Insight Dashboard**
- Run prebuilt SQL queries to analyze violations, demographics, time patterns, and locations.  
- Auto-calculated percentage insights (arrest rate, search rate, drug-related rate).  
- Interactive results table powered by pandas and Streamlit.

✅ **Input Form**
- Simulate or predict traffic stop outcomes.  
- Enter driver and stop details to estimate violation and stop outcome.  
- Clean summary visualization.

✅ **Database Integration**
- Connects directly to a MySQL database (`police_db`) with a table `police_logs`.  
- Supports data filtering, aggregation, and real-time updates.

---

## ⚙️ Tech Stack

| Layer | Technology |
|--------|-------------|
| Frontend | Streamlit |
| Backend | Python (pandas, pymysql) |
| Database | MySQL |
| Visualization | Streamlit DataFrame / Markdown |
| Deployment | GitHub + Streamlit Cloud (optional) |

---

## 🧱 Architecture

          ┌────────────────────────────┐
          │        User Input          │
          │  (Streamlit Frontend)      │
          └─────────────┬──────────────┘
                        │
                        ▼
          ┌────────────────────────────┐
          │   Business Logic Layer     │
          │ (SQL Query Engine + Pandas)│
          └─────────────┬──────────────┘
                        │
                        ▼
          ┌────────────────────────────┐
          │        MySQL Database       │
          │  (police_logs table)        │
          └────────────────────────────┘







