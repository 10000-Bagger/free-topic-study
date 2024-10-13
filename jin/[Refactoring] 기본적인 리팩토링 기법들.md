
# 6. 기본적인 리팩토링 기법

"코드에서 나는 냄새" 문서와 상당 부분 겹칠 것으로 예상된다. <br>
이번 단원에서 주로 하고 싶은 이야기는 "책임을 확실히 하자" 인것 같다.


1. **함수 추출하기**
2. `<->` 함수 인라인하기
3. **변수 추출하기**
4. `<->` 변수 인라인하기
5. 함수 선언 바꾸기
6. 변수 캡슐화하기
7. 변수 이름 바꾸기
8. 매개변수 객체 만들기
9. 여러 함수를 클래스로 묶기
10. 여러 함수를 변환 함수로 묶기
11. 단계 쪼개기


결국 객체이향이다 "함수 추출하기"와 "변수 추출하기"는 "함수 선언 바꾸기", "단계 쪼게기"와 함께  책임을 분리하는 행위이다. <br>
"함수와 변수 인라인 하기"는 이들과 반대의 일을 한다.

캡슐화와 관련이 큰 기법도 많다. <br>
"변수 이름 바꾸기", "변수 캡슐화" <br>
그리고 관련있는 매개변수들을 합치는 "매개변수 객체 만들기", <Br>
여러 함수를 묶는 "여러 함수를 클래스로 묶기", "여러 함수를 변환 함수로 묶기" 모두 캡슐화와 관련이 있다. <br> <Br>

<!-- 책에서는 위 11가지 방법을 쭉 나열하지만, 나는 크게 "쪼게기"와 "합치기"로 나누어 보고 싶다. 왜냐하면 내가 이해하기도 편하고, 나중에 "코드에서 나는 악취" 문서와 겹치는 부분을 합칠 때도 유용할 것으로 예상되기 때문이다. -->

## 6.1 함수 추출하기
함수는 언제 추출해야 하는가? <br>
수많은 기준들이 있다.
1. **책임을 나누기 위해**
3. 함수가 너무 길 떄
4. 재사용성이 높은 부분을 발견했을 때. (중복되는 구현)

<Br>

사실 가장 함수 추출의 가장 강력한 힘은 책임을 분리하는데에 있다. <br>
함수가 너무 길던, 어떻던 어떤 함수의 목적을 쉽게 파악할 수 없다면, 함수의 부분을 추출해 함수로 만들면서 "이름을 지어줄 수 있다." 함수 하나가 가지고 있는 책임을 여러 함수로 나눔으로써 읽는 사람은 힘들게 코드가 무슨 동작을 하는지 생각하는 일을 줄이고, 함수 이름에게 우선적으로 힌트를 얻을 수 있다. <br> <Br>

레거시 코드를 읽다 보면 함수를 최대한 길게 짜려 노력한게 아닐까 싶은 코드가 매우 많다. 옛날에는 함수를 짧게 만드는 경우 간혹 성능 문제가 있었다고 한다. 추측건데 메모리 공간이 매우 작고, 언어건 하드웨어건 성능이 떨어지던 시절이여서, 함수 수행을 위한 세팅들이나 콜 스택을 쌓는 일 자체가 성능에 나쁜 영향을 주지 않았을까 싶다. <br>

하지만, 현대엔 다르다. 함수가 짧으면 오히려 캐싱하기 쉽고, 컴파일러가 최적화 하기 더 유리할 때가 많다고 한다. (잘 생각이 안나서 찾아봐야겠지만, JVM Method 캐싱 관련 이야기인듯??)

<br> 

우리는 그냥, 코드 덩어리를 보며 분리할 수 있는 부분을 찾는다.
함수에 여러 책임이 있는 것으로 생각되면, 나누는 것이다.


1. 함수를 새로 만들고, 목적을 잘 드러내는 이름을 붙인다.
    **"어떻게"가 아니라, "무엇을"에 집중한다.**
2. 추출할 코드를 원본 함수에서 복사해 새로운 함수를 만든다.
3. 테스트 한다.


<br>

예를 들어 아래와 같이 너무 많은 일을 해내는 메서드가 있을 때, 위 순서를 따르며 분리해볼 수 있을 것이다.

```java

@Transactional
public void approveStudents(Long lectureId, Long studentId) {
    // lecture id와 studentId로 enrollmentInfo를 조회한 다음 검증한다.
    EnrollmentInfo enrollmentInfo = getEnrollmentInfo(lectureId, studentId);
    Long enrollmentInfoLectureId = enrollmentInfo.getLecture().getMember().getId();
    authenticationHelper.verifyRequestMemberLogInMember(enrollmentInfoLectureId);

    // enrollmentInfo의 상태를 바꾼다.
    enrollmentInfo.approveEnrollment();

    // OpenLecture를 캐싱한다.
    Optional<OpenLecture> openLectureOptional = openLectureService.find(lectureId);
    openLectureOptional.ifPresent(openLecture -> {
        Long studentId = enrollmentInfo.getMember().getId();
        eventPublisher.publishEvent(new AttendeeCacheEvent(lectureId, new StudentIds(studentId)));
    });

    Lecture lecture = enrollmentInfo.getLecture();
    Member student = enrollmentInfo.getMember();
    // 수강 신청 승인 결과를 로깅한다.
    log.info("[수강신청 승인] 강의 : {} ({}) 학생 : {} ({})", lecture::getLectureName, lecture::getLecturerName, student::getUnivId, student::getName);
}
```


<br>

위 메서드를 여러 메서드로 분리한다.
메서드 이름만으로 어떤 일들이 일어나고 있는지 더 빠르게 파악할 수 있다.

```java
@Transactional
public void approveEnrollment(Long lectureId, Long studentId) {
    EnrollmentInfo enrollmentInfo = getEnrollmentInfo(lectureId, studentId);
    validateLecturerOwnLecture(enrollmentInfo.getLecture());

    enrollmentInfo.approveEnrollment();

    cacheStudentIfLectureIsOpen(lectureId, enrollmentInfo);

    logApproveEnrollment(enrollmentInfo);
}

private void cacheStudentIfLectureIsOpen(Long lectureId, EnrollmentInfo enrollmentInfo) {
    Optional<OpenLecture> openLectureOptional = openLectureService.find(lectureId);

    openLectureOptional.ifPresent(openLecture -> {
        Long studentId = enrollmentInfo.getMember().getId();
        eventPublisher.publishEvent(new AttendeeCacheEvent(lectureId, new StudentIds(studentId)));
    });
}

private void validateLecturerOwnLecture(Lecture lecture) {
    Long lectureId = lecture.getMember().getId();
    authenticationHelper.verifyRequestMemberLogInMember(lectureId);
}

private void logApproveEnrollment(EnrollmentInfo enrollmentInfo) {
    Lecture lecture = enrollmentInfo.getLecture();
    Member student = enrollmentInfo.getMember();
    
    log.info("[수강신청 승인] 강의 : {} ({}) 학생 : {} ({})", 
        lecture::getLectureName, lecture::getLecturerName, 
        student::getUnivId, student::getName
    );
}
```


## 6.2 함수 인라인하기
함수 인라인하기는 반대로, 함수 본문이 이름만큼 명확한 경우 다시 인라인으로 만드는 것이다. <br>
이 리팩터링은 보통 잘못 추출된 함수들이나 불필요한 추출 함수를 되돌리는 일을 한다.

```java
@Transactional
public void approveEnrollment(Long lectureId, Long studentId) {
    EnrollmentInfo enrollmentInfo = getEnrollmentInfo(lectureId, studentId);
    validateLecturerOwnLecture(enrollmentInfo.getLecture());

    enrollmentInfo.setEnrollmentState(EnrollmentState.APPROVAL);

    cacheStudentIfLectureIsOpen(lectureId, enrollmentInfo);

    logApproveEnrollment(enrollmentInfo);
}
```


