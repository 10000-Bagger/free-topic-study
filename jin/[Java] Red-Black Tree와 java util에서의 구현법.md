- 레드 블랙 트리란?
- 규칙
- 동작 원리
- 회전과 recoloring
- Java에서의

# Red-Black Tree와 java.util에서의 구현

## 1. Red-Black Tree란
![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/b5492724-25b2-48ce-8854-c10f731f6e5c)


레드 블랙 트리란 Balanced Binary-Search Tree로, 모든 노드들을 빨간 색 혹은 검은 색으로 칠해 놓았기 때문에 레드-블랙 트리라고 부른다. <br>

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/251fdb6c-11b1-4675-a18f-5f51d406ac7f)

<br>

어이 없지만, 이런 이유로 Red-Black 트리이다. 트리를 처음 고안한 논문의 저자들이 사용할 수 있었던 프린터가 만들어낸 가장 "멋진"색이기 때문이라고 한다. <br> <br>

레드 블랙 트리는, 이런 빨강-검정으로 트리의 노드들을 색칠하고, 색에 대한 규칙을 세워 규칙을 어기는 경우 다시 균형을 맞춰 높이를 낮춘다. <br> 
균형을 맞추는 트리들이 균형을 맞추는 이유는 트리 Depth를 줄여 빠르게 탐색하기 위해서이다! 편향된 트리를 보면 알겠지만, 탐색 시간 복잡도가 O(N)이 된다. <br>

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/5cb52a3d-29a9-4667-a00b-245c46a2fc78)

가장 아래에 있는 데이터를 찾는 경우 데이터 전체 갯수만큼 탐색하게 된다. <br>

균형을 맞췄을 때, 최악 탐색 시간 복잡도가 줄어들게 되기 떄문에, 균형을 맞추는 것이다.

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/afac3f0b-ed2e-4696-b422-633ca215ccd0)

어떤 데이터를 탐색해도 균일하게 빠르다. (시간 복잡도 증명은 3번 글에 기재) <br> <br>

<!-- ## 1. 트리 탐색 시간 복잡도에 관하여 -->
<!--  -->
<!-- 트리의 탐색 시간 복잡도를 계산해보자. <br> -->
<!-- 한 노드에서 자식 노드를 선택할 때, 선택지가 M개라고 해보자. 예를 들어 이진트리의 경우 단 2개의 자식 노드 밖에 없어 M = 2이다. <br> -->
<!-- 그리고 탐색 할 때 데이터가 위치한 Depth를 h라고 해보자. 트리 탐색 시간 복잡도는 이 h에 비례해 증가할 것이다. 결국 h 횟수 만큼 어떤 탐색을 하는데, O(h)라고 나타내보자. <br> -->
<!-- 탐색할 데이터가 N개이고, 한 노드는 M개의 자식 노드를 가졌다고 생각해보자. M개의 자식노드를 전부 살펴보고 자식 노드로 이동하는데, 최악 h회 이동한다. 따라서, 정렬된 트리에서 N개의 데이터 중 원하는 데이터를 찾는 최악 탐색 횟수는 M^h회이다. N개의 데이터 중 원소 하나를 찾는 함수를 S(X)라고 했을 때 ->  O(S(N)) = M^h 이다. <br> -->
<!-- h와 M, N의 관계는 어떨까? <br> -->

<!-- 루트를 Depth 1이라고 할 때, k번째 Depth에는 M^k개의 노드가 있다. 그러니까, 1층 부터 M개, 2층엔 M^2개, 3층엔 M*3개.. <br>  -->
<!-- 따라서, M^1 + M^2 + M^3 + ...  + M^k + ... + M^h 이 전체 노드 갯수인 것이다!  -->
<!-- - 멱급수이므로, N = M^(h + 1) - 1 / (M - 1)과 같은 형태이다. -->
<!-- - 정리하면, Log_M((M - 1) * N + 1) = h + 1이다. -->
<!-- - Big-O Notation으로 O(Log_M(M-1) + Log_M(N + 1))이므로, 앞의 상수가 무의미해서 O(Log_M(N + 1)) 이고, -->
<!-- - O(Log_M(N + 1)) -->


<!-- AVL Tree나, B-Tree -->

## 2. Red-Black Tree 규칙
레드 블랙 트리는 균형을 맞추기 위해 색을 칠한다고 했다. 색칠된 노드들의 규칙을 살펴보자.

1. 모든 노드는 빨강 혹은 검정으로 색칠 되어 있다.
2. Root는 Black이다.
3. 모든 Leaf Node는 Black이다.
4. **빨강 노드는 연속될 수 없다.**
5. Root 노드에서 모든 Leaf 노드까지 가는 경로의 Black Node 갯수는 같다!
6. **새로 삽입되는 노드는 빨강이다.** 

