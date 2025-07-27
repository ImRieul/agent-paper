# Agent Paper Crew

Agent Paper는 [CrewAI](https://crewai.com)를 활용한 다중 에이전트 AI 시스템으로, AI 에이전트들이 협업하여 자동으로 연구 논문을 작성할 수 있는 프로젝트입니다. 이 시스템은 초기화, 분석, 개요 작성, 섹션별 작성 등의 단계를 통해 체계적으로 문서를 생성합니다.

## 📚 문서

- **[시스템 아키텍처](docs/architecture.md)** - 전체 시스템 설계와 워크플로우 상세 설명
- **[개발자 가이드](docs/development-guide.md)** - 개발 환경 설정, 코드 구조, 확장 방법
- **[API 레퍼런스](docs/api-reference.md)** - 모든 클래스, 메서드, 함수의 상세 문서

## 🚀 빠른 시작

### 1. 설치

이 프로젝트를 실행하기 위해서는 Python 3.10 이상, 3.13 미만의 버전이 필요합니다. 의존성 관리를 위해 [UV](https://docs.astral.sh/uv/)를 사용합니다.

```bash
# UV 설치
pip install uv

# 의존성 설치
crewai install
```

### 2. 환경 설정

**`.env.sample` 파일을 복사하여 `.env` 파일을 만들고 `OPENAI_API_KEY`를 추가하세요**

```bash
cp .env.sample .env
# .env 파일에 OPENAI_API_KEY 추가
```

### 3. 실행

```bash
crewai run
```

## 🔄 워크플로우 개요

Agent Paper는 다음 5단계로 작동합니다:

```
Initialize → Analysis → Outline → Section Loop → Assemble
    ↓          ↓          ↓           ↓           ↓
 요구사항     주제분석    구조설계    섹션작성    최종조립
```

1. **Initialize (초기화)**: 사용자 요구사항 수집
2. **Analysis (분석)**: 주제에 대한 심층 분석 수행
3. **Outline (개요)**: 문서 구조와 섹션 정의
4. **Section Loop (섹션 작성)**: 각 섹션 내용을 AI가 순차 작성
5. **Assemble (조립)**: 모든 섹션을 통합하여 최종 문서 생성

실행 결과로 `output/guide.md` 파일이 생성됩니다.

## 📂 프로젝트 구조

```
agent_paper/
├── src/
│   ├── config.py                   # 프로젝트 설정
│   └── agent_paper/
│       ├── main.py                 # 메인 워크플로우
│       ├── state.py                # 상태 관리
│       ├── crews/                  # AI 에이전트 그룹
│       │   ├── initialize/         # 초기화
│       │   ├── analysis/           # 분석
│       │   ├── outline/            # 개요 작성
│       │   ├── section_loop/       # 섹션 작성
│       │   └── assemble/           # 조립
│       └── tools/                  # 커스텀 도구
├── docs/                           # 개발자 문서
├── output/                         # 생성된 파일들
└── README.md
```

## 🛠️ 커스터마이징

### 에이전트 설정 수정

`src/agent_paper/crews/` 디렉토리 내의 각 crew 폴더에서 YAML 설정 파일을 수정하여 에이전트의 역할, 목표, 백스토리를 조정할 수 있습니다.

### 워크플로우 조정

`src/agent_paper/main.py` 파일을 수정하여 워크플로우의 단계나 로직을 변경할 수 있습니다.

### 출력 경로 설정

`src/config.py` 파일에서 출력 디렉토리와 파일 경로를 설정할 수 있습니다.

## 🔧 고급 사용법

자세한 개발 가이드, API 문서, 시스템 아키텍처에 대해서는 위의 문서 링크를 참조하세요:

- 새로운 에이전트 추가 방법: [개발자 가이드](docs/development-guide.md#새로운-에이전트-추가)
- 커스텀 도구 개발: [개발자 가이드](docs/development-guide.md#커스텀-도구-개발)
- 상태 관리 확장: [API 레퍼런스](docs/api-reference.md#상태-관리-모델)
- 워크플로우 이해: [시스템 아키텍처](docs/architecture.md#워크플로우-상세)

## 🤝 기여하기

프로젝트에 기여하고 싶으시다면:

1. 이슈를 생성하여 기능 요청이나 버그를 리포트하세요
2. 포크 후 브랜치를 생성하세요 (`feature/amazing-feature`)
3. 변경 사항을 커밋하세요 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시하세요 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성하세요

자세한 기여 가이드라인은 [개발자 가이드](docs/development-guide.md#기여-워크플로우)를 참조하세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 💡 지원

문제가 발생하거나 질문이 있으시면:

- 이슈를 생성하세요
- [시스템 아키텍처](docs/architecture.md) 문서를 확인하세요
- [개발자 가이드](docs/development-guide.md)의 디버깅 섹션을 참조하세요
