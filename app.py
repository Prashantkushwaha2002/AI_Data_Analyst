import streamlit as st
import pandas as pd

st.set_page_config(page_title="CSV Analyzer, Cleaner & Power BI Assistant", layout="wide")

st.title("CSV Analyzer, Cleaner & Power BI Assistant")
st.write("Upload any CSV file to analyze it, clean it, discover what can be created from it, and get Power BI suggestions based on your goal.")


def analyze_data(df):
    missing = df.isnull().sum()
    missing_percent = (missing / len(df) * 100).round(2)

    report = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Missing Values": missing.values,
        "Missing %": missing_percent.values
    })

    duplicates = int(df.duplicated().sum())
    empty_cols = [col for col in df.columns if df[col].isnull().all()]
    object_cols = df.select_dtypes(include="object").columns.tolist()
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

    possible_date_cols = [
        col for col in df.columns
        if "date" in col.lower() or "time" in col.lower() or "at" in col.lower()
    ]

    return report, duplicates, empty_cols, object_cols, numeric_cols, possible_date_cols


def clean_data(df):
    df_clean = df.copy()

    empty_cols = [col for col in df_clean.columns if df_clean[col].isnull().all()]
    df_clean.drop(columns=empty_cols, inplace=True, errors="ignore")

    df_clean.columns = df_clean.columns.str.strip()

    object_cols = df_clean.select_dtypes(include="object").columns.tolist()
    for col in object_cols:
        df_clean[col] = df_clean[col].astype(str).str.strip()

    duplicates_before = int(df_clean.duplicated().sum())
    df_clean.drop_duplicates(inplace=True)

    converted_date_cols = []
    for col in df_clean.columns:
        if "date" in col.lower() or "time" in col.lower() or "at" in col.lower():
            converted = pd.to_datetime(df_clean[col], errors="coerce")
            if converted.notna().sum() > 0:
                df_clean[col] = converted
                converted_date_cols.append(col)

    summary = {
        "original_rows": df.shape[0],
        "cleaned_rows": df_clean.shape[0],
        "original_columns": df.shape[1],
        "cleaned_columns": df_clean.shape[1],
        "dropped_empty_columns": empty_cols,
        "duplicates_removed": duplicates_before,
        "converted_date_columns": converted_date_cols
    }

    return df_clean, summary


def generate_dataset_possibilities(df):
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    object_cols = df.select_dtypes(include="object").columns.tolist()

    date_cols = [
        col for col in df.columns
        if "date" in col.lower() or "time" in col.lower() or "at" in col.lower()
    ]

    location_cols = [
        col for col in df.columns
        if any(word in col.lower() for word in ["country", "state", "city", "region", "location"])
    ]

    possibilities = {
        "kpis": [],
        "charts": [],
        "pages": [],
        "questions": []
    }

    if numeric_cols:
        possibilities["kpis"].append(f"Total {numeric_cols[0]}")
        possibilities["kpis"].append(f"Average {numeric_cols[0]}")
        possibilities["kpis"].append("Total Record Count")
        if len(numeric_cols) > 1:
            possibilities["kpis"].append(f"Compare {numeric_cols[0]} and {numeric_cols[1]}")

    if date_cols and numeric_cols:
        possibilities["charts"].append(f"Line Chart: {numeric_cols[0]} over {date_cols[0]}")
    if object_cols and numeric_cols:
        possibilities["charts"].append(f"Bar Chart: {numeric_cols[0]} by {object_cols[0]}")
        possibilities["charts"].append(f"Donut Chart: contribution of {numeric_cols[0]} by {object_cols[0]}")
    if len(numeric_cols) >= 2:
        possibilities["charts"].append(f"Scatter Plot: {numeric_cols[0]} vs {numeric_cols[1]}")
    if location_cols and numeric_cols:
        possibilities["charts"].append(f"Map: {numeric_cols[0]} by {location_cols[0]}")

    possibilities["pages"].append("Overview Dashboard")
    if date_cols:
        possibilities["pages"].append("Trend Analysis Page")
    if object_cols:
        possibilities["pages"].append("Category / Segment Analysis Page")
    if location_cols:
        possibilities["pages"].append("Geographic Analysis Page")

    if object_cols and numeric_cols:
        possibilities["questions"].append(f"Which {object_cols[0]} contributes the most to {numeric_cols[0]}?")
    if date_cols and numeric_cols:
        possibilities["questions"].append(f"How does {numeric_cols[0]} change over time?")
    if len(numeric_cols) >= 2:
        possibilities["questions"].append(f"Is there any relationship between {numeric_cols[0]} and {numeric_cols[1]}?")
    if location_cols and numeric_cols:
        possibilities["questions"].append(f"Which {location_cols[0]} performs best on {numeric_cols[0]}?")

    return possibilities, numeric_cols, object_cols, date_cols, location_cols


