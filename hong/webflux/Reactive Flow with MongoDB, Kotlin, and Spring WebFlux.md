# Reactive Flow with MongoDB, Kotlin, and Spring WebFlux

참고 링크: https://www.baeldung.com/kotlin/mongodb-spring-webflux

### Overview

Spring Data Reactive MongoDB를 사용해서 간단한 Spring WebFlux 애플리케이션을 만들기.

- Spring Data Reactive MongoDB를 사용해서 Mongo reactive database에 저장
- Server-Sent-Events 방식을 사용해서 subscribed clients에게 데이터 전달

### Setup

1. Maven(또는 gradle)을 통해 project에 Spring Data Reactive MongoDB, Kotlin standard library 추가
- Spring Data Reactive MongoDB

```kotlin
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-mongodb-reactive</artifactId>
</dependency>
```

- Kotlin standard library

```kotlin
<dependency>
    <groupId>org.jetbrains.kotlin</groupId>
    <artifactId>kotlin-stdlib</artifactId>
</dependency>
```

### Reactive Mongo Configuration

reactive Spring Data를 지원하기 위한 설정을 추가한다.

- Mongo Reactive client와 Spring Data Repository 설정을 위한 `AbstractReactiveMongoConfiguation` 클래스

```kotlin
@Configuration
@EnableReactiveMongoRepositories(
  basePackageClasses = arrayOf(EventRepository::class))
class MongoConfig : AbstractReactiveMongoConfiguration() {
 
    override fun getDatabaseName() = "mongoDatabase"
 
    override fun reactiveMongoClient() = mongoClient()
 
    @Bean
    fun mongoClient() = MongoClients.create()
 
    @Bean
    override fun reactiveMongoTemplate()
     = ReactiveMongoTemplate(mongoClient(), databaseName)
}
```

- 위 설정은 reactive가 아닌 일반적인 MongoDB를 사용할 때는 필수가 아님.
- `@*EnableReactiveMongoRepositories`* 어노테이션은 Spring Data repositories이 어디에 위치하고 있는지에 대한 설정.

다음은 DB에 데이터를 담을 class와 운영에 필요한 Spring Data reactive repository를 개발한다.

### Document

- document는 MongoDB 데이터베이스에 데이터를 저장하는 유닛을 뜻한다.
- 이 유닛은 JSON 스타일을 사용해서 DB에 저장한다.

```kotlin
@Document
class Event(id: String, name: String)
```

### Spring Data Reactive Repository

- Spring Data abstraction: DB에 접근하는 layer를 구현하기 위한 코드의 양을 줄이기 위해 라이브러리에서 제공하는 기능.
- reactive version도 같은 방식으로 respository interface를 생성하면 된다.

```kotlin
interface EventRepository : ReactiveMongoRepository<Event, String>
```

### Controller

- Controller class는 Server-Sent Event를 보내는 역할을 수행한다.
- 아래의 `saveAndSend` 함수는 인자로 받은 값을 EventRepository를 통해 reactive database에 저장하는 역할을 한다.

```kotlin
@GetMapping(value = "/save", 
  produces = arrayOf(MediaType.TEXT_EVENT_STREAM_VALUE))
fun saveAndSend(@RequestParam("eventName") eventName: String) =
  eventRepository
    .save(Event(UUID.randomUUID().toString(), eventName))
    .flux()
```

- 위 코드를 보면, 새로운 데이터를 저장한 후에 Spring Data reactive repository는 SSE를 리턴한다 (SSE: subscribed client에게 전달될 객체. Server-Sent Event의 약자)
    - Flux: n개의 데이터를 emit
    - Mono: 0개 또는 1개의 데이터만 emit
- Spring WebFlux는 SSE를 이용하여 데이터를 스트리밍 할 수 있다.
- SSE는 Spring 4.2부터 지원되었으며, Spring 5에서부터는 Reactor의 Publisher타입인 Flux를 이용해서 SSE를 편리하게 사용할 수 있다.

### SSE(Server Sent Event)

클라이언트가 서버로부터 전송되는 업데이트 데이터를 지속적으로 수신 가능한 단방향 서버 push 기술

**지속적으로 스트리밍을 하는 프로토콜**

- 데이터를 여러번에 나누어 보낼 수 있다.
- 연결선(Stream)을 유지할 수 있다.

<img width="489" alt="Screenshot 2024-06-23 at 12 51 13 AM" src="https://github.com/10000-Bagger/free-topic-study/assets/34956359/a82325cb-8a66-4172-aad5-d18e4ee4276f">

- 일반적인 통신은 1개의 요청당 1개의 응답이 돌아가지만, SSE를 이용하면 한번의 커넥션에 서버가 지속적으로 데이터를 보내줄 수 있다.

**스트리밍 형태로 반환하려면?**

- Flux 타입을 적용하기. Flux를 이용해서 여러번의 응답 데이터를 나누어 보내줄 수 있다.

### Flux를 이용해 SSE를 두 번 전송하는 예제

1. 클라이언트는 백엔드 서버에 요청을 보낸다.
2. 외부 서버로의 요청은 응답까지 5초가 걸린다고 가정한다.
3. 백엔드 서버는 클라이언트의 요청을 받으면 외부 서버로 요청을 보내놓고, 바로 첫번째 응답을 준다.
4. 백엔드 서버로 외부 서버의 응답을 받으면, 클라이언트에게 두번째 응답을 돌려 준다.

```kotlin
@RestController
@RequestMapping("/test")
public class TestController {

    @GetMapping("/data")
    public Flux<ServerSentEvent<String>> getData() {
		
        Mono<String> firstResponse = Mono.just("First response");
        Mono<String> secondResponse = Mono.just("second response");
        
        Flux<ServerSentEvent<String>> responseStream = Flux.concat(
                firstResponse.map(data -> ServerSentEvent.<String>builder().data(data).build()),
                secondResponse.delayElement(Duration.ofSeconds(5)).map(data -> ServerSentEvent.<String>builder().data(data).build())
        );

        return responseStream;
    }
}
```

여기까지가 reactive를 지원하는 server-side project 개발 예제이다. 이후에는 간단한 web client를 통해 SSE를 보내고 받는 과정을 설명한다.

### Subscriber

데이터 저장을 요청하고 변경된 정보를 서버로부터 전달 받는 간단한 방법을 설명한다.

**Save Data**

- 간단히 save 버튼 클릭 시 `/save`endpoint로 HTTP 요청을 보낸다.

```html
<form method="get" action="/save">
    <input type="text" name="eventName">
    <button type="submit">Save new event</button>
</form>
```

**Receive Data**

- save 요청을 보냄과 동시에 client 쪽에서는 해당 endpoint에 대해 listening을 수행한다. 언어마다 SSE를 지원하는 framework가 있기때문에 확인 필요.
- HTML로 작성한 가장 간단한 예제는 아래와 같다.

```html
<div id="content"></div>
<script>
    var source = new EventSource("save");
source.addEventListener('message', function (e) {
        console.log('New message is received');
        const index = JSON.parse(e.data);
        const content = `New event added: ${index.name}<br>`;
        document.getElementById("content").innerHTML += content;
    }, false);
</script>
```

이렇게 client-side에서 수행할 작업까지 끝났다. 
이후에는 SSE 방식과 React에서는 어떻게 EventSource를 처리하는지 공부할 예정.
