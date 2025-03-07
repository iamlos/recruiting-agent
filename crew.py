from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import BrowserbaseLoadTool, SeleniumScrapingTool

@CrewBase
class RecruitingCrew:
    """Crew for automating college sports recruiting questionnaire submissions"""

    # Agent definitions
    @agent
    def navigator(self) -> Agent:
        return Agent(
            role='Web Navigation Specialist',
            goal='Locate and access specific college sport recruiting questionnaires',
            backstory=(
                "You are an expert web navigator with extensive experience in "
                "traversing college athletic websites. Your specialty is efficiently "
                "locating recruiting questionnaires across various university platforms."
            ),
            verbose=True,
            tools=[BrowserbaseLoadTool()]
        )

    @agent
    def form_handler(self) -> Agent:
        return Agent(
            role='Form Interaction Specialist',
            goal='Accurately complete and submit recruiting questionnaires',
            backstory=(
                "You are a form automation expert who specializes in filling out "
                "web forms with precision. You understand form validation requirements "
                "and can handle various input types effectively."
            ),
            verbose=True,
            tools=[SeleniumScrapingTool()]
        )

    @agent
    def verification_agent(self) -> Agent:
        return Agent(
            role='Submission Verification Specialist',
            goal='Confirm form submissions and generate status reports',
            backstory=(
                "You are a detail-oriented verification specialist who ensures "
                "form submissions are successful and generates comprehensive "
                "status reports. You can identify submission confirmations and "
                "handle error scenarios effectively."
            ),
            verbose=True,
            tools=[SeleniumScrapingTool()]
        )

    # Task definitions (moved from tasks.yaml)
    @task
    def navigate_to_questionnaire(self) -> Task:
        return Task(
            description=(
                "Navigate to {college}'s athletic website and locate the recruiting "
                "questionnaire for {sport}. Ensure the correct form is found and accessible."
            ),
            expected_output=(
                "The URL of the recruiting questionnaire page and confirmation that "
                "the form is accessible."
            ),
            agent=self.navigator(),
            tools=[BrowserbaseLoadTool()],
            callback=self._navigate_to_questionnaire_callback,
            feedback=True,
            feedback_message="🧭 Navigation complete! Form found and accessible."
        )

    def _navigate_to_questionnaire_callback(self, college: str, sport: str) -> str:
        """Callback to actually use the BrowserbaseLoadTool to find the recruiting form."""
        search_url = f"https://www.google.com/search?q={college}+{sport}+recruiting+questionnaire"
        
        # Check if the agent has tools
        agent = self.navigator()
        if not agent.tools:
            return "❌ ERROR: No tools connected to the navigation agent."

        # Locate the BrowserbaseLoadTool
        load_tool = next((tool for tool in agent.tools if isinstance(tool, BrowserbaseLoadTool)), None)
        if not load_tool:
            return "❌ ERROR: BrowserbaseLoadTool not found. Ensure the tool is assigned to the navigation agent."

        try:
            # Log tool execution
            print(f"🌐 Loading URL: {search_url} using BrowserbaseLoadTool...")

            # Run the tool with the search URL
            result = load_tool.run(url=search_url)

            # Log and return the result
            print(f"📄 Tool Result: {result}")
            if result:
                return f"✅ Successfully loaded the page. URL: {search_url}"
            else:
                return f"❌ Failed to load the page: {search_url}"
        
        except Exception as e:
            error_message = f"❌ Error loading page: {str(e)}"
            print(error_message)
            return error_message

    @task
    def fill_questionnaire(self) -> Task:
        return Task(
            description=(
                "Complete the recruiting questionnaire with test data. Include standard "
                "fields like name, contact information, academic details, and athletic experience."
            ),
            expected_output=(
                "Confirmation that all required fields have been filled with appropriate "
                "test data."
            ),
            agent=self.form_handler()
        )

    @task
    def verify_submission(self) -> Task:
        return Task(
            description=(
                "Submit the completed questionnaire and verify the submission was successful. "
                "Generate a detailed status report."
            ),
            expected_output=(
                "A status report containing submission confirmation or error details, "
                "and any relevant response messages."
            ),
            agent=self.verification_agent(),
            output_file='output/submission_report.md',
            feedback=True,
            feedback_message="✅ Submission verified and report generated.",
            tools=[SeleniumScrapingTool()],
            callback=self._verify_submission_callback
        )

    def _verify_submission_callback(self):
        """Callback to explicitly run the SeleniumScrapingTool and verify submission."""
        submission_page_url = "https://example-university.edu/sports/recruiting/confirmation"
        confirmation_message_selector = ".submission-confirmation"

        agent = self.verification_agent()

        # Check if the agent has the necessary tools
        if not agent.tools:
            error_message = "❌ ERROR: No tools connected to the verification agent."
            print(error_message)
            return error_message

        # Find the SeleniumScrapingTool
        scraping_tool = next((tool for tool in agent.tools if isinstance(tool, SeleniumScrapingTool)), None)
        if not scraping_tool:
            error_message = "❌ ERROR: SeleniumScrapingTool not found."
            print(error_message)
            return error_message

        try:
            # Explicitly set tool parameters
            scraping_tool.website_url = submission_page_url
            scraping_tool.css_element = confirmation_message_selector

            # Log tool execution attempt
            print(f"🔍 Running SeleniumScrapingTool with URL: {submission_page_url} and CSS Selector: {confirmation_message_selector}")

            # Explicitly run the tool
            result = scraping_tool.run(
                website_url=submission_page_url,
                css_element=confirmation_message_selector
            )

            # Check if the tool executed
            if not result:
                return "❌ ERROR: Tool execution failed. No result returned."

            # Output the result
            print(f"📄 Tool Result: {result}")
            if "Success" in result or "Thank you" in result:
                return "✅ Form submission successful!"
            else:
                return f"❌ Submission failed. Response: {result}"
        
        except Exception as e:
            error_message = f"❌ Error during tool execution: {str(e)}"
            print(error_message)
            return error_message

    # Crew definition
    @crew
    def crew(self) -> Crew:
        """Creates the recruiting automation crew"""
        return Crew(
            agents=[self.navigator(), self.form_handler(), self.verification_agent()],
            tasks=[self.navigate_to_questionnaire(), self.fill_questionnaire(), self.verify_submission()],
            process=Process.sequential,
            verbose=True
        )
