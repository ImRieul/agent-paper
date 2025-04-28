from pydantic import BaseModel

from crewai.flow import Flow, listen, start, router

from agent_paper.crews import Analysis, Initialize, Outline


class AgentPaperFlow(Flow):
    @start()
    def initialize(self):
        initialize_crew = Initialize().crew()
        return initialize_crew.kickoff()

    @listen(initialize)
    def analysis(self, previous_value: str):
        analysis_crew = Analysis().crew()
        return analysis_crew.kickoff()

    @router(analysis)
    def analysis_router(self, previous_value: str):
        return "outline"

    @listen(analysis_router)
    def outline(self):
        outline_crew = Outline().crew()
        return outline_crew.kickoff()

        # @listen(outline)
        # def section_loop(self, previous_value: str):
        #     pass
        # @listen(section_loop)
        # def assemble(self, previous_value: str):
        #     pass


if __name__ == "__main__":
    flow = AgentPaperFlow()
    flow.kickoff()