<br>

보통 5번까지만 규칙으로 언급되고, 6번은 이해를 용이하기 위해 기재했다. <br> 
**결국 새로운 노드는 무조건 빨강색으로 삽입되기 때문에, 빨강이 연속되는 순간이 나오게 되는 것이고, 빨강 노드가 연속되는 경우에 균형을 맞추는 작업이 이루어진다.** <br>



### 5번 규칙 확인
간단하게 위 그림을 살펴보면 정말로 `5번 규칙 : Root 노드에서 모든 Leaf 노드까지 가는 경로의 Black Node 갯수는 같다`를 확인할 수 있다. <br>
 ![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/fa4e5451-dfda-48b4-b357-9d7b2fb186bb)

 왼쪽 끝 부터 살펴보자. K번 노드에 도착하기까지 Balck Node 갯수를 세어보자. 간단하게 노드가 가지고 있는 값으로 `K번 노드` 라고 칭하겠다.
 1. `1번 노드` : 13, 1 노드 -> 2개
 2. `6번 노드` : 13, 1 노드 -> 2개
 3. `11번 노드` : 13, 11 노드 -> 2개
 4. `15번 노드` : 13, 15 노드 -> 2개
 5. `22번 노드` : 13, 25 노드 -> 2개
 6. `27번 노드` : 13, 25 노드 -> 2개

<br>

이렇게 직접 세어보면 5번 규칙을 만족하는 것을 확인할 수 있다.

### 왜 새로운 Node는 빨강색인가?
검은 노드를 넣는 것보다 규칙을 맞추기가 더 쉽기 때문이다. <br>
예를 들어 검은 노드를 넣는다면, 5번 규칙을 어기기 쉬울 것이다. 이때, 5번 규칙을 지키기 위해서는 복잡한 재정렬이 필요한데, 이것 보다는 빨간 노드를 넣고, 빨간 노드가 연속했을 때 고치는 과정이 쉽다고 한다. (안 쉽던데..) <br>



## 3. Red-Black Tree의 균형을 맞추기 위한 연산
Red-Black Tree가 균형을 맞추는 방식은 2가지이다.
1. `Recoloring` : 주변 노드들의 색을 변경해 균형을 맞춘다.
2. `Rotation` : 노드들을 회전 시켜 균형을 맞춘다. AVL Tree처럼 회전시킨다. Restructring이라고 표현하는 한글 아티클도 많은데, 이는 Recolor를 포함하는 표현인듯 하다.

<br>

두 가지 방법을 좀 더 자세히 살펴보자. 그다음 삽입과 삭제시에 무슨 일이 일어나는지 두 가지 방법을 통해 설명하겠다. 그리고 Java 라이브러리의 구현을 살펴보자. 

<br>

### 설명하기 전에..
![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/fa4e5451-dfda-48b4-b357-9d7b2fb186bb)
1. NIL 노드 : **아무 데이터가 없는 Black 노드이다.** Red-Black Tree에서 규칙을 지키기 위해 데이터가 없는 검은 리프 노드를 NIL 노드로 사용한다.
2. NIL로 채워져 있는 Leaf : Red-Balck Tree의 Leaf Node들은 NIL로 채워져 있다 (위 그림 참고..)
3. Grand Parent 노드 : 부모의 부모 노드이다.
4. Parent Sibling 노드 : 말 그대로 부모 노드의 형제 노드이다. Grand Parent Node의 자식 노드 중 부모 노드가 아닌 노드를 이렇게 부르겠다.
5. 균형은 여러번 맞춰질 수 있다 : 균형을 맞추는 작업을 1회 실시하더라도, 빨간 노드가 연속하는 상황이 벌어질 수 있다. <br> 그런 경우 균형을 맞추는 작업은 여러번 반복된다.

<br>

### 3.1 Recoloring

Recoloring은 말 그대로 노드들의 색을 다시 칠하는 것이다. <br>

