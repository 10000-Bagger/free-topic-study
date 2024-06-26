# Static Factory Method Pattern: Naming Convention

## Static Factory Method Pattern

- 정적 팩토리 메서드 패턴은 개발자가 구성한 Static Method를 통해 간접적으로 생성자를 호출하는 객체를 생성하는 디자인 패턴.
- 객체를 인스턴스화 할 때 constructor를 사용하지않고, 별도의 객체 생성의 역할을 하는 클래스 메스드를 통해 간접적으로 객체 생성을 유도하는 것.

```kotlin
// constructor
class Book(
    val title: String
) {
    // static factory method
    companion object {
        fun of(title: String): Book = Book(title)
    }
}
```

## 생성자 대신 정적 팩토리 메서드를 고려하라

그렇다면 왜 멀쩡한 생성자를 놔두고 한단계 거쳐 정적 팩토리 메서드를 통해 객체를 생성하는걸까?

**정적 팩토리 메소드**

- 객체 생성의 역할을 하는 클래스 메소드
- Effective Java에서는 아래와 같은 이유로 “생성자보다 정적 팩토리 메소드를 고려하라.”고 주장한다.

## **정적 팩토리 메소드의 장점**

### **1. 생성 목적에 대한 이름 표현이 가능하다.**

객체를 new 캐워드를 통해 생성자로 생성하려면, 개발자는 해당 생성자의 인자 순서와 내부 구조를 알고 있어야 목적에 맞게 객체를 생성할 수 있다는 제약이 있다.

예를 들어 다음과 같이 Book 클래스는 title과 author로 생성자를 생성할 수도 있고 author 필드를 선택적으로 입력받을 수도 있다. 

```kotlin
// primary constructor
class Book(
    val title: String,
    val author: String
) {
    // Secondary constructor
    constructor(title: String) : this(title, "Unknown Author")
}

```

```kotlin
// Using the primary constructor
val book1 = Book("My Book", "Roo")
// Using the secondary constructor
val book2 = Book("Secret Book")
```

위에서 보는 것과 같이 생성자로 넘기는 매개변수만으로는 반환될 객체의 특성을 제대로 표현하기가 어렵다.

따라서 정적 메서드를 통해 적절한 메서드 네이밍을 해준다면 반환될 객체의 특성을 한번에 유추할 수 있게 된다.

```kotlin
class Book(
    val title: String,
    val author: String
) {
    // static factory method
    companion object {
        fun authorUnknownFrom(title: String): Book = Book(title, "Unknown Author")
    }
}
```

```kotlin
val book = Book.authorUnknownFrom("Secret Book")
```

이처럼 생성자 대신 정적 팩토리 메서드를 호출함으로써 생성될 객체의 특성에 대해 쉽게 묘사할 수 있다는 장점이 있어 코드의 가독성을 높여주게 된다.

따라서 생성자로 만드는 것보다 의미를 가진 메서드를 이용하면 객체 생성의 의미를 파악하기 더 쉬워진다.

### 2. 인스턴스에 대해 통제 및 관리가 가능하다.

메스드를 통해 한단계 거쳐 간접적으로 객체를 생성하기 때문에, 기본적으로 전반적인 객체 생성 및 통제 관리를 할 수 있게 된다.

즉 필요에 따라 항상 새로운 객체를 생성해서 반환할 수도 있고, 아니면 객체 하나만 만들어두고 이를 재사용하게 하여 불필요한 객체를 생성하는 것을 방지할 수 있다.

- 예: Singleton design pattern (getInstance()라는 정적 팩토리 메서드를 사용해 오로지 하나의 객체만 반환하도록 하여 객체를 재사용해 메모리를 아끼도록 유도할 수 있다.)

```kotlin
class Singleton private constructor() {

    companion object {
        @Volatile
        private var instance: Singleton? = null

        fun getInstance(): Singleton {
            return instance ?: synchronized(this) {
                instance ?: Singleton().also { instance = it }
            }
        }
    }
}
```

### 3. 하위 자료형 객체를 반환할 수 있다.

클래스의 다형성의 특징을 응용하여 메서드 호출을 통해 얻을 객체의 인스턴스를 자유롭게 선택할 수 있는 유연성을 제공한다.

```kotlin
interface SmarPhone {
    public static SmarPhone getSamsungPhone() {
        return new Galaxy();
    }

    public static SmarPhone getApplePhone() {
        return new IPhone();
    }
}
```

이러한 아이디어는 인터페이스를 static factory method의 반환 타입으로 사용하는 인터페이스 기반 프레임워크를 만드는 핵심.

## 정적 팩토리 메서드 네이밍 규칙

정적 팩토리 메서드 사이의 역할을 구분짓기 위해 독자적인 naming convention이 존재한다. 정적 팩토리 메서드에서의 네이밍은 해당 방식의 문제점을 보완하기 위해 정립된 내용이기 때문에 정적 팩토리 메서드에 대한 개념을 아는 것만큼 중요하다.

정적 팩토리 메서드에서 사용되는 네이밍 단어 종류는 아래와 같다.

- from: 하나의 매개 변수를 받아서 객체를 생성

```kotlin
Date d = Date.from(instant)
```

- of: 여러개의 매개 변수를 받아서 객체를 생성

```kotlin
Set<Rank> faceCards = EnumSet.of(JACK, QUEEN, KING)
```

- valueOf: from과 of의 더 자세한 버전

```kotlin
BigInteger prime = BigInteger.valueOf(Integer.MAX_VALUE)
```

- getInstance | instance: 인스턴스를 생성. 이전에 반환했던 것과 같을 수 있음.

```kotlin
Calender instance = Calender.getInstance()
```

- newInstance | create: 항상 새로운 인스턴스를 생성

```kotlin
Object newArray = Array.newInstance(classObject, arrayLen)
```

- get[OrderType]: 다른 타입의 인스턴스를 생성. 이전에 반환했던 것과 다를 수 있음.

```kotlin
// get[Type]: getInstance와 같으나, 생성할 클래스가 아닌 다른 클래스에 팩터리 메서드를 정의할 때 사용.
// Type은 팩터리 메서드가 반환할 객체의 타입.
FileStore fs = Files.getFileStore(path)
```

- new[OrderType]: 항상 다른 타입의 새로운 인스턴스를 생성

```kotlin
BufferedReader br = Files.newBufferedReader(path)
```

- [type] : getType과 newType의 간결한 버전

```kotlin
List<Complaint> litany = Collections.list(legacyLitany)
```
