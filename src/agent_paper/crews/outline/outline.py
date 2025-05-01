from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class Outline():
    """Outline crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def outline_creator(self) -> Agent:
        return Agent(
            config=self.agents_config['outline_creator'],
            verbose=True
        )

    @agent
    def outline_describer(self) -> Agent:
        return Agent(
            config=self.agents_config['outline_describer'],
            verbose=True
        )

    @task
    def outline_creation_task(self) -> Task:
        return Task(
            config=self.tasks_config['outline_creation_task'],
        )

    @task
    def outline_description_task(self) -> Task:
        return Task(
            config=self.tasks_config['outline_description_task'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Outline crew"""
        return Crew(
            agents=[self.outline_creator(), self.outline_describer()],
            tasks=[self.outline_creation_task(), self.outline_description_task()],
            process=Process.sequential,
            verbose=True,
        )
