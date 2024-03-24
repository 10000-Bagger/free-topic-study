# Domain-Driven Design

> DDD 는 해당 도메인과 일치하도록 소프트웨어를 모델링하는 데 중점을 둔 소프트웨어 설계 접근 방식이다.
> 

## 요약

- Domain이란 유사한 업무의 집합을 말한다. (마케팅, 구매, 연구, 영업 등)
- Domain Driven Design은 비즈니스 도메인별로 나누어 설계하는 방법론이다.
- 한 Domain 내에서는 Ubiquitous Language가 사용되어야 한다. 즉, 모두가 공통으로 이해하는 통일된 용어가 필요하다.
- Context란 도메인의 사용자, 프로세스, 정책 등을 의미한다. 고유의 비즈니스 목적별로 Context를 나눈 것이 Bounded Context이다.
- DDD는 전략설계와 전술설계로 나뉜다.
- 전략설계의 산출물은 Domain Model이고, Domain 분해도와 Context Map으로 구성된다.
- Domain 분해도는 최상위 도매인을 서브도메인으로 나누고 각 서브도메인의 Type을 Core, Support, Generic으로 나눈 것이다.
- Context Map은 Bounded Context간의 관계를 도식화한 것이다.
- Event Storming은 도메인에 대한 공통의 이해를 위해 도메인에서 일어나는 것들을 찾는 방법이고, 일련의 과정을 통해 Bounded Context를 식별한다.
- 각 Bounded Context를 Micro Service로 나눈 후 각 Micro Service별로 설계한다.
- 마이크로서비스는 Layered Architecture로 설계하는 것을 권장한다. Presentation, Service, Domain Model, Data Access Layer를 사용한다.
- 전술설계의 객체에는 Entity, VO(Value Object), Aggregate, Factory, Repository가 있다. Entity (구별 필요), VO (구별 불필요), Aggregate (Entity 집합)
- 전술설계의 결과물은 User story (주체가 사람인 요구사항 명세서), Usecase Diagram, Sequence Diagram, Class diagram, Data Model, Storyboard(화면설계서), API설계서와 같이 기존과 유사한 산출물과 메시지 설계서, 마이크로 서비스 패턴 적용 설계서와 같은 마이크 서비스에 특화된 설계서가 있다.
- Design Thinking은 사용자에 대한 공감과 이해를 통해 사용자 경험을 향상시킬 아이디어를 찾는 방법론이다. DDD 시작 전에 Ideation을 위해 수행하면 좋으며, 그 결과를 DDD로 구체화 시킨다.

## 1. Domain이란?

1) 사전적 의미는 ‘영역’, ‘집합’이다.

2) DDD에서 말하는 Domain은 비즈니스 Domain이다.

3) 비즈니스 Domain은 유사한 업무의 집합이다.

4) 애플리케이션은 비즈니스 Domain 별로 나누어 설계 및 개발될 수 있다.

## 2. DDD란?

Domain Driven Design

1) Business Domain 별로 나누어 설계하는 방식

- 기존의 애플리케이션 설계가 비스니스 Domain에 대한 이해가 부족한 상태에서 설계 및 개발되었다는 반성에서 출발함.
- DDD에서는 기존의 현업에서 IT로의 일방향 소통구조를 탈피하여 현업과 IT의 쌍방향 커뮤니케이션을 매우 중요하게 생각함.

2) DDD의 핵심 목표는 “Loosly coupling”, “High cohesion”이다.

