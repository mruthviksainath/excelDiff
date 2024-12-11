import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import requests
from io import StringIO

# Load the dataset from GitHub
@st.cache
def load_data_from_github(url):
    response = requests.get(url)
    if response.status_code == 200:
        csv_data = StringIO(response.text)
        return pd.read_csv(csv_data)
    else:
        st.error("Failed to fetch data from GitHub. Please check the file URL.")
        return pd.DataFrame()

# Summarize report counts
def summarize_report_counts(data):
    summary = data.groupby(['name', 'year'])['report_count'].sum().unstack(fill_value=0)
    return summary

# Plot report counts for a specific company (Line Chart)
def plot_reports_for_company(company_data, company_name):
    # Create a full list of months
    months = pd.date_range(start='2023-01-01', end='2023-12-31', freq='M').strftime('%B').tolist()

    # Add missing months with 0 counts
    company_data['month_name'] = pd.to_datetime(company_data['month'], format='%m').dt.month_name()
    company_data = company_data.groupby(['year', 'month_name'])['report_count'].sum().unstack(fill_value=0)
    company_data = company_data.reindex(months, axis=1, fill_value=0)

    # Plot each year as a line
    plt.figure(figsize=(12, 6))
    for year in company_data.index:
        plt.plot(company_data.columns, company_data.loc[year], label=str(year), marker='o')

    # Customize the chart
    plt.title(f'Report Count by Month for {company_name}', fontsize=16)
    plt.xlabel('Month', fontsize=14)
    plt.ylabel('Report Count', fontsize=14)
    plt.legend(title='Year', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True)
    st.pyplot(plt)

# Streamlit app
def main():
    st.title("Report Analysis Dashboard")
    st.markdown("### Analyze report counts for various companies")

    # GitHub raw URL for the CSV file
    github_url = "https://raw.githubusercontent.com/mruthviksainath/excelDiff/main/query_result_2024-12-11T07_54_17.36189Z.csv"

    # Load the data
    data = load_data_from_github(github_url)

    # Validate if the data was loaded successfully
    if data.empty:
        st.error("The dataset is empty or failed to load. Please check the file.")
        return

    # Show available companies
    company_names = sorted(data['name'].astype(str).unique())
    selected_company = st.selectbox("Select a company:", company_names)

    # Show report counts for the selected company
    if selected_company:
        company_data = data[data['name'] == selected_company]
        if not company_data.empty:
            st.subheader(f"Report Count for {selected_company}")
            plot_reports_for_company(company_data, selected_company)
        else:
            st.warning(f"No data available for {selected_company}.")

    # Summarize report counts and display table
    st.markdown("### Yearly Report Summary")
    summary = summarize_report_counts(data)

    # Handle missing years dynamically
    valid_years = [col for col in range(2021, 2025) if col in summary.columns]
    summary = summary.reindex(columns=valid_years, fill_value=0)

    # Highlight reductions in the table
    summary['Reduction'] = summary[2023] > summary[2024]
    def highlight_reduction(val):
        return 'background-color: red' if val else ''

    styled_summary = summary.style.applymap(highlight_reduction, subset=['Reduction']).format(na_rep='-')
    st.write(styled_summary)

if __name__ == "__main__":
    main()
