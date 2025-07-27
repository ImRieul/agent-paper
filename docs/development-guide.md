# 개발자 가이드

이 문서는 Agent Paper 프로젝트에 기여하거나 확장하고자 하는 개발자를 위한 가이드입니다.

## 📂 프로젝트 구조

```
agent_paper/
├── src/
│   ├── config.py                   # 프로젝트 설정
│   └── agent_paper/
│       ├── main.py                 # 메인 워크플로우
│       ├── state.py                # 상태 관리 모델
│       ├── crews/                  # AI 에이전트 그룹
│       │   ├── __init__.py
│       │   ├── initialize/         # 초기화 에이전트
│       │   ├── analysis/           # 분석 에이전트
│       │   ├── outline/            # 개요 작성 에이전트
│       │   ├── section_loop/       # 섹션 작성 에이전트
│       │   └── assemble/           # 조립 에이전트
│       └── tools/                  # 커스텀 도구
│           ├── custom_tool.py
│           └── __init__.py
├── docs/                           # 문서
├── output/                         # 생성된 파일들
├── pyproject.toml                  # 프로젝트 설정
├── uv.lock                         # 의존성 락 파일
└── README.md
```

## 🛠️ 개발 환경 설정

### 1. 요구사항

- Python 3.10 이상, 3.13 미만
- UV 패키지 매니저

### 2. 설치

```bash
# UV 설치
pip install uv

# 프로젝트 클론 후 의존성 설치
cd agent_paper
crewai install

# 환경 변수 설정
cp .env.sample .env
# .env 파일에 OPENAI_API_KEY 추가
```

### 3. 개발 실행

```bash
# 워크플로우 실행
crewai run

# 또는 직접 Python 실행
python src/agent_paper/main.py
```

## 🏗️ 핵심 구성 요소

### 1. Flow 컨트롤러 (`main.py`)

```python
class AgentPaperFlow(Flow[AgentPaperState]):
    # 워크플로우의 각 단계를 데코레이터로 정의
    @start()
    @listen()
    @router()
```

**주요 메서드:**

- `initialize()`: 워크플로우 시작점
- `analysis()`: 주제 분석 단계
- `outline()`: 구조 설계 단계
- `section_loop()`: 섹션별 작성 단계

### 2. 상태 관리 (`state.py`)

```python
class AgentPaperState(BaseModel):
    outline: Optional[OutlineStructure] = None
    id: Optional[str] = None

class OutlineStructure(BaseModel):
    title: str = ""
    sections: List[OutlineSection] = Field(default_factory=list)
    review: Optional[OutlineReview] = None
```

**특징:**

- Pydantic 모델을 사용한 타입 안전성
- JSON 직렬화 지원
- 중첩된 구조로 복잡한 데이터 관리

### 3. Crew 구조

각 crew는 다음과 같은 구조를 가집니다:

```python
@CrewBase
class YourCrew():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def your_agent(self) -> Agent:
        return Agent(config=self.agents_config['your_agent'])

    @task
    def your_task(self) -> Task:
        return Task(config=self.tasks_config['your_task'])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential
        )
```

## 🔧 커스터마이징 및 확장

### 1. 새로운 에이전트 추가

#### 단계 1: Crew 디렉토리 생성

```bash
mkdir src/agent_paper/crews/your_new_crew
cd src/agent_paper/crews/your_new_crew
mkdir config
```

#### 단계 2: 에이전트 클래스 작성

```python
# your_new_crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class YourNewCrew():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def specialist_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['specialist_agent'],
            verbose=True
        )

    @task
    def specialized_task(self) -> Task:
        return Task(
            config=self.tasks_config['specialized_task']
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
```

#### 단계 3: YAML 설정 파일 작성

```yaml
# config/agents.yaml
specialist_agent:
  role: >
    전문 분야 분석가
  goal: >
    특정 영역에 대한 심층 분석을 수행합니다
  backstory: >
    당신은 해당 분야의 전문가로서 상세한 분석을 제공합니다
```

