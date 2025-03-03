import streamlit as st
import openai
import pandas as pd
import matplotlib.pyplot as plt
import json
import io
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="SiteRecon Insights",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1E3A8A;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .info-box {
        background-color: #F0F9FF;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: pre-wrap;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True) 

# Main content
# st.markdown('<div class="main-header">Site Visit Analysis Dashboard</div>', unsafe_allow_html=True)

# Load and process the dataset
@st.cache_data
def load_data():
    df = pd.read_json('/Users/ruthvik/Desktop/site_visit_tracker_df.json')
    df['reportCreatedAt'] = pd.to_datetime(df['reportCreatedAt'])
    df['orderPlacedAt'] = pd.to_datetime(df['orderPlacedAt'])
    
    # Fill NA values in string columns
    string_columns = ['propertyState', 'propertyCity', 'propertyAddress', 'reportCreatorName', 'propertyName']
    for col in string_columns:
        if col in df.columns:
            df[col] = df[col].fillna('')
    
    # Ensure proper data types
    df['propertyState'] = df['propertyState'].astype(str)
    df['propertyCity'] = df['propertyCity'].astype(str)
    df['propertyAddress'] = df['propertyAddress'].astype(str)
    df['propertyName'] = df['propertyName'].astype(str)
    
    return df

# Load data before any UI elements
df = load_data()

# Sidebar - simplified version without filters
# with st.sidebar:
#     st.image("https://siterecon.ai/wp-content/uploads/2023/03/SiteRecon-Logo-1.png", width=200)
#     st.markdown("## Site Visit Tracker")

# Main content
st.markdown('<div class="main-header">Site Visit Analysis Dashboard</div>', unsafe_allow_html=True)

# Load and process the dataset
# @st.cache_data
# def load_data():
#     df = pd.read_json('/Users/ruthvik/Desktop/site_visit_tracker_df.json')
    
#     # Convert datetime columns with error handling
#     for col in ['reportCreatedAt', 'orderPlacedAt']:
#         try:
#             # First try with default parsing
#             df[col] = pd.to_datetime(df[col])
#         except ValueError:
#             # If that fails, try with errors='coerce' to handle mixed formats
#             df[col] = pd.to_datetime(df[col], errors='coerce')
    
#     # Fill NA values in string columns
#     string_columns = ['propertyState', 'propertyCity', 'propertyAddress', 'reportCreatorName', 'propertyName']
#     for col in string_columns:
#         if col in df.columns:
#             df[col] = df[col].fillna('')
    
#     # Ensure proper data types for key columns
#     df['propertyState'] = df['propertyState'].astype(str)
#     df['propertyCity'] = df['propertyCity'].astype(str)
#     df['propertyAddress'] = df['propertyAddress'].astype(str)
#     df['propertyName'] = df['propertyName'].astype(str)
    
#     return df

# df = load_data()

# OpenAI API Key
OPENAI_API_KEY = "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"
# OPENAI_API_KEY ="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"

# Fine-Tuned Model ID
MODEL_ID = "ft:gpt-3.5-turbo-0125:siterecon::B4o7ZKcW"

# Configure OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# System prompt (shortened for brevity)
SYSTEM_PROMPT = """You are a data analysis assistant for a property inspection dataset. 
Return responses in this JSON format:
{
    "summary": {
        "queries": ["pandas query 1", "pandas query 2"],
        "labels": ["Description for query 1", "Description for query 2"]
    },
    "table": {
        "queries": ["pandas query 1", "pandas query 2"],
        "labels": ["Description for table 1", "Description for table 2"]
    },
    "graph": {
        "commands": ["plotting command 1", "plotting command 2"],
        "labels": ["Description for graph 1", "Description for graph 2"]
    },
    "followup_questions": ["Question 1", "Question 2", "Question 3"]
}

# If you don't understand the user's question:
# 1. Ask for clarification about specific data points needed
# 2. Request examples if the query is ambiguous
# 3. Suggest alternative ways to phrase the question
# 4. Break down complex queries into simpler parts

**When a user asks show all data, you need to show User, total reports, open issues and enhancements. This is grouped by user. Only these 4 columns. 

Never Show reportID column, use reportUrl instead.
Incase you don't have the data to answer a question, return False for that field.
Always: remember you need to give in this format. 
Always remember, if user asks something reportURL makes more sense than report name. So use reportURL column. Show this instead of reportID as reportID does not make sense to the user. Rather reportURL makes more sense.  
1.	reportId (string): Unique identifier for each report.
Example: "bbb78e64-2a25-4154-94e9-fc39b55dc675"
Auto-generated for every report created on the platform.
	2.	reportType (string): Type of report generated. Remember
Example: "SESSION_REPORT"
Default: Consider all report types unless the user specifies "SESSION_REPORT" or "PLATO_NOTES_EXPORT_PDF".
	3.	reportOrderId (integer): Platform-specific property ID where the report was created.
Example: 462435
	4.	reportCreatedAt (datetime): Timestamp when the report was created/exported.
Example: "2023-04-14T20:46:00.708637+05:30"
Format: YYYY-MM-DD hh:mm:ss.xxx +yyyy (includes timezone).
	5.	reportFilename (string): Name of the generated report.
Example: "Session Report: April 14, 01:24PM | 6501 Dower House Road"
	6.	reportCreatedBy (integer): User ID of the report creator.
Example: 2695
	7.	reportCreatorEmail (string): Email of the report creator.
Example: "maryellen.burton@levelgreenlandscaping.com"
	8.	reportCreatorName (string): Name of the report creator.
Example: "Mary Ellen Burton"
ALWAYS use str.contains() for searching names, never use ==.
	9.	reportUrl (string): Direct link to the generated report.
Example: "https://storage.siterecon.ai/prod/notes-export/989984e0-58c4-4661-aa2b-36cea7817667.pdf"
Format: HTTPS URL
	10.	countOfNotes (integer): Number of notes included in the report.
Example: 1
	11.	openNoteCount (integer): Number of unresolved/open notes in the report.
Example: 0
Represents open issues at the property.
	12.	anyNoteTakenOnsite (boolean): Indicates whether the report was created onsite.
Example: false
	13.	orderPlacedAt (datetime): Timestamp when the order was created on the platform.
Example: "2023-03-22T18:39:07.647194+05:30"
Format: YYYY-MM-DD hh:mm:ss.xxx +yyyy (includes timezone).
	14.	orderWorkspaceId (integer): ID of the workspace to which the order belongs. DONT USE THIS FIELD.
Example: 21
	15.	orderUserId (integer): User ID associated with the order.
Example: 2695
	16.	propertyAddress (string): Full property address (street, city, state, country).
Example: "6501 Dower House Road, Upper Marlboro, MD, USA"
ALWAYS use str.contains() for searching addresses, never use ==.
	17.	parcelAreaInAcres (float): Size of the property in acres.
Example: 13.29
	18.	propertyLatitude (float): Geographical latitude of the property.
Example: 38.7999579
	19.	propertyLongitude (float): Geographical longitude of the property.
Example: -76.843369
	20.	propertyCity (string): City where the property is located.
Example: "Melwood"
	21.	propertyState (string): State where the property is located.
Example: "Maryland"
	22.	propertyName (string): Name of the property.
Example: "6501 Dower House Road, Upper Marlboro, MD, USA"
Important: This name is user-defined and may sometimes match the propertyAddress.

Always:
- Use fillna('') for string operations
- Use case=False for searches
- Include proper sorting
- Set unused outputs to false
- ALWAYS use str.contains() for searching addresses, never use ==
- Includes timezone information
- ALWAYS use str.contains() for searching names, never use ==
- report (string): URL link to a detailed PDF report
   - Example: "https://storage.siterecon.ai/prod/notes-export/[uuid].pdf"
   - Format: HTTPS URL
- Consider all report types unless the user specifies "SESSION_REPORT" or "PLATO_NOTES_EXPORT_PDF".
orderWorkspaceId (integer): ID of the workspace to which the order belongs. DONT USE THIS FIELD.

Remember: 
If a user asks for summary, always return column with user, total properties, rating (average) and openIssues
You need to group them by user. 

Another important point: When showing property level data. Try inclucating Report COlumn whever it makes sense

When giving output for the graph, think very logically dont overdo the x axis as it wont be visible. Think smart on how to show. You can group data or use different charts. 

If a single line solution is not possible, multiline solutions or functions are acceptable, but the code must end with an assignment to the variable
Avoid importing any additional libraries than pandas and matplotlib. 


**** IMP:  Dont Give Report ID, always when you want to show report it has to show reportURL*******
When talking abuot notes created, its preferred to show property and total count of notes on it.

When generating graph make sure the highest count of values on x axis is 10

DONT SHOW REPORT ID. IT is only for calculation for you. If you want to show report use reportURL
"""

# Function to ask OpenAI
def ask_openai(user_input):
    """Send user input to the fine-tuned OpenAI model and return a structured response."""
    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            response_format={"type": "json_object"}
        )
        
        # Get token usage with proper type checking
        if hasattr(response, 'usage') and response.usage is not None:
            input_tokens = getattr(response.usage, 'prompt_tokens', 0)
            output_tokens = getattr(response.usage, 'completion_tokens', 0)
            total_tokens = getattr(response.usage, 'total_tokens', 0)
            
            # Calculate cost
            input_cost = (input_tokens * 0.0010) / 1000
            output_cost = (output_tokens * 0.0020) / 1000
            total_cost = input_cost + output_cost
            
            # Parse response with type checking
            if (hasattr(response, 'choices') and 
                response.choices and 
                hasattr(response.choices[0], 'message') and 
                response.choices[0].message and 
                response.choices[0].message.content):
                
                result = json.loads(response.choices[0].message.content)
                
                return result, {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "total_cost": total_cost
                }
        
        return None, None
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None, None

