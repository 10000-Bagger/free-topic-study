
# 자바 버전별 주요 변화 총정리 (~17)

대단원은 LTS로 구분되고, 소단원이 그 전 LTS 버전의 다음 버전 부터 ~ 대단원이 다루는 LTS 버전까지의 내용이다. <br>
말을 너무 못 했는데, **예를 들어 2단원이 LTS인 Java 11을 다루는데, 그 전 LTS가 8이었다. 그래서 2단원은 `Java 9 ~ Java 11`을 다룬다.**

# 1. Java 8 (LTS, ~2030)
Java 8 이전의 주요 변화와 Java 8의 변화를 살펴보자.

## 1.1 Java 7
### 1.1.1 자동 자원 반환 Try-with-resource
반환이 필요한 자원을 선언하며 try문을 실행하고, 반환하는 것을 돕는다. (돕는다고 쓰고 "강제로 반환한다"고 읽는다.) <Br>

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/c5f1fe30-d0e2-4399-993b-9faa28d0f62d)

위와 같이 try문의 괄호에 자동으로 반환할 자원을 선언할 수 있다. <br>
원래는 `try-catch`의 `finally`를 통해 반환해야 했지만
1. 개발자가 반환하는 것을 까먹을 수도 있음..ㅠ
2. `finally`에서 예외가 발생할 수 있음. 죽음의 다중 `try-catch` 중첩이 만들어질 수도 있다..

### 반환되는 원리는?
반환할 수 있는 객체는 java.lang의 AutoCloseable의 구현체이다! <br>
try문이 전부 끝나면, 객체의 `close()`를 자동으로 호출해준다. 아이 편해~

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/7a026bf0-558f-484d-a25f-b8f5861d7878)

<br>

