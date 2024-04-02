# 자바 언어 성능 향상 기법

이 단원에서는 다양한 Collections와 내부에 이미 구현된 알고리즘들을 파악해, 상황별로 좀 더 성능에 좋은 선택지를 고려할 수 있게 하는 것이다. JVM 레벨 보다는 직접 자바 언어를 사용해 코드를 작성하는 레벨에서의 안내다.

<br>

## 1. 컬렉션 최적화 (아님)
(책의 단원 제목이 컬렉션 최적화지만, 그냥 자바 컬렉션에 대한 내용이 적혀 있었다) 

<br>

대부분의 PL 라이브러리는 최소한 두 개의 컨테이너를 제공한다. (이하를 내 편의대로 더 익숙한 용어인 '자료구조' 라고 부르겠다.)
- Sequential Container: 수치 인덱스로 표기한 특정 위치에 객체를 저장하는 자료구조 (ex index가 있는 Array와 같은 형태의 자구)
- Associative Container: 객체 자체를 이용해 컬렉션 내부에 저장할 위치를 결정하는 자료구조. (ex HashTable을 내부적으로 사용하는 자료구조를 생각해보면 될 것 같다. 객체가 가진 상태 값을 통해 해쉬 값을 만들고 저장될 버킷을 결정하는..)

<br>

컨테이너들이 자신이 가진 역할과 기능대로 "잘" 작동하려면, 객체는 Comparability(호환성)과 Equivalence(동등성)가 있어야 한다. 예를 들어 코어 자바 컬렉션 API에서는 모든 객체가 반드시 `hashCode()` 메서드와 `equals()` 메서드를 구현해야 한다고 표현한다. <br> <br>