# Create tabs
tab1, tab2, tab3 = st.tabs(["Dashboard", "Query Assistant", "Data Explorer"])

# Use the full dataset for all visualizations and queries
filtered_df = df.copy()

with tab1:
    # Dashboard tab
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="section-header">Total Properties</div>', unsafe_allow_html=True)
        total_properties = df['propertyName'].nunique()
        st.markdown(f"<h1 style='text-align: center; color: #3B82F6;'>{total_properties}</h1>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-header">Total Reports</div>', unsafe_allow_html=True)
        total_reports = len(df)
        st.markdown(f"<h1 style='text-align: center; color: #3B82F6;'>{total_reports}</h1>", unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="section-header">Open Issues</div>', unsafe_allow_html=True)
        open_issues = df['openNoteCount'].sum() if 'openNoteCount' in df.columns else 0
        st.markdown(f"<h1 style='text-align: center; color: #3B82F6;'>{open_issues}</h1>", unsafe_allow_html=True)
    
    # Charts
    st.markdown('<div class="section-header">Reports by State</div>', unsafe_allow_html=True)
    if 'propertyState' in filtered_df.columns:
        state_counts = filtered_df['propertyState'].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(10, 6))
        state_counts.plot(kind='bar', ax=ax)
        plt.title('Reports by State')
        plt.xlabel('State')
        plt.ylabel('Number of Reports')
        plt.tight_layout()
        st.pyplot(fig)
    
    # More charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">Reports Over Time</div>', unsafe_allow_html=True)
        if 'reportCreatedAt' in filtered_df.columns:
            # Use filtered_df instead of df
            filtered_df['month'] = filtered_df['reportCreatedAt'].dt.strftime('%Y-%m')
            monthly_reports = filtered_df.groupby('month').size()
            
            if not monthly_reports.empty:
                fig, ax = plt.subplots(figsize=(10, 6))
                monthly_reports.plot(kind='line', marker='o', ax=ax)
                plt.title('Reports Created by Month')
                plt.xlabel('Month')
                plt.ylabel('Number of Reports')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
            else:
                st.info("No data available for the selected time period")
    
    with col2:
        st.markdown('<div class="section-header">Top Report Creators</div>', unsafe_allow_html=True)
        if 'reportCreatorName' in filtered_df.columns:
            # Use filtered_df instead of df
            creator_counts = filtered_df['reportCreatorName'].value_counts().head(10)
            
            if not creator_counts.empty:
                fig, ax = plt.subplots(figsize=(10, 6))
                creator_counts.plot(kind='barh', ax=ax)
                plt.title('Top 10 Report Creators')
                plt.xlabel('Number of Reports')
                plt.ylabel('Creator Name')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
            else:
                st.info("No data available for the selected filters")

with tab2:
    # Query Assistant tab
    st.markdown('<div class="section-header">Ask Questions About Your Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Ask questions in natural language about your site visit data. For example: "Show me the top 5 properties with the most reports" or "What are the trends in site visits over the last 3 months?"</div>', unsafe_allow_html=True)
    
    # Get user query from session state if available, otherwise use empty string
    user_query = st.session_state.get('user_query', '') 
    
    # Text input with the value from session state
    user_query = st.text_input("Enter your question:", value=user_query, placeholder="e.g., Show me properties with open issues")
    
    if st.button("Submit Query", type="primary"):
        with st.spinner("Analyzing your data..."):
            # Add column name mapping to help the model
            column_info = "Note: For inspector or creator information, use 'reportCreatorName' column, not 'inspectorName'."
            enhanced_query = user_query + "\n\n" + column_info
            
            result, token_info = ask_openai(enhanced_query)
            
            if result and token_info:
                # Display token usage in an expander
                with st.expander("Query Details"):
                    st.markdown(f"""
                    - Input tokens: {token_info['input_tokens']}
                    - Output tokens: {token_info['output_tokens']}
                    - Total tokens: {token_info['total_tokens']}
                    - Estimated cost: ${token_info['total_cost']:.6f}
                    """)
                
                # Display summary
                if result.get("summary") and result["summary"] is not False:
                    st.markdown('<div class="section-header">Summary</div>', unsafe_allow_html=True)
                    summary_data = result["summary"]
                    queries = summary_data.get("queries", [])
                    labels = summary_data.get("labels", [])
                    
                    for query, label in zip(queries, labels):
                        if isinstance(query, str) and query.strip():  # Add type check
                            try:
                                query_result = eval(query.strip())
                                st.markdown(f"**{label}**")
                                st.write(query_result)
                            except Exception as e:
                                st.error(f"Error in query '{label}': {str(e)}")
                
                # Display tables
                if result.get("table") and result["table"] is not False:
                    st.markdown('<div class="section-header">Tables</div>', unsafe_allow_html=True)
                    table_data = result["table"]
                    queries = table_data.get("queries", [])
                    labels = table_data.get("labels", [])
                    
                    for query, label in zip(queries, labels):
                        if isinstance(query, str) and query.strip():  # Add type check
                            try:
                                query_result = eval(query.strip())
                                st.markdown(f"**{label}**")
                                
                                # Convert reportUrl column to clickable links
                                if isinstance(query_result, pd.DataFrame) and 'reportUrl' in query_result.columns:
                                    display_df = query_result.copy()
                                    def make_clickable(url):
                                        return f'<a href="{url}" target="_blank">Report</a>'
                                    display_df['reportUrl'] = display_df['reportUrl'].apply(make_clickable)
                                    st.write(display_df.to_html(escape=False), unsafe_allow_html=True)
                                else:
                                    st.dataframe(query_result)
                            except Exception as e:
                                st.error(f"Error in table '{label}': {str(e)}")
                
                # Display graphs
                if result.get("graph") and result["graph"] is not False:
                    st.markdown('<div class="section-header">Visualizations</div>', unsafe_allow_html=True)
                    graph_data = result["graph"]
                    commands = graph_data.get("commands", [])
                    labels = graph_data.get("labels", [])
                    
                    for command, label in zip(commands, labels):
                        if command.strip():
                            try:
                                st.markdown(f"**{label}**")
                                fig = plt.figure(figsize=(10, 6))
                                exec(command.strip())
                                plt.tight_layout()
                                st.pyplot(fig)
                                plt.close()
                            except Exception as e:
                                st.error(f"Error in graph '{label}': {str(e)}")
                
                # Display follow-up questions
                if result.get("followup_questions"):
                    st.markdown('<div class="section-header">Follow-up Questions</div>', unsafe_allow_html=True)
                    for i, question in enumerate(result["followup_questions"], 1):
                        if st.button(f"{question}", key=f"followup_{i}"):
                            st.session_state.user_query = question
                            st.rerun()

with tab3:
    # Data Explorer tab
    st.markdown('<div class="section-header">Explore Raw Data</div>', unsafe_allow_html=True)
    
    # Column selector
    columns = df.columns.tolist()
    selected_columns = st.multiselect("Select columns to display", columns, default=columns[:5])
    
    # Display data
    if selected_columns:
        st.dataframe(df[selected_columns], use_container_width=True)
    
    # Download option
    csv = df[selected_columns].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name="site_visit_data.csv",
        mime="text/csv",
    )

# Footer
st.markdown("---")
st.markdown("© 2023 SiteRecon Insights ")