![image](https://github.com/binary-ho/Algorithm-and-Data-Structure/assets/71186266/1537a362-0080-4c63-8ad5-aee56ef98e14)

<br>

위 그림에서 파란색 동그라미로 표시한 것이 새 노드이다.
위 그림처럼 노드들의 색을 바꾸는 것인데, 삽입과 삭제시 색 변경이 다르게 진행될 수 있다.

<br>

### 삽입시 Recoloring
**Recoloring은 삽입시 부모와, 부모의 형제 노드가 둘 다 빨간색인 경우 발생한다.** <br>

1. 부모 노드와 Parent Sibling 노드를 검은 색으로 변경한다.
2. 이후 Grand Parent Node를 빨간 색으로 변경한다.
   - 만약 Grand Parent Node가 루트였다면 검은 색으로 변경한다.
   - 만약 Grand Parent Node가 빨간색이 되면서, "빨간색 노드는 연속으로 2개가 올 수 없다"규칙이 깨지는 경우, Recoloring 혹은 Rotation을 진행한다.


<br>


### 3.2 Rotation
노드들을 회전시킨다. <br>
AVL Tree의 Rotation을 안다면 그것과 동일하다. <br>
설명을 너무 복잡하게 하는 곳이 많은데, 그림과 코드를 먼저 보는게 훨씬 쉽다. 코드는 짧지만 상상하면 머리가 복잡해진다. 종이에 직접 그려보면 괜찮다. <br> 

마치 핸들을 돌리듯이 x와 y를 잡고 왼쪽, 오른쪽으로 돌리는 모습을 상상하면 된다!  <br>


### Left-Rotate
![image](https://github.com/binary-ho/Algorithm-and-Data-Structure/assets/71186266/5faec6e8-5640-4530-9ce5-43e77e583afa)

x, y, 감마를 잡고 왼쪽으로 회전한다고 생각해보면 된다. 위와 같은 상황에서 y에 자식이 있다면, 그 값은 x보다 크고, y보다 작은 것이므로, x의 오른쪽에 가게 된다. 간단한 c++ 코드로는 아래와 같이 구현할 수 있다.

```c++
x->rightChild = y->leftChild;
y->leftChild = x;
```

### Right-Rotate


![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/ee5b1670-c594-4430-925e-b44650032049)

Left Rotate와 반대이다.

코드로는 아래와 같이 구현할 수 있다 (c++)
```c++
y->leftChild = x->rightChild;
x->rightChild = y;
```


### LR, RL Rotate
AVL Tree처럼 LR, RL 회전도 있다. 


![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/cd13f4ef-d4a6-4169-aede-b6d1e2015ce3)

LR 회전은 위와 같이 수행되는데, 더 아래에 있는 xy먼저 잡고 Left Rotate를 한 다음, yz를 잡고 Right Rotate한다. 보통 새로 삽입된 노드가 부모의 오른쪽 자식이고, 부모는 Grand Parent Node의 왼쪽 자식일 대 발생한다. <br>
RL 회전은 반대 상황에서 발생한다.

![image](https://github.com/binary-ho/Algorithm-and-Data-Structure/assets/71186266/1ea8e769-d42d-459c-99e0-4fb76d0683f9)


<br>

이렇게 균형을 맞추기 위한 연산들을 알아봤다. 이제, 균형을 맞추는 두 연산 `Recolor`와 `Rotate`를 통해  Red-Black Tree의 삽입 연산과 삭제 연산을 알아보자. 그리고 코드를 살펴본 다음, Java 라이브러리에서 어떻게 사용하는지 살펴보자 (HashMap과 TreeSet, TreeMap에서 사용)



## 4. Red-Black의 삽입
이제 Red-Black Tree의 삽입과 삭제를 알아보자. <Br>
간단하게 동작을 그림과 함께 살펴본 다음, Java Code를 읽으며 이해해보자. <br>
나도 각종 블로그에서 설명만 보며 공부했을 때 보다 코드와 함께 공부했을 때 훨씬 이해가 잘 됐었다. <br>

### 4.1 검색 연산
삽입 삭제를 설명하기에 앞서 검색 연산을 먼저 설명하고 싶다. <Br>
왜냐하면 삽입과 삭제 과정에선 항상 검색 연산이 선행되기 때문이다. 이 노드가 들어갈만한 위치를 찾아야, 지우고 싶은 값이 트리상에서 어디에 있는지를 알아야 삽입하고 삭제할 수 있다. <br>

![RBTree22찾기1](https://github.com/10000-Bagger/free-topic-study/assets/71186266/1bb60276-b362-409e-8210-1c2526508962)


검색 연산은 간단하다. 레드 블랙트리는 정렬된 이진트리인 만큼, 루트에서 부터 시작해서 대소비교를 통해 현재 노드보다 넣어야 할 value가 작으면 왼쪽, 크면 오른쪽으로 이동하면 된다. (오름차순 정렬로 가정했을 때) <br>

정렬된 트리의 검색을 아는 사람이라면 지루하겠지만, 한번 살펴보자.. <br>
예를 들어 위 그림에서 파란색 동그라미로 표시된 22 노드를 찾는다고 생각해보자.
1. 탐색은 루트에서 시작한다
2. 22는 13보다 크므로, 오른쪽 자식으로 이동한다.
3. 22는 17보다 크므로, 오른쪽 자식으로 이동한다.
4. **22는 25보다 작으므로, 왼쪽 자식으로 이동한다.**
5. 완성! -> 아래 표시한 루트대로 이동할 것이다.

![22찾기2](https://github.com/10000-Bagger/free-topic-study/assets/71186266/8ccbebbf-4d18-44ec-8807-98f25f6602b7)

<br>

찾기 연산은 간단하고, 꼭 레드 블랙 트리만의 특징이 아니므로, 코드로 나타내지 않겠다. <br>


### 4.2 삽입
삽입은 앞서 언급한 Red-Black Tree의 규칙과 정렬 트리의 규칙대로 삽입된다.
1. 노드가 들어갈 위치를 찾는다.
2. **<U>빨간 노드를 넣는다.</U>**
3. **<U>만약 `빨간 노드는 연속해서 놓일 수 없다` 규칙을 어기는 경우, 규칙을 만족할 때까지 Recoloring이나 Rotation을 적용한다.</U>**

<br>

단순히 삽입하는 과정은 어렵지 않다. 복잡한 것은 균형을 맞추는 과정이다. 보통 insert이후 현재 노드와 부모 노드가 빨간색인 경우 빨간 노드 연속을 제거한다. 제거 과정에서 색도 바꾸고 돌리고 하다 보면 또 빨간 노드 연속이 발생할 수 있는데, 재귀적으로 처리한다. <br> 

### 4.3 삽입시 균형을 맞추는 과정

**아래 항목을 `"현재 노드"`와 그 `"부모 노드"`가 빨간 노드인 동안 반복한다.** <br>

1. 만약 `부모 노드`가 `조부모 노드`(부모의 부모)의 왼쪽 자식인 경우
   - `Case 1` : 만약 `부모의 형제 노드`가 **빨간색인** 경우 (부모 형제가 모두 빨간 색인 경우)
     1. `부모 노드`와 `부모의 형제` 노드를 **둘 다 검은색으로 칠한다.** 
     2. 그리고 `조부모 노드`를 **빨간색으로 칠한다.** **이들은 앞서 소개한 Recoloring 방식에 해당한다.**
     3. 이후 `현재 노드`를 `조부모 노드`로 설정한다. (재귀 호출을 위한 과정)
   - `Case 2` : `Case 1`이 아닌 경우 
     1. `부모 노드`를 검은 색으로 칠한다. 
     2. 그리고 조부모 노드를 빨간 색으로 칠한다.
     3. **Right Rotate를 수행한다.**
   - `Case 2 - 1` : `Case 2`를 적용하기 전의 전처리이다, **만약 `현재 노드`가 `부모 노드`의 오른쪽 자식인 경우**
     1. `현재 노드`를 `부모 노드`로 설정한다.
     2. **Left Rotate를 수행한다.** 
2. 만약 `부모 노드`가 `조부모 노드`의 오른쪽 자식인 경우 - 위 과정을 모두 반대로 수행하면 된다.

<br> <br>

머리가 너무 아프다. 특히 인터넷에 올라온 코드들이 죄다 복잡 복잡하다. -> [이런거](https://www.programiz.com/dsa/red-black-tree)

<br>

### 4.4 Java TreeMap 코드로 살펴보자.
가장 깔끔하고 읽기 좋은 코드는 java util에 있었다. <br> 
역시 형이야! 구하러 와줬구나? Red-Black Tree.. 그 유명한 Java HashMap 거기지? <br>
-> 절대 아니다 일단 변수명이 너무하다. 아래와 같다.
![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/64fad093-fe70-4722-b8e4-1ae32edc5b66)


<br>

의외로 잘 쓰이지 않는 TreeMap에도 Red-Black Tree가 있는데, (PS할떄 가끔 TreeSet을 쓴다) 이게 아주 읽기 좋게 만들어져 있다. 그래서 Java TreeMap을 기준으로 설명하겠다.

<br>

### TreeMap 보조 연산
들어가기 전에.. TreeMap의 아름다운 보조 연산을 살펴보자.

1. **색을 확인하는 `colorOf()`**
2. 부모를 확인하는 `parentOf()`
3. 색을 칠하는 `setColor()`
4. 자식을 확인하는 `leftOf()`

<br>

![image](https://github.com/depromeet/amazing3-be/assets/71186266/8e7b0557-f05d-48a6-ac37-ab0ae8046fa0)

**1번 `colorOf()`는 마음 속에 새겨야 한다. 그리고 NIL의 표현도 확인할 수 있다.** <br>

**p가 Null인지 확인하고, null이 아닌 경우 p의 color를, null인 경우 BLACK을 반환하는데, 이는 NIL의 표현이다. NIL은 무조건 검은 색이기 때문이다.** <Br>

나머지 연산들은 모두 null check이후 연산하는데, 평범한 null safe call을 위한 일종의 연산 Wrapping들이다. p가 null인 경우 변수를 그냥 꺼내면 예외가 발생할 수 밖에 없기 때문이다.


### 4.5 Put Method
put Method는 Map에 데이터를 삽입하는 메서드로, 우리가 찾는 insert 연산을 구현했다. <br> 

![put1](https://github.com/10000-Bagger/free-topic-study/assets/71186266/00493b5e-52d6-4cb3-a60d-c2b313eb2f25)

가장 윗 부분을 보자. 기본적으로, Tree가 비어있는 경우 addEntryToMap을 호출하는데, 그 메서드는 바로 위에 있다. 단순히 루트에 새 노드를 할당해주고, 사이즈와 연산 횟수를 센다. <br> 

put의 3번째 파라미터 `replaceOld`는 대체 여부를 따지는데, Map의 `put`과 `putIfAbsent`를 구분하는데에 쓰인다.

![put2](https://github.com/10000-Bagger/free-topic-study/assets/71186266/81cd3dd6-d5d3-476d-8003-0926fe779563)

<br>

나머지 부분은 역시 들어가게 될 위치를 찾는 과정이다. TreeMap은 생성자를 통해 `Comparator`를 넣어 생성할 수 있는데, 그런 `Comparator`가 있는 경우엔 그것을 사용하고, 없는 경우엔 key를 Comparable로 변환해 찾는다. <br> 

![put3](https://github.com/10000-Bagger/free-topic-study/assets/71186266/ac8ed927-bec5-4560-b534-67fcfa3fb532)


앞서 설명한 탐색과정 처럼 대소비교를 통해 왼쪽, 오른쪽으로 이동한다. 이후 최하단을 보면 `addEntry`를 호출하는데, 여기가 실제 삽입이 발생하는 곳이다. 마지막 파라미터를 통해 왼쪽과 오른쪽 중 어느 곳에 넣을지 또한 전달한다.

![addEntry](https://github.com/10000-Bagger/free-topic-study/assets/71186266/83617382-1c43-41bc-aaf5-f8322c1260f2)

꽤나 심플하게 삽입하는 모습이다. 사이즈를 체크하고, 연산 횟수를 센다. **중요한 것은 `fixAfterInsertion()` 인데 여기서 앞서 설명한 균형 맞추기가 이뤄진다.**

### 4.6 `fixAfterInsertion()`
이 `fixAfterInsertion`은 아주 잘 짜여져 있다.. 한번 java HashMap의 균형을 맞추는 부분인 `balanceInsertion()`를 보고 오면 이해할 것이다. 정말 어질어질 하다.. <br>

![insert1](https://github.com/10000-Bagger/free-topic-study/assets/71186266/52ec5d28-6a43-4eeb-94aa-b5b69e35b791)

앞서 설명한 삽입 이후 균형을 맞추는 과정이 while문 안에서 이루어지고 있다. (메서드의 역할은 이름 그대로 생각하면 된다.)  <br> <br>

이하 설명은 주석에 달아 두었다.

- 메서드 시작 ~ While문 조건
![fix1](https://github.com/depromeet/amazing3-be/assets/71186266/3b0bf49a-f358-404d-9794-bf28f3e5b943)


- while문 안의 분기 `Case A` : 부모가 조부모의 왼쪽 자식일 때 <br> + `Case A-1` : 부모와 형제 노드가 모두 빨간 색일 때.
![caseA1](https://github.com/depromeet/amazing3-be/assets/71186266/69463faf-dfa6-481d-9bd3-4e75e67a49c0)

- `Case A-2` : 부모가 빨간색이며, 부모의 형제 노드는 검은 색일 때
![caseA2](https://github.com/depromeet/amazing3-be/assets/71186266/9c4be355-f6bd-496b-98cd-edba550333c3)


- `Case B` : 부모가 조부모의 오른쪽 자식일 때이다. Case A와 대동소이하다. 부모 형제 노드를 찾는 부분과 회전 방향이 반대된다.
![caseB1](https://github.com/depromeet/amazing3-be/assets/71186266/f684e2b9-4ed0-411b-90e3-8289c64a33ab)
![caseB2](https://github.com/depromeet/amazing3-be/assets/71186266/1ef1a83e-b704-405e-b755-48832ea19978)

이렇게 코드로 살펴보니, 앞서 설명만 봤을 때보다 훨씬 이해하기 쉽지 않은가? 특히 TreeMap은 코드를 아주 읽기 좋게 구성해 놓았다. <br> 
현재 노드가 x, 부모의 형제가 y인 것만 빼면 나머지는 전부 이름을 통해 이해할 수 있다. 

<br>

![image](https://github.com/depromeet/amazing3-be/assets/71186266/070814fa-0272-4734-9560-96a54200e094)

마지막으로 루트를 검은 색으로 칠하는데, 재조정 과정에서 루트가 검은색이 되는 경우를 방지하기 위해서이다! <br>
이렇게 하면 삽입과 재조정 과정이 끝나게 된다. 이제 삭제와 재조정 과정을 알아보자.

## 5. 삭제와 재조정
삭제는 아주 간단하다. 노드를 삭제한 다음, 자식 노드 중 하나로 그 노드를 대체한다. 대신 여기서도 빨간 노드 2개가 연속할 수 있고, 재조정 과정이 필요하다.


![image](https://github.com/depromeet/amazing3-be/assets/71186266/1e5defa0-7c4c-4c72-9b65-2b94ffdfdf1e)

위와 같이 getEntry라는 메서드를 통해 지울 노드를 특정하고 deleteEntry를 호출한다. 

<br>


![image](https://github.com/binary-ho/imhere-server/assets/71186266/2d667899-66bf-482e-b6d9-cc1e0b0694f8)

DeleteEntry의 가장 윗 부분이다.
연산 횟수를 세고, 사이즈를 줄인 다음 **왼쪽 오른쪽 자식이 있는 경우 현재 노드 `p`를 Successor를 호출해 설정한다.** 

<br>

`Successor`는 지워질 노드를 차지할 새로운 노드를 찾는다! 발견된 값은 **`지워질 노드를 루트로 하는 서브 트리 안에서 현재 노드보다 크면서 가장 작은 값`** 이다. 

![image](https://github.com/depromeet/amazing3-fe/assets/71186266/872ef0c8-a4ce-4d3f-9292-c957d6780b24)

위의 빨간 표시를 한 부분을 보자. 어차피 successor는 left와 right가 null이 아닐 때만 호출되므로, 무조건 빨간색으로 표시한 부분이 호출된다. <br>

그리고 그림과 함께 코드를 이해해보자.

![17delete](https://github.com/binary-ho/imhere-server/assets/71186266/84af2944-c38d-4a16-b3e6-2be905e45b84))

예를 들어 17번 노드를 지운다고 생각해보자. (값 17을 가지고 있는 노드) 이 노드는 **오른쪽 자식, 왼쪽 자식 모두 가지고 있다** 따라서 succssosr가 호출된다. 다음으로 넘어가기 전에, 어떤 값이 17번 노드를 대체하면 좋을지 생각해보자. <br>

1. 13의 오른쪽이니 13보다 커야 하고
2. 15를 왼쪽 자식으로 가졌으니, 15보다 커야 한다
3. 그리고 25를 오른쪽 자식으로 가졌으니, 25 보다 작아야 한다.

<br>

왼쪽에서 노드를 끌어올 것이 아니라면, `22번 노드`를 17번 노드가 지워진 자리에 두면 딱 좋을 것이다! `22`는 13보다 크고 && 15보다 크며 && 25보다 작기 때문이다.

![17del2](https://github.com/binary-ho/imhere-server/assets/71186266/70c3cb37-da5a-4c3f-b795-286b88f8f353)

<br>

그래서 코드가 아래와 같은 것이다. **오른쪽 자식을 현재 노드로 둔 다음, 왼쪽 자식을 계속 타고 이동한다. 그러면 지울 노드가 루트인 하위 트리에서 지울 노드보다는 숫자가 크면서 가장 숫자가 작은 "22"를 발견할 수 있다.** <br>

8을 지우는 경우에도 똑같이 11을 발견한다.
![image](https://github.com/binary-ho/imhere-server/assets/71186266/dc989931-38f2-49d4-9f97-12b87105ca93)

루트를 지운다면? 15를 발견할 것이다. <br> <br>


호출한 이후엔 어떻게 될까?

![image](https://github.com/binary-ho/imhere-server/assets/71186266/2d667899-66bf-482e-b6d9-cc1e0b0694f8)

p에 key와 value를 대체한다 위에서 예시로 든 17을 지우는 경우 아래와 같이 22라고 "표시"하는 것이다. 그리고 현재 노드는 아래에 있는 22 노드가 된다.

![image](https://github.com/depromeet/amazing3-fe/assets/71186266/9fa405b4-b2e0-4e8b-9a87-01681ea72451)

<br>

**이제 문제는 아래의 22번 노드를 지우는 문제로 바뀌게 된 것이다!**


### 5.1 fixAfterDelete

대체 노드를 찾은 이후엔 코드가 위와 같이 진행된다. 이 코드를 설명하기 전에, 중간 중간에 있는 현재 노드가 Black인 경우 균형을 맞추는 `fixAfterDelete`를 먼저 설명하겠다. <Br> 

일단, 왜 검은색에서 균형을 잡아야 할까? <Br>
Red-Black Tree는 빨간색이 두번 연속 올 때 균형을 맞춰야 한다고 했다. 만약 지워지는 노드가 빨간색이었다면, 균형이 깨질 일이 있을까? 없다. <Br>
균형이 깨지는 순간은 오직 빨간 노드가 검은 노드를 대체할 때 뿐이다. 따라서, 균형을 잡는다면 무조건 검은 노드가 지워질 때이다.


![image](https://github.com/depromeet/amazing3-fe/assets/71186266/7e45815c-70b4-4261-97dd-9a68f88932a7)

![setlastblack](https://github.com/depromeet/amazing3-be/assets/71186266/a9d389e8-9a99-4454-bde5-676d5ac4cece)

따라서, 현재 노드 `x`가 검은색이며, 루트가 아닌 동안 while문이 반복된다. 앞서, fixAfterInsertion에서 그랬던 것처럼 if문을 통해 x가 부모의 왼쪽 자식인지 오른쪽 자식인지를 통해 가장 큰 분기를 나눈다음, `sib`이라는 노드에 현재 노드의 형제 노드를 담는다. <br>

**while문을 빠져나간 다음에는 노드를 검은색으로 칠한다.**

1. `현재 노드`가 `부모`의 왼쪽 자식인 경우 - `sib`은 부모의 오른쪽 자식
   - `Case 1` : 형제의 두 자식이 모두 검은색인 경우 Or 형제가 Leaf Node여서 두 자식이 NIL인 경우
     1. 형제를 빨간 색으로 색칠한다.
     2. 현재 노드를 부모 노드로 변경.
    ![beforedelete2](https://github.com/depromeet/amazing3-be/assets/71186266/1de99cdf-d45f-4687-8a3b-087d6ec91424)
    
    예를 들어 위와 같은 상태를 생각해보자. 여기서 1이나 11을 지우면, Case 1에 해당한다.
    
    ![afterdelete2](https://github.com/depromeet/amazing3-be/assets/71186266/801edecb-bf91-41ac-ba30-46390ad1b8f6)
    
    형제인 11을 빨간 색으로 칠한 다음, x를 부모 노드 8로 변경한다. <br> 8은 빨간색이므로 while문을 빠져나가고, 메서드 가장 아래에 닿아 노드는 검은색으로 칠해진다. <br> 보다싶이 모든 규칙을 만족하는 트리가 됐다. <br> <br>

   - `Case 2` : 형제의 두 자식 중 하나라도 빨간 색이 있는 경우
     1. 형제 노드를 부모 노드와 같은 색으로 색칠한다.
     2. 이후 부모를 검은 색으로 칠한다.
     3. 형제의 오른쪽 자식을 검은 색으로 칠한다.
     4. "Left Rotate"를 실시한다.
     5. 현재 노드를 루트로 둔다. (break에 해당)

    ![afterdelete2](https://github.com/depromeet/amazing3-be/assets/71186266/801edecb-bf91-41ac-ba30-46390ad1b8f6)

    위 그림에서 15를 지우면 `Case 2`에 해당한다. 부모의 왼쪽 자식이고, 형제의 두 자식이 빨간 노드이기 때문이다. <br> **형제 노드 25는 부모와 같은 색인 빨간색이 되고, 부모인 17과 오른쪽 자식인 27은 검은색이 된다.** <br> 이후 "Left Rotate" -> 25가 루트가 되고, 17이 왼쪽 자식 27이 오른쪽 자식이 될 것이다. 결과는 아래와 같이 될 것이다.

    ![afterdelete3](https://github.com/depromeet/amazing3-be/assets/71186266/a566c920-5f5d-4df0-beab-93bad8970795)

    모든 규칙을 만족하는 트리가 됐다. <br> <br>

     - `Case 2의 공통 연산` : 만약 오른쪽 자식이 검은 색이고, 왼쪽 자식이 빨간 색이라면
       1. 빨간색인 왼쪽 자식을 검은 색으로 바꾼다. 
       2. 형제를 빨간 색으로 바꾼다.
       3. 형제에 "Right Rotate"를 수행한다. (그러면 형제 노드가 자식 노드가 될 것이고, 오른쪽 자식이 위로 올라오게 될 것이다.)
       4. 이후, 형제 노드를 갱신한다.
   - `전체 공통 연산` : `형제`가 **빨간색인** 경우 (나는 검정, 형제는 빨강)
     1. 형제를 검은 색으로 칠한다.
     2. 부모를 빨간 색으로 칠한다.
     3. 부모에 "Right Rotate"를 수행한다. <br> -> 그러면 검은색인 현재 노드가 부모의 자리에 가고, 부모 노드는 오른쪽 자식이 된다.
     4. 새로운 sib을 갱신한다. -> 기존 부모였던 빨간 노드가 형제 노드가 된다.  
2. 만약 `현재 노드`가 `부모`의 오른쪽 자식인 경우 - `sib`은 부모의 왼쪽 자식이며, 위 과정을 모두 반대로 수행하면 된다.


### 5.2 대체 노드를 찾은 이후

![image](https://github.com/depromeet/amazing3-fe/assets/71186266/fad37635-c96b-4a07-9c42-ea9c6acf3be6)

(if, else if, else를 각각 A, B, C번 분기라고 부르겠다.) <br>

이제부터 위의 대체 노드를 찾은 이후 연산을 살펴보자. 여기서도 케이스는 3가지 케이스가 있을 수 있다.

- `Case A` : 왼쪽 자식, 오른쪽 자식이 모두 존재하여, succssor를 호출한 경우
- `Case B` : 왼쪽 자식이 비어 있던 경우
- `Case C` : 오른쪽 자식이 비어 있던 경우

### C번 분기
C번 분기 부터 살펴보자. C번 분기는 replace가 null이며, parent는 null이 아닌 경우이다. <br> <br>

이는 리프 노드일 때 도착할 수 있는데, 아래와 같은 경우에 리프 노드가 현재 노드이다
1. 그냥 리프 노드를 삭제하는 경우 
2. **왼쪽 자식, 오른쪽 자식이 모두 존재해서 succssor를 호출한 경우** -> succssor는 리프 노드이기 때문에 replace가 null이다.

<br>

C번 분기의 경우 만약 현재 노드가 검은색이라면, fixAfterDeletion을 호출한다. <br>

균형을 맞춘이후 부모가 null이 아니라면 노드를 참조하는 래퍼런스를 모두 떼어낸다.
1. 부모에서 자식 참조 제거
2. 현재 노드에서 부모 참조 제거...

### A번 분기
지울 노드에 자식 노드가 하나라도 있으면 도착하는 곳이다. <br>

평범하게 지우는데, 대체할 노드의 부모를 지울 노드의 부모로 삼는다. <Br> 만약 지울 노드가 루트 노드라서, 부모가 없다면, 대체할 노드를 새로운 root로 삼는다. <br>

있는 경우 지울 노드의 부모가 대체할 노드를 새로운 자식으로 삼게 한다. <br> 지울 노드가 왼쪽 자식인 경우 `p.parent.left  = replacement;` 오른쪽 자식인 경우 `p.parent.right = replacement;`로 대체한다. <br>


이렇게 지울 노드가 갈 곳이 없게되면, 모든 레퍼런스를 지워낸다. `p.left = p.right = p.parent = null;` 이후 지워진 노드가 검은색이였던 경우 fix한다. `fixAfterDeletion(replacement);`


### B번 분기

B번 분기는 간단하다. 지울 노드의 parent가 null인 경우 지울 노드가 root 노드라는 의미기 때문에, 단순히 트리 자체를 null로 만들어 버리면 된다. `root = null;`


## 6. 자바에서의 Red-Black Tree
자바에서는 앞서 살펴본 것과 같이 자료구조 TreeMap이 내부적으로 Red-Black Tree를 쓰고 있다. <br>
더 유명한 곳은 HashMap이다. Java 8에서 HashMap에 Treeify 연산이 추가되었는데, "트리화"연산이다. <br> <br>

원래 HashMap은 내부적으로 HashTable을 사용하고 있다. 잘 알려진 평범한 HashTable처럼 여러 버킷을 가지고 있고, 해쉬코드로 버킷을 식별한 다음, 버킷마다 LinkedList 형태로 주렁 주렁 노드들을 달아 노드 안에 값을 저장해두었다. <br>
버킷 식별엔 `hashCode()` 메서드가, 노드끼리의 동등성 비교엔 `equals()`가 쓰인다. <Br>
이런 링크드 리스트가 충분히 길어지는 경우 탐색 시간은 길어질 수 밖에 없다. 링크드리스트는 탐색 시간이 O(N)이기 때문이다. <br>

이런 상황에서 도입된 것이 `treeify`인데, 아래와 같이 기준 Threshold값을 가지고 있다.

![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/29625db6-1e41-4652-be3a-9339e4343423)


노드 갯수가 5개가 넘어가면, 트리화 시키고, 더 적으면 다시 링크드 리스트로 만든다. <br>

**이 트리가 바로 레드 블랙 트리이다!**

<br>

이 treeify에 대해 좀 더 자세히 적고 싶지만, 글이 너무 길어졌고 주제는 레드 블랙 트리이기 때문에 이만 줄여보려 한다.