이 두 메서드의 역할은 해당 객체가 가지게 될 `해시코드 값을 만들고`, `두 객체가 동일한 객체인지 확인하는 것`이다. <br>
객체는 `hashCode()`를 통해 HashTable 형식의 자료구조에서 자신이 들어가게 될 Bucket을 고른다. 그리고, Bucket 내부는 보통 Associative한 형태의 자료구조로 구현되어 있는데, 같은 해쉬코드 값을 가진 객체들끼리 누가 누구인지 비교하기 위해 `equals()`가 사용된다. 이는 조슈아 블로크의 이펙티브 자바에서도 다룬 규칙이다. [심심한 사람은 읽어보라우 - Item 11. equals를 재정의 하려거든 hashCode도 재정의하라.](https://github.com/binary-ho/TIL-public/blob/main/Effective%20Java/Item%2011.%20equals%EB%A5%BC%20%EC%9E%AC%EC%A0%95%EC%9D%98%ED%95%98%EB%A0%A4%EA%B1%B0%EB%93%A0%20hashCode%EB%8F%84%20%EC%9E%AC%EC%A0%95%EC%9D%98%ED%95%98%EB%9D%BC.md) 
<br> <br>

자바는 기본적으로 컨테이너에 객체 자신이 아니라, 래퍼런스를 가리키기 때문에 C/C++의 배열이나 벡터만큼의 성능을 얻을 수 없다고 한다. 게다가 서브시스템이 가비지 수집까지 해주는 만큼, 저수준의 메모리 제어는 포기해야만 한다. <br>
아줄 시스템의 CTO 길 테네는 이것이 자바와 C의 성능 장벽을 만든다고 주장한다.

<br> <br>

단원 제목이 최적화지만, 단순히 컬렉션에 대한 내용만 있었다. 그냥 책에 실린 계보도나 보고 가자 (아래 그림 말고도 더 있고, 컨커런트 패키디들도 없다. 모두 포함된 그림을 못 찾음) <br>
![image](https://github.com/binary-ho/TIL-public/assets/71186266/e183ec9c-fa96-4d88-9b30-ae786eb04045)

<br>

## 1.2 List의 최적화

Java List는 대표적으로 ArrayList와 LinkedList의 두가지 기본 형태로 나누어 볼 수 잇다. 앞에는 시퀀셜한 자구고, 두 번째는 Associative한 자구이다. <br> 

너무 기본이라 읽는 사람 지루하겠지만, 기본적으로 Random Access는 시퀀셜한 ArrayList가 빠르다 - O(1). 물론 그만큼 데이터 추가 및 삭제가 느리다. 중간에 데이터를 삽입하거나 삭제하는 경우, 한칸씩 밀고 땡겨야 할 것 아닌가? 꽉차기라도 한다면 최악이다. 더 큰 배열로 이사가기 위해 데이터들의 복사가 발생한다. 그래서 - O(N)이다.

![image](https://github.com/binary-ho/TIL-public/assets/71186266/076371db-04bc-4f47-af75-7a2fa649cdb7)

<br>

 그리고 LinkedList는 반대이다. 인덱스가 없고 레퍼런스로 다음 객체와 이전 객체를 가르키는 형태인만큼, 랜덤 Access는 O(N)에 육박하고, 삽입 삭제는 O(1)이다. 단지, 사이에 끼워 넣으면 되기 때문.. <br>

 상황에 맞게 ArrayList와 LinkedList를 적절하게 사용하면 되겠다. LinkedList의 특별한 기능을 사용하지 않고 && RandomAccess가 잦다면 -> 그냥 ArryList를 쓰는 것이 좋다.

 <br>


 ### 1.2.1 ArrayList
 앞서 그림으로도 보인 이 자료구조는 **Java에서 기본적으로 10의 사이즈를 가졌다.** <br> 따라서, 크기가 10보다 더 커질 수 있다면 길고 시간이 오래 걸리는 복사 과정이 일어난다. 특히 객체에 들어갈 데이터의 수가 매우 많아, `꽉차면 조금 늘리고 -> 꽉차면 조금 늘리고 -> 꽉차면..` 과정이 반복된다면, 엄청난 시간이 소요될 것이다. <br> <br>

 **따라서, 미리 크기를 추측할 수 있다면, 그 크기만큼 선언해라! <br> 생성자로도 설정이 가능하고, `ensureCapacity()` 메서드를 통해 용량을 늘릴 수도 있다.** <br>
 
 **마이크로 벤치 실험 결과에 따르면, 100만개 데이터를 Array에 추가할 때, 크기를 미리 100만으로 선언한 배열은 초당 100회의 연산을 추가적으로 처리한다.** <br>
 그러니까, ArrayList를 사용할 때, 크기가 추측 가능하다면 미리 그 크기만큼 선언해보자! 

<br> <br>

LinkedList는 어차피 뒤에다가 "원소를 붙이는"과정만으로 간단하게 노드를 추가하기 때문에, 작업은 항상 O(1)이다. 미리 크기를 정해둘 필요가 없다.


## 1.3 Map 최적화

### 1.3.1 HashMap 
HashMap은 우리가 CS책에서 접해본 HashTable의 Java 버전이라고 생각하면 된다. 앞서 `hashCode()`와 `equals()`에 대해 이야기 할때 언급한 방식으로 데이터가 저장된다. <br>

![image](https://github.com/binary-ho/TIL-public/assets/71186266/b033d11e-4854-413f-a100-11d10ee3124b)

<Br>

`hashCode()`를 통해 객체가 들어갈 bucket을 구한다. 그림에서는 왼편에 세로로 서있는 배열이 bucket이다. 보통 hashCode로 얻은 값을 버킷 갯수로 모듈러 해서 들어갈 곳을 구한다. 그 다음에는 데이터를 그냥 쌓는다. 단, `equals()`를 통해 버킷 안에서의 동등성을 판단한다. <Br>
다들 알겠지만 이 동등성은 탐색과 삭제시 객체를 찾기 위해 사용되고, 저장시에도 중복 저장하지 않기 위해 같은 객체가 있는지 확인하는 과정에서 쓰이게 된다. <br> <br>


이러한 **HashMap를 생성할 때, 성능에 영향을 줄 수 있는 중요한 매개변수 2개가 있다. (생성자를 통해 조절 가능)** <br>
1. `initialCapacity`: 초기 생성시 버킷의 수이다. **default 16**
2. `loadFactor`: 버킷 용량을 자동 2배 증가하기 위한 한계치. 보통 %로 표현하고, **default 0.75** <br> **용량을 2배 늘린 이후에는 저장된 데이터들을 재배치하고 해시를 다시 계산하는 Rehash 과정을 거친다.**

<br>

1. initialCapcity가 정확 -> 테이블이 커져도 Rehash 과정이 없어서 좋다
2. loadFactor 값이 0.75 이상 (크다) -> **Rehash 빈도는 주는 대신 대체적으로 버킷이 꽉꽉 찬다. -> 꽉차면 탐색과 순회의 속도가 느려진다!!**

<br>

### Bucket Treeify

"트리화"는 버킷 원소 저장 방식을 트리로 바꾼다. <br>
원래는 LinkedList로 구현되어 있어야 하는데, 크기가 커지면 순회 속도가 매우 느려질 것이다. 재수가 없어서 한 버킷에 데이터들이 엄청 모이다 보면, O(N)와 비슷해지며 고통 받을 것 아닌가? **이 문제를 해결하기 위해 버킷당 미리 설정된 `TREEIFTY_THRESHOLD`이 정해진 갯수만큼 모이면, 버킷을 TreeNode로 바꿔버린다.** (옛날에 처음 이 이야기를 들었을 때 매우 신기했다.) <br> 

처음부터 트리로 가기에는 비록 용량이 적은 Red-Black Tree를 썼음에도, 리스트 형태 노드 보다도 2배 정도 거대하다고 한다. 따라서, 기본적으로 LinkedList 형식으로 구현되어 있다. <br>
그래서 값이 버킷마다 아주아주 골골 들어간다면 버킷을 TreeNode로 바꿀 일도 없다. 있더라도 **initailCapacity나 loadFactor를 먼저 손볼 수 있는지 보는게 맞다.**

### 1.3.2 TreeMap
TreeMap은 Red-Black Tree를 구현한 Map으로, 기존 이진 트리 구조에 "컬러링"을 통한 메타데이터를 추가해 균형을 맞추는 "균형 트리"이다. <br>
키가 다양할 때 유리하고, 트리인만큼 "범위 검색"에 탁월하다. <br>
**`get()`, `put()`, `containsKey()` - key가 트리내 있는지 search 하는 메서드, `remoce()`는 무려 O(log(N))에 연산 가능하다.** <br>


#### 멀티맵 이야기
자바는 하나의 키에 여러 값이 묶인 MultiMap을 제공해주지 않는다. `Map<Key, List<Value>>` 형태로도 충분히 해결 가능하기 때문이다. 나는 옛날에 Map의 사용이 능숙하지 못할 때 구글의 "구아바"라이브러리에서 제공해주는 MultiMap을 살 썼던 기억이 있다. <br> <br>

### EnumMap 이야기
책에는 나오지 않는데, Java에는 Enum Type만을 위한 Map이 따로 있다. 장점이 아주 다양한데, 너무 졸리기 때문에 궁금한 사람은 옛날에 정리해둔 글을 참고해보자.

- [Item 37 ordinal 인덱싱 대신 EnumMap을 사용하라](https://github.com/binary-ho/TIL-public/blob/main/Effective%20Java/Item%2037.%20ordinal%20%EC%9D%B8%EB%8D%B1%EC%8B%B1%20%EB%8C%80%EC%8B%A0%20EnumMap%EC%9D%84%20%EC%82%AC%EC%9A%A9%ED%95%98%EB%9D%BC.md)

<br>

## 1.4 Set 최적화
Set의 성능을 고려할 때 생각해야 할 부분은 Map과 비슷하다. <br>
무려 HashSet은 내부적으로 HashMap을 해쉬 테이블로써 사용하고 있기 때문에, 비슷한게 당연하다. LinkedHashSet도, LinkedHashMap을, TreeSet도 HashSet을 내부적으로 활용한다. <Br> <br>
그런만큼, 시간 복잡도도 거의 유사한데, HashSet은 삽입 삭제, 검색을 O(1)만에 수행할 수 있고, TreeSet은 삽입 삭제 복잡도가 lon(n)이다. <br>

**또한 LinkedHashSet으로 Set을 사용하지 않는 한 원소 순서를 유지하지 않는다. TreeSet은 순서가 유지된다.**  

<br> <br>

여기도 EnumSwet에 대한 이야기가 없는데, 궁금하면 참고해보자

- [Item 36. 비트 필드 대신 EnumSet을 사용하라](https://github.com/binary-ho/TIL-public/blob/main/Effective%20Java/Item%2036.%20%EB%B9%84%ED%8A%B8%20%ED%95%84%EB%93%9C%20%EB%8C%80%EC%8B%A0%20EnumSet%EC%9D%84%20%EC%82%AC%EC%9A%A9%ED%95%98%EB%9D%BC.md)

