## Observer Pattern은 무엇인가?
--- 
`Observer Pattern`이란 한 객체의 상태가 바뀌면 그 객체에 의존하는 다른 객체들에게 변경 사실을 알리고 자동으로 연관된 상태들이 바뀌도록 하는 구조로 1:N의 의존 관계를 가진다.
이 설명을 들었을 때 처음 Pub/Sub 구조를 떠올렸는데 아래와 같은 공통적인 특징들 때문에 이런 생각이 들었던 것 같다.
하지만 Observer Pattern에서는 Message Queue 형태의 Broker가 없다는 점에서 Pub/Sub 구조와는 확연한 차이가 있다.
- 1:N 관계
- 느슨한 결합
- 알림 메커니즘
  <br></br>



Observer Pattern에는 `Subject`와 `Observer`라는 주요 개념이 존재한다. 앞서 설명했듯이 Observer Pattern은 한 객체의 상태가 바뀌면 이 변화를 다른 객체들에게 알리는 구조이다.
이때 알림의 주체가 되는 객체를 Subject, 알림을 전달 받는 객체가 Observer이고 Subject와 Observer가 1:N 관계인 것이다.  
<br></br>

![observer-pattern.jpg](img/observer-pattern.jpg)
다이어그램을 살펴보면 Subject와 Observer Interface 그리고 구현체들이 존재한다. Subject 구현체인 WeatherData는 List로 Observer들을 관리한다.
그리고 내부 필드인 pressure, humidity, temperature가 변할 때마다 관리하고 있는 Observer들에게 변경 사실을 알리게 된다.
각 Observer들은 알림을 받은 후 내부 필드인 Subject 구현체를 통해 변경된 데이터를 얻게 된다.
<br></br>


### (1) 코드로 알아보는 Observer Pattern: Push 방식
Observer Pattern은 크게 Push 방식과 Pull 방식으로 구현할 수 있다. Push 방식은 Subject가 알림과 함께 알리고자 하는 데이터를 일괄적으로 넘기는 방식이라면
Poll 방식은 Observer가 알림을 받은 후 원하는 데이터를 가져가는 형식이다. 우선 Push 방식부터 알아보자.


```java
public interface Subject {
    void registerObserver(Observer o);
    void removeObserver(Observer o);
    void notifyObservers();
}

public interface Observer {
    void update(float temperature, float humidity, float pressure);
}
```
Push 방식에서 Subject, Observer 인터페이스이다. Subject의 메서드들을 살펴보면 Obrserver를 등록/삭제하는 메서드와 모든 Observer들에게 알림을 보내는 메서드가 정의되어있다.
Observer 인터페이스에는 Subject로부터 알림을 받은 후 넘어온 데이터를 기반으로 자신이 수행할 로직을 담는 update 메서드가 정의되어 있다.  
<br></br>

```java
public class WeatherData implements Subject {
    private List<Observer> observers;
    private float temperature;
    private float humidity;
    private float pressure;

    public WeatherData() {
        observers = new ArrayList<>();
    }

    public WeatherData(List<Observer> observers) {
        this.observers = observers;
        this.temperature = -1;
        this.humidity = -1;
        this.pressure = -1;
    }

    @Override
    public void registerObserver(Observer o) {
        observers.add(o);
    }

    @Override
    public void removeObserver(Observer o) {
        observers.remove(o);
    }

    @Override
    public void notifyObservers() {
        if (!isAllSetup()) {
            throw new IllegalStateException("기상 데이터가 준비되지 않았습니다.");
        }

        observers.forEach(observer -> observer.update(temperature, humidity, pressure));
    }

    public void setMeasurements(float temperature, float humidity, float pressure) {
        this.temperature = temperature;
        this.humidity = humidity;
        this.pressure = pressure;
        notifyObservers();
    }
}

```
Subject의 구현체인 WeatherData 코드이다. Observer의 등록/삭제하는 간단한 메서드를 확인할 수 있고 notifyObserver는 Observer들을 순회하며 update를 수행하는 방식으로 알림을 보내는 것을 확인할 수 있다.
WeatherData는 setMeasurements(...) 메서드를 통해 내부 필드에 변경이 발생하는 시점에 notifyObservers()를 호출해 각 Observer들에게 알림을 보낸다.  
<br></br>

```java
// CurrentConditionDisplay 중 일부
@Override
public void update(float temperature, float humidity, float pressure) {
    this.temperature = temperature;
    this.humidity = humidity;
    display();
}
    
// StaticsDisplay 중 일부
@Override
public void update(float temperature, float humidity, float pressure) {
    this.temperature = temperature;
    this.humidity = humidity;
    this.pressure = pressure;
    display();
}
```
Observer의 두 구현체의 update 메서드이다. CurrentConditionDisplay에서는 temperature와 humidity만 필요하기 때문에 파라미터 중 2가지 값을 이용해 원하는 로직 (내부 필드 update)을 수행하고,
StaticsDisplay는 모든 값을 사용하여 원하는 로직을 수행한다. 하지만 이렇게 될 경우 아쉬운 점이 생긴다. 만약 알림을 통해 새로운 필드를 매개변수로 넘겨야 한다면 모든 Display 객체의 update 필드에는 변경이 필요할 것이다.
또한 CurrentConditionDisplay의 update 메서드와 같이 사용하지 않는 데이터도 매개변수로 받아와야 하는 점도 아쉬운 점 중 하나이다.