이펙티브 자바 아이템 9에서도 try-finally 보다는 try-with-resources를 사용하라고 권한다. 궁금한 사람은 정리 내용 읽어보자. [Item 9. try-finally 보다는 try-with-resources를 사용하라](https://github.com/binary-ho/TIL-public/blob/main/Effective%20Java/Item%209.%20try-finally%20%EB%B3%B4%EB%8B%A4%EB%8A%94%20try-with-resources%EB%A5%BC%20%EC%82%AC%EC%9A%A9%ED%95%98%EB%9D%BC.md)

### 1.1.2 ArrayList Resize 방식 변경
Java 7 이전에는 배열이 가득 찬 경우 `(oldCapacity * 3) / 2 + 1`의 수식으로 Resize를 진행했다. <Br>
하지만 이 방식은 3을 곱하는 과정에서 Overflow가 발생할 수도 있기 때문에, Java 7에서 계산식을 바꾸었다. 

```java
int newCapacity = oldCapacity + (oldCapacity >> 1);
```

이 계산식을 통해 1.5배인 것은 비슷하게 유지하되, Overflow 가능성을 줄였다.

## 1.2 Java 8! (LTS)
### 1.2.1 람다와 스트림!
여기에도 간단하게라도 적고 싶었지만, 너무 간단하게 쓰기도 싫고, 너무 길게 쓰기도 싫다. (충분히 글이 길어지고 있다.) <br>
대신 예전에 쓴 글을 첨부하려 한다.  <br>

[Lambda & Stream의 도입 배경과 원리, 최적화 전략까지 알아보자.](https://dwaejinho.tistory.com/entry/Java-Lambda-Stream-%EB%8F%84%EC%9E%85-%EB%B0%B0%EA%B2%BD%EA%B3%BC-%EC%9B%90%EB%A6%AC-%ED%8C%8C%ED%95%B4%EC%B9%98%EA%B8%B0)

### 1.2.2 Intreface Default Method, Static Method
Java 8에 Intergace Default Method와 Static Method가 도입되었다! <br>
이들은 Interface의 기본 맴버 규칙을 싸그리 무시하는 애들인데, (정확히는 따르지 않아도 되게 해준다.) Default Method는 메서드가 몸체를 가질수 있게 해주고, Static Method는 말 그대로 Static Method이다. <br> <br>

참고로 이 메서드들을 쓰다보면, 메서드가 너무 길어지거나 책임이 많아질 수 있는데, 걱정 마시라 java 9에서 interface private method가 추가되는데, 이걸 통해서 메서드를 쪼겔 수 있다. <br>


### 1.2.2.1 Default Method
Defualt Method는 메서드가 `abstract` 속성을 갖지 않아도 되게 해준다. <Br>

이제, 메서드는 몸체를 가질 수 있다. **어떤 메서드의 구현 방법이 너무나도 명백한 경우, Default 메서드를 제공해줄 수 있다.**

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/08e37870-3cec-4aa5-b5ac-47126b22e52e)

<br>

### 1.2.2.2 Default Method 주의할 점
Default Method는 단순히 메서드를 구현의 편의를 준다고만 생각하면 안된다. <Br>

**문제는 해당 인터페이스를 구현한 구현체들에 메서드를 "끼워 넣을 수 있다"는 점이다!** <Br>

무슨 말이냐면, 어떤 인터페이스에 내가 default method를 통해 메서드를 추가했다고 생각해보자. 이 인터페이스의 구현체들은 영문도 모른체 어떤 메서드 하나가 추가될 수도 있다. 이 메서드들이 "모든" 상황에서 이전의 "모든" 구현들과 문제를 일으키지 않을 것이라고 확신할 수 있는가? <Br> 

예를 들어 자바 8 이전에 구현된 아파치 커먼즈 라이브러리의 SynchronizedCollection은 클라이언트가 제공한 객체로 락을 건다. <br> 
모든 메서드에서 주어진 락 객체로 동기화를 진행한 다음, 내부 컬렉션 객체에 기능을 위임하는 래퍼 클래스인데, 자바 8에서 Collection 인터페이스에 추가된 removeIf를 바로 구현하고 있지는 않다. <br>
어떤 클래스를 이용중인 클래스들은 이런 새로운 메서드의 등장에 바로바로 대응하지 못 할테고, 대응하는 동안 문제가 발생할 수도 있다. <br> <br>
같은 이유로 Object의 equals와 hashCode를 default로 안 된다. <br>
이펙티브 자바 아이템 20에서 짧게 이유는 언급하지 않는 문제인데, 아래 아티클을 참고해보자. <br>

[Java8: Why is it forbidden to define a default method for a method from java.lang.Object](https://stackoverflow.com/questions/24016962/java8-why-is-it-forbidden-to-define-a-default-method-for-a-method-from-java-lan) <br>

equals나 hashCode는 두 객체가 같은 객체인지 확인하기 위해 쓰인다.  단순히 같은지 비교할 때나, Set, Map 같은 유일 Key자료구조에서 "다름"을 확인하기 위해 쓰인다. <br>
만약 어떤 인터페이스에 내 마음대로 equals나 hashCode를 default method로 구현한다면 어떤 일이 생길까??? <br>

내 인터페이스를 구현해서 사용하던 사람들은 기본적인 Object의 equals나 hashCode의 동작을 기대하면서 다양한 로직을 짜거나, 혹은 이미 그렇게 작성했다. <br>

그 결과는 더는 설명하지 않아도 될 것이다. <br>

**우리가 default method로 위의 메서드들을 구현하는 순간 마음대로 "대체" 하게 된다.** <br> **이후의 사용자들은 그냥 아무 것도 안 했는데, 코드가 원하는대로 동작하지 않는다.** <Br>

**이런 논리적 오류는 당연히 찾아내기 쉽지 않고, 많은 문제로 이어질 수 있다.** <Br>

**그래서 디폴트 메서드를 작성할 때는 인터페이스를 구현하거나 상속하는 다른 인터페이스들을 위해 문서화를 해주는 것이 중요하다! (이펙티브 자바 Item 21)** <br>
**그리고 Object의 equals와 hashCode를 default로 구현하면 안 된다. (이펙티브 자바 아이템 20)** <Br>
**가장 중요한건 웬만하면 진짜 디폴트 메서드의 추가가 필요한지 고민해 보는 것이 되겠다.**  <Br> <Br>

애초에! 인터페이스의 Defult Method와 Static 메서드는 "좋은" 것일까? 초심자들에게 인터페이스와 추상 클래스의 차이를 더 헷갈리게만 하는 존재가 아닐까? <Br>
이 "끼워 넣음"에 항상 주의해라.


### 1.2.2.3 Static Methods
Interface의 Static 메서드는 인스턴스와 독립적이기 때문에 사실 인터페이스에 추가되지 못할 이유는 없었다. 생각해보면 그렇지 않나? 애초에 인스턴스가 없어도 되는데 없을 이유가 없다. <Br>

없었던 이유는 Java를 만든 사람들이 자바를 배울 때 좀 더 쉽게 배울 수 있게 하기 위해서였다고 한다... (허무) <br>
기본 인터페이스 맴버 규칙인 `abstract` 메서드만을 갖는다...를 지키기 위해서이기도 한다. <Br>

그래서 각종 부산물(?)들이 생기게 되었는데, static 메서드를 만들 수 없어서 `Collections`나 `Objects`등의 클래스가 생겨났다. s가 없는 버전의 `Collection`, `Object`에 static 메서드를 만들 수 없어, static method를 넣기 위한 클래스들이다.  

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/d2cd766e-86fd-4de0-8d09-9ecbd7df16b4)


<Br> <br>

Java 8 부터는 static 메서드의 선언이 가능해졌다. body는 필수이다. 아래는 static method 선언과 body가 없는 경우의 잔소리이다

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/85f89031-5e93-427a-b405-189809b3fa2a)
![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/490feea5-1f16-4d5a-9274-128e473ac1c7)

### 1.2.2.4 Default Method

# 2. Java 11 (LTS ~ 2027)
Java 8 이후 부터 11까지의 변화를 확인해보자.

