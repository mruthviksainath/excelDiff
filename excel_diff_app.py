import openpyxl
import json
import streamlit as st


def excel_diff(original_file, user_file):
    # Load the workbooks
    original_wb = openpyxl.load_workbook(original_file)
    user_wb = openpyxl.load_workbook(user_file)

    differences = {}

    # Compare sheets
    for sheet_name in original_wb.sheetnames:
        if sheet_name not in user_wb.sheetnames:
            differences[sheet_name] = {'missing_in_user_file': True}
            continue

        original_sheet = original_wb[sheet_name]
        user_sheet = user_wb[sheet_name]

        sheet_diff = {
            'added_rows': [],
            'removed_rows': [],
            'modified_rows': []
        }

        # Get the maximum row count from both sheets
        max_rows = max(original_sheet.max_row, user_sheet.max_row)

        # Compare each row
        for row_index in range(1, max_rows + 1):
            original_row = [cell.value for cell in original_sheet[row_index]]
            user_row = [cell.value for cell in user_sheet[row_index]]

            # Check if row was added, removed, or modified
            if original_row == [None] * len(original_row) and user_row != [None] * len(user_row):
                sheet_diff['added_rows'].append({'row': row_index, 'data': user_row})
            elif original_row != [None] * len(original_row) and user_row == [None] * len(user_row):
                sheet_diff['removed_rows'].append({'row': row_index, 'data': original_row})
            elif original_row != user_row:
                sheet_diff['modified_rows'].append({
                    'row': row_index,
                    'original_data': original_row,
                    'user_data': user_row
                })

        if sheet_diff['added_rows'] or sheet_diff['removed_rows'] or sheet_diff['modified_rows']:
            differences[sheet_name] = sheet_diff

    # Check for sheets in user_file but not in original_file
    for sheet_name in user_wb.sheetnames:
        if sheet_name not in original_wb.sheetnames:
            differences[sheet_name] = {'extra_in_user_file': True}

    return json.dumps(differences, indent=2)


# Streamlit UI
st.title("Excel File Difference Checker")
st.write("Upload the original and user Excel files to compare them.")

# File upload widgets
original_file = st.file_uploader("Upload Original Excel File", type=["xlsx"])
user_file = st.file_uploader("Upload User Excel File", type=["xlsx"])

# Check if both files are uploaded
if original_file and user_file:
    # Run the comparison function
    diff = excel_diff(original_file, user_file)

    # Display the results
    st.subheader("Differences:")
    st.json(diff)