```yaml
# config/tasks.yaml
specialized_task:
  description: >
    주어진 정보를 바탕으로 전문적인 분석을 수행하세요
  expected_output: >
    구조화된 분석 결과와 권장사항
```

#### 단계 4: 워크플로우에 통합

```python
# main.py에 추가
from agent_paper.crews.your_new_crew import YourNewCrew

@listen(previous_step)
def your_new_step(self, previous_value: str):
    new_crew = YourNewCrew().crew()
    return new_crew.kickoff()
```

### 2. 커스텀 도구 개발

```python
# tools/your_custom_tool.py
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class YourToolInput(BaseModel):
    input_param: str = Field(..., description="입력 파라미터 설명")

class YourCustomTool(BaseTool):
    name: str = "Your Tool Name"
    description: str = "도구의 용도와 기능 설명"
    args_schema: Type[BaseModel] = YourToolInput

    def _run(self, input_param: str) -> str:
        # 도구의 핵심 로직 구현
        result = self.process_input(input_param)
        return result

    def process_input(self, input_param: str) -> str:
        # 실제 처리 로직
        return f"처리된 결과: {input_param}"
```

### 3. 상태 모델 확장

```python
# state.py 확장
class ExtendedAgentPaperState(AgentPaperState):
    custom_data: Optional[Dict[str, Any]] = None
    processing_metadata: Optional[ProcessingMetadata] = None

class ProcessingMetadata(BaseModel):
    start_time: datetime
    processing_steps: List[str] = Field(default_factory=list)
    quality_scores: Dict[str, float] = Field(default_factory=dict)
```

## 📋 코딩 컨벤션

### 1. 파일 구조

- 각 crew는 독립적인 디렉토리에 구성
- `config/` 폴더에 YAML 설정 분리
- 클래스명은 PascalCase, 파일명은 snake_case

### 2. 에이전트 설계 원칙

- 단일 책임 원칙: 각 에이전트는 하나의 명확한 역할
- 설정 외부화: 하드코딩 대신 YAML 설정 활용
- 입출력 명세화: 예상 입력과 출력을 명확히 정의

### 3. 오류 처리

```python
try:
    result = crew.kickoff()
    return result
except Exception as e:
    print(f"에러 발생: {str(e)}")
    import traceback
    print(f"상세 에러:\n{traceback.format_exc()}")
    return f"처리 실패: {str(e)}"
```

## 🧪 테스트 및 디버깅

### 1. 개별 Crew 테스트

```python
# test_individual_crew.py
def test_initialize_crew():
    crew = Initialize().crew()
    result = crew.kickoff()
    assert result is not None
    print(f"결과: {result}")
```

### 2. 상태 검증

```python
def validate_state(state: AgentPaperState):
    if state.outline:
        assert len(state.outline.sections) > 0
        for section in state.outline.sections:
            assert section.title
            assert section.why
```

### 3. 디버깅 팁

- `verbose=True` 설정으로 상세 로그 활성화
- 중간 결과 파일들을 확인하여 각 단계 검증
- `output/` 디렉토리의 생성 파일들로 진행 상황 추적

## ⚡ 성능 최적화

### 1. 건너뛰기 로직 활용

```python
def skip_if_exists(file_path: str, next_step: str):
    if Path(file_path).exists():
        print(f"기존 파일 발견, {next_step} 단계로 이동")
        return next_step
```

### 2. 배치 처리 최적화

- Section Loop에서 섹션 수 제한 조정
- 병렬 처리 고려 (향후 개선 사항)

### 3. 메모리 관리

- 대용량 컨텐츠 처리 시 스트리밍 고려
- 중간 결과의 적절한 정리

## 🔄 기여 워크플로우

1. **이슈 생성**: 기능 요청이나 버그 리포트
2. **브랜치 생성**: `feature/your-feature-name`
3. **개발 및 테스트**: 로컬에서 충분한 테스트
4. **커밋**: 명확한 커밋 메시지 작성
5. **Pull Request**: 변경 사항과 테스트 결과 포함

### 커밋 메시지 컨벤션

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 업데이트
refactor: 코드 리팩토링
test: 테스트 추가/수정
```