## 2.1 Java 9
### 2.1.1 `Module`
`Module` : 매우 큰 주제. 패키지의 묶음이다. Jigsaw Project에서 만들었고, 결국 classpath의 한계점 때문에 등장했다. 

### 2.1.1.1 classPath의 한계점
1. `그룹화에 한계가 있었다` : Java는 접근 제한자를 통해 클래스 단위의 캡슐화가 가능했는데, 패키지 단위로는 캡슐화가 불가능했다. <br> **그리고 한 패키지의 클래스를 다른 패키지가 의존하려면 억지로 클래스를 public으로 만들어야만 했다!** <br> **기본적으로 모든 클래스와 리소스가 전역적으로 접근 가능해지는 문제가 발생했다.** <br> 
2. `명시적인 의존성 선언을 강제하지 않음` : 제한 없는 접근성은 떄문에 충돌 문제를 발생시켰다. 버전에 대한 문제도 많았는데, 패키지가 포함된 클래스의 경로는 같은 패키지 클래스의 다른 버전을 구분할 수 있는 장치가 따로 없다. <br> 따라서 여러 컴포넌트가 같은 라이브러리의 다른 버전을 사용하는 경우 문제가 발생할 수 있다. 이는 클래스들을 컴파일 한 후에 하나의 jar 파일에 전부 넣기 때문에 발생한다. <br>

<Br>

이런 문제들을 module로 해결할 수 있다! <br> <br>

### 2.1.1.2 Module의 도입
module은 java 8에 도입된 기능으로 module이라는 키워드로 정의할 수 있다. <br>
module-info.java 파일을 작성해 모듈을 이용함으로써, 앞서 언급한 classpath의 문제를 해결할 수 있다.

```java
module jinho.subpackage {
    requires bul.ka.jin;
 
    exports com.example.jinho.subpackage;
    exports com.example.jinho.subpackage.aaaa;
    exports com.example.jinho.subpackage.bbbb;
}
```

`jinho.subpackage` 모듈은 export된 패키지들을 다른 모듈에게 공개한다.
그리고 bul.ka.jin라는 모듈을 필요로 한다. <br>
이를 통해 모듈 의존성과 공개 여부를 패키지-모듈별로 명시할 수 있다. 리소스들끼리 의존성이 명확해지고, 접근을 제한하면서 캡슐화를 조절할 수 있게 되었다. <br>

**각 모듈의 이름이 고유하므로, 버전 충돌 문제도 해결된다!** <br>

또 의존성 그래프를 구축하고, 필요한 모듈들만 로드하면서 classpath를 사용할 때보다 컴파일 시간이 줄어들고, 클래스 검색 과정의 시간을 아낄 수 있다고 한다. <br>
실행할 때는 아래와 같이 실행해줄 수 있다.

```java
javac --module-source-path project -d mods --module moduleA --module moduleB 
java --module-path mods --module moduleB/com.example.ModuleB
```

<br>

### 2.1.2 `interface private method`
`interface private method` : Default Method 사용의 편의상 나왔다고 생각된다. Default Method는 인터페이스에도 Body가 있는 메서드 선언이 가능하게 해주는데, 자연스럽게 사이즈가 커지거나, 여러 책임을 가질 수 있게 됐다. <br> 

이런 경우 보통의 클래스에선 메서드를 분리해주면 됐다. 하지만 interface default method는 딱히 메서드를 분리할 방법이 없었는데, 그를 위해 Private Method 사용을 지원해준 것 같다.

### 2.1.3 Collection들
- Collection 정적 팩토리 메서드 
  - `List.of()` : 기존엔 불편 클래스를 만드는 것이 번거로웠다. `Collections.unmodifiableList()` 호출 등..
  - `Map.of()`, `Set.of()` 등
- Arrays Method
  - `compare()` : 두 배열을 비교한다. 어떤 배열이 논리적으로 앞서 있는지 확인한다(?)
  - `mismatch()` : 두 배열의 다른 "첫" 인덱스를 찾아낸다. 만약 두 Array에 원소가 다른 부분이 있다면 첫 위치를 찾아 반환하는 것인데, 내용물이 전부 같은 경우 `-1`을 반환한다. 