- 애플리케이션 또는 그 안의 모듈간의 의존성(결합도)은 최소화하고, 응집성은 최대화.
    - 모듈:
        - 모듈(module)은 역사적으로 프로그래밍이라는 관점에서는 기본적으로 본체에 대한 독립된 하위 단위라는 필연적인 개념의 큰 틀을 따르고 있지만 본체와 모듈간에 가지고 있었던 문제들을 해결해 나가는 과정에서 발전함.
        - 여기서 모듈이란 크기와 상관없이 클래스나 패키지, 라이브러리와 같이 프로그램을 구성하는 임의의 요소를 의미함.
        - 클린 코드의 정의: 모든 모듈은 1. **제대로 실행**되어야 하고, 2. **변경이 용이**해야되고, 3. **이해하기 쉬워야** 한다.
    - 응집도:
        - 응집도(Cohesion)은 모듈에 포함된 **내부 요소들**이 **하나의 책임/목적을 위해 연결**되어있는 연관된 정도.
            - 모듈이 하나의 목적을 수행하는 요소들간의 연관성 척도
            - 모듈 내부의 기능적인 응집 정도를 나타냄
            - 높을수록 좋음.
            - 하나의 모듈(A 모듈)에 하나의 책임/목적을 위해 연결(a 기능들)이 잘 모여 있는 것과 아닌 경우 수정하기가 어느쪽이 어려울지 생각해보면 됨.
                - 예: a라는 기능을 수정하기 위해 a 기능이 모여있는 A 모듈만 참아서 수정하면 됨.
                - Controller, Service, Repository 등 하나의 도메인에 대한 책임/목적을 위해 연결됨.
    - 결합도:
        - 결합도(Coupling)은 다른 모듈과의 의존성 정도. 모듈 수정을 위해 다른 모듈의 변경을 요구하는 정도.
            - 모듈이 다른 모듈에 의존하는 정도의 척도
            - 모듈과 모듈간의 상호 결합 정도를 나타냄
            - 낮을수록 좋음.
                - 예: b라는 기능을 수정하기 위해 b 기능이 모여있는  B 모듈을 수정하는 데, 다른 모듈들(A, D, C)의 기능들과 연관되어 수정하려면 다른 모듈의 소스도 확인하면서 수정해야 한다. 필요 시 다른 모듈들까지 수정해야 된다면 유지보수가 더욱 힘들 것임.
                - 반대로 A 모듈이 다른 모듈들을 참조하는 부분이 거의 없어 의존도가 낮은 상황이라면 유지보수가 편할 것임. 이렇게 참조가 적은 상황을 ‘느슨하게 연결되었다’ 표현 = 결합도가 낮음.

3) DDD는 Strategic Design과 Tactical Design으로 나눌 수 있다. 

- Strategic Design은 개념 설계
- Tactical Design은 프로그래밍하기 위한 구체적 설계

## 3. Strategic Design

1) Business Domain의 상황(Context: 대상 사용자, 상황)에 맞게 설계하자는 컨셉

- 예: 선물 구매라는 도메인을 설계할 때 대상이 애인, 부모, 자식인지에 따라 달라져야 함)

2) 전략적 설계를 위해 Business Domain의 상황(Context)를 Event storming으로 공유하고, 비즈니스 목적별로 서비스들을 그룹핑함.

3) Bounded Context & Domain Model

- Bounded Context는 Business Domain의 사용자, 프로세스, 정책/규정 등을 고유한 비즈니스 목적별로 그룹핑한 것.
    - 사용자, 프로세스, 정책/규정들을 그 Business Domain의 Context라고 말할 수 있으므로 Bounded Context는 Domain 안의 서비스를 경계 지은 Context의 집합이라고 할 수 있음.
- Domain Model은 비즈니스 도메인의 서비스를 추상화한 설계도.
    - Domain을 Sub domain으로 분해한 것과 Bounded Context가 Domain model 임.

4) Bounded Context & Micro Service

- 1개의 Bounded Context는 최소한 1개 이상의 Micro service로 구성됨.

5) Context Map

- Bounded Context간의 관계를 나타낸 도식화한 Diagram.

6) Ubiquitous Language

- 현업, 개발자, 디자이너 등 참여자들이 동일한 의미로 이해하는 언어.
- 비즈니스 도메인에 따라 동음이의어가 많기 때문에 정확한 커뮤니케이션을 위해 공통언어를 정의하고 사용해야 함.
- 하나의 도메인 내에서는 어떤 단어나 문장이 동일한 의미로 소통된다. 예를 들어 ‘마우스’라는 단어는 ‘컴퓨터부속품생산’ 도메인 내에서는 ‘컴퓨터 화면 안에서 커서를 옮기는 컴퓨터 부속품’으로 통용됨. 하지만 ‘해충박멸서비스’ 도메인 내에서는 ‘꼬리 달리고 털이  나있는 짐승’으로 통용됨.

7) Strategic Design의 결과물: Domain Model

- Problem Space: Business Domain 분할
    - Core Sub-Domain: 비즈니스 목적 달성을 위한 핵심 도메인으로 차별화를 위해 가장 많은 투자가 필요함.
    - Supporting Sub-Domain: 핵심 도메인을 지원하는 도메인.
    - Generic Sub-Domain: 공통 기능(메일, SSO 등) 도메인으로서 3rd Party 제품을 구매하는 것이 효율적임.

8) Event Storming: 비즈니스 도메인 내에서 일어나는 것들을 찾아 Bounded context를 식별하는 방법론

- Step 1. Domain Event 정의: 비즈니스 도메인 내에서 발생하는 모든 이벤트를 과거형으로 기술
    - 이벤트는 Actor가 Action을 해서 발생한 결과이다. 보통 문장은 “XXX가 되었다.” 형태가 됨.
    - 각자 생각나는 Event를 적고 바로 순서없이 붙임. 더 이상 생각이 안 날 때까지 적은 후,
    - 서로 상의하면서 중복된 것을 없애거나 합친다.
    - 이벤트가 발생하는 시간 순서대로 붙인다. 동시 수행되는 이벤트는 수직으로 붙인다.
