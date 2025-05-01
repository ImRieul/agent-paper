from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from crewai_tools import DirectoryReadTool, FileReadTool


@CrewBase
class SectionLoop():
    """SectionLoop crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    directory_read_tool = DirectoryReadTool(directory='output')
    file_read_tool = FileReadTool()

    @agent
    def content_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['content_writer'],
            verbose=True,
            tools=[self.directory_read_tool, self.file_read_tool],
        )

    @agent
    def content_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['content_reviewer'],
            verbose=True,
            tools=[self.directory_read_tool, self.file_read_tool],
        )

    @task
    def write_section_task(self) -> Task:
        return Task(
            config=self.tasks_config['write_section_task'],
        )

    @task
    def review_section_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_section_task'],
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the SectionLoop crew"""

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