예를 들어 위 메서드에서 `enrollmentInfo.setEnrollmentState(EnrollmentState.APPROVAL);`를 분리했다고 해보자.

```java
@Transactional
public void approveEnrollment(Long lectureId, Long studentId) {
    EnrollmentInfo enrollmentInfo = getEnrollmentInfo(lectureId, studentId);
    validateLecturerOwnLecture(enrollmentInfo.getLecture());

    setEnrollmentApproval();

    cacheStudentIfLectureIsOpen(lectureId, enrollmentInfo);

    logApproveEnrollment(enrollmentInfo);
}

private void setEnrollmentApproval() {
    enrollmentInfo.setEnrollmentState(EnrollmentState.APPROVAL);
}
```

<br>

분명 의미는 더 확실해졌지만, 사실 그럴 필요 없이 enrollmentInfo의 상태를 APPROVAL로 바꾼다는 것을 알 수 있다. <br>
따라서 너무 간단해서 따로 설명할 필요가 없는 경우, 다시 인라인 시킨다.


## 6.3 변수 추출하기, 인라인하기
이번엔 표현식이 너무 복잡한 경우, 변수로 끊어 표현하는 방식이다.
예를 들어 아래와 같이 복잡한 표현식을 변수를 선언하며 끊어 내는 것이다.

```java
    return order.quantity * order.itemPrice 
        - Math.max(0, order.quantity - 600) * order.itemPrice * 0.05
        + Math.min(order.quantity * order.itemPrice * 0.1, 100);
```

<br>

위 식의 중간 중간 이름을 지어주자

```java
    const basePrice = order.quantity * order.itemPrice;
    const quantityDiscount = Math.max(0, order.quantity - 600) * order.itemPrice * 0.05;
    const shipping = Math.min(order.quantity * order.itemPrice * 0.1, 100);
    return basePrice - quantityDiscount + shipping;
```

<br>

인라인 하기는 그 반대로, 이번에도 불필요하게 너무 분리해 놓았다면 다시 되돌리는 것이다. <br>
사실 현실에서 마주하는 케이스들은 너무 분리를 안 해서 문제지 분리한게 문제가 되지는 않아서 쓸 일이 있나 싶다.

## 6.4 함수 선언 바꾸기, 변수 이름 바꾸기
간단하다. 함수나 변수의 이름이 그 책임을 충분히 설명해주지 않는다면 더 구체적인 이름으로 바꿔 주자는 이야기이다. <br>

당연한 소리를 왜 또 하는가 싶겠지만, 이 단원에서는 이름을 "잘" 짓는 것의 중요성을 강조한다. 지금 우리에게는 흔한 조언이지만, 이 책이 옛날 책이라는 점을 감안하면 한 단원을 할애할만 하다.  <br>
나는 10년도 더 된 코드를 거의 매일 같이 보는 생활을 하고 있는데, 모두가 이 단원을 읽어볼 수 있다면 얼마나 좋을까 싶다. <Br>  <br>

얘기가 나와서 내가 생각하는 올바른 상수 이름에 대해 얘기해보겠다. <br>
나는 금융권 개발자로서 매우 복잡한 코드 값들을 변수로 사용하는 경우를 많이 본다. 아무 예나 들어보겠다. 

```java
"RF-EQDSF-1203" // 튼튼보험
"RF-EQDSF-1204" // 감자보험
"RF-EQDSF-1205" // 치킨보험
"RF-EQDSF-1206" // 피자보험
```

