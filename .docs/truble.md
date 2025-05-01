# CrewAI Flow 관련 트러블슈팅 가이드

## 1. StateWithId 객체에 outline 필드가 없는 문제

### 에러 내용

```
목차 파일 읽기 오류: "StateWithId" object has no field "outline"
에러 타입: ValueError
상세 에러 내역:
Traceback (most recent call last):
  File "/Users/kimdonggeon/programming/agent_paper/src/agent_paper/main.py", line 65, in section_loop
    self.state.outline = OutlineStructure.model_validate(outline_data)
    ^^^^^^^^^^^^^^^^^^
  File "/Users/kimdonggeon/programming/agent_paper/.venv/lib/python3.12/site-packages/pydantic/main.py", line 1000, in __setattr__
    elif (setattr_handler := self._setattr_handler(name, value)) is not None:
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/kimdonggeon/programming/agent_paper/.venv/lib/python3.12/site-packages/pydantic/main.py", line 1047, in _setattr_handler
    raise ValueError(f'"{cls.__name__}" object has no field "{name}"')
ValueError: "StateWithId" object has no field "outline"
```

### 원인

CrewAI Flow의 state 타입인 `StateWithId`에 `outline` 필드가 정의되어 있지 않았습니다. Flow 클래스를 상속할 때 제네릭 타입으로 적절한 상태 클래스를 지정해야 합니다.

### 해결 방법

1. 적절한 상태 클래스(`AgentPaperState`)를 생성하고 필요한 필드를 정의합니다:

   ```python
   class AgentPaperState(BaseModel):
       outline: Optional[OutlineStructure] = None
       id: Optional[str] = None  # CrewAI Flow에서 자동으로 할당하는 ID 필드
   ```

2. `AgentPaperFlow` 클래스가 `Flow[AgentPaperState]`를 상속하도록 수정합니다:

   ```python
   class AgentPaperFlow(Flow[AgentPaperState]):
       # ...
   ```

3. 초기 상태를 적절히 설정합니다:
   ```python
   initial_state = AgentPaperState(outline=OutlineStructure(title="", sections=[]))
   flow = AgentPaperFlow(initial_state=initial_state)
   ```

## 2. flow.state 속성에 setter가 없는 문제

### 에러 내용

```
목차 파일 읽기 오류: property 'state' of 'AgentPaperFlow' object has no setter
에러 타입: AttributeError
상세 에러 내역:
Traceback (most recent call last):
  File "/Users/kimdonggeon/programming/agent_paper/src/agent_paper/main.py", line 70, in section_loop
    self.state = AgentPaperState(id=self.state.id, outline=outline_obj)
    ^^^^^^^^^^
AttributeError: property 'state' of 'AgentPaperFlow' object has no setter
```

### 원인

CrewAI Flow에서 `state` 속성은 property로 구현되어 있어서 직접 값을 할당(`self.state = ...`)할 수 없습니다.

### 해결 방법

`state` 객체의 내부 딕셔너리를 직접 수정하여 우회합니다:

```python
# state의 outline 필드 업데이트
self.state.__dict__["outline"] = outline_obj
```

## 3. Crew.kickoff() 호출 시 인자 형식 오류

### 에러 내용

```
목차 파일 읽기 오류: Crew.kickoff() got an unexpected keyword argument 'section_title'
에러 타입: TypeError
상세 에러 내역:
Traceback (most recent call last):
  File "/Users/kimdonggeon/programming/agent_paper/src/agent_paper/main.py", line 93, in section_loop
    result = SectionLoop().crew().kickoff(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: Crew.kickoff() got an unexpected keyword argument 'section_title'
```

### 원인

CrewAI의 `Crew.kickoff()` 메서드는 개별 인자가 아닌 `inputs` 딕셔너리를 통해 데이터를 전달받아야 합니다.

### 해결 방법

`kickoff()` 호출 시 `inputs` 인자에 딕셔너리를 전달합니다:

```python
result = SectionLoop().crew().kickoff(inputs={
    "section_title": section.title,
    "section_description": section.why,
    "previous_sections": previous_sections_text
})
```

## 4. 템플릿 변수 누락 오류

### 에러 내용

```
목차 파일 읽기 오류: Missing required template variable 'Template variable 'draft_content' not found in inputs dictionary' in description
에러 타입: ValueError
상세 에러 내역:
Traceback (most recent call last):
  File "/Users/kimdonggeon/programming/agent_paper/.venv/lib/python3.12/site-packages/crewai/task.py", line 512, in interpolate_inputs_and_add_conversation_history
    self.description = interpolate_only(
                       ^^^^^^^^^^^^^^^^^
  File "/Users/kimdonggeon/programming/agent_paper/.venv/lib/python3.12/site-packages/crewai/utilities/string_utils.py", line 71, in interpolate_only
    raise KeyError(
KeyError: "Template variable 'draft_content' not found in inputs dictionary"
```

### 원인

`SectionLoop` 클래스의 작업 정의에서 `{draft_content}` 템플릿 변수를 사용하고 있는데, `kickoff()` 호출 시 이 변수가 제공되지 않았습니다.

### 해결 방법

`inputs` 딕셔너리에 필수 템플릿 변수를 추가합니다:

```python
result = SectionLoop().crew().kickoff(inputs={
    "section_title": section.title,
    "section_description": section.why,
    "previous_sections": previous_sections_text,
    "draft_content": "",  # 초안 내용은 처음에는 비어 있음
})
```

## 5. 리스트 인덱싱 오류

### 에러 내용

```
목차 파일 읽기 오류: list indices must be integers or slices, not str
에러 타입: TypeError
상세 에러 내역:
Traceback (most recent call last):
  File "/Users/kimdonggeon/programming/agent_paper/src/agent_paper/main.py", line 102, in section_loop
    completed_sections.append(section)
TypeError: list indices must be integers or slices, not str
```

### 원인

`self.state.outline.sections`가 리스트인데 문자열 ID(`section.id`)를 인덱스로 사용하려고 시도했습니다. 리스트는 정수 인덱스만 허용합니다.

### 해결 방법

1. 결과를 섹션 객체의 content 필드에 직접 저장합니다:

   ```python
   # 결과를 섹션의 content 필드에 저장
   section.content = result.raw
   ```

2. 또한 completed_sections에 추가할 때 안전하게 처리합니다:
   ```python
   # 이전 섹션 내용을 표시할 때 content 필드가 있는지 확인
   if hasattr(completed_section, 'content') and completed_section.content:
       previous_sections_text += f"{completed_section.content}\n\n"
   ```

## 일반적인 CrewAI Flow 사용 팁

1. **적절한 상태 클래스 정의**: Flow 클래스를 상속할 때 필요한 모든 필드를 포함하는 상태 클래스를 정의하고, 이를 제네릭 타입으로 지정하세요.

2. **state 속성 직접 수정 지양**: `self.state = ...`와 같이 직접 할당하지 말고, `self.state.field = value`와 같이 개별 필드를 수정하세요.

3. **Crew.kickoff() 호출 형식 준수**: 항상 `inputs` 딕셔너리를 통해 데이터를 전달하세요.

4. **템플릿 변수 확인**: Crew 및 Task 정의에서 사용하는 모든 템플릿 변수를 `inputs` 딕셔너리에 제공하세요.

5. **오류 메시지 활용**: 오류 메시지에는 대부분 해결 방법에 대한 힌트가 포함되어 있습니다. 메시지를 자세히 분석하여 문제의 원인을 파악하세요.
