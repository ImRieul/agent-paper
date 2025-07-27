# 시스템 아키텍처

Agent Paper는 CrewAI 프레임워크를 기반으로 한 다중 에이전트 AI 시스템입니다. 이 문서는 시스템의 전체 아키텍처와 워크플로우를 설명합니다.

## 🏗️ 전체 아키텍처

### 시스템 개요

Agent Paper는 **Flow 패턴**을 사용하여 다중 에이전트가 순차적으로 협업하는 구조로 설계되었습니다. 각 단계는 이전 단계의 결과를 입력으로 받아 처리하며, 최종적으로 완성된 연구 문서를 생성합니다.

```
[Initialize] → [Analysis] → [Outline] → [Section Loop] → [Assemble]
     ↓             ↓           ↓           ↓              ↓
  요구사항 정의   주제 분석    구조 설계   섹션별 작성    최종 조립
```

### 핵심 구성 요소

#### 1. Flow 컨트롤러 (`AgentPaperFlow`)

- 전체 워크플로우를 관리하는 중앙 컨트롤러
- CrewAI의 Flow 클래스를 상속받아 구현
- 각 단계 간의 데이터 전달과 상태 관리를 담당

#### 2. 상태 관리 (`AgentPaperState`)

- 워크플로우 전체에서 공유되는 상태 정보
- Pydantic 모델을 사용한 타입 안정성 보장
- 목차 구조와 메타데이터 저장

#### 3. 에이전트 Crews

- 각 단계별로 특화된 AI 에이전트 그룹
- YAML 설정 파일을 통한 에이전트 구성 관리
- 독립적인 실행 단위로 모듈화

## 🔄 워크플로우 상세

### 1단계: Initialize (초기화)

**목적**: 사용자의 요구사항을 수집하고 기본 설정을 정의

- **에이전트**: `requirements_agent`
- **입력**: 사용자의 직접 입력 (human_input=True)
- **출력**: `requirements.md` 파일
- **건너뛰기 조건**: 기존 요구사항 파일이 존재할 경우

```python
@start()
def initialize(self):
    if Path(f"{OUTPUT_DIR}/requirements.md").exists():
        return "analysis"
    initialize_crew = Initialize().crew()
    return initialize_crew.kickoff()
```

### 2단계: Analysis (분석)

**목적**: 요구사항을 기반으로 주제를 심층 분석

- **입력**: 이전 단계의 요구사항 정보
- **출력**:
  - `analysis_result.md` - 상세 분석 결과
  - `analysis_summary.md` - 분석 요약
- **건너뛰기 조건**: 기존 분석 파일들이 존재할 경우

### 3단계: Outline (개요 작성)

**목적**: 문서의 전체 구조와 각 섹션을 정의

- **입력**: 분석 결과
- **출력**: `outline.json` - 구조화된 목차 정보
- **데이터 모델**: `OutlineStructure`
- **건너뛰기 조건**: 기존 목차 파일이 존재할 경우

```python
class OutlineStructure(BaseModel):
    title: str = ""
    sections: List[OutlineSection] = Field(default_factory=list)
    review: Optional[OutlineReview] = None
```

### 4단계: Section Loop (섹션별 작성)

**목적**: 정의된 각 섹션의 내용을 순차적으로 작성

- **입력**:
  - 목차 구조 (`outline.json`)
  - 이전에 작성된 섹션들의 컨텍스트
- **처리 방식**:
  - 각 섹션을 순차적으로 처리
  - 현재 제한: 최대 10개 섹션
  - 컨텍스트 유지를 위해 이전 섹션 내용 전달
- **출력**: 각 섹션의 완성된 내용

```python
for i, section in enumerate(self.state.outline.sections):
    if len(completed_sections) >= 10:
        break

    result = SectionLoop().crew().kickoff(inputs={
        "section_title": section.title,
        "section_description": section.why,
        "previous_sections": previous_sections_text,
        "draft_content": ""
    })

    section.content = result.raw
    completed_sections.append(section)
```

### 5단계: Assemble (최종 조립) - 현재 비활성화

**목적**: 모든 섹션을 조합하여 최종 문서를 생성

- **현재 상태**: 주석 처리됨
- **대안**: Section Loop 단계에서 직접 `guide.md` 생성

## 📁 데이터 플로우

### 파일 시스템 구조

```
output/
├── requirements.md      # 1단계 출력
├── analysis_result.md   # 2단계 출력
├── analysis_summary.md  # 2단계 출력
├── outline.json        # 3단계 출력
└── guide.md           # 최종 출력
```

### 상태 전달 메커니즘

1. **파일 기반 상태 저장**: 각 단계의 결과를 파일로 저장
2. **메모리 상태 관리**: `AgentPaperState`를 통한 런타임 상태 관리
3. **건너뛰기 로직**: 기존 파일 존재 시 해당 단계 생략

## 🔧 기술적 특징

### CrewAI Flow 패턴 활용

- `@start()`: 워크플로우 시작점 정의
- `@listen()`: 이전 단계 완료 감지
- `@router()`: 조건부 라우팅 (현재 단순 전달)

### 상태 관리 패턴

- Pydantic 모델을 통한 타입 안전성
- JSON 직렬화를 통한 영속성 보장
- 선택적 필드를 통한 유연성 제공

### 확장성 고려사항

- 각 crew는 독립적인 모듈로 구성
- YAML 설정을 통한 에이전트 구성의 외부화
- 플러그인 방식의 도구 시스템

## 🚀 성능 및 최적화

### 현재 제한사항

- Section Loop에서 최대 10개 섹션 제한
- 순차 처리로 인한 시간 소요
- 메모리 상주를 통한 컨텍스트 유지

### 개선 가능 영역

- 병렬 섹션 처리
- 캐싱 메커니즘 도입
- 중간 결과 체크포인팅
