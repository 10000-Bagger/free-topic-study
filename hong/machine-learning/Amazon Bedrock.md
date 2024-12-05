# Amazon Bedrock

### Amazon Bedrock 소개

- 기본 모델을 사용하여 생성형 AI 애플리케이션을 구축하고 규모를 조정하는 가장 쉬운 방법
- Amazon Bedrock은 선도적인 AI 회사의 다양한 고성능 파운데이션 모델을 단일 API를 통해 제공하는 완전 관리형 서비스.
- 이 서비스를 사용하면 보안, 개인정보 보호 및 책임형 AI를 포함하여 생성형 AI 애플리케이션을 구축하는 데 필요한 광범위한 기능 세트를 활용함.

Amazon Bedrock 개발자 경험

- 개발자가 다양한 고성능 파운데이션 모델을 손쉽게 사용할 수 있는 Amazon Bedrock
- 주요 FM 중에서 선택
- 다양한 태스크에서 FM을 실험
    - 텍스트, 채팅, 이미지 등 다양한 형식의 대화형 플레이그라운드를 사용하여 다양한 FM을 실험. 플레이그라운드에서 사용 사례에 맞는 다양한 모델을 시험해 봄으로써 주어진 태스크에 모델이 적합한지 확인할 수 있음.

FM을 평가하여 사용 사례에 가장 적합한 FM 선택

- Amazon Bedrock의 모델 평가를 사용하면 자동 및 인적 평가를 사용하여 특정 사용 사례에 맞는 FM을 선택할 수 있음.
- 자동 모델 평가는 큐레이트된 데이터세트를 사용하며 정확성, 경고성, 유해성과 같은 사전 정의된 지표를 제공함.

자체 데이터를 사용하여 FM을 비공개로 사용자 지정

- Amazon bedrock을 사용하면 몇 가지 간단한 단계로 일반 모델을 회사의 비즈니스 및 사용 사례에 맞게 특화되고 사용자 지정된 모델로 전환할 수 있음.
- FM을 특정 태스크에 맞게 조정하려면 미세 조정이라는 기술을 사용하면 됨.
- Amazon S3의 레이블링된 예제 몇 개를 가리키면 Amazon Bedrock이 기본 모델의 사본을 만들고, 데이터로 훈련하고, 사용자만 엑세스할 수 있는 미세 조정된 모델을 생성하므로 사용자 지정된 응답을 받을 수 있음.
- 또한 지속적인 사전 훈련을 사용하는 방법도 있음. 이 기법은 레이블링되지 않은 dataset를 사용하여 도메인 또는 산업에 맞게 FM을 사용자 지정.

Amazn Bedrock이 비즈니스에서 적용되는 부분

- Scales to your needs: 작은 프로젝트부터 대규모 프로젝트까지 빠르게 실행.
- Plug & Play foundation models: FM은 지속적으로 변경됨 (비용, 성능 등 더 개선된 버전이 지속적으로 출시됨) 이런 부분을 즉각적으로 적용할 수 있음.
- Easily deliver RAG patterns: RAG를 쉽게 만들기
- Customize foundation models: RAG, Prompt로 부족한 부분을 직접 학습시킴.
- Orchestrate tasks
- Data remains private & secure

### Use Cases

예제: Octtank Financial, LLC

- Multiple Business units
- Dozens of Product & Engineering teams
- Hundreds of use cases

Amazon Bedrock Use Cases (가장 흔하게 사용되는 Gen AI 작업)

