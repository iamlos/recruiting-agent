from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import BrowserbaseLoadTool, SeleniumScrapingTool

@CrewBase
class RecruitingCrew():
    """Crew for automating college sports recruiting questionnaire submissions"""

    @agent
    def navigator(self) -> Agent:
        return Agent(
            config=self.agents_config['navigator'],
            verbose=True,
            tools=[BrowserbaseLoadTool()]
        )

    @agent
    def form_handler(self) -> Agent:
        return Agent(
            config=self.agents_config['form_handler'],
            verbose=True,
            tools=[SeleniumScrapingTool()]
        )

    @agent
    def verification_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['verification_agent'],
            verbose=True,
            tools=[SeleniumScrapingTool()]
        )

    @task
    def navigate_to_questionnaire(self) -> Task:
        return Task(
            config=self.tasks_config['navigate_to_questionnaire']
        )

    @task
    def fill_questionnaire(self) -> Task:
        return Task(
            config=self.tasks_config['fill_questionnaire']
        )

    @task
    def verify_submission(self) -> Task:
        return Task(
            config=self.tasks_config['verify_submission'],
            output_file='output/submission_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the recruiting automation crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )