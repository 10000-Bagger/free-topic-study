---
title: 디자인 패턴 - Singleton Pattern
description: 이 글은 Singleton Pattern에 대해 설명합니다. Singleton Pattern은 클래스의 인스턴스를 하나만 생성하고, 해당 인스턴스에 전역적으로 접근할 수 있도록 보장하는 디자인 패턴입니다. 이 글에서는 synchronized 키워드, static 필드, 그리고 DCL (Double-Checked Locking) 방식의 세 가지 Singleton 구현 방법을 비교합니다. 또한, volatile 키워드가 적용된 변수와 그렇지 않은 변수의 조회 성능을 비교하는 코드를 통해 성능 차이를 분석합니다. Singleton Pattern의 개념과 구현 방법을 이해하는 데 중점을 둡니다.
authors: [woosuk]
tags: [design pattern, singleton pattern]
date: 2024-05-26
---
**:white_check_mark: ChatGPT 요약**   
이 글은 Singleton Pattern에 대해 설명합니다. Singleton Pattern은 클래스의 인스턴스를 하나만 생성하고, 해당 인스턴스에 전역적으로 접근할 수 있도록 보장하는 디자인 패턴입니다. 이 글에서는 synchronized 키워드, static 필드, 그리고 DCL (Double-Checked Locking) 방식의 세 가지 Singleton 구현 방법을 비교합니다. 또한, volatile 키워드가 적용된 변수와 그렇지 않은 변수의 조회 성능을 비교하는 코드를 통해 성능 차이를 분석합니다. Singleton Pattern의 개념과 구현 방법을 이해하는 데 중점을 둡니다.
<!-- truncate -->
<br></br>

## Singleton Pattern은 무엇인가?
---
> Singleton Pattern은 클래스 인스턴스를 하나만 만들고, 그 인스턴스로의 전역 접근을 제공하는 패턴을 뜻한다.

디자인 패턴 중 가장 친숙하다. 책에서 제시된 방식을 사용하지는 않지만 Spring Framework의 Bean Scope Default값이 Singleton이기 때문이다. 
책에서도 언급되지만 가장 간단한 Design Pattern 중 하나이기 때문에 구현 방식 3가지만 알아보려 한다.
<br></br>


### (1) synchronized 키워드 사용하기
```java
public class SynchronizedSingleton {
    private static SynchronizedSingleton instance;

    private SynchronizedSingleton() {}

    public static synchronized SynchronizedSingleton getInstance() {
        if(instance == null) {
            instance = new SynchronizedSingleton();
        }

        return instance;
    }
}
```
메서드에 synchronized 키워드를 추가해 private 생성자의 호출이 1번만 일어날 수 있도록 강제하는 방식이다. 
하지만 getInstance() 메서드를 이용할 때마다 매번 synchronized가 동작해 성능 측면에서 아쉬움이 있다. 
성능이 크게 중요하지 않다면 이렇게 사용해도 무방하다고 한다.
<br></br>


### (2) static 필드 사용하기
```java
public class StaticSingleton {
    private static StaticSingleton instance = new StaticSingleton();

    private StaticSingleton() {}

    public static StaticSingleton getInstance() {
        return instance;
    }
}
```
getInstance() 메서드에서 초기화 로직을 제거하고 정적 초기화 단계에서 필드 초기화를 진행한다. 
만약 Application 실행 중 사용되지 않을 수도 있는 클래스라면 사용하지 않을 인스턴스를 만들기 때문에 낭비이다.


### (3) DCL(Double-Checked Locking) 사용하기
```java
public class VolatileSingleton {
    private volatile static VolatileSingleton instance;

    private VolatileSingleton() {}

    public static VolatileSingleton getInstance() {
        if (instance == null) {
            synchronized (VolatileSingleton.class) {
                if (instance == null) {
                    instance = new VolatileSingleton();
                }
            }
        }

        return instance;
    }
}
```
싱글톤 필드에 volatile 키워드를 적용해 항상 main memory의 정확한 인스턴스를 읽도록 적용한다. 
이후 getInstance()에서 synchronized 키워드를 method에 적용하지 않고 synchronized 코드 블럭을 활용해 instance 값이 null일 경우에만 synchronized를 적용해 초기화 이후에는 바로 instance를 반환하도록 한다.


## 정리
---
구현과 개념이 간단하고 자주 접하는 패턴이라 어렵지 않았다. 3가지 방식 중 DCL이 단점이 없어 보이지만 3개 중에서는 가장 복잡해 보인다. 복잡함 이외의 단점이라면 volatile 키워드가 적용되어 읽기 속도가 느릴 수 있을 것 같다.
<br></br>

```java
public class VolatilePerformanceTest {
    private static final int ITERATIONS = 100_000_000;

    public static void main(String[] args) {
        // warm up
        VolatileVariable warmUpVolatileVar = new VolatileVariable();
        for (int i = 0; i < ITERATIONS; i++) {
            warmUpVolatileVar.getValue();
        }

        NonVolatileVariable warmUpNonVolatileVar = new NonVolatileVariable();
        for (int i = 0; i < ITERATIONS; i++) {
            warmUpNonVolatileVar.getValue();
        }

        // Test with volatile variable
        VolatileVariable volatileVar = new VolatileVariable();
        long volatileStartTime = System.nanoTime();
        for (int i = 0; i < ITERATIONS; i++) {
            volatileVar.getValue();
        }
        long volatileEndTime = System.nanoTime();
        long volatileDuration = (volatileEndTime - volatileStartTime) / 1_000_000; // Convert to milliseconds

        // Test without volatile variable
        NonVolatileVariable nonVolatileVar = new NonVolatileVariable();
        long nonVolatileStartTime = System.nanoTime();
        for (int i = 0; i < ITERATIONS; i++) {
            nonVolatileVar.getValue();
        }
        long nonVolatileEndTime = System.nanoTime();
        long nonVolatileDuration = (nonVolatileEndTime - nonVolatileStartTime) / 1_000_000; // Convert to milliseconds

        // Print results
        System.out.println("Volatile variable duration: " + volatileDuration + " ms");
        System.out.println("Non-volatile variable duration: " + nonVolatileDuration + " ms");
    }

    static class VolatileVariable {
        private volatile int value = 42;

        public int getValue() {
            return value;
        }
    }

    static class NonVolatileVariable {
        private int value = 42;

        public int getValue() {
            return value;
        }
    }
}

// Volatile variable duration: 4 ms
// Non-volatile variable duration: 1 ms
```
위 코드로 테스트를 진행해보니 volatile 키워드가 적용된 변수를 읽는 것이 평균적으로 약 4배 느린 것 같다. 하지만 단순 변수 접근에서 10억 번을 수행했을 때 4ms라면.. 큰 문제가 생기는 정도는 아닐 것 같다. 
사실 복잡함도 상대적인 거라 절대적인 복잡함이 크지는 않아 보이기 때문에 Singleton 객체를 생성해야 한다면 DCL 방식을 사용하는 게 가장 합리적일 것 같다.