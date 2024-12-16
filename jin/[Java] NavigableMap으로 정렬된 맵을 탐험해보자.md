Navigable이란, "가항(可航)의" 라는 뜻으로, "배가 다닐 수 있는", "항해할 수 있는" 의 의미가 있다. HashMap도 결국 전부 이어져 있어 내부를 순회할 수 있다. 버킷이 있고, 버킷 안은 연결 리스트 혹은 레드-블랙 트리의 형태로 이어져 있다. 하지만, NavigableMap만큼 자유롭지는 않다. <br>
NavigableMap은 배열 만큼은 아니지만, 정렬된 상태의 Map을 여러 방법으로 자유롭게 탐색할 수 있게 해준다. <br>
오늘은 Red-Black Tree를 공부하다 알게 된, Java TreeMap이 구현한 SortedMap의 하위 클래스인 NavigableMap을 소개하겠다.

< 간략한 목차 >
1. Java에서의 O(log)급 lower_bound, upper_bound 제공
   + 가중치가 있는 랜덤 문제
2. 빠른 SubTree 제공
   + 순위가 자주 상황에서, 어떤 점수의 순위

# 1. Java에서의 O(log)급 lower_bound, upper_bound 제공
예전에 나는 주로 C++로 자료구조-알고리즘 문제를 500개 이상 풀어왔다. <br>
그러나 오직 Java만 코딩 테스트 언어로 허용하는 회사가 있기도 하고, 언어 인터페이스도 외울 겸 Java로 갈아타기로 했다. <br>
그때는 Java에 대한 책 고작 한 두권을 읽은 후였기 때문에 자바에 대해 잘 몰랐다. C++ STL vector의 lower_bound나 uppder_bound과 같은 연산이 Java에는 없어서 불편하다고 여기 저기 말하고 다녔다. 당시 인터넷에 대충 Java lower_bound라고 검색해 보았을 때도 이분 탐색을 통해 직접 구현하는 방법만 알려줬기 때문에 없는 줄 알았다 <br>
그러나 자바에도 있다! Java TreeMap은 집합 내에서 어떤 수 "이상", "초과", "미만", "이하" 모두 제공해준다. <br>

TreeMap은 NavigableMap의 구현체 중 하나이며, **값이 정렬 되어 있다.** NavigableMap이 아래 인터페이스들을 제공해준다. <br>

1. `이상` : `getCeilingEntry(K key))`, `getCeilingKey(K key))` 
2. `초과` : `getHigherEntry(K key))`, `getHigherKey(K key))`
3. `이하` : `getFlooringEntry(K key))`, `getFlooringKey(K key))`
4. `미만` : `getLowerEntry(K key))`, `getLowerKey(K key))`

<Br>

- getEntry는 말 그대로 Map의 Entry를 가져오고, getKey는 Key를 가져온다. Value값이 필요하냐 마냐의 차이에 따라 잘 사용하면 될 것이다.
- ceiling은 "천장"이라는 의미로 입력한 Key와 값이 같거나 더 큰 Key 중 가장 작은 Key를 가져온다.
- higher는 "초과"의 개념으로 Key보다 더 큰 Key들 중 가장 작은 Key를 가져온다.
- floor는 "바닥"이라는 의미로 "이하"의 개념이다. Key와 값이 같거나 작은 Key 중 가장 큰 Key를 가져온다.
- lower는 "미만"의 개념이다.

<br> <br>

## 1.1 어떻게 빠른 lower_bound를 제공해줄까?

TreeMap은 Red-Black Tree으로 구현되어, **높이 균형이 맞춰진 정렬된 이진 트리이다!** (Depth가 일정하다는 의미) <br>
덕분에, 이분 탐색급의 아주 빠른 속도로 O(log)의 시간복잡도만에, 앞서 언급한 연산들을 제공한다. Red-Black Tree가 왜 빠른지 궁금하면 이 글을 읽어보자. [코드로 이해하는 Red-Black Tree의 연산과 Java TreeMap에서의 구현](https://dwaejinho.tistory.com/entry/Java-Red-Black-Tree%EC%9D%98-%EC%97%B0%EC%82%B0-%EA%B3%BC%EC%A0%95%EA%B3%BC-Java-Util%EC%97%90%EC%84%9C%EC%9D%98-%EA%B5%AC%ED%98%84) <br> <br>

예시로 한번 `getCeilingEntry()`의 내부 동작을 확인해보자.

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/3bfced86-0412-42a0-b341-0c75bfaa0bf1)


