import json
import os
import sys
from typing import List
from pathlib import Path

from pydantic import BaseModel

from crewai.flow import Flow, listen, start, router

from agent_paper.crews import Analysis, Initialize, Outline
from agent_paper.crews.section_loop.section_loop import SectionLoop
from agent_paper.state import OutlineSection, OutlineStructure, AgentPaperState

# 프로젝트 설정 가져오기
from src.config import GUIDE_PATH, OUTPUT_DIR


class AgentPaperFlow(Flow[AgentPaperState]):
    @start()
    def initialize(self):
        if Path(f"{OUTPUT_DIR}/requirements.md").exists():
            print("이미 생성된 목차 파일이나 요구사항 파일이 있습니다. 초기화 단계를 건너뜁니다.")
            return "analysis"

        initialize_crew = Initialize().crew()
        return initialize_crew.kickoff()

    @listen(initialize)
    def analysis(self, previous_value: str):
        if Path(f"{OUTPUT_DIR}/analysis_result.md").exists() and Path(f"{OUTPUT_DIR}/analysis_summary.md").exists():
            print("이미 생성된 목차 파일이나 요구사항 파일이 있습니다. 초기화 단계를 건너뜁니다.")
            return "analysis"

        analysis_crew = Analysis().crew()
        return analysis_crew.kickoff()

    @router(analysis)
    def analysis_router(self, previous_value: str):
        return "outline"

    @listen(analysis_router)
    def outline(self):
        if Path(f"{OUTPUT_DIR}/outline.json").exists():
            print("이미 목차 파일이 있습니다. 섹션 루프 단계를 건너뜁니다.")
            return "section_loop"

        outline_crew = Outline().crew()
        return outline_crew.kickoff()

    @listen(outline)
    def section_loop(self, previous_value: str):

        # 파일이 존재하는지 확인
        if not Path(f"{OUTPUT_DIR}/outline.json").exists():
            print("목차 파일을 찾을 수 없습니다.")
            return "목차 파일 없음"

        # JSON 파일 읽기
        try:
            with open(f"{OUTPUT_DIR}/outline.json", 'r', encoding='utf-8') as file:
                outline_data = json.load(file)

            # OutlineStructure 모델로 변환
            outline_obj = OutlineStructure.model_validate(outline_data)

            # state의 outline 필드 업데이트
            self.state.__dict__["outline"] = outline_obj

            print(
                f"목차를 성공적으로 로드했습니다. 총 {len(self.state.outline.sections)}개 섹션이 있습니다.")

            # 여기서 outline 객체를 활용하여 추가 작업 수행 가능
            completed_sections = []

            # 각 섹션에 대한 작업 수행
            for i, section in enumerate(self.state.outline.sections):

                # 임시로 10개 작업만 수행
                if len(completed_sections) >= 10:
                    break

                previous_sections_text: str = ""

                if not completed_sections:
                    previous_sections_text = "이전에 작성된 섹션이 없습니다."
                else:
                    previous_sections_text = "# 이전에 작성된 섹션\n\n"
                    for completed_section in completed_sections:
                        previous_sections_text += f"## {completed_section.title}\n\n"
                        if hasattr(completed_section, 'content') and completed_section.content:
                            previous_sections_text += f"{completed_section.content}\n\n"

                # SectionLoop가 draft_content를 필요로 하므로 빈 문자열로 추가
                result = SectionLoop().crew().kickoff(inputs={
                    "section_title": section.title,
                    "section_description": section.why,
                    "previous_sections": previous_sections_text,
                    "draft_content": ""  # 초안 내용은 처음에는 비어 있음
                })

                # 결과를 섹션의 content 필드에 저장
                section.content = result.raw
                # 섹션 객체를 completed_sections에 추가
                completed_sections.append(section)

                print(f"섹션 {section.title} 작성 완료")

            # 최종 안내서 작성
            guide_content = f"# {self.state.outline.title}\n\n"

            # 모든 섹션의 내용을 추가
            for section in self.state.outline.sections:
                guide_content += f"## {section.title}\n\n"
                if hasattr(section, 'content') and section.content:
                    guide_content += f"{section.content}\n\n"
                else:
                    guide_content += "이 섹션의 내용이 아직 작성되지 않았습니다.\n\n"

            # 안내서 저장
            with open(GUIDE_PATH, 'w', encoding='utf-8') as file:
                file.write(guide_content)

            # 처리된 결과를 확인할 수 있도록 출력
            print(f"\n안내서가 {GUIDE_PATH}에 저장되었습니다.")
            print(f"총 {len(completed_sections)}개 섹션이 작성되었습니다.")

            # 각 섹션 제목과 내용 길이 출력
            for section in completed_sections:
                content_length = len(section.content) if hasattr(
                    section, 'content') and section.content else 0
                print(f"- {section.title}: {content_length}자")

            return self.state.outline
        except Exception as e:
            print(f"목차 파일 읽기 오류: {str(e)}")
            print(f"에러 타입: {type(e).__name__}")
            import traceback
            print(f"상세 에러 내역:\n{traceback.format_exc()}")
            return f"목차 파일 읽기 오류: {str(e)}, 에러 타입: {type(e).__name__}"

    # @listen(section_loop)
    # def assemble(self, previous_value: str):
    #     pass


def make_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        print("output 폴더가 존재하지 않습니다. 새로 생성합니다.")
        os.makedirs(OUTPUT_DIR)
    else:
        print("output 폴더가 이미 존재합니다.")


def kickoff():
    make_output_dir()
    # 기본 상태 정의 - 비어 있는 AgentPaperState 객체
    initial_state = AgentPaperState(
        outline=OutlineStructure(title="", sections=[]))
    flow = AgentPaperFlow(initial_state=initial_state)
    flow.kickoff()


if __name__ == "__main__":
    kickoff()