정말 생각나는데로 아무렇게나 휘갈긴 예시이다.
예를 들어 저런 4가지 보험을 의미하는 코드값들이 있다고 생각해보자. 
우리 프로젝트에선 저렇게 Raw String으로 그대로 사용하는 사람이 많다.
끝 숫자의 오타 한번에 아예 다른 보험으로 바뀔 수도 있고, String 내용이 바뀌게 된다면 변경하기가 너무 어렵다.
예를 들어 오늘 부터 피자 보험의 코드를 "RF-EQDSF-1206"이 아닌 ""RF-EQDSF-1277"로 바꾼다고 생각해보자.

상수나 Enum과 같이 관리하고 있지 않다면, 우리는 이 값들을 사용하는 곳을 모두 찾아 바꿔 주어야만 하는 대참사가 벌어진다.

이를 막기 위해서 상수를 쓰는데, 문제는 아래와 같이 쓰는 코드가 꽤 많았다.

```java
private static final String RF_EQDSF_1203 = "RF-EQDSF-1203" // 튼튼보험
private static final String RF_EQDSF_1204 = "RF-EQDSF-1204" // 감자보험
private static final String RF_EQDSF_1205 = "RF-EQDSF-1205" // 치킨보험
private static final String RF_EQDSF_1206 = "RF-EQDSF-1206" // 피자보험
```

<br>

이것은 상수로 쓰는 이점이 거의 없다.
생각해보자면 누군가 상수로 관리하라고 조언 했을 것인데, "왜" 상수로 관리해야 하는지는 안 알려준 것 같다........................ ㅠㅠ
위와 같이 사용하면 상수로 관리하는 것의 장점을 누리지 못한다.

1. 오타를 방지할 수 없다. 맨 끝 숫자를 3으로 쓸 것을 4로 쓸 수도 있는데, 이런 실수를 막을 수 있는건가? -> 아님
2. 코드의 의미를 알 수 없다. 코드를 짜다가 저 상수를 쓰는 곳을 발견했을때, 어떤 보험의 코드인지 전혀 파악할 수 없다. 예를 들어 아래와 같은 상황이다. 
```java
if (보험코드.RF_EQDSF_1204.equals(code)) {
    // 무언가 호출한다.
}
```


<br> <br>

나는 저런 방식을 무의미한 상수화라고 부르고 싶다.
아래와 같이 쓰는게 베스트일 것이다.

```java
public class 보험코드 {
    private static final String 튼튼보험 = "RF-EQDSF-1203";
    private static final String 감자보험 = "RF-EQDSF-1204";
    private static final String 치킨보험 = "RF-EQDSF-1205";
    private static final String 피자보험 = "RF-EQDSF-1206";
}

```

1. 복잡한 코드를 직접 사용하지 않기 때문에, 오타로 인한 대참사를 방지할 수 있다.
2. 코드의 의미를 바로 알 수 있다. 아래 코드를 보면 `튼튼 보험인 경우 무언가를 호출하는 거구나~` 하고 바로 알 수 있다.
    ```java
    if (보험코드.튼튼보험.equals(code)) {
        // 무언가 호출한다.
    }
    ```
3. 변경하기가 쉽다. 튼튼보험의 코드가 바뀌는 경우 아주 쉽게 상수의 value만 바꿔주면 된다.


## 6.5 변수 캡슐화하기
getter, setter를 활용해 변수를 캡슐화 하자는 이야기이다.
우리에겐 평범한 조언이다. 이번 기회에 내가 생각하는 캡슐화의 장점을 다시 한번 적어본다.

1. 불변으로 제공하기 좋다.
    그냥 public이어도 final로 선언하면 불변이지 않나?
    라고 할 수 있지만, Reference Type의 경우 내부 값을 변경할 수도 있다.
    특히 단순한 컬렉션을 public final로 둔다고 생각해보자. 컬렉션의 내용물 값을 바꾸거나 추가하고 삭제하는 것을 막을 수 있는가?
    이때, 캡슐화와 함께, getter에서 방어적 복사를 하고 제공해주면 안전하게 원본을 지킬 수 있을 것이다. 
