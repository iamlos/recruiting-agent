__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
from crew import RecruitingCrew
from gsheets_utils import GSheetManager

# Set page config
st.set_page_config(
    page_title="College Sports Recruiting Questionnaire Automation",
    page_icon="🏫",
    layout="centered"
)

# Add header
st.title("College Sports Recruiting Questionnaire Automation")
st.markdown("""
    This application automates the process of filling out college sports recruiting questionnaires.
    Simply enter the college name and select the sport to begin the automation process.
""")

# Input fields
college = st.text_input("College Name", placeholder="Enter college name (e.g., University of South Florida)")
sport = st.selectbox(
    "Sport",
    options=[
        "Baseball", "Basketball", "Cross Country", "Field Hockey", "Football",
        "Golf", "Gymnastics", "Ice Hockey", "Lacrosse", "Rowing",
        "Soccer", "Softball", "Swimming & Diving", "Tennis", "Track & Field",
        "Volleyball", "Water Polo", "Wrestling"
    ]
)

# Google Sheets integration
st.markdown("---")
st.subheader("Athlete Data Source")
spreadsheet_id = st.text_input(
    "Google Sheet ID",
    placeholder="Enter the ID from your Google Sheet URL",
    help="Find this in the URL of your Google Sheet: docs.google.com/spreadsheets/d/[THIS-IS-THE-ID]/edit"
)
worksheet_name = st.text_input(
    "Worksheet Name (Optional)",
    placeholder="Leave blank to use first sheet",
    help="The name of the specific worksheet containing athlete data"
)

# Submit button
if st.button("Submit", type="primary", disabled=not (college and sport and spreadsheet_id)):
    # Initialize GSheet manager
    gsheet_manager = GSheetManager()
    
    try:
        # Fetch athlete data
        with st.spinner("Fetching athlete data..."):
            athlete_data = gsheet_manager.get_athlete_data(
                spreadsheet_id=spreadsheet_id,
                worksheet_name=worksheet_name if worksheet_name else None
            )
            st.success("✅ Successfully loaded athlete data")
            
            # Display the athlete data
            st.subheader("Athlete Data")
            st.write("The following data was retrieved from your Google Sheet:")
            st.json(athlete_data)
    except Exception as e:
        st.error(f"❌ Failed to load athlete data: {str(e)}")
        st.stop()
    with st.spinner("Initializing automation process..."):
        # Create crew instance
        crew = RecruitingCrew()

    # Navigation phase
    with st.status("Navigating to questionnaire...", expanded=True) as status:
        st.write("🔍 Searching for the recruiting questionnaire...")
        navigation_result = crew.navigate_to_questionnaire()
        st.write(f"✅ Found questionnaire: {navigation_result}")
        status.update(label="Navigation complete", state="complete")

    # Form filling phase
    with st.status("Filling out questionnaire...", expanded=True) as status:
        st.write("📝 Entering test information...")
        fill_result = crew.fill_questionnaire()
        st.write("✅ Form filled successfully")
        status.update(label="Form filling complete", state="complete")

    # Verification phase
    with st.status("Verifying submission...", expanded=True) as status:
        st.write("🔍 Checking submission status...")
        verification_result = crew.verify_submission()
        
        # Display verification results
        if verification_result:
            st.success("✅ Questionnaire submitted successfully!")
        else:
            st.error("❌ Submission failed. Please check the report for details.")
        
        status.update(label="Verification complete", state="complete")
    
    # Display submission report in an expander (moved outside the status component)
    if verification_result:
        with st.expander("View Submission Report"):
            st.markdown(verification_result)

# Add footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <small>Powered by CrewAI 🤖</small>
    </div>
""", unsafe_allow_html=True)