- Q & A
    - 도메인에 따라 수천개 문서에서 정답을 찾아야 함 (모델이 생각하는 정답이 아닌 회사의 정보를 기반으로 답하기)
    - 단계 1: knowledge base 생성
        - Document archive → ingest documents → knowledge base
        - ingest API를 사용해서 Amazon Bedrock에 전달
        - knowlege base = Amazon Titan Text Embeddings (embedding 모델) + Vector Database
        - 예: 100 페이지 PDF → knowledge base가 적절한 chunk size를 구분해서 효율적인 vector를 생성함. → 해당 chunk가 embeddings model에 전달.
        - 단계 2: Customer가 chatbot으로 질문
            - customer → search → knowledge base → Amazon Titan Text Lite → customer
        - 단계 3: Support Associate가 Internal Support Portal로 확인
            - support associate → Order Support Agent (Amazon Bedrock Agent) → Search → policy 검색 → Order Support Agent → Order detais → Orders DB → Support Associate가 적절한 action을 수행함.
    - Key Feature 1: Knowledge Base for Amazon Bedrock
        - Automated Ingestion of the data
        - prompt augmentation (ex: I want to cancel my order → I 가 누구인지, my order가 어떤 건지 확인 등)
        - Automatic citations with retrievals
    - Key Feature 2: Agents for Amazon Bedrock
        - “Agent will help you plan and execute tasks on your behalf.”
        - Agent takes in a query, a question from the customer, breaks down and orchestrates tasks, securely accesses and retrieves company data for RAG, takes action by invoking API calls on your behalf, Chain-of-thought trace and ability to modify agent’s prompt.
        - Select your foundation model → Provide basic instructions → select relevant data sources → specify available actions
          
- Summarization
    - 수천개의 문서를 확인해서 portfolio decision을 수행해야 함.
    - 단계 1: Document feed → Document DB → curated test suite & summaries → Builder → prompt engineering → test model → Amazon Bedrock API (Claude, Claude Instant, …) → Evaluate model
    - 단계 2: Document DB → Batch (ex: 500,000 docs from docs repo using Batch for Amazon Bedrock. 모든 문서를 문서 저장소에서 비동기로꺼내서 모델 파이프라인을 통과한 결과값을 S3 bucket에 저장) → Document Summary DB
    - 단계 3: 이후 신규 Document feed → Event driven → Step Functions (Amazon Bedrock integration 실행. Step Functions calls the invoke model API to Amazon Bedrock) → Research Portal에서 확인 가능 → Research Analyst가 활용
    - Key Feature 1: Batch for Amazon Bedrock
        - Avoids throttling to get large jobs done faster
        - Fully managed model invocation jobs
        - No need to write code to handle failure and restarts
        - Works with base models and custom models
          
- Entity Extraction
    - 사용자가 Support Personal에게 보낸 이메일에서 사용자 정보를 추출 (ex: account number, stock symbol, city, address, any entities)
    - 단계 1: e-mail server → curated test suite & emails → builder → Prompt engineering → test model (ex: Llama 2)  → Evaluate Model (ex: 50% confidence rate) → **Fine-tuning** → Fine tuned - Llama 2 → Evaluate Model (ex: 90% confidence rate)
    - 단계 2: Customer → e-mail server → Agents → fine tuned - Llama 2 → Automated response to customer (if confidence rate is over 85%) → if not, Draft response → support team queue → support personnel이 직접 처리.
    - Key Feature 1: Fine-tuning. Amazon Bedrock custom models
        - Maximize accuracy of FMs by providing labeled or raw unlabeled data
        - Fine-tune Llama 2, Command, and Titan FMs for specific tasks
        - Once deployed, custom models are invoked the same way as base models (playground or API)

### Amazon Bedrock 구성

**Bedrock Console**: 다양한 모델, 프롬프트 및 추론 매개변수를 실험해 볼 수 있는 기능.

- Open in Playground에서 실제로 동작하는 것을 확인 가능
    - Temperature: 온도가 0이면 무작위성이 없음. 매번 가장 가능성이 높은 단어가 선택됨. 응답의 다양성을 높이려면 Temperature 값을 더 높게 설정하고 동일한 요청을 여러 번 실행할 수 있음.
        - 콘텐츠 제작과 같은 창의적인 시나리오에서는 Temperature가 높을수록 도움이 될 수 있음.
        - 비즈니스 프로세스 시나리오 및 코드 생성에서는 Temperature를 0으로 설정하는 것이 가장 좋을 수 있음.
    - Response length: 응답에 반환할 토큰의 수를 결정. 길이를 너무 낮게 설정하면 응답이 완료되기 전에 끊어질 수 있음.
    - Info: 링크를 통해 각 파라미터에 대한 설명을 확인할 수 있음.
- View API request를 선택하면 지정된 프롬프트 및 구성에 대한 AWS CLI를 확인할 수 있음.

**Bedrock API**