def suggest_based_on_user_goal(user_goal, numeric_cols, object_cols, date_cols, location_cols):
    goal = user_goal.lower().strip()
    suggestions = []

    if not goal:
        return ["Please describe what you want to build or show in Power BI."]

    if "trend" in goal or "over time" in goal or "monthly" in goal or "daily" in goal:
        if date_cols and numeric_cols:
            suggestions.append("Recommended visual: Line Chart")
            suggestions.append(f"Use '{date_cols[0]}' on the X-axis and '{numeric_cols[0]}' on the Y-axis.")
            suggestions.append("This will show how the metric changes over time.")
        else:
            suggestions.append("A trend view needs at least one date column and one numeric column.")

    if "top" in goal or "best" in goal or "highest" in goal:
        if object_cols and numeric_cols:
            suggestions.append("Recommended visual: Bar Chart")
            suggestions.append(f"Use '{object_cols[0]}' as the category and '{numeric_cols[0]}' as the value.")
            suggestions.append("Sort descending to highlight the top performers.")
        else:
            suggestions.append("A top-performers view needs one categorical column and one numeric column.")

    if "compare" in goal or "comparison" in goal:
        if object_cols and numeric_cols:
            suggestions.append("Recommended visual: Clustered Column Chart")
            suggestions.append(f"Use '{object_cols[0]}' on the axis and '{numeric_cols[0]}' as the value.")
            suggestions.append("This is useful for comparing groups.")
        else:
            suggestions.append("A comparison view needs one categorical column and one numeric column.")

    if "distribution" in goal or "share" in goal or "contribution" in goal:
        if object_cols and numeric_cols:
            suggestions.append("Recommended visual: Donut Chart or Treemap")
            suggestions.append(f"Use '{object_cols[0]}' as the legend/group and '{numeric_cols[0]}' as the value.")
            suggestions.append("This will show contribution by category.")
        else:
            suggestions.append("A contribution view needs one categorical column and one numeric column.")

    if "relationship" in goal or "correlation" in goal:
        if len(numeric_cols) >= 2:
            suggestions.append("Recommended visual: Scatter Chart")
            suggestions.append(f"Use '{numeric_cols[0]}' on the X-axis and '{numeric_cols[1]}' on the Y-axis.")
            suggestions.append("This helps check whether two numeric variables move together.")
        else:
            suggestions.append("A relationship view needs at least two numeric columns.")

    if "kpi" in goal or "summary" in goal or "overview" in goal or "dashboard" in goal:
        if numeric_cols:
            suggestions.append("Recommended visual: KPI Cards")
            suggestions.append(f"Use fields like: {', '.join(numeric_cols[:4])}")
            suggestions.append("Place them at the top of the Power BI page for a quick overview.")
        else:
            suggestions.append("KPI cards need at least one numeric column.")

    if "map" in goal or "region" in goal or "country" in goal or "location" in goal:
        if location_cols and numeric_cols:
            suggestions.append("Recommended visual: Map")
            suggestions.append(f"Use '{location_cols[0]}' as the location and '{numeric_cols[0]}' as the value.")
            suggestions.append("This is useful for geographic performance analysis.")
        else:
            suggestions.append("A map needs a location-type column and a numeric value column.")

    if not suggestions:
        suggestions.append("I could not confidently match your request to a specific Power BI visual from the detected columns.")
        suggestions.append(f"Numeric columns found: {numeric_cols if numeric_cols else 'None'}")
        suggestions.append(f"Categorical columns found: {object_cols if object_cols else 'None'}")
        suggestions.append(f"Date columns found: {date_cols if date_cols else 'None'}")
        suggestions.append("Please check whether the dataset contains the right columns for the view you want.")

    return suggestions


uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        st.subheader("1. Data Overview")
        c1, c2 = st.columns(2)
        c1.metric("Rows", df.shape[0])
        c2.metric("Columns", df.shape[1])

        st.write("### Preview")
        st.dataframe(df.head())

        st.write("### Column Names")
        st.write(list(df.columns))

        report, duplicates, empty_cols, object_cols, numeric_cols, possible_date_cols = analyze_data(df)

        st.subheader("2. Data Quality Report")
        st.dataframe(report)

        st.write(f"**Duplicate Rows:** {duplicates}")
        st.write(f"**Fully Empty Columns:** {empty_cols if empty_cols else 'None'}")
        st.write(f"**Numeric Columns:** {numeric_cols if numeric_cols else 'None'}")
        st.write(f"**Categorical/Text Columns:** {object_cols if object_cols else 'None'}")
        st.write(f"**Possible Date Columns:** {possible_date_cols if possible_date_cols else 'None'}")

        st.subheader("3. Recommended Cleaning Steps")
        recommendations = []

        if empty_cols:
            recommendations.append("Drop fully empty columns.")
        if duplicates > 0:
            recommendations.append("Remove duplicate rows.")
        if report["Missing Values"].sum() > 0:
            recommendations.append("Review missing values and decide whether to fill, keep, or drop them.")
        if object_cols:
            recommendations.append("Trim spaces and standardize text values in object columns.")
        if possible_date_cols:
            recommendations.append("Convert likely date/time columns into proper datetime format.")
        if not recommendations:
            recommendations.append("The dataset looks fairly clean and ready for analysis.")

        for i, rec in enumerate(recommendations, 1):
            st.write(f"{i}. {rec}")

        st.subheader("4. Auto Clean")
        if st.button("Run Auto Clean"):
            df_clean, summary = clean_data(df)

            st.write("### Cleaned Data Preview")
            st.dataframe(df_clean.head())

            st.write("### Cleaning Summary")
            st.write(summary)

            csv = df_clean.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Cleaned CSV",
                data=csv,
                file_name="cleaned_data.csv",
                mime="text/csv"
            )

        possibilities, numeric_cols, object_cols, date_cols, location_cols = generate_dataset_possibilities(df)

        st.subheader("5. What Can Be Generated from This Dataset?")

        st.write("### Possible KPIs")
        if possibilities["kpis"]:
            for item in possibilities["kpis"]:
                st.write(f"- {item}")
        else:
            st.write("No obvious KPI fields detected.")

        st.write("### Possible Power BI Visuals")
        if possibilities["charts"]:
            for item in possibilities["charts"]:
                st.write(f"- {item}")
        else:
            st.write("No strong chart suggestions could be inferred from the dataset structure.")

        st.write("### Possible Dashboard Pages")
        if possibilities["pages"]:
            for item in possibilities["pages"]:
                st.write(f"- {item}")

        st.write("### Business Questions This Data Can Answer")
        if possibilities["questions"]:
            for item in possibilities["questions"]:
                st.write(f"- {item}")
        else:
            st.write("No clear business questions could be generated automatically from the dataset structure.")

        st.subheader("6. Tell Me What You Want to Show in Power BI")
        user_goal = st.text_area(
            "Describe what you want to build",
            placeholder="Example: I want to show monthly trends, top performers, and regional comparison."
        )

        if st.button("Suggest Based on My Goal"):
            goal_suggestions = suggest_based_on_user_goal(
                user_goal,
                numeric_cols=numeric_cols,
                object_cols=object_cols,
                date_cols=date_cols,
                location_cols=location_cols
            )

            st.write("### Power BI Suggestions Based on Your Goal")
            for item in goal_suggestions:
                st.write(f"- {item}")

    except Exception as e:
        st.error(f"Error reading file: {e}")

else:
    st.info("Please upload a CSV file to begin.")