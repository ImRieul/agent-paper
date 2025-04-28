from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from crewai_tools import DirectoryReadTool, FileReadTool

from agent_paper.tools.custom_tool import DataReadToDataFrameTool


@CrewBase
class Analysis():
    """Analysis crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # dataReadToDataFrameTool = DataReAadToDataFrameTool('output')

    directory_read_tool = DirectoryReadTool(directory='output')
    file_read_tool = FileReadTool()

    @agent
    def analysis_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['analysis_agent'],
            verbose=True,
            tools=[self.directory_read_tool, self.file_read_tool],
        )

    @agent
    def analysis_summary_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['analysis_summary_agent'],
            verbose=True,
            tools=[self.directory_read_tool, self.file_read_tool],
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'],
            human_input=True
        )

    @task
    def analysis_summary_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_summary_task'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Analysis crew"""

        return Crew(
            agents=[self.analysis_agent(), self.analysis_summary_agent()],
            tasks=[self.analysis_task(), self.analysis_summary_task()],
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
