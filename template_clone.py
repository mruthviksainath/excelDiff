import streamlit as st
import requests
import pandas as pd

# Static template IDs per template type
sqa_template_ids = [19215, 19214, 19213, 19216]
lqa_template_ids = [20533, 20534, 20535, 20536]
psa_template_ids = [21732, 21733, 21734]

# Environment Base URLs for cloning note-templates
env_clone_urls = {
    "Dev": "https://dev.siterecon.ai/api/emporio/v2/note-template/clone",
    "QA": "https://qa.siterecon.ai/api/emporio/v2/note-template/clone",
    "Prod": "https://app.siterecon.ai/api/emporio/v2/note-template/clone"
}

# Environment prefixes for other API calls (reportStyles, mapping)
env_prefix = {
    "Dev": "dev",
    "QA": "qa",
    "Prod": "app"
}

# Authorization Tokens (Replace with your valid tokens)
auth_token = "e5c1fdd8e34e0b1b96fb2df6c5a70bf07f237797"
template_api_key = "ebc6MTQyNDQ6MTEzMDY6cFhaMDBURFZFY2s5Rk94NQ="

# Initialize session state
if "cloned_template_ids" not in st.session_state:
    st.session_state["cloned_template_ids"] = []

if "selected_template_index" not in st.session_state:
    st.session_state["selected_template_index"] = None

st.title("Template Cloning and Report Style Mapping Utility")
st.markdown("""
# **How to Use the Utility**
Follow these steps to clone templates, fetch report styles, and map them to a report template:

1. **Select Environment**:  
   Use the dropdown at the top to choose the environment where you want to perform the operations (Dev, QA, or Prod).

2. **Enter Target Workspace ID**:  
   Provide the workspace ID where templates will be cloned and mapped.

3. **Choose Template Type**:  
   Select one of the available template types:
   - **SQA**: Site Quality Audits  
   - **LQA**: Land Quality Audits  
   - **PSA**: Property Site Audits  

4. **Clone Templates**:  
   - Click the **"Clone Templates"** button.  
   - The cloned template IDs will appear under **Cloned Template IDs**.

5. **Fetch Report Styles**:  
   - Input the workspace ID from which you want to fetch report styles.  
   - Click **"Fetch Report Styles"** to display the styles in a table format.

6. **Select a Report Template**:  
   - Click on a template name from the list to select it as the report template.  
   - The selected template details (Template ID, Name, Status) will be displayed.

7. **Map Cloned Templates to Report ID**:  
   - Review the cloned template IDs and the selected report template.  
   - Click **"MAP templates to Report ID"** to complete the mapping.
---
### **Quick Tips**
- Double-check workspace IDs and the selected environment.
- Clone templates before attempting to map them.
- Ensure at least one template is selected as the report template for mapping.
---
""")

# 1. Select Environment
environment = st.selectbox("Select Environment", ["Dev", "QA", "Prod"])

# 2. Enter Target Workspace ID (for cloning and mapping)
workspace_id = st.number_input("Enter Target Workspace ID (for cloning/mapping)", min_value=1, step=1)

# 3. Choose Template Type
st.write("### Choose Template Type")
template_type = st.radio("Select Template Type", ["SQA", "LQA", "PSA"])

if template_type == "SQA":
    template_ids = sqa_template_ids
elif template_type == "LQA":
    template_ids = lqa_template_ids
elif template_type == "PSA":
    template_ids = psa_template_ids
else:
    template_ids = []

# 4. Clone Templates Button
if st.button("Clone Templates"):
    if not workspace_id:
        st.error("Please enter a valid Target Workspace ID.")
    else:
        # Reset before cloning
        st.session_state["cloned_template_ids"] = []
        api_url = env_clone_urls[environment]
        headers = {
            "Authorization": f"token {auth_token}",
            "Content-Type": "application/json"
        }

        for tid in template_ids:
            payload = {
                "templateId": tid,
                "workspaceId": workspace_id
            }
            response = requests.post(api_url, json=payload, headers=headers)

            # Assuming success returns JSON with a "template" object and "id"
            if response.status_code == 200:
                data = response.json()
                cloned_id = data.get("template", {}).get("id")
                if cloned_id:
                    st.session_state["cloned_template_ids"].append(cloned_id)
                    st.success(f"Template {tid} cloned successfully. New template.id: {cloned_id}")
                else:
                    st.warning(f"Template {tid} cloned, but 'template.id' not found in response.")
            else:
                st.error(f"Failed to clone Template {tid}. Status: {response.status_code}, Message: {response.text}")

        if st.session_state["cloned_template_ids"]:
            st.write("Cloned Template IDs:", st.session_state["cloned_template_ids"])

