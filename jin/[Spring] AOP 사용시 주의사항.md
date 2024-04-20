# 스프링 AOP 주의사항

# 1. 내부 호출 문제

스프링 AOP는 프록시를 기반으로 동작한다. <br>
스프링은 내가 적용하고 싶은 횡단 관심사를 구현한 프록시 객체를 빈으로 대신 등록해서, 
빈 메서드를 호출하면 프록시 객체의 메서드를 호출하게 도와준다. <br> 
**문제는 한 클래스의 메서드에서 같은 클래스 안의 다른 메서드를 호출 했을 때 발생한다.** <br> <br>

예를 들어 아래 코드에서 exteranl 메서드는 내부적으로 internal 메서드를 호출한다. <br>

```java
@Slf4j
@Component
public class CallServiceV0 {

    @Transactional
    public void external() {
        log.info("call external");
        // 내부 메서드호출
        this.internal();
    }

    @Transactional
    public void internal() {
        log.info("call internal");
    }
}
```

이때 외부에서 `exteranl()`를 호출한다면, 프록시가 적용되어 횡단 관심사 코드가 추가된 버전의 external이 호출되겠지만, <br>
**그 메서드에서 호출한 `this.internal()`는 실제 객체의 메서드로 프록시의 것이 아니다.** <br>
**따라서, 횡단 관심사가 적용되지 않았다!**

<br>

아래와 같은 상황인 것이다. exteranl만 프록시 객체의 것이 호출되었다.

