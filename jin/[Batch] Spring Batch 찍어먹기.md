이 글은 업무에 빠르게 적용하기 위해 큰 그림을 잡는 용도로 공부한 내용들의 정리입니다. 더 깊은 원리와 최적화에 대해선 후에 공부할 예정입니다. <br>
내용은 Spring Batch 공식 문서와 조졸두님의 블로그 Spring Batch 시리즈 1 ~ 8편을 읽고, 이런 저런 자료들과 함께 저의 언어로 정리한 글입니다. <Br>

# 1. Spring Batch와 구조
# 2. Spring Batch의 기본 구성 요소
# 3. Chunk-Oriented Processing

![image](https://github.com/binary-ho/batch-4-practice/assets/71186266/d8a76ae7-b7dc-4642-b5d6-fca4147d1b31)

**Chunk란 "큰 덩어리"라는 의미이다.** 위 그림과 같은 초콜릿 덩어리를 "초콜릿 청크", 영단어 여러개가 모여 하나의 의미를 갖고, 그걸 통째로 이해하는 것도 "Chunking"이라고 부른다. <br> 
Spring Batch에서의 Chunk란 **"데이터 덩어리"를** 의미한다. Chunk 값은 커밋 사이에 처리되는 Row 수를 의미하게 된다. 예를 들어 **1만개의 데이터를 저장한다고 생각 할 때, 하나 하나 1만번 저장하기 보다는 1000개씩 "덩어리 지어" 저장하면 10번만에 저장할 수 있다**. <Br> <br>

## 3.1 Chunk-Oriented Processing 장점
데이터 처리를 적절한 Chunk 단위로 처리하면 여러 장점이 있다. <br>
1. **수많은 데이터를 묶어서 저장해 저장 횟수나 통신 횟수를 줄일 수 있다.** (Disk나 외부 DB 서버와의) 
2. **만약 하나의 청크를 활용한 작업이 실패하더라도, 한번의 작업만 Rollback된다.** 10개의 청크로 나누어 10번의 작업 중 1번의 작업이 실패하더라도 하나의 청크를 활용한 작업만 롤백된다. <br> 
3. **한번에 더 적은 데이터만을 메모리에 올릴 수 있다.** 코드 레벨에서 데이터를 조작하기 위해 많은 데이터를 가져와 메모리에 올리는 것은 메모리에겐 버거운 일일 수 있다. 한번에 많은 데이터를 보내는 것 보다 대역폭 효율도 좋을 것이다.

<br> 

## 3.2 작업을 어떻게 덩어리로 만들까?
![image](https://github.com/binary-ho/batch-4-practice/assets/71186266/71f88e88-252d-4709-83bc-e1ec78a759bd)


그림을 설명하기에 앞서, 간단하게 설명하자면 ItemReader는 아이템을 읽는 역할을 한다. DB나 데이터 더미에서 데이터 레코드 하나를 가져온다 - 이 하나의 데이터를 Item이라고 부르는 것! <br>
그리고 이름 그대로 Processor는 Item으로 우리의 작업을 처리해준다. ("Processing"한다.) 그리고 ItemWriter가 데이터를 저장한다. <br>



위 그림을 보면 Reader와 Processor는 "Item"을 다루고, Writer는 "Items"를 다룬다. 단수와 복수다 즉, **Reader와 Processor는 "Item"을 데이터를 가져오는 것 자체는 하나씩 가져오지만, 그렇게 가져온 데이터들로 Chunk를 만들어 한번에 Write 한다.** <br>

이러한 작업을 코드로 나타내면 아래와 같은 것이다.
```java
List<Item> chunk = new ArrayList<>();

for(int i = 0; i < 전체_데이터; i += 청크_크기) {

  // 청크 크기만큼 반복!
  for(int j = 0; j < 청크_크기; j++) {
      Item item = itemReader.read(); // 데이터를 가져온다.
      Item processedItem = itemProcessor.process(item); // 몬가 몬가 처리한다.
      
      // 데이터를 모은다
      chunk.add(processedItem);
  }
  // 한번에 데이터를 쓴다.
  itemWriter.write(chunk);
}
```

### 3.2.1 Read와 Process, Write 코드 간단하게 확인하기

이런 ChunkOriented Processing의 로직을 다루는 곳은 ChunkOrientedTasklet이다. 배치를 수행하는 exectue 메서드를 보면 
데이터를 가져오는 provide와 처리하고 저장하는 process 메서드가 있다. <br>
간단하게 어디서 어떤 일이 일어나는지만 알아보자. 


![image](https://github.com/binary-ho/batch-4-practice/assets/71186266/152d80a5-806a-4b73-8209-27729e9b436b)


provide는 ChunkSize 만큼 반복될까? 

![image](https://github.com/binary-ho/batch-4-practice/assets/71186266/36087002-eb14-4d5e-8689-9b880742f869)


밑줄친 부분들을 보면, item이 null이 될 때까지 계속 채워 넣는 것을 확인할 수 있다. <br>

그리고 process는 아래와 같은데, 밑줄친 부분의 주석을 해석해보면 각각 데이터를 변환시키고, (작업 처리) 저장한다는 것을 알 수 있다.

![image](https://github.com/binary-ho/batch-4-practice/assets/71186266/b5c0713e-e9d1-45d2-895f-11852a2f5449)


## 3.3 ItemReader과 ItemStream
이제 ItemReader를 좀 더 자세히 살펴보자. <br>
 
Chunk-Oriented로 처리하는 작업은 ChunkOrientedTasklet의 execute를 통해 처리됨을 확인했다. <br>
**Step은 Tasklet 단위로 처리되므로, 이를 구성하는 요소들인 ItemReader와 "ItemProcessor & ItemWrite" 묶음 또한 Tasklet이다.** <br>

이러한 ItemReader는 데이터를 읽어들이는 역할을 하는데, DB의 데이터, 파일, XML이나 JSON, 다른 Messaging Service에서의 요청 등 여러 데이터 소스를 읽어내 배치 처리의 입력으로써 사용할 수 있게 한다. <br>
이외에도 지원해주지 않는 형식의 경우 커스텀 가능하다. ItemReader는 단지 `read()`하나만을 가지고 있기 때문에, 이 메서드를 구현해주면 된다. 그리고, ItemStream 인터페이스를 구현하면 된다.

![image](https://github.com/binary-ho/batch-4-practice/assets/71186266/09af20cd-81cd-46ac-b855-b73bde70ea8d)

<br>

![image](https://github.com/binary-ho/batch-4-practice/assets/71186266/00b446de-4394-4e2f-9d63-5285ad06a452)

<Br>

ItemStream은 Step 실행의 상태에 대한 정보를 제공해준다! 따라서, ItemStream은 Step이 실패했을 때 상태를 확인하는데에 필수고, Retry 등의 실패시 처리에 관여한다. <br>

보통은 커스텀 할 일이 없지만, 만약 Querydsl이나 Jooq를 사용한다면 직접 구현해야 할 수도 있다. ItemReader는 Spring Batch의 성능을 좌우하는 매우 중요한 구현체이다. 어떤 ORM과 어떻게 사용하는지, fetchSize나 ChunkSize는 어떻게 구성하는지 등을 고려해야 한다. <br>
일단 나의 목적은 급한 회사 업무를 위해 큰 그림을 그리고, 차차 빈 공간을 채워 나가는 것이므로, 나중의 나를 위한 래퍼런스를 남기고 넘어가겠다. <br>

TODO
1. [조졸두 - ItemReader (커스텀, 주의할 점 등)](https://jojoldu.tistory.com/336?category=902551)
2. [Spring Batch 영속성 컨텍스트 문제](https://jojoldu.tistory.com/146)


## 3.4 ItemWriter & ItemProcessor
ItemWriter & ItemProcessor는 묶어서 하나의 Tasklet으로 볼 수 있다. Processor는 선택이지만 ItemWriter는 ChunkOrientedTasklet의 필수 요소가 되시겠다. <br>
그리고 Processor와 Writer는 트랜잭션의 범위에 포함되어 Jpa를 사용하는 경우 Lazy Loading이 가능하다. <br>
ItemWriter는 Spring Batch의 출력 기능으로 청크 단위로 Item을 저장한다. 애초에 Reader와 달리 제공하는 메서드가 List를 받는다. 

![image](https://github.com/binary-ho/batch-4-practice/assets/71186266/7d4daef1-285f-45a4-be1a-cabc2f0d8cde)

<Br>

Writer는 Chunk를 처리하는 마지막 단계이다. **따라서 Commit과 관련된 작업을 Writer가 구현해줘야 함을 잊지 말아라.** 실제로 구현체인 JpaItemWriter나 HibernateItemWirter에 구현된 write를 확인해보면, 각각 `flush()` 메서드를 호출한다. 실제로 커밋 되기 전에 처리해주는 것이다. <br>

Writer는 주로 JdbcBatchItemWirter를 사용한다고 한다. 

### ItemProcessor
ItemProcessor는 데이터를 가공하거나, 어떠한 처리를 하기 위한 구성요소로, Reader와 Writer와 달리 필수 요소는 아니다. 필요에 따라 비즈니스 코드를 분리하고자 할 때 만들면 되는 것이다. <br>

주로 Reader에서 넘겨준 개별 데이터를 가공하기 위해 사용한다. Writer와 함께 묶어 하나의 Tasklet이지만, 여기에선 개별건을 처리한다. 헷갈리지 말자. <br>

일반적으로 데이터를 변환시키거나 필터링 할 때 사용하면 좋다. Reader에서 읽은 데이터틀을 Writer에 주기 전에 형을 변환시키던가, 뺄건 빼겠다는 것이다. 아래 메서드를 구현하면 된다. <br>

![image](https://github.com/binary-ho/batch-4-practice/assets/71186266/7ae3a5c8-5213-434d-9f42-22d8a267b263)


제네릭을 사용해 인풋 아웃풋을 자유롭게 만들었다. Reader에서 건내주는 타입이 I, Wirter에 넘겨줄 타입이 O가 되겠다. <br> <br>

ItemWriter와 ItemProcessor는 지금 당장 자세히 아는 것이 목적이 아니므로 이정도만 정리하고 넘어가겠다.


# 3. 나중을 위한 Reference들
1. [조졸두 - ItemReader (커스텀, 주의할 점 등)](https://jojoldu.tistory.com/336?category=902551)
2. [Spring Batch 영속성 컨텍스트 문제](https://jojoldu.tistory.com/146)
3. [Page Size vs Chunk Size 차이](https://jojoldu.tistory.com/331?category=902551)
4. [Spring Batch를 더 우아하게 사용하기 - Spring Batch Plus](https://d2.naver.com/helloworld/9879422)
5. [[Data] Batch Performance 극한으로 끌어올리기: 1억 건 데이터 처리를 위한 노력](https://youtu.be/2IIwQDIi3ys?si=SQeSntdxT8Q5P-wQ), [5번 글 버전](https://tech.kakaopay.com/post/ifkakao2022-batch-performance-read/)
6. [Spring Batch 애플리케이션 성능 향상을 위한 주요 팁](https://www.youtube.com/watch?v=VSwWHHkdQI4&t=85s), [6번 글 버전](https://tech.kakaopay.com/post/spring-batch-performance/)
7. [Spring Batch ItemWriter 성능 비교](https://jojoldu.tistory.com/507)
8. [Batch N + 1 문제 해결](https://jojoldu.tistory.com/414?category=902551)
9. [Spring Batch에서 @StepScope 사용시 주의사항](https://jojoldu.tistory.com/132)
