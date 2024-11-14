import streamlit as st
import pandas as pd
from openpyxl import load_workbook


def compare_excel_sheets(original_excel_path, user_excel_path):
    # Load both Excel files
    original_wb = load_workbook(original_excel_path, data_only=True)
    user_wb = load_workbook(user_excel_path, data_only=True)

    # Initialize an empty list to store differences
    differences = []

    # Compare each sheet in both workbooks
    for sheet_name in original_wb.sheetnames:
        if sheet_name in user_wb.sheetnames:
            original_sheet = original_wb[sheet_name]
            user_sheet = user_wb[sheet_name]

            # Convert sheets to DataFrames for easy comparison
            original_df = pd.DataFrame(original_sheet.values)
            user_df = pd.DataFrame(user_sheet.values)

            # Ensure both DataFrames have the same structure
            max_rows = max(original_df.shape[0], user_df.shape[0])
            max_cols = max(original_df.shape[1], user_df.shape[1])
            original_df = original_df.reindex(index=range(max_rows), columns=range(max_cols))
            user_df = user_df.reindex(index=range(max_rows), columns=range(max_cols))

            # Compare row by row and column by column
            for row_idx in range(max_rows):
                original_row = original_df.iloc[row_idx].fillna("").tolist()
                user_row = user_df.iloc[row_idx].fillna("").tolist()

                if original_row != user_row:
                    differences.append({
                        "Sheet": sheet_name,
                        "Row": row_idx + 1,
                        "Old": original_row,
                        "New": user_row,
                    })

    return differences


# Streamlit interface
st.title("Excel Sheet Difference Checker")
st.write("Upload the original Excel file and the user-updated Excel file to compare differences.")

# Upload file inputs
original_file = st.file_uploader("Upload Original Excel File", type=["xlsx"])
user_file = st.file_uploader("Upload User Excel File", type=["xlsx"])

# Run comparison if both files are uploaded
if original_file and user_file:
    st.write("Comparing files...")

    # Compare the Excel files and retrieve the differences
    differences = compare_excel_sheets(original_file, user_file)

    # Display results
    if differences:
        st.write("### Differences Found")
        for diff in differences:
            st.write(f"**Sheet:** {diff['Sheet']} - **Row:** {diff['Row']}")

            # Display the comparison side by side using columns
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Old**")
                st.write(diff["Old"])
            with col2:
                st.write("**New**")
                st.write(diff["New"])

            st.write("---")
    else:
        st.write("No differences found between the original and user Excel files.")