2. 변경 추적이 쉽다.
    setter를 사용하는 부분만 추적하면 된다. 만약 캡슐화가 없다면 `변수 = 새로운_값`과 같이 사용하는 부분을 전부 힘들게 찾아내야 한다.
    캡슐화를 했다면 setter의 사용만 IDE의 기능을 활용해 추적할 수 있다.


## 6.6 매개변수 객체 만들기
매개변수가 너무나도 많거나, 연관성이 큰 경우 객체로 만들 수 있다.
그러면 매개변수의 갯수가 줄어들어 코드가 간결해진다. 
그 외에도 단 하나의 매개변수더라도 객체로 만들어 의미를 만들어주면, 관리하기도 쉽고 실수도 줄어든다. 예를 들어 아무 예시나 들어보겠다.

```java
void doSomething(String 금액, String 단위);
```

위와 같은 메서드는 잘못 사용하면 순서를 뒤바꿔 넣을 수도 있다. <br>
이러한 실수는 의외로 잦은데, 며칠 전에도 프로젝트의 어떤 개발자 분께서 인수 순서를 착각하셨고 정말 많은 시간을 들여서 원인을 파악 하셨었다. <br>
하지만, 각각 클래스로 만들어준다면 실수할 일이 확 줄어든다

```java
void doSomething(금액 금액, 화폐_단위 단위);
```

어떤가 실수를 할래도 하기가 어렵다. IDE상에서, 컴파일시 오류를 뱉어버린다.
그리고 아래와 같이 합칠 수도 있다.

```java
class 돈 {
    private final 금액 금액;
    private final 단위 단위;
}
```

매개변수를 객체로 만드는데엔 이러한 장점들이 잇다.

## 6.7 여러 함수를 클래스로 묶기
마치 여러 코드 라인을 함수로 만들었던 것처럼, **관련있는 행위들과 상태를 발견한다면 하나의 클래스로 묶을 수 있다.**

한 클래스가 너무 여러 책임 (여러 종류의 역할을 하는 함수들)을 갖거나, 같은 역할을 하는 함수가 이 클래스 저 클래스 산개해 있는 경우, 하나의 클래스로 묶을 수 있을 것이다.



## 6.8 단계 쪼개기

단계 쪼게기는 너무 함축적인 코드들을 쪼게어 보여주는 방식이다.
나에게는 추출 관련 기술들의 종합으로 느껴진다

```js
const orderData = orderString.split(/\s+/);
const productPrice = priceList[orderData[0].split("-")[1]];
const orderPrice = parseInt(orderData[1]) * productPrice;
```

예를 들어 위와같은 코드가 있다.
코드는 복잡하고, 정말 여러 연산들이 참여한다.
이 코드들에서 정확히 어떤 일이 일어나는지 추측하기란 쉽지 않다.


<br>

특히 orderData의 0번째와 1번째가 무엇을 의미하는지 파악하려면 조금 생각해야만 한다. 아래와 같이 분리해볼 수 있다.

```js
const orderInfo = parseOrder(orderString);
const orderPrice = calculateOrderPrice(orderInfo, priceList);

function parseOrder(orderString) {
    const orderIdAndQuantity = orderString.split(/\s+/);
    const orderId = orderIdAndQuantity[0];
    const ids = parseIds(orderId);

    return ({
        productId: ids.productId,
        quantity: parseInt(productIdAndQuantity[1]),
    });
}

function parseIds(orderId) {
    const ids = orderId.split("-");
    return ({
        orderId: ids[0], 
        productId: ids[1],
    })
}

function calculateOrderPrice(orderInfo, priceList) {
    const productPrice = priceList[orderInfo.produceId];
    return productPrice * orderInfo.quantity;
}
```

위와 같이 각 단계들을 쪼게고, 이름을 붙임으로써
의미를 부여해줄 수 있다.
특히 각종 ID를 채번할 때, 다양한 정보들을 구분자와 함께 합치게 되는데, 이러한 ID들에서 정보를 파싱할 때 사용해볼 수 있을 것 같다.

