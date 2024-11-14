import streamlit as st
import requests

#SQA and LQA templates to copy from
sqa_template_ids = [19215, 19214, 19213, 19216]
lqa_template_ids = [20533, 20534, 20535, 20536]  # LQA is mostly used by mariani group!!!


env_urls = {
    "Dev": "https://dev.siterecon.ai/api/emporio/v2/note-template/clone",
    "QA": "https://qa.siterecon.ai/api/emporio/v2/note-template/clone",
    "Prod": "https://app.siterecon.ai/api/emporio/v2/note-template/clone"
}

##auth for the API
auth_token = "e5c1fdd8e34e0b1b96fb2df6c5a70bf07f237797"
csrf_token = "SvxKN2HYw7OTM9AbFITmUWQ8mplS7ZuuBVk1U6bdQBwyuvYU6NLvOqwMYwnMZDm3"

#steamlit ui
st.title("Utility: Add SQA/LQA Template")

#selecting env
environment = st.selectbox("Select Environment", ["Dev", "QA", "Prod"])
api_url = env_urls[environment]

#enteting workspace id
workspace_id = st.number_input("Enter Target Workspace ID")

# Display selected environment and workspace ID
st.write(f"### Selected Environment: {environment}")
st.write(f"### Workspace ID: {workspace_id}")

# Step 3: Select template type (SQA or LQA)
st.write("### Choose Template Type")
template_type = st.radio("Select Template Type", ["SQA", "LQA"])

# Determine template list based on selection
if template_type == "SQA":
    template_ids = sqa_template_ids
elif template_type == "LQA":
    template_ids = lqa_template_ids
else:
    template_ids = []

# Step 4: Perform cloning action based on selected template type
if st.button("Clone Templates"):
    if not workspace_id:
        st.error("Please enter a valid Workspace ID.")
    else:
        for template_id in template_ids:
            payload = {
                "templateId": template_id,
                "workspaceId": workspace_id
            }
            headers = {
                "Authorization": f"token {auth_token}",
                "Content-Type": "application/json",
                "Cookie": f"csrftoken={csrf_token}"
            }
            response = requests.post(api_url, json=payload, headers=headers)

            # Display results based on the response status
            if response.status_code == 204:
                st.success(f"Template {template_id} cloned successfully.")
            else:
                st.error(f"Failed to clone Template {template_id}. Status: {response.status_code}, Message: {response.text}")

        st.write("All templates processed.")





##run command streamlit run template_clone.py