### (2) 코드로 알아보는 Observer Pattern: Pull 방식
```java
public interface Observer {
    
    void update();
}

package org.example.observer;

import java.util.ArrayList;
import java.util.List;

public class WeatherData implements Subject {
    private List<Observer> observers;
    private float temperature;
    private float humidity;
    private float pressure;

    ...

    public float getTemperature() {
        return temperature;
    }

    public float getHumidity() {
        return humidity;
    }

    public float getPressure() {
        return pressure;
    }
}

```
Push 방식의 아쉬운 점들을 해결할 수 있는 방식이 Poll 방식이다. 우선 이전과 다르게 Observer 인터페이스의 update() 메서드의 파라미터가 모두 사라진다.
Subject의 구현체에서 알림을 통해 전달하고자 했던 데이터에 접근할 수 있는 public getter 메서드를 추가해준다.  
<br></br>

```java
// CurrentConditionDisplay 중 일부
@Override
public void update() {
    this.temperature = weatherData.getTemperature();
    this.humidity = weatherData.getHumidity();
    display();
}
    
// StaticsDisplay 중 일부
@Override
public void update() {
    this.temperature = weatherData.getTemperature();
    this.humidity = weatherData.getHumidity();
    this.pressure = weatherData.getPressure();
    display();
}
```
이후 Observer 구현체의 update() 메서드에서는 이전처럼 파라미터로 전달된 데이터를 사용하는 것이 아니라 Subject 구현체의 getter 메서드를 활용해 직접 데이터를 가져온다.  
이렇게 구현할 경우 각 Observer 구현체에서 자신에게 필요한 데이터에만 접근할 수 있기 때문에 데이터가 추가되어도 모든 Observer 구현체의 코드를 수정할 필요가 사라진다.

### (3) 느슨한 결합
Observer Pattern의 장점은 Subject와 Observer가 느슨한 결합으로 1:N 관계를 맺고 상호작용을 할 수 있다는 점이다.  
<br></br>

느슨한 객체들이 서로 상호작용은 가능하지만 서로를 잘 모르는 관계를 뜻한다.
Observer Pattern에서 Subject와 Observer가 서로 느슨한 관계일 수 있는 이유는 Subject가 Observer의 인터페이스만 알고 있기 때문이다.
Subject와 Observer가 느슨한 결합을 가지기 때문에 아래와 같은 강점을 가지게 되는데, 이러한 이점들 때문에 객체들간의 관계는 최대한 느슨하게 가져가는 것이 좋다.
- Subject는 Observer들이 Observer 인터페이스를 구현한다는 사실만 안다.
- Observer의 새로운 구현체는 언제든지 추가될 수 있고 Observer 인터페이스만 만족한다면 Subject의 코드 변경 없이 새로운 구현체를 이용할 수 있다.
- Observer 인터페이스를 만족한다면 Observer 구현체는 어떻게 변경되어도 무방하다.

## Observer Pattern 실제 사용 예시: ApplicationEventPublisher와 ApplicationListener
---
Spring Framework에서 Observer Pattern을 활용한 대표적인 예시는 ApplicationEventPublisher과 ApplicationListener이다.
ApplicationEventPublisher는 Subject이고 ApplicationListener는 Observer 그리고 ApplicationEvent는 Subject가 Observer에 전달하는 데이터를 의미한다.
Spring의 Event 기능에 대해서는 깊게 알아볼 계획이 있기에 여기서는 생략하려고 한다.   
<br></br>

```java
@FunctionalInterface
public interface ApplicationEventPublisher {
    default void publishEvent(ApplicationEvent event) {
        this.publishEvent((Object)event);
    }

    void publishEvent(Object event);
}

@FunctionalInterface
public interface ApplicationListener<E extends ApplicationEvent> extends EventListener {
    void onApplicationEvent(E event);

    default boolean supportsAsyncExecution() {
        return true;
    }

    static <T> ApplicationListener<PayloadApplicationEvent<T>> forPayload(Consumer<T> consumer) {
        return (event) -> {
            consumer.accept(event.getPayload());
        };
    }
}
```
간단히 Subject와 Observer 역할을 하는 두 인터페이스만 살펴보자면, ApplicationEventPublisher에는 Event를 publish하는 메서드가 존재하고 이 메서드는 이전 예시의 notifyObservers()와 같은 역할을 한다.
ApplicationListener에서 이전 예시의 update() 역할을 하는 메서드는 void onApplicationEvent(E event)이고 Subject가 전달하는 데이터를 받아 각 Observer가 원하는 로직을 수행하는 부분이다.
onApplicationEvent(E event) 메서드의 매개변수에서도 알 수 있듯이 Spring에서 제공하는 Event 기능은 Push와 Pull 방식 중 Push 방식을 사용한다.


## 정리
앞서 언급했듯이 Observer Pattern은 Pub/Sub 구조와 유사하다고 느껴진다. 두 구조 모두 결합을 느슨하게 가져가는 것에 가장 큰 이점이 있다는 생각이 든다.
하지만 중간에 Message Queue 형태의 Broker가 없고 Observer가 원하는 만큼의 데이터를 가져가는 형태가 아니기 때문에 Observer가 처리할 수 있는 양을 Subject에서 고려해야 한다는 생각이 든다.
전략 패턴만큼 자주 사용될 거라 생각되는 패턴은 아니지만 자주 사용하는 Spring Framework의 Event 기능이 어떤 구조로 이루어졌는지 알아볼 수 있어 재밌었다.