- Step 2. Tell the story: 도출된 이벤트로 도메인의 업무 흐름을 이해하고 토론하여 보완
    - 도메인 전문가가 도출된 이벤트를 갖고 업무 흐름을 설명한다.
    - 상호 질문을 통해 도메인 이벤트를 추가하거나 조정한다.
    - 이슈/개선사항/관심/재논의 사항이 있으면 “빨간색” 포스트잇으로 이벤트 옆에 붙인다.
- Step 3. 프로세스로 그룹핑: 이벤트들을 프로세스로 그룹핑
    - 동일한 비즈니스 주제(업무 프로세스)로 이벤트들을 그룹핑한다. “보라색” 포스트잇에 프로세스명과 간략한 설명을 기술.
    - 비즈니스적으로 중요한 핵심 프로세스에 집중. 핵심 프로세스에 중요한 이벤트가 누락되지 않았는지 검토.
- Step 4. Command 정의: 각 Domain Event를 발생시키는 명령을 현재형으로 정의하며 명령형(ex: 제품 목록을 검색)으로 기술
    - 사용자의 행위가 Command가 됨. Command는 일반적으로 ‘무엇을 CRUD 요청한다.’ 또는 ‘무엇을 XX한다’의 형태가 된다.
    - 각 Event별로 그 Event를 발생시키는 Command가 무엇인지 생각하여 Event 왼쪽에 붙인다. Command 하나에 1개 이상의 Event가 발생할 수 있음.
- Step 5: Trigger 정의: Command를 일으키는 Actor와 Event를 일으키는 External System와  Policy/Rule을 정의
- Step 6: Aggregate 정의: Command 수행을 위해 CRUD해야 하는 데이터 객체 정의
    - Aggregate는 Entity와 VO의 집합이다.
    - Aggregate 이해하기
        - 한 단위로 취급 가능한 경계 내부의 도메인 객체로서 한개의 root entity와 기타 entity + value object로 구성됨.
        - 쉽게 말해, Aggregate는 고유의 비즈니스 목적 수행을 위한 데이터 객체들의 집합.
    - Command를 수행해서 Event를 발생시키려면 어떤 데이터(정보)가 필요한지 각 Command와 Event 사이 위에 적는다.
    - 어떤 데이터가 다른 데이터에 포함될 수 있으면 한 데이터로 묶는다. 예를 들면, “배송지 주소”는 “주문자 정보”에 묶일 수 있고, “결재 방식 종류”는 “결제 수단 정보”에 묶일 수 있다.
    - 또한 유사한 목적의 데이터들도 하나로 묶는다.
    - 이렇게 그룹핑된 데이터를 Entity라고 함.
- Step 7. Bounded Context 정의
    - Entity, Command, event, actor, policy/rule을 보면서 어떤 주제와 관련되었는지 논의
    - 바운디드 컨텍스트는 사용자, 프로세스, 정책/규정 등을 고유한 비즈니스 목적별로 그룹핑한 것.
- Step 8. Context Map 작성
    - Bounded Context간의 관계를 도식화함.
    - 바운디드 컨텍스트(B/C)간의 관계와 외부 시스템이 어떤 B/C와 관계 되는지를 표현함.
    - 쉽게 관계를 생가가하는 팁은 B/C를 마이크로 서비스라고 생각하는 것.

## 4. Tactical Design

1) 개발을 위한 구체적인 설계도

2) Model Driven Design

- Strategic Design에서 설계한 각 Sub-domain별 Domain Model(Context Map)을 중심으로 설계한느 것을 말함.

3) Layered Architecture

- Tactical Design 시 목적별 계층으로 나누어 설계하는 것을 의미함.
- 대표적인 layer는 **Presentation, Service, Domain, Data** Layer가 있다.
- 아래는 Martin Fowler가 이야기하는 Layer 구조:
    - Presentation
    - Service
    - Domain Objects
    - Data Mapper
    - Data Access
- Presentation Layer: UI Layer
- Service Layer: Domain Layer와 Data layer의 class들간의 제어(Control) 또는 연결(Interface)을 수행함. Business Logic을 이 layer에 구현하지 않는다.
- Domain Layer: Domain Object 별로 Business Logic 처리를 담당하는 layer.
- Data Layer: Database와의 CRUD 처리 Layer
- Spring Boot에서는 각 layer의 목적에 맞게 3가지 어노테이션을 지원.
    - Presentation Layer: @Controller, @RestController
    - Service Layer, Domain Layer: @Service
    - Data Layer: @Repository