```python
# 1. bedrock_api_kr.py 파일 생성
# 2. import문 추가 
import json
import boto3

# 3. bedrock client 라이브러리 초기화
session = boto3.Session()
bedrock = session.client(service_name='bedrock-runtime') #Bedrock client 생성

# 4. API 호출을 위한 payload 생성
bedrock_model_id = "anthropic.claude-3-sonnet-20240229-v1:0" #파운데이션 모델 설정

prompt = "뉴햄프셔에서 가장 큰 도시가 어디인가요?" #모델에 보낼 프롬프트 설정

body = json.dumps({
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1024, 
    "temperature": 0,
    "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt 
                        }
                    ]
                }
            ],
}) #요청 payload 설정

# 5. Bedrock API 호출
response = bedrock.invoke_model(body=body, modelId=bedrock_model_id) #payload를 Bedrock으로 전송

# 6. 응답 표시
response_body = json.loads(response.get('body').read()) # response 읽기
results = response_body.get("content")[0].get("text")

print(results)
```

- 저장 후, 스크립트 실행

**Converse API**: Amazon Bedrock을 사용하여 LLM에 엑세스하는 일관된 방법을 제공.

- 사용자와 생성 AI 모델 간의 턴 기반 메시지를 지원.
- 도구 사용(”함수 호출”)을 지원하는 모델에 대한 도구 정의에 일관된 형식을 제공.
- 지원 모델: Amazon Titan, Anthropic Claude,

```python
# converse_api_kr.py 파일 생성
import boto3, json

print("\n----A basic call to the Converse API----\n")

session = boto3.Session()
bedrock = session.client(service_name='bedrock-runtime')

message_list = []

initial_message = {
    "role": "user",
    "content": [
        { "text": "오늘 하루 어떠셨나요?" } 
    ],
}

message_list.append(initial_message)

# maxTokens 값 설정, 응답의 변동성을 최소화하기 위해 temperature를 0으로 설정 
response = bedrock.converse(
    modelId="anthropic.claude-3-sonnet-20240229-v1:0",
    messages=message_list,
    inferenceConfig={
        "maxTokens": 2000,
        "temperature": 0
    },
)

response_message = response['output']['message']
print(json.dumps(response_message, indent=4, ensure_ascii=False))

```

- 예상 결과:

```json
{
    "role": "assistant",
    "content": [
        {
            "text": "제가 인공지능 대화 모델이라 하루 일과를 겪는 건 아니지만, 여러분과 대화를 나누면서 많은 것을 배웁니다. 오늘도 유익한 대화가 있었으면 좋겠네요. 혹시 오늘 있었던 특별한 일이나 느낌 등을 말씀해 주시면 함께 이야기를 나눌 수 있을 것 같습니다."
        }
    ]
}
```

- 사용자와 어시스턴트 메시지 교환하기

```python
print("\n----Alternating user and assistant messages----\n")

# 'user' 역할과 'assistant' 역할을 번갈아 보내야 함.
# 목록의 마지막 메시지는 'user' 역할에서 보낸 것이어야 LLM이 응답할 수 있음
message_list.append(response_message)

print(json.dumps(message_list, indent=4, ensure_ascii=False))
```

**도구 사용(function calling)**: LLM이 호출 애플리케이션에 모델에서 제공한 메개 변수를 사용하여 함수를 호출하도록 지시할 수 있는 기능.

**스트리밍 API**: 스트리밍 응답은 최종 사용자에게 콘텐츠를 즉시 반환하고 싶을 때 유용함. 전체 응답이 생성될 때까지 기다리지 않고 한 번에 몇 단어씩 출력을 표시할 수 있음.

**Embeddings**: Vector라고 하는 일련의 숫자로 텍스트의 의미를 포착함. 그런 다음 이 Vector를 사용하여 텍스트가 얼마나 유사한지 확인할 수 있음.

- Vector Database를 사용해 이러한 임베딩을 저장하고 빠른 유사도 검색을 수행할 수 있음.
- Vector Database와 결합된 embeddings은 검색 증강 생성(RAG)의 핵심 구성 요소임.

## References:

- [Amazon Bedrock 소개](https://aws.amazon.com/ko/bedrock/)
- [Accelerate generative AI application development with Amazon Bedrock](https://www.youtube.com/watch?v=vleGSQ_mIvc)
- [Building with Amazon Bedrock](https://catalog.us-east-1.prod.workshops.aws/workshops/10435111-3e2e-48bb-acb4-0b5111d7638e/ko-KR)