# 5. Separate input for fetching reportStyles from a different workspace
report_styles_workspace_id = st.number_input("Enter Workspace ID for fetching reportStyles", min_value=1, step=1)

if st.button("Fetch Report Styles"):
    if not report_styles_workspace_id:
        st.error("Please provide a valid Workspace ID for fetching reportStyles.")
    else:
        prefix = env_prefix[environment]
        styles_url = f"https://{prefix}.siterecon.ai/api/emporio/v2/report/styles/{report_styles_workspace_id}"
        headers = {
            "Authorization": f"token {auth_token}"
        }
        resp = requests.get(styles_url, headers=headers)
        if resp.status_code == 200:
            styles_data = resp.json()
            report_styles = styles_data.get("reportStyles", [])
            if report_styles:
                st.write("### Report Styles")
                df_styles = pd.DataFrame(report_styles)
                st.dataframe(df_styles)
            else:
                st.warning("No report styles found for this workspace.")
        else:
            st.error(f"Failed to fetch report styles. Status: {resp.status_code}, Message: {resp.text}")

# 6. Fetch templates from the template API and display them
st.write("### Fetching Available Templates from API")
def fetch_templates(api_key):
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    response = requests.get("https://rest.apitemplate.io/v2/list-templates", headers=headers)
    if response.status_code == 200:
        return response.json().get("templates", [])
    else:
        st.error(f"Failed to fetch templates. Status code: {response.status_code}")
        return []

templates = fetch_templates(template_api_key)
if templates:
    template_data = [
        {
            "template_id": template.get("template_id"),
            "name": template.get("name"),
            "status": template.get("status"),
            "group_name": template.get("group_name", "N/A")
        }
        for template in templates
    ]
    df = pd.DataFrame(template_data)

    st.write("### Template List")
    # Display templates as clickable items
    for i, row in df.iterrows():
        # Combine template_id, name, and status into the desired format
        display_text = f"{row['template_id']}: {row['name']} ({row['status']})"

        # Render as a button
        if st.button(display_text, key=f"template_{i}"):
            st.session_state["selected_template_index"] = i

    # Show selected template details
    if st.session_state["selected_template_index"] is not None:
        selected_template = df.iloc[st.session_state["selected_template_index"]]
        st.write("### Selected Template Details")
        st.write(f"**Template ID:** {selected_template['template_id']}")
        st.write(f"**Name:** {selected_template['name']}")
        st.write(f"**Group Name:** {selected_template['group_name']}")
        st.write(f"**Status:** {selected_template['status']}")
    else:
        selected_template = None
        st.write("No template selected.")
else:
    st.warning("No templates available to display.")
    selected_template = None

# 7. MAP templates to Report ID (Selected Template)
st.write("## Mapping Details")
# Show all cloned template IDs
st.write("Cloned Template IDs:", st.session_state["cloned_template_ids"])

# Show selected report template info if available
if selected_template is not None:
    st.write("Selected Report Template:", selected_template["template_id"], "-", selected_template["name"])
else:
    st.write("No report template selected yet.")

if st.button("MAP templates to Report ID"):
    if not st.session_state["cloned_template_ids"]:
        st.error("No cloned template IDs available. Please clone templates first.")
    elif selected_template is None:
        st.error("No report template selected. Please select a template from the table.")
    elif not workspace_id:
        st.error("Please enter a valid Target Workspace ID for mapping.")
    else:
        # Use the selected template's template_id as the reportTemplateId
        report_template_id = selected_template["template_id"]

        prefix = env_prefix[environment]
        mapping_url = f"https://{prefix}.siterecon.ai/api/emporio/v2/report/note-template-id-mapping"
        headers = {
            "Authorization": f"token {auth_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "workspaceId": workspace_id,
            "noteTemplateIds": st.session_state["cloned_template_ids"],
            "reportTemplateId": str(report_template_id)
        }
        resp = requests.post(mapping_url, json=payload, headers=headers)

        if resp.status_code in [200, 204]:
            st.success("Templates mapped successfully.")
        else:
            st.error(f"Failed to map templates. Status: {resp.status_code}, Message: {resp.text}")