### 2.1.4 Java 9 Flow
- [[Java] Concurrency 3 - Java 9 Flow](https://github.com/10000-Bagger/free-topic-study/blob/main/jin/%5BJava%5D%20Concurrency%203%20-%20Java%209%20Flow%201.md)
- TODO : 보충 필요 - Non-Blocking, Backpressure

### 2.1.5 대망의 G1GC의 Default GC 지정!
Java 9에서 G1GC가 Default GC로 선정 되었다! G1GC에 대해 간단하게 알아보자. <br>
GC는 Live 객체를 식별하고 사용하는 곳이 없는 객체를 지우는 과정에서 발생하는 Stop-The-World 시간을 줄이는 방향으로 진화해왔다. 물론 처리량이나 효율과 같은 요소도 중요하지만, STW를 줄이는 것이 중요했다. G1GC 이전에 기본 GC로 쓰인 Parallel GC가 가진 Mark And Sweep시 발생하는 긴 STW 문제를 해결한 CMS GC 또한, Compaction이 없어 나중에 긴 Full GC를 갖는다는 문제점을 안고 있었다. <br> <br>

![image](https://github.com/binary-ho/TIL-public/assets/71186266/663122f2-f7e5-4a7d-b2b4-aabfe0a45727)

이런 문제를 해결하기 위해 등장한 것이 Garbage First GC인 G1GC이다. 쓰레기가 가득 찬 영역 부터 치우겠다는 뜻으로 위 그림과 같이 Heap을 바둑판 모양의 "region"으로 나누어 칸마다 영역을 할당한다. <br>

**G1GC는 CMS GC처럼 여러 수행 과정을 병렬적으로 처리하고, STW가 매우 짧으며, Heap 영역을 나눈 특성상 GC 과정에서 "조각 모음"과 같은 Compaction 과정이 일어난다.** <Br> <br>

우리가 기존에 알던, Eden 영역, Survior, Old 영역은 이제 논리적으로 구분된다. **기존 GC는 영역을 물리적으로 나누었다면, G1GC는 영역을 논리적으로 나눈다.** <br> <br>

빈 영역에 새로운 객체를 할당하며 Eden영역으로 만들고, Minor GC때 이 Eden 영역의 Live 객체를 **또다른 빈 공간에 할당하며** Survivor 영역이나 Old 영역으로 만든다. 이후 기존 공간은 깨끗하게 비운다. <br>

이렇게 빈 공간을 옮겨다니며, 논리적으로 영역을 할당한다. `remember set`에 사용중인 공간을 비교한 다음 꽉 찬 영역을 청소한다. <br> <br>

이러한 region 하나의 크기는 기본 heap 사이즈의 `1/2048`이다. (2^-11) `-XX:G1HeapRegionSize`값으로 조절할 수 있다. 이러한 region이 너무 작으면 많은 GC가 발생할 것이다. 애초에 G1GC는 어느 정도 큰 메모리에서 사용할 것을 상정하고 있다. 또한 region 크기는 Humongous 객체가 할당되기 위한 기준이 된다. <br> <br>
그림을 보면 region 2개를 차지한 영역이 있는데, 이 영역에 Humongous Object가 저장된다. <Br>
 
**하나의 region의 `1/2` 절반 보다 거대한 객체의 경우 Humongous 영역에 할당된다.** 이들은 연속된 메모리에 할당되며, 크기가 애매하게 남은 경우 그냥 "잉여 공간"으로 남기고 사용하지 않기 때문에 이런 영역이 많으면 Full GC를 유발할 수 있다. <br> <br>

![image](https://github.com/binary-ho/TIL-public/assets/71186266/6c94d6f1-90cc-4cc2-98fc-eb2f003af8e9)

마킹은 SATB를 사용하고, Cycle Phase는 Young, Old GC가 발생하는 `Young Only Phase`와, Mixed GC가 발생하는 `Space Reclamaton Phase`로 나뉜다. 이 글에서는 G1GC를 간단하게만 다루는 것이 목적이므로 다른 래퍼런스를 참고하라 
- 더 자세히 쓴 버전 [Java G1GC](https://github.com/10000-Bagger/free-topic-study/blob/main/jin/%5BJava%5D%20GC%204%ED%8E%B8%20-%20G1GC.md)
- 훌륭한 오라클 래퍼런스 [Getting Started with the G1 Garbage Collector](https://www.oracle.com/webfolder/technetwork/tutorials/obe/java/G1GettingStarted/index.html)

 
### 2.1.6 그 외 Compact String, Optional, Try-with-resource
- Comapct String : Java는 UFT 16을 사용하기 때문에, 모든 문자가 2 byte로 구성 된다. String 또한 문자들을 내부적으로 2 byte의 char로 저장하고 있었다. 따라서 1 byte로 표현할 수 있는 영어도 String에 저장해야 했고, 공간의 낭비가 있었다. <br> 자바 9 부터는 Compact String이 추가되어 byte로 저장한다. 따라서 1 byte로 영어를 저장할 수 있다.
- Try-With-Resource 개선 : Try문 밖에서 선언한 변수를 try문 괄호에 사용할 수 있게 되었다. (Try의 Resource로 사용할 수 있게 되었다.)
- Optional API 추가
  - `or()` : 값이 없을 경우 Optional 객체를 리턴한다. 메서드 체이닝 하면서 사용할 수 있다. 예를 들어 캐시 먼저 확인한 다음 없는 경우 DB에서 가져오고, 없는 경우 새로 만든다면 `or()`를 활용할 수 있겠다.
  ```java
  Member memeber = memberCacheRepository.findById(id)
      .or(() -> memberRepository.findById(id))
      .or(() -> memberRepository.findByEmail(email)) // 그냥 넣은 예시
      .orElseGet(this::createNewMember);
  ```
  - `ifPresentOfElse()` : 비어 있을 경우 무엇을 할지 지정할 수 있다.
  - `stream()` : Optional을 Stream 객체로 변환할 수 있다.

## 2.2 Java 10

### 2.2.1 로컬 변수 타입 추론 `var`
Java 10에서 지역변수 유형 추론을 위해 도입되었다. <br>
var는 js나 C#의 var처럼, 변수를 선언할 때 타입을 var라고 적기만 하면 알아서 타입을 추론해서 초기화 해준다. 엄격한 타입이 강점인 자바에서 당연히! var의 도입은 많은 반발이 있었지만, 편리한 경우도 꽤 있다. <br>

편리해질 수 있는 예시를 보자. **타입의 추론은 매우 명확한데에 비해 그 타입의 이름이 너무 긴 경우에 좋다.** <Br>

아래와 같은 케이스는, `Map.Entry` 부분이 너무 길다.
![image](https://github.com/binary-ho/TIL-public/assets/71186266/5b33c3c6-47ac-42ed-8604-71bda63cb1b4)

<br> <br>

var를 사용한다면, 아래와 같이 고칠 수 있다.

![image](https://github.com/binary-ho/TIL-public/assets/71186266/47dea2e8-5d4c-4ccf-b64f-7431a2a74b62)


확실히 깔끔해졌다. <Br>
또한, Non-Denotable한 요소에 사용하는 경우 용이하다. <br>

어떤 경우인고 하면, **예를 들어 익명 클래스는 타입을 마땅히 표현하기가 어렵다.** 

![image](https://github.com/binary-ho/TIL-public/assets/71186266/bce2695c-46be-4f47-9cbb-e294dcf96ad5)

위와 같이 인텔리제이의 도움을 받아 익명 클래스를 변수로 받아 맴버를 호출해 보았다.

Object에는 저런 맴버가 없기 때문에 빨간 줄이 그어지며 컴파일에 실패했다.

하지만 var를 사욯하면 아래와 같이 고칠 수 있다.

![image](https://github.com/binary-ho/TIL-public/assets/71186266/e945de6d-62c6-48fd-b5bd-b092d94befe1)

### 2.2.2 var 사용시 주의할 점

#### var를 사용할 수 없는 경우가 있다.
1. 매개변수로 사용할 수 없다.
2. 변수를 선언만 하는 경우 사용할 수 없다.
3. 람다와 함께 사용할 수 없다.

<br>

이 3가지 경우는 모두 타입을 추측할 거리가 없다.

#### 또한 var에 대한 가독성 
var에 대한 가독성은 고민해 보아야 한다. <br>
var는 코드 가독성을 박살낸다.

![image](https://github.com/binary-ho/TIL-public/assets/71186266/0ea2d00f-5515-4755-9fc2-f1a1d7c9645c)


첫 번째 줄은 직관적으로 `getChicken()`이 무엇을 반환하는지 알 수 있다. 하지만, 두 번째 줄은 대체 무엇을 반환하는지 확인하기 어렵다. (물론 사진에서는 인텔리제이가 알려주고 있다.)


### 2.2.4 Thread-Local Handshakes
`Thread-Local Handshakes` : 예전에는 GC시 발생하는 STW 발생 시 모든 쓰레드가 동시에 중단 되었다. **Thread-Local Handshakes는 STW시 Thread가 개별로 중단 가능하게 해준다.** <Br> 개발자가 직접 손댈 수 있는 영역은 아니고, gc 에서 STW시 쓰레드를 멈출 때 사용하는 safepoint 메커니즘의 최적화라고 한다. 나도 명확하게 설명하지 못 하겠다. 
- [공식 문서](https://openjdk.org/jeps/312)
- [GC safepoint가 궁금하다면..](https://github.com/10000-Bagger/free-topic-study/blob/main/jin/%5BJava%5D%20GC%201%ED%8E%B8%20-%20GC%20trade-off%EC%99%80%20safepoint.md)



### 2.2.4 그 외 추가된 점들
- Optional API 추가
  - `orElseThrow()` : 객체가 비어있는 경우 `NoSushElementException`를 던진다. 물론 지정할 수도 있다.

- Unmodifiiable Collections 추가
  - 방어적 복사 `copyOf()` : `List.copyOf()`, `Set.copyOf()`, `Map.copyOf()` <br> 방어적 복사는 Collection의 불변을 위해 return문에 사용하면 좋다. 예를 들어 어떤 클래스가 내부적으로 `foods`라는 리스트를 가지고 있다고 생각해보자. <Br> 아무리 `final`로 선언되어 있더라도, `getCards()`와 같은 메서드에서 `foods`를 그대로 반환한다면, 밖에서 리스트를 조작할 수 있게 된다. <br> 이 경우 방어적 복사를 통해 `return List.copyOf(foods)`와 같이 반환한다면, 밖에서 조작하더라도 List를 조작할 수 없다.
  - `toUnmodifiable()` : `toUnmodifialbeList()`, `toUnmodifialbeMap()`, `toUnmodifialbeSet()`

## 2.3 Java 11
- `var`를 람다 매게변수로 사용할 수 있게 되었다. -> 어노테이션 사용이 가능해져서 좋다.
- String API
  - `repeat()`
  - `lines()` : 여러 줄의 String을 line 단위로 분리해서 stream으로 변환해준다. 예를 들어 
  - 공백 관련 메서드
    - `strip()` : 문자열의 앞 뒤 공백을 제거한다. 이미 `trim()`이 있는데 뭐가 다른걸까? `trim()`은 "공백"과 그 이하를 제거한다. `strip()`은 유니코드의 공백도 구분한다.
    - `stripLeading()` : 문자열 앞 공백 제거
    - `stripTrailing()` : 문자열 뒤 공백 제거
    - `isBlank()` : 문자열이 비어있는지 확인한다. 내부적으로 `Character.isWhitespace()`를 사용한다.
  - File Method : 지정 경로 파일에서 String을 읽고 쓰는 것을 더 쉽게 만들어준 베서드들이다.
    - `writeString()`
    - `readString()`
  - `toArray()` : List를 Array로 바꿀 때 사용한다. 예전에는 사이즈를 직접 입력해야 했어서 사용이 쉬운 편은 아니였는데, java `` 부터는 `intFuntion`을 받아 편리해졌다. 


# 3. Java 17 (LTS)
이제 11 부터 17까지의 변화를 살펴보자.

## 3.1 Java 12
- String API
  - `indent(int n)` : n만큼 들여쓴다. String의 줄마다 공백을 n개 만큼 붙여준다. 이후 마지막에 줄바꿈 문자를 붙여준다.
  - `transform()` : String을 변환시키는 용도로 보인다. `<R> R transform(Function<? super String, ? extends R> f)` 이런 시그니처를 가졌고, 아래와 같이 사용한다.
  ![image](https://github.com/depromeet/amazing3-be/assets/71186266/24251814-c4f4-442a-8f17-b766ebbf177c)

## 3.2 Java 14
- Switch문 화살표 연산자 도입
  - 화살표를 통해 더욱 쉽게 선언하고 사용할 수 있게 되었다.
  - 또 다른 점은, case에 모든 경우의 수를 선언하면, `default`를 만들지 않아도 된다. 아래와 같이 사용할 수 있다. (모든 Enum을 case화 하니, default가 없어도 괜찮은 상황)
  ![image](https://github.com/depromeet/amazing3-be/assets/71186266/45a88dd8-cab7-40eb-b9a1-3b0ac44f4247)

## 3.3 Java 15
- ZGC 정식 GC 인정 Java 15 [ZGC](https://d2.naver.com/helloworld/0128759)
- String
  - Text Block
    - 여러 줄의 String을 편하게 선언하고 사용할 수 있다. 편한 기능이다.
    ![image](https://github.com/depromeet/amazing3-be/assets/71186266/ㄴedeb625b-6c0c-46d2-ad62-4a747f305971)
  - `formatted()` : String `format()`을 대체하기 위해 만들어졌다. 더 코드를 깔끔하게 짤 수 있는데, 아래와 같이 사용한다.
    ![image](https://github.com/depromeet/amazing3-be/assets/71186266/e53aab28-f063-413c-aea8-37374d8e006e)


<br>

- NullPointerException 메시지 개선!
  - 기존엔 NullPointerException이 발생하더라도, 정확히 어디서 발생한 것인지 파악하기가 힘들었다. Java 15에서 많이 개선되어 어디서 발생한지 확인하기 편해졌다. <br> 아래 예시를 보면 알겠지만, NPE가 발생한 이유를 정확히 짚어 주고 있다.
  - 예시 1 뇌가 없는 경우
  - ![image](https://github.com/depromeet/amazing3-be/assets/71186266/84b6c866-eeef-401c-882e-21e3025889f8) <br> 
  - 예시 2 치킨(사랑)이 없는 경우
  - ![image](https://github.com/depromeet/amazing3-be/assets/71186266/f454835c-e1bc-43dc-9627-d224a8dd37d0)


## 3.4 Java 16
- **Stream 개선! 아 너무 좋다!**
  - `toList()` : Stream을 List로 바꾸려면 예전에는 `collect(Collectors.toList())` 라는걸 호출해야 했는데, **이제 `toList()`만 호출하면 된다!!**
  - `mapMulti()` : 값을 하나를 받아서 여러 값을 생성할 수 있다. 기존에는 flatMap을 통해 복잡하게 생성해야 했다. (TODO 좀 더 알아보기)

<br>

- `instanceof Pattern Matching`
  - 이제 instanceof 에 패턴 변수를 넣어 패턴 매칭을 할 수 있다.
  - 자동 형변환 되며 블록 안에서 사용할 수 있다.
  - 얼리 리턴의 경우 패턴 변수 밖에서도 사용이 가능하다.

<br>

## 3.5 Record Class (Java 16)
대망의 `record class` Java 14에서 Preview로 등장했고, 16에서 정식 도입 되었다. <br>

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/6b369a11-c109-467b-b7a0-85703bdda2cf)

<br>
위와 같이 괄호 안에 만들고 싶은 맴버를 선언하면, 아래 4가지 요소가 기본적으로 자동 생성 된다.

1. **맴버 변수들이 `private final`로 선언됨**
2. **파라미터를 가진 생성자 선언됨** 
3. **같은 이름의 Getter 추가됨.** 단, `getXXX()`가 아닌 그냥 `XXX()`로 만들어 진다.
4. 필드들을 전부 활용한 **`hashCode()`, `equals()`, `toString()`를 만들어 준다.** (아래에서 자세히 다룰 예정)

<br> 

그러니까, 
- `private final List<String> brain`, `private final int level`이 선언되고, <br> 
- 이들 전부를 파라미터로 갖는 생성자가 선언되고 (`new Jinho(List<String> brain, int level)`) <br>
- `jinho.brain()`, `jinho.level()`과 같은 Getter가 추가된다.
- 기본 Object Override 메서드들은 필드를 전부 조합해서 Override하는데 아래서 자세하게 설명하겠다.


![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/dd76be45-1aaf-4629-baf0-fc3525093356)

<br> <br>

### 3.5.1 Record Class의 4가지 특징

1. 기본 생성자 없음
2. **값 변경 메서드 없음**
3. **final 클래스로 선언됨. (+ 당연히 추상 클래스가 아님)**
4. 다른 클래스를 상속할 수 없다.


![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/ba6dfa36-0070-4c31-a938-2a9630a54059)


### 3.5.2 Record Class는 불변입니까?
-> 필드들이 전부 `private final`이지만, 얕은 불변이다. <br>
**객체는 분명 private final로 선언 되었지만, 컬렉션 Getter가 방어적 복사를 하지 않는다.** <Br> 
예를 들어 컬렉션인 경우, 변경할 수 있다. 그래서 Jinho가 가진 `List<String> brain`에 add()를 할 수 있다. <br>


### 3.5.3 Record의 toString(), hashCode(), equals()

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/6b369a11-c109-467b-b7a0-85703bdda2cf)

<br>

1. `toString` : 모든 필드이름과 그 값이 포함된다! <br> Jinho 클래스가 있고, 아래와 같이 선언 되어 있을 때의 출력을 확인해보자. <br>

![toString](https://github.com/10000-Bagger/free-topic-study/assets/71186266/949df902-ac61-445f-9e9b-8d105d7a6ea2)

2. `eqauls()` : **필드 값이 모두 같으면, 같도록 정의되어 있다.** (같은 객체인 것은 당연)


![equals](https://github.com/10000-Bagger/free-topic-study/assets/71186266/a996e627-930e-42cb-80a8-7efc845320a2)

3. `hashCode()` : 모든 필드를 사용. 모든 필드가 같은 경우 같은 hashCode를 반환한다!

![hashCode](https://github.com/10000-Bagger/free-topic-study/assets/71186266/a81599ef-89c1-44aa-8eb2-e0466b92917a)

### 3.5.4 Record와 생성자

#### 1. 생성시 인수를 검증하는 법
아래와 같이 Class 이름에 중괄호만 붙이면, Record 기본 생성자시 넘겨 받은 값들에 대한 검증 메서드를 선언할 수 있다! <br>

![검증](https://github.com/10000-Bagger/free-topic-study/assets/71186266/ff6f48c3-425e-4e1c-b8f1-9cffb3176d8e)



<br>

예시는 brain list가 비어 있는 경우 예외를 발생시킨다. <br>
한번 결과를 살펴보자.

![검증 메서드에 의해 생성되지 않는다](https://github.com/10000-Bagger/free-topic-study/assets/71186266/3270dd89-490e-41bd-b8b5-d8b5aa4f9898)


<Br>

noBrain만 생성시 예외가 발생하는 것을 확인할 수 있다.


#### 2. 다른 생성자를 선언하는 방법

아래와 같이 `this()`를 호출하여 생성자를 재정의 할 수 있다! <br>

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/f6e63217-4b70-43ac-b17d-7040172cf17e)

<Br> 

결과는 아래와 같다.

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/83a0fed4-4006-4b63-91ba-cd78589d3b42)

<br>

결국 기본으로 생성되는 생성자를 호출해야 하는 구조임을 명심해라.


## 3.5 Java 17
### 3.5.1 Sealed 키워드 (JDK 15 추가)
Sealed Class/Interface는 "밀봉된"이라는 의미로, 오직 허가된 Class와 Interface만 해당 클래스를 상속하거나, 구현할 수 있다. <br>
이를 통해 개발자는 하위 클래스나 구현체를 쉽게 제어하고, 알아낼 수 있다. <Br>

또한 superclass 사용을 제한하기 위해 access modifier 보다 좀 더 선언적인 방법을 제공해준다. 에를 들어 private, protected 보다 조금 더 분명하게 이해할 수 있다. <Br>
(abstract class도 가능하다.)

#### 사용하는 방법
상속을 제한하고 싶은 상위 클래스에 `sealed` 키워드를 사용한다. 이후, `permits` 키워드 뒤에 이 클래스를 상속하거나 구현할 수 있는 하위 클래스들을 선언한다! <br> <br>

`permits`의 대상이 된 클래스들은 아래 규칙을 지켜야 한다.
1. **final, sealed, non-sealed 중 하나를 선택해서 구현해야 한다!** <br> sealed인 경우 당연히 permits를 지정해야 한다. <br> 그리고 **permits 대상이 구현체인 경우 record type도 가능하다.** 아마 record는 final로 선언되기 때문인 것 같다.
2. sealed type과 같은 패키지에 있거나, 같은 모듈에 위치해야 한다. (java 9의 named module)

<br> <br>

**참고로 같은 클래스 파일 안에 있는 클래스는 `permits`으로 지정하지 않아도 아니여도 상속 받을 수 있다.**


위와 같이 검사 이후 하위 클래스 

### Sealed Class의 장단점
#### 장점
1. 높은 안정성 : 명시적이기 때문에 상속 구조에서의 불안정성이 줄어든다.
2. 새로운 유형의 추상화 : 더욱 유연한 추상화 가능
3. 가독성 향상 : 하위 클래스 목록을 명시하기 때문에, 파악이 빠르다.
4. 실수 방지
#### 단점
1. 계층 구조의 복잡성이 증가한다.
2. 유지 보수시 손이 더 많이간다 : 하위 클래스 목록을 바꿀 때마다 코드를 수정해야 한다.
3. 유연성 감소 : 실드 클래스를 사용하면 하위 클래스를 제한할 수 있는 대신 유연성이 감소한다.

### 3.5.2 Pattern Matching for switch (preview)
21에 정식으로 도입된다. 패턴 매칭과 Sealed Class <br>
앞서 소개한 `instanceof`의 패턴 매칭과 똑같이 사용 가능하다.

```java
static double getDoubleUsingSwitch(Object object) {
    return switch (object) {
        case Integer integer -> integer.doubleValue();
        case Float floatValue -> floatValue.doubleValue();
        case String string -> Double.parseDouble(string);
        default -> 0d;
    };
}
```

위와 같이 case문에서 Type 검사 이후, 형변환된 채로 바로 사용할 수 있어 편리하다!

## 3.6 Preparing for Spring Boot 3.0
**Java 17이 중요한 또 하나의 이유는 Spring Boot 버전을 3.0으로 올리기 위해선 필수 적으로 Java 17이 준비 되어야 하기 때문이다!** <br>
언어나 기술을 항상 최신 버전으로 유지하는 것은 아직 발견 못한 버그를 받아버릴 수도 있다는 위험성이 있지만, Java나 JS처럼 핵심 언어들은 주요 버전 기준으로 혹은 LTS를 기준으로 최신 버전을 유지하는 것이 나쁘지 않다. <br>

왜냐하면 관련 생태계 라이브러리나 프레임 워크의 최신 버전 중 기본 언어의 최소 버전을 요구하는 경우가 있기 때문이다. <br> <br>

물론 그 외에도 "새로운 기능 사용 가능", "이전 버전에서의 bug fix" 등의 장점은 기본적으로 따라온다. <Br> 
하여튼, Java 17까지의 변화를 알아봤으니, 이번엔 Spring Boot 3로 마이그레이션 하는 법을 살펴보자. <br>
너무 잘 쓰여진 글이 있어서 첨부한다. 래퍼런스를 너무 잘 달아 놓아서, 내가 적는게 무의미 할 것 같아 링크를 단다...
- [Preparing for Spring Boot 3.0](https://revf.tistory.com/260)


## Reference

- 그동안 내가 작성해온 블로그와 TIL의 여러 글들..  + 자바의 정석 + 이펙티브 자바 + 모던 자바인 액션 등..
- [호호의 Java 11](https://www.youtube.com/watch?v=LcIyHlE2NlA)
- [Java Records : A Deep Dive - Muhammad Ali](https://medium.com/@ikhaleepha/java-records-a-deep-dive-e06fec984462)
- [우리 팀이 Java 17을 도입한 이유](https://techblog.gccompany.co.kr/%EC%9A%B0%EB%A6%AC%ED%8C%80%EC%9D%B4-jdk-17%EC%9D%84-%EB%8F%84%EC%9E%85%ED%95%9C-%EC%9D%B4%EC%9C%A0-ced2b754cd7)
- [Java Sealed class 와 Switch - ysk(0soo)](https://0soo.tistory.com/222?category=580548#Sealed%--%ED%--%B-%EB%-E%--%EC%-A%A-%EC%-D%--%--%EC%-E%A-%EB%-B%A-%EC%A-%--)