![image](https://github.com/binary-ho/TIL-public/assets/71186266/09fead5e-58c9-4a9f-9ccf-d4f230e921ea)


<br>

이러한 문제가 발생할 수 있다는 것을 인지하고, 내부 호출 문제를 만들지 않도록 주의해야 한다.


## 1.1 내부 호출 대안 
1. 자기 자신을 주입해 호출한다. : 자기 자신을 주입 받아 가지고 있게 한다. 그 다음 주입 받은 객체를 호출하면 된다. <br> 이때 순환 참조가 발생할 수 있으므로 `Setter`를 통해 주입 받아야 한다. <br> 예를 들어 위 예시의 경우엔 `internal()`메서드를 주입 받은 자기 자신 객체의 `internal()`을 호출하는 것
2. 지연 조회 : ObjectProvider<>나 아예 ApplicationContext에서 빈을 뽑아 사용한다. <br> ObjectProvider는 객체를 스프링 컨테이너에서 조회하는 시점을 빈 생성 시점이 아니라, 실제 객체를 사용하는 시점으로 지연할 수 있다. 호출할 때가 되서야 컨테이너에서 빈을 조회한다.
3. **구조를 변경한다.** : 그냥 내부 호출의 대상 메서드인 `internal()`과 같은 메서드를 다른 객체로 분리해서 사용한다. (제일 괜찮은 방법이고 권해진다.) <Br> 다만 구조가 이미 합리적인데도, 이러한 목적으로 객체를 분리해야 한다는 점이 껄끄럽다. 스프링 프록시 방식 AOP의 한계점이다.


# 2. 프록시 기술과 한계점

결국 앞서 말한 것처럼 프록시 기술을 사용하면서 한계점이 있을 수 밖에 없다. 내부 호출 문제가 있다.

## 2.1 타입 캐스팅 문제
JDK Dynamic Proxy와 CGLIB를 사용해 AOP 프록시를 만드는 방법에는 장단이 있지만, <br>
JDK Dynamic Proxy는 인터페이스가 필수이고, CGLIB는 구체 클래스를 기반으로 만들어야 한다는 한계점이 있다. <Br>

그런데, 스프링 AOP는 CGLIB를 인터페이스인 경우에도 `proxyTargetClass` 옵션을 통해 사용할 수 있게 해준다. (true인 경우 CGLIB, flase인 경우 JDK 동적 프록시) <br>
반대로 **JDK 동적 프록시는 구현체인 구체 클래스로 타입 캐스팅이 되지 않는다는 한계가 있다.** <br>

그러니까, 인터페이스 MemberService가 있고, 그 구현체인 MemberServiceImpl이 있다고 해보자. <br>
이떄 MemberServiceImpl를 기반으로 만든 프록시는 MemberServiceImpl로 변환이 불가능하다!

```java
@SpringBootTest
public class ProxyTest {

    @Test
    public void test() {
        /* MemberServiceImpl의 프록시를 생성한다. */
        MemberServiceImpl memberServiceImpl = new MemberServiceImpl();
        ProxyFactory proxyFactory = new ProxyFactory(memberServiceImpl);
        /* JDK 동적 프록시 사용 설정 */
        proxyFactory.setProxyTargetClass(false);

        /* 이건 되는데 */
        MemberService memberService = (MemberService) proxyFactory.getProxy();

        /* 이건 안 된다. */
        MemberServiceImpl memberServiceImpl2 = (MemberServiceImpl) proxyFactory.getProxy();
    }

}

/*
 * 결과 - ClassCastException 발생
 * java.lang.ClassCastException: class jdk.proxy3.$Proxy105 cannot be cast to class hello.aop.order.aop.proxy.MemberServiceImpl (jdk.proxy3.$Proxy105 is in module jdk.proxy3 of loader 'app'; hello.aop.order.aop.proxy.MemberServiceImpl is in unnamed module of loader 'app')
 *	at hello.aop.proxy.ProxyTest.test(ProxyTest.java:24)
 * */
```

MemberServiceImpl을 기반으로 만든 프록시지만, MemberServiceImpl로 변환이 불가능하다. <br>
MemberServiceImpl를 기반으로 만든 프록시지만, MemberSerivce의 구현체이고, MemberServiceImpl는 모르기 떄문이다! (아래 그림 참고) <br>

![image](https://github.com/binary-ho/TIL-public/assets/71186266/b431594f-80f0-478f-b8e9-8f2567dfc3c3)


![image](https://github.com/binary-ho/TIL-public/assets/71186266/633863a7-4776-4397-a85e-d1daf10d6c3a)


<br> <br>

그러나, CGLIB는 부모-자식 관계이므로, 당연히 캐스팅이 가능하다.

![image](https://github.com/binary-ho/TIL-public/assets/71186266/3c8d9e83-ffdc-4f6a-86b5-96007c32da63)


그래서 이게 뭐가 중요하냐?

## 2.2 CGLIB의 구체 클래스 기반 프록시 문제

CGLIB는 구체 클래스를 기반으로 프록시를 만드는데 그래서 아래의 문제를 겪는다.
1. 대상 클래스에 기본 생성자가 필수이다.
2. 생성자가 2번 호출되는 문제가 발생할 수도 있다.
3. final 키워드 클래스나 final 메서드를 사용할 수 없음.


<Br>

### 2.2.1. 대상 클래스에 기본 생성자가 필수이다.
CGLIB는 대상 클래스를 상속 받기 떄문에, 자식 클래스의 생성자를 호출할 때, 부모 클래스의 생성자도 호출된다. 
CGLIB 프록시는 대상 클래스를 상속 받고, 생성자에서 대상 클래스의 기본 생성자를 호출한다. <br> 
**따라서 대상 클래스에 파라미터가 하나도 없는 기본 생성자를 꼭 만들어야 한다.** <br>


<br> 

### 2.2.2 생성자가 2번 호출되는 문제가 발생할 수도 있다.
CGLIB는 구체 클래스를 상속 바고, 부모 클래스의 생성자도 호출한다. <br>
이때 생성자가 2번 호출되는데
1. Target의 객체를 생성하면서 한번 (내가 직접 생성할 때 호출)
2. 프록시 객체를생성할 때 부모 클래스의 생성자가 호출되며 두번 호출된다.

![image](https://github.com/binary-ho/TIL-public/assets/71186266/7a555899-685f-4ec1-9ad8-44e4d9394bc8)

<br>

생성자에서 뭔가를 변화시키는 로직이 있다면 즐거운 상황은 아니다.

<br>

### 2.2.3 final 키워드 클래스나 final 메서드를 사용할 수 없음.

CGLIB는 상속을 기반으로 하기 떄문에 클래스나 메서드에 `final`이 붙어있다면 꼼짝없이 프록시가 생성되지 않거나, 정상 동작하지 않는다.

<br> <br>

- 결국 JDK 동적 프록시는 대상 클래스 타입으로 주십시의 문제가 있고
- CGLIB는 대상 클래스에 기본 생성자가 필수이며, 2번 호출된다는 문제가 있다.


# 3. 스프링에서 위 문제들을 해결한 방식
스프링은 AOP 프록시 생성을 편리하게 해주기 위해 많이 고민했고, 계속해서 기술을 변경해왔다.

#### 1. CGLIB를 스프링 코어 내부에 함꼐 패키징 (스프링 3.2 ~ )
#### 2. CGLIB에서 기본 생성자 없이 객체를 생성하도록 변경 (스프링 4.0 ~ )
-> `objensis`라는 기본 생성자 없이 객체 생성을 가능하게 하는 특별한 라이브러리를 도입해서 문제를 해결했다.


#### 3. 생성자 2번 호출 문제 해결 (스프링 4.0 ~ )
-> `objensis`의 기능을 사용해 생성자가 1번만 호출되도록 변경


#### 4. CGLIB 기본 사용 (스프링 부트 2.0 ~ )
-> 스프링 부트 2.0 부터 CGLIB를 기본으로 사용해, 구체 클래스 타입으로 의존관계를 주입하는 문제를 해결 (애초에 구체 클래스로 구현하니까) <br>

<Br> <br>

## 결론
1. 내부 호출을 조심하자
2. CGLIB로 AOP 구현시 final 키워드만 조심하자.
스프링은 CGLIB의 여러 단점들을 해결하는 한편, 별도 설정이 없다면 인터페이스가 있더라도 JDK 동적 프록시가 아닌 CHLIB를 사용해 구체클래스를 기반으로 프록시 생성하도록 했다. <br>
덕분에 final 키워드 문제 외의 문제들은 전부 해결됐다. 개발자는 아무것도 모르고 써도 손쉽게 AOP를 구현할 수 있다. 


