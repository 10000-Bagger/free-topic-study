# Spring Cloud Stream - Programming Model
- 프로그래밍 모델을 이해하기 위해서는 아래 3가지 Core Concepts를 이해하고 있어야 한다.
- Destination Binders: 외부 messaging system과 통합(integration)을 제공하는 컴포넌트
- Bindings: 외부 messaging system과 application(producer, consumer 기능을 제공하는)을 연결하는 매개체이다. (Destination Binders에 의해 생성된다.) 
- Message: producer와 consumer가 Destination Binders와 통신하기 위해 사용되는 표준 데이터 구조이다.
