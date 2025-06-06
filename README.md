# 🧠 세상에 나쁜 프롬프트는 없다.

**LLM 기반 워크플로우에서 프롬프트 성능을 자동으로 평가하는 멀티 에이전트 프레임워크**  

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./src/langgraph_studio_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="./src/langgraph_studio_light.png">
  <img alt="LangGraph Studio" src="http://LIGHT_IMAGE_URL.png">
</picture>



<br/>
<br/>

## 📌 개요

> _"세상에 나쁜 프롬프트는 없다 — 평가받지 않은 프롬프트만 있을 뿐이다."_

`no-bad-prompts`는 LLM(대형 언어 모델) 기반 도구에서 사용되는 **프롬프트의 품질을 자동으로 평가**하는 시스템입니다. 기존에는 프롬프트를 실행해 결과를 눈으로 확인하는 수작업이 필요했지만, 이 프로젝트는 LangGraph 기반의 구조화된 평가 플로우를 통해 반복 검증 과정을 자동화합니다.

프롬프트 품질 관리, 리그레션 테스트, 실험 비교 등에 유용하게 사용할 수 있습니다.



<br/>
<br/>

## ⚙️ 아키텍처

> 🧩 노드 간의 책임을 분리함으로써 평가의 **객관성**과 **재현성**을 확보합니다.

이 시스템은 **Planner → Executor → Evaluator** 구조로 구성됩니다.

### 1. Planner 노드
- **입력:** 전체 프롬프트 전문
- **역할:** 평가 기준(예: 적절성, 정확성, 간결성 등)을 동적으로 추출
- **출력:** 평가 지표 리스트

### 2. Executor 노드
- **입력:** 프롬프트 전문
- **역할:** LLM을 호출해 결과 생성
- **출력:** LLM 응답 결과

### 3. Evaluator 노드
- **입력:** Planner에서 생성한 평가 기준 + Executor의 결과물
- **역할:** 프롬프트를 모른 채 결과물만을 기반으로 평가 수행
- **출력:** 평가 점수 및 피드백

<br/>
<br/>

## 프로젝트 구조

```
.
├── main.py                # 진입점
├── src/
│   ├── graph.py           # 워크플로우의 핵심 로직
│   ├── prompt.py          # 프롬프트
│   ├── node.py            # 노드 함수
│   └── state.py           # 상태 정의
├── .example.env           # 환경 변수 예시 파일
├── pyproject.toml         # 프로젝트 메타데이터 및 의존성
├── langgraph.json         # LangGraph 설정 파일
└── README.md
```

<br/>
<br/>

## 기술 스택

- Python 3.12+
- [LangChain](https://python.langchain.com/)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [OpenAI GPT-4o-mini](https://platform.openai.com/docs/models/gpt-4o)
- python-dotenv

<br/>
<br/>

## 🚀 시작하기

### 요구 사항

- Python 3.10 이상
- LangGraph
- LangChain
- OpenAI API
- `python-dotenv` (환경 변수 관리)

### 설치

```bash
git clone https://github.com/your-org/no-bad-prompts.git
cd no-bad-prompts
pip install -r requirements.txt
```

<br/>
<br/>


## 설치 및 실행 방법

### 1. 의존성 설치

Python 3.12 이상이 필요합니다.

```bash
pip install -r requirements.txt
```
또는
```bash
pip install .
```

### 2. 환경 변수 설정

OpenAI API 키가 필요합니다.

```bash
cp .example.env .env
# .env 파일에 OPENAI_API_KEY를 입력하세요.
```

### 3. 실행

LangGraph 개발 서버를 실행합니다.

```bash
langgraph dev
```

<br/>
<br/>

## 사용 예시

1. 프롬프트를 입력하면, 시스템이 자동으로 평가 가능 여부를 진단합니다.
2. 평가가 가능하면, 프롬프트에 맞는 평가 기준을 생성합니다.
3. 프롬프트 실행 결과를 바탕으로 각 항목별 점수와 상세 피드백을 제공합니다.
4. 정보가 부족하면, 추가 정보를 요청하는 대화가 진행됩니다.

<br/>
<br/>

## 기여

- maintainer: [your-email@example.com]
