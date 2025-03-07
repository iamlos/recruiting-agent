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
            tools=[BrowserbaseLoadTool()],
            verbose=True
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
            tools=[SeleniumScrapingTool()],
            verbose=True
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
            tools=[SeleniumScrapingTool()],
            verbose=True
        )

    # Task definitions
    @task
    def navigate_to_questionnaire(self) -> Task:
        return Task(
            description=(
                "Navigate to {college}'s athletic website and locate the recruiting "
                "questionnaire for {sport}. Ensure the correct form is found and accessible."
            ),
            expected_output="The URL of the recruiting questionnaire page and confirmation that the form is accessible.",
            tools=[BrowserbaseLoadTool()],
            agent=self.navigator(),
            callback=self._navigate_to_questionnaire_callback,
            feedback=True,
            feedback_message="🧭 Navigation complete! Form found and accessible."
        )

    def _navigate_to_questionnaire_callback(self, college: str, sport: str) -> str:
        """Callback to use BrowserbaseLoadTool to find the recruiting form."""
        search_url = f"https://www.google.com/search?q={college}+{sport}+recruiting+questionnaire"
        agent = self.navigator()

        # Ensure agent has the tool
        if not agent.tools:
            return "❌ ERROR: No tools connected to the navigation agent."

        load_tool = next((tool for tool in agent.tools if isinstance(tool, BrowserbaseLoadTool)), None)
        if not load_tool:
            return "❌ ERROR: BrowserbaseLoadTool not found."

        try:
            print(f"🌐 Loading URL: {search_url} using BrowserbaseLoadTool...")
            result = load_tool.run(url=search_url)

            print(f"📄 Tool Result: {result}")
            return f"✅ Successfully loaded the page: {search_url}" if result else f"❌ Failed to load page: {search_url}"
        except Exception as e:
            return f"❌ Error loading page: {str(e)}"

    @task
    def fill_questionnaire(self) -> Task:
        return Task(
            description="Complete the recruiting questionnaire with test data.",
            expected_output="Confirmation that all required fields have been filled with appropriate test data.",
            agent=self.form_handler(),
            tools=[SeleniumScrapingTool()],
            callback=self._fill_questionnaire_callback
        )

    def _fill_questionnaire_callback(self):
        """Callback to execute SeleniumScrapingTool for form filling."""
        agent = self.form_handler()

        if not agent.tools:
            return "❌ ERROR: No tools connected to the form handler agent."

        scraping_tool = next((tool for tool in agent.tools if isinstance(tool, SeleniumScrapingTool)), None)
        if not scraping_tool:
            return "❌ ERROR: SeleniumScrapingTool not found."

        try:
            print("📝 Filling the questionnaire using SeleniumScrapingTool...")
            result = scraping_tool.run()

            return "✅ Questionnaire successfully filled." if result else "❌ Failed to fill the questionnaire."
        except Exception as e:
            return f"❌ Error while filling questionnaire: {str(e)}"

    @task
    def verify_submission(self) -> Task:
        return Task(
            description="Submit the completed questionnaire and verify the submission.",
            expected_output="A status report with submission confirmation or error details.",
            agent=self.verification_agent(),
            tools=[SeleniumScrapingTool()],
            callback=self._verify_submission_callback,
            output_file='output/submission_report.md',
            feedback=True,
            feedback_message="✅ Submission verified and report generated."
        )

    def _verify_submission_callback(self):
        """Callback to execute SeleniumScrapingTool for submission verification."""
        submission_page_url = "https://example-university.edu/sports/recruiting/confirmation"
        confirmation_message_selector = ".submission-confirmation"
        agent = self.verification_agent()

        if not agent.tools:
            return "❌ ERROR: No tools connected to the verification agent."

        scraping_tool = next((tool for tool in agent.tools if isinstance(tool, SeleniumScrapingTool)), None)
        if not scraping_tool:
            return "❌ ERROR: SeleniumScrapingTool not found."

        try:
            scraping_tool.website_url = submission_page_url
            scraping_tool.css_element = confirmation_message_selector

            print(f"🔍 Running SeleniumScrapingTool on {submission_page_url}")
            result = scraping_tool.run(
                website_url=submission_page_url,
                css_element=confirmation_message_selector
            )

            if not result:
                return "❌ ERROR: Tool execution failed. No result returned."

            print(f"📄 Tool Result: {result}")
            return "✅ Form submission successful!" if "Success" in result or "Thank you" in result else f"❌ Submission failed. Response: {result}"
        except Exception as e:
            return f"❌ Error during tool execution: {str(e)}"

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
