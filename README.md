# CSV Analyzer, Cleaner & Power BI Assistant

A Streamlit-based application that accepts any CSV file, analyzes data quality, performs automated cleaning, and suggests Power BI-ready KPIs, visuals, dashboard pages, and business questions based on the dataset structure and user goals.

## Project Overview

This project is designed to help users quickly understand what can be built from a CSV dataset before moving into Power BI. It combines dataset profiling, cleaning recommendations, automated cleaning, and dashboard planning in a single interface.

The app can:
- Upload and inspect any CSV file
- Detect missing values, duplicates, empty columns, and data types
- Perform basic automated cleaning
- Suggest what can be generated from the dataset
- Recommend Power BI visuals, KPI ideas, dashboard pages, and business questions
- Accept user goals and return tailored Power BI suggestions

## Features

### 1. Data Profiling
The app reads any uploaded CSV file and displays:
- Number of rows and columns
- Column names
- Data preview
- Missing values report
- Duplicate row count
- Empty columns
- Numeric, categorical, and possible date columns

### 2. Automated Cleaning
The app can automatically:
- Drop fully empty columns
- Trim whitespace from column names
- Trim whitespace from text columns
- Remove duplicate rows
- Attempt conversion of likely date/time columns

### 3. Power BI Suggestions from Dataset
The app analyzes the uploaded dataset and suggests:
- Possible KPI cards
- Possible Power BI visuals
- Possible dashboard pages
- Business questions the dataset can answer

### 4. Power BI Suggestions from User Goal
Users can also describe what they want to build in Power BI, and the app recommends:
- Suitable visuals
- Suggested columns to use
- Dashboard elements aligned with the goal

## Tech Stack

- Python
- Streamlit
- Pandas

## Folder Structure

```bash
AI_Data_Analyst_agent/
│── app.py
│── requirements.txt
│── README.md

├── outputs/
│   ├── cleaned_data/
│   └── screenshots/