- 참고: 왜 Service Layer와 Domain Layer를 나눠야 하나?
    - Domain Model에서는 Service Layer의 class들은 흐름 제어만 하고 Domain Layer의 class들이 비즈니스 로직을 처리함.
    - Service Layer와 Domain layer를 나누는 이유는, 새로운 비즈니스 요구에 대응할 때 기존 소스에 영향도를 최소화하고, Domain layer의 재활용성을 극대화하기 위함.

4) Entity & Value Object: 식별성과 가변성으로 구별

- Entity는 각 record간에 구별이 필요한 객체이고, VO는 각 record간에 구별이 필요없는 객체이다.
    - 예: ‘지폐’라는 객체는 ‘일련번호’라는 고유ID로 구별되어야 하므로 Entity. ‘금액’이라는 객체는 ‘액수’와 ‘통화’라는 속성이 중요하지 구별할 필요가 없으므로 VO.
- Entity는 가변적(Mutable)이고, VO는 불변성(Immutable)을 가짐.
- VO를 권고하는 이유는 속성 자체도 객체화하여 애플리케이션의 유연석을 높이자는 취기.
- 개발 시 Entity의 property는 string과 같은 기본형이 아닌 VO 객체로 하는 것이 좋다. 그리고 VO class는 자체적으로 속성에 대한 type 변환과 validation 체크를 구현하는 것이 좋다.
- VO vs MAP 논쟁: VO의 장점은 속성의 type이나 validation rule 같은 것이 변경 되었을 때 유용하다는 것. 단점은 잘못쓰면 복잡성이 증가하고, DB 스키마 변경 시 관련 VO도 수정해야 한다는 것. 현실적으로 SQL에 많이 의존하거나 (DAO 사용), DB 스키마의 변경이 빈번하게 예상된다면 VO class보다 구조체(MAP)가 더 효율적일 수 있음.

5) Aggregate & Factory

- Aggregate는 Entity들을 대표하는 추상화된 객체 (논리적인 DB 객체)
- 유연한 애플리케이션 개발을 위해 Entity간에 직접 커뮤니케이션하지 않고 Aggregate간에만 커뮤니케이션 하도록 설계.
- 위 Event Storming에서 정의한 Aggregate가 Tactic 설계 시 그대로 이용됨.
- Factory는 Aggregate의 생성 처리를 담당하는 객체. 개발에 따라서 Entity의 생성을 담당할 수도 있음.
- 예시 (영화 예매 애플리케이션):
    - Entity: 사용자, 영화, 영화예매, 영화상영, 할인정책, 할인규정은 식별되어야 하고 속성이 변할 수 있기 때문에 Entity가 됨.
    - VO: 설계 단계에서는 발견하기 어려움.
    - Aggregate: 사용자, 영화, 영화예매가 Aggregate가 됨. 영화 Aggregate는 하위에 Aggregate root인 “영화”가 있고 영화 밑에 “영화상영”, “할인정책”, “할인규정” Entity를 가짐.
    - Factory: 영화Creator
- **영화 Aggregate가 없다면, 영화예매 entity는 영화, 할인정책, 할인규정 entity와 직접 통신해야하나, 영화 Aggregate가 있으면 영화예매 aggregate는 영화 Aggregate에 요청만 하면 됨**
- **“영화Creator” Factory가 없으면, 새 정책 추가 시 영화 Aggregator를 수정해야 함. 영화 Creator Factory가 있으면, 새 정책 추가 시 새 정책에 맞는 영화 Aggregator를 하나 더 만들고 영화Creator Factory는 정책에 맞는 영화Aggregator를 생성하면 됨.**

6) Repository

- Data access를 처리하는 객체
- Aggregate, Entity를 위해 데이터 CRUD를 담당
- 실제 구현 시에는 ORM을 쓰는 것이 가장 이상적 (ORM → JPA → Hibernate)

7) Tactical Design 객체 관계도

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/69c1083f-6973-43ff-a2b5-99157e550b98/cae71482-73c8-49e7-b2d9-67149c3a2666/Untitled.png)

8) Tactical Design 결과물

- User Story: B/C 내 기능과 Test case를 사용자 중심으로 기술
- Sequence Diagram: B/C 내 객체(Entity)간의 처리 순서를 기술
- Class Diagram: Service layer, Domain Model layer의 class를 정의
- Data Diagram: Data 구조 정의 (ERD와 동일함)
- Storyboard: 화면설계서
- API 설계서: Micro service의 API 명세서
- Message 설계서: 비동기 메시징 설계서. 마이크로 서비스 간 통신 방법을 기술
- 마이크로 서비스 패턴 적용 설계서: 마이크로 서비스의 최적 아키텍처 설계를 위한 다양한 패턴 적용 방법 기술.


## Reference
DDD 핵심만 빠르게 이해하기: https://happycloud-lee.tistory.com/94