### 1. `while문 전`
root로 부터 null이 아닐 때 까지 탐색한다. 헌재 노드는 p로 나타낸다.
### 2. `while문 ~ 첫 if문`
compare메서드는 두 값을 비교한다. 첫 파라미터가 큰 경우 양수가 반환된다. 
내부적으로 트리 자체의 `comparator`가 있다면 우선적으로 사용하고, 없다면 Key의 compareTo를 호출한다. (Map의 Key들은 기본적으로 Comparable을 구현해야 한다.)
![compare](https://github.com/10000-Bagger/free-topic-study/assets/71186266/2fa0287e-c8a0-474a-a3ae-15f07e828331) <br>

### 3. `첫 if문`
cmp값이 음수인 경우, 찾고자 하는 값인 key가 현재 노드 보다 작다는 것이다. null이 아니라면 왼쪽으로 이동한다.
**만약 왼쪽 노드가 없다면, 현재 노드를 루트로 하는 서브트리 내에서 현재 노드가 가장 작은 값인 것이다!** 
**지금 찾고 있는 값은 key값 이상의 값인데, 현재 노드는 key보다 값이 크면서 && 현재 노드 보다 더 작은 값은 없다.** 따라서 현재 노드를 반환한다.

### 4. `else if (cmp > 0)`
cmp가 양수이므로, 찾고자 하는 key가 현재 노드 보다 크다는 것이다. null이 아니라면 오른쪽으로 이동한다.
오른쪽 노드가 없을 때가 문제인데, 이는, 현재 노드를 루트로 하는 서브트리 내에서는 현재 노드가 가장 큰 값이라는 것이다. <Br>
오른쪽으로 빠져야 한다는 것은, 찾고자 하는 키는 현재 노드 값 보다 더 크다는 것인데 이보다 큰 값이 없다는 것이다. <br>
그래서 부모가 존재하고 && 현재 노드가 부모 노드의 오른쪽 자식인 동안 계속해서 타고 올라간다. **즉, 더 작은 값을 찾아 타고 올라가는 것이다.** <br>
이 분기로 들어오게 되는 경우는 아래 2가지 경우가 있을 것이다. <br>

1. 만약 트리 내에 Key 이상의 값이 아예 없다면, Root에 도착하고, TreeMap Root의 부모는 Null이기 때문에 **Null이 반환된다.**
2. 중간에 해당 분기로 들어가는 경우가 있는데, 타고 올라가다가 왼쪽 자식인 경우 더 큰 값인 부모를 반환하게 된다. **이 값이 바로 Key보다 크면서 가장 작은 값이다.**

<br>

둘 다 감이 안 올테니 그림으로 보는게 좋다.

![redblacktree](https://github.com/10000-Bagger/free-topic-study/assets/71186266/333a8b59-e73a-483c-98ec-bb7a6d2aa9b1)

<br>

위 그림은 Red-Black Tree이다. 앞서 말한 1번 경우를 확인해보자. `getCeilingKey()`에 "30"을 넣었다고 가정해보자. <Br>
![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/e773a18f-6c72-4a16-8044-457cd02fe801)

<br>

13 -> 17 -> 25 -> 27 순서대로 현재 노드 보다 Key값이 30으로 크므로 오른쪽 자식으로 계속해서 이동할 것이다. 그러다가 27에 도착하면 오른쪽 자식이 없는 케이스가 나오게 된다. 이때 앞서 보여준 While문을 통해 계속해서 부모로 타고 올라간다.

```java
  ...생략

  Entry<K,V> parent = p.parent;
  Entry<K,V> ch = p;
  while (parent != null && ch == parent.right) {
      ch = parent;
      parent = parent.parent;
  }
  return parent;

  ...생략
```

결국 Root에 도착할 것이고, Root의 부모인 null을 반환하게 된다. <br>
**트리에 30 이상인 Key값은 없으니, null을 반환한 것은 적절한 결과가 맞다!** <br> <br>

그리고 두 번째 케이스를 살펴보기 위해 "24"를 넣는다고 생각해보자. <br>
13 -> 17 -> 25까지 오른쪽 자식으로 이동할 것이다. 그리고, 24는 25보다 작기 때문에 cmp 값은 음수일 것이고, 앞서 보인 첫 번째 `if` 분기로 이동할 것이다. 그렇다면 22에 도착할 것이다. <br>

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/3bc2386a-5935-4023-a41e-d98d3d473f4f)

즉, 여기까지는 `13 -> 17 -> 25 -> 22`이다. <br>
이때, 24는 22보다 크기 때문에, cmp 값은 0 보다 클 것이고, 오른쪽으로 가야 하는데 자식이 없어서 앞서 보인 부모를 타고 올라가는 while문에 도착할 것이다. <br>

**문제는, 22는 25의 오른쪽 자식이 아니다.**

```java
  ...생략

  Entry<K,V> parent = p.parent;
  Entry<K,V> ch = p;
  while (parent != null && ch == parent.right) {
      ch = parent;
      parent = parent.parent;
  }
  return parent;

  ...생략
```

그래서 이번에는 while문에 들어가지 않고, 현재 노드 p의 부모인 (22의 부모인) 25 노드를 return하고 메서드가 끝날 것이다. <br>
**이는 적절한 답이다! 왜냐하면, 위 트리에서 24 이상이면서, 가장 작은 값은 바로 25이기 때문이다!** <br> <br>

### 5. `else`

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/d5d4167a-ff61-4435-be50-ad65f9c6f884)

