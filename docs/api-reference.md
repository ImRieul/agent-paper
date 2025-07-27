# API 레퍼런스

이 문서는 Agent Paper 시스템의 모든 클래스, 메서드, 함수에 대한 상세한 API 문서입니다.

## 📋 목차

- [워크플로우 클래스](#워크플로우-클래스)
- [상태 관리 모델](#상태-관리-모델)
- [에이전트 Crews](#에이전트-crews)
- [커스텀 도구](#커스텀-도구)
- [설정 및 유틸리티](#설정-및-유틸리티)

## 워크플로우 클래스

### `AgentPaperFlow`

메인 워크플로우를 관리하는 클래스입니다.

```python
class AgentPaperFlow(Flow[AgentPaperState])
```

#### 메서드

##### `initialize()`

워크플로우의 첫 번째 단계를 실행합니다.

```python
@start()
def initialize(self) -> str
```

**반환값:**

- `str`: 다음 단계 이름 또는 결과

**동작:**

- `{OUTPUT_DIR}/requirements.md` 파일 존재 확인
- 파일이 있으면 "analysis" 반환 (건너뛰기)
- 없으면 Initialize crew 실행

##### `analysis(previous_value: str)`

주제 분석 단계를 실행합니다.

```python
@listen(initialize)
def analysis(self, previous_value: str) -> str
```

**파라미터:**

- `previous_value` (str): 이전 단계의 결과

**반환값:**

- `str`: 분석 결과 또는 다음 단계 이름

**동작:**

- 분석 결과 파일들 존재 확인
- Analysis crew 실행

##### `outline()`

문서 구조 설계 단계를 실행합니다.

```python
@listen(analysis_router)
def outline(self) -> str
```

**반환값:**

- `str`: 목차 생성 결과

**동작:**

- `outline.json` 파일 존재 확인
- Outline crew 실행

##### `section_loop(previous_value: str)`

각 섹션을 순차적으로 작성하는 단계입니다.

```python
@listen(outline)
def section_loop(self, previous_value: str) -> OutlineStructure | str
```

**파라미터:**

- `previous_value` (str): 이전 단계의 결과

**반환값:**

- `OutlineStructure`: 완성된 목차 구조
- `str`: 오류 메시지

**동작:**

- `outline.json` 파일 로드
- 각 섹션에 대해 SectionLoop crew 실행 (최대 10개)
- 완성된 내용을 `guide.md`로 저장

## 상태 관리 모델

### `AgentPaperState`

워크플로우 전체의 상태를 관리하는 모델입니다.

```python
class AgentPaperState(BaseModel):
    outline: Optional[OutlineStructure] = None
    id: Optional[str] = None
```

**필드:**

- `outline` (OutlineStructure, optional): 문서의 목차 구조
- `id` (str, optional): CrewAI Flow에서 자동 할당되는 ID

### `OutlineStructure`

문서의 전체 구조를 정의하는 모델입니다.

```python
class OutlineStructure(BaseModel):
    title: str = ""
    sections: List[OutlineSection] = Field(default_factory=list)
    review: Optional[OutlineReview] = None
```

**필드:**

- `title` (str): 문서의 제목
- `sections` (List[OutlineSection]): 섹션들의 목록
- `review` (OutlineReview, optional): 목차 검토 결과

### `OutlineSection`

개별 섹션의 정보를 담는 모델입니다.

```python
class OutlineSection(BaseModel):
    id: str
    title: str
    why: str
    how: Optional[str] = None
    data: Optional[str] = None
    subsections: List[T] = Field(default_factory=list)
    content: Optional[str] = None
```

**필드:**

- `id` (str): 섹션의 고유 식별자
- `title` (str): 섹션 제목
- `why` (str): 섹션의 목적과 중요성
- `how` (str, optional): 섹션 작성 방법
- `data` (str, optional): 섹션 관련 데이터
- `subsections` (List[OutlineSection]): 하위 섹션들
- `content` (str, optional): 실제 작성된 내용

### `OutlineReview`

목차 검토 결과를 담는 모델입니다.

```python
class OutlineReview(BaseModel):
    topic_alignment: str
    structure_coherence: str
    completeness: str
```

**필드:**

- `topic_alignment` (str): 주제와의 일치성 평가
- `structure_coherence` (str): 구조적 일관성 평가
- `completeness` (str): 완성도 평가

## 에이전트 Crews

### `Initialize`

초기화 단계를 담당하는 crew입니다.

```python
@CrewBase
class Initialize():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
```

#### 에이전트

##### `requirements_agent()`

요구사항을 수집하는 에이전트입니다.

```python
@agent
def requirements_agent(self) -> Agent
```

**반환값:**

- `Agent`: 설정된 요구사항 수집 에이전트

#### 태스크

##### `requirements_task()`

요구사항 수집 태스크입니다.

```python
@task
def requirements_task(self) -> Task
```

**반환값:**

- `Task`: 사용자 입력을 받는 태스크 (`human_input=True`)

#### Crew

##### `crew()`

Initialize crew를 생성합니다.

```python
@crew
def crew(self) -> Crew
```

**반환값:**

- `Crew`: 순차 처리 방식의 crew

### `Analysis`

주제 분석을 담당하는 crew입니다.

```python
@CrewBase
class Analysis():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
```

**구성:**

- 분석 전문 에이전트
- 요약 생성 에이전트
- 순차적 태스크 실행

### `Outline`

문서 구조 설계를 담당하는 crew입니다.

```python
@CrewBase
class Outline():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
```

**구성:**

- 구조 설계 에이전트
- 검토 에이전트
- JSON 형태의 목차 출력

### `SectionLoop`

개별 섹션 작성을 담당하는 crew입니다.

```python
@CrewBase
class SectionLoop():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
```

**입력 파라미터:**

- `section_title` (str): 작성할 섹션의 제목
- `section_description` (str): 섹션의 목적과 설명
- `previous_sections` (str): 이전에 작성된 섹션들의 내용
- `draft_content` (str): 초안 내용 (보통 빈 문자열)

**출력:**

- 완성된 섹션 내용

## 커스텀 도구

### `MyCustomTool`

기본 커스텀 도구 템플릿입니다.

```python
class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = "Clear description for what this tool is useful for"
    args_schema: Type[BaseModel] = MyCustomToolInput
```

#### 메서드

##### `_run(argument: str)`

도구의 핵심 실행 로직입니다.

```python
def _run(self, argument: str) -> str
```

**파라미터:**

- `argument` (str): 도구 실행을 위한 입력 인수

**반환값:**

- `str`: 도구 실행 결과

### `DataReadToDataFrameTool`

데이터 파일을 읽어 DataFrame으로 변환하는 도구입니다.

```python
class DataReadToDataFrameTool(BaseTool):
    name: str = "Data Reader Tool"
    description: str = "Read data from a file and return a pandas DataFrame"
    args_schema: Type[BaseModel] = FilePathModel
```

#### 메서드

##### `_run(file_path: str)`

파일을 읽어 DataFrame으로 변환합니다.

```python
def _run(self, file_path: str) -> pd.DataFrame
```

**파라미터:**

- `file_path` (str): 읽을 파일의 경로

**반환값:**

- `pd.DataFrame`: 로드된 데이터프레임

**지원 파일 형식:**

- `.csv`: CSV 파일
- `.xlsx`, `.xls`: Excel 파일
- `.json`: JSON 파일
- `.sav`: SPSS 파일

**예외:**

- `ValueError`: 지원하지 않는 파일 형식일 경우

## 설정 및 유틸리티

### 설정 상수 (`config.py`)

#### `PROJECT_ROOT`

프로젝트의 루트 디렉토리 경로입니다.

```python
PROJECT_ROOT: Path
```

#### `OUTPUT_DIR`

출력 파일들이 저장되는 디렉토리 경로입니다.

```python
OUTPUT_DIR: Path = PROJECT_ROOT / "output"
```

#### `OUTLINE_PATH`

목차 JSON 파일의 경로입니다.

```python
OUTLINE_PATH: Path = OUTPUT_DIR / "outline.json"
```

#### `GUIDE_PATH`

최종 가이드 파일의 경로입니다.

```python
GUIDE_PATH: Path = OUTPUT_DIR / "guide.md"
```

### 유틸리티 함수

#### `make_output_dir()`

출력 디렉토리를 생성합니다.

```python
def make_output_dir() -> None
```

**동작:**

- `OUTPUT_DIR`이 존재하지 않으면 생성
- 이미 존재하면 메시지 출력

#### `kickoff()`

전체 워크플로우를 시작합니다.

```python
def kickoff() -> None
```

**동작:**

1. 출력 디렉토리 생성
2. 초기 상태 설정
3. AgentPaperFlow 인스턴스 생성 및 실행

## 🔧 사용 예제

### 기본 워크플로우 실행

```python
from agent_paper.main import kickoff

# 전체 워크플로우 실행
kickoff()
```

### 개별 Crew 실행

```python
from agent_paper.crews import Initialize, Analysis

# 초기화 crew만 실행
init_crew = Initialize().crew()
result = init_crew.kickoff()

# 분석 crew 실행
analysis_crew = Analysis().crew()
analysis_result = analysis_crew.kickoff()
```

### 상태 모델 사용

```python
from agent_paper.state import AgentPaperState, OutlineStructure, OutlineSection

# 새로운 상태 생성
state = AgentPaperState(
    outline=OutlineStructure(
        title="AI 연구 보고서",
        sections=[
            OutlineSection(
                id="intro",
                title="서론",
                why="연구의 배경과 목적을 설명"
            )
        ]
    )
)
```

### 커스텀 도구 사용

```python
from agent_paper.tools.custom_tool import DataReadToDataFrameTool

# 데이터 읽기 도구 사용
tool = DataReadToDataFrameTool()
df = tool._run("data/sample.csv")
```
