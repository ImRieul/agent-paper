from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class Initialize():
    """Initialize crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def requirements_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['requirements_agent'],
            verbose=True
        )

    @task
    def requirements_task(self) -> Task:
        return Task(
            config=self.tasks_config['requirements_task'],
            human_input=True,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Initialize crew"""

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