마지막 else는 cmp 값이 0일 때이다. 즉, 값이 "같을" 때이다. ceiling은 "이상"이므로 현재 노드 p를 return 하는 것은 적절하다고 볼 수 있다. <br> <br>


### 나머지도 비슷하다.
나머지 3가지 메서드도 거의 비슷하게 진행된다고 생각하면 된다. TreeMap은 이렇게 Depth가 일정한 정렬 이진트리인 Red-Black Tree를 활용해, NavigableMap의 인터페이스들을 빠른 시간복잡도로 구현했다. <br>

혹시 TreeSet이 궁금하다면, 애초에 TreeSet은 HashSet이 그러하듯, 내부적으로 TreeMap을 가지고 있는 형태로 구현 되었기 때문에 자신이 가지고 있는 TreeMap의 메서드들을 그대로 호출한다. <br>

## 1.2 가중치가 있는 랜덤 선택 문제

이런 4가지 메서드를 활용해 다양한 이분탐색 문제를 해결할 수 있다. 그 중에서 쏘카 기술 블로그에서 NavigableMap 글을 읽으며 사용법을 알게 된, "가중치가 있는 랜덤 선택 문제" 해결을 소개하겠다. <br> 

[Java Map의 확장 인터페이스 NavigableMap 이야기](https://tech.socarcorp.kr/dev/2021/10/19/sub-interfaces-navigablemap.html)


# 2. 빠른 SubTree 제공
NavigableMap은 앞서 소개한 메서드 외에도 다양한 서브 맵을 제공해준다. <br>

원소 범위만 정해주면, 트리를 뚝 잘라서 서브 트리를 제공해준다.

### 1. 범위 서브 트리
범위를 지정해 SubTree를 만들 수 있다. 범위가 되는 두 숫자를 포함할지 말지 여부를 결정하는 boolean 파라미터가 있는 버전이 오버라이드 되어 있다.

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/25380400-662a-485c-aaaf-01febd23f0aa)


### 2. HeadMap, TailMap

더 보여주고 싶었던 쪽은 이쪽이다. 이 두 메서드는, **어떤 값 보다 큰 숫자들로 이루어진 Map, 혹은 더 작은 숫자들로 이루어진 Map을 제공해준다!** <br>
![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/106ffae6-a6c6-449c-a85a-987c3ba84c94)

<br>

- `headMap()` : Map에서 인수로 전달한 Key가 가장 큰 값인 서브 트리를 만들어 반환해준다. (어떤 Key의 앞쪽 - 헤드로 이루어진 맵)
- `tailMap()` : Map에서 인수로 전달한 Key가 가장 작은 값인 서브 트리를 만든다. (어떤 Key의 뒤쪽 - 꼬리로 이루어진 맵)

Red-Black Tree의 경우 서브트리만 그냥 갖다가 주면 되니까 서브 트리를 복사하는 방식으로 빠르게 구현했겠다 싶었는데, 더 빠르게 제공해준다. <br>
그냥 복사를 안 한다;; 원본 트리를 그대로 래퍼런스로 들고 있고, 범위만을 제한하면서 사용한다! <br>

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/26a6b7fb-4d2f-4608-9c7a-1f5cad26b8e3)

<Br>

위 그림과 같이, headMap을 떼어낸 다음 원소를 지우니, 원래의 맵에서도 지워진 것을 확인할 수 있다! <Br>
이름만 보고 실제로 트리를 떼어낸다고 혹시나 오해해서는 안 된다. 

1. 장점 : 래퍼런스만 저장하니까 복사 속도가 매우 빠름
2. 단점 : SubMap만 변경해도 실제 Map까지 변경된다. 모르고 사용하는 경우 실수할 수 있다. 


<br> <br>

이러한 headMap과 tailMap을 통해 순위가 빠르게 변화는 상황에서 빠르게 현재 순위를 확인할 수 있다.
