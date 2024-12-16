# JDBC, DataSource, HikariCP
## 개요
---
1. JDBC API
2. DataSource
3. HikariCP  
   <br></br>
## JDBC (Java Database Connectivity)
---
![jdbc.jpg](img/jdbc.jpg)
JDBC는 Java Application과 DB 사이에 연결을 위한 표준 API이다. JDBC를 통해 개발자는 DB의 구체적인 종류와 관계 없이 일관된 접근 방식으로 DB에 접근할 수 있다.
위 그림을 보면 알 수 있듯이 JDBC를 사용하기 위해서는 JDBC 구현체인 JDBC Driver가 필요하고 개발자는 Driver의 사용법은 알 필요 없이 JDBC를 사용해 DB에 접근하게 된다.
<br></br>

### (1) DriverManager
```java
private static Connection getConnection(String url, java.util.Properties info, Class<?> caller) throws SQLException {
    ... 생략

    for (DriverInfo aDriver : registeredDrivers) {
        // If the caller does not have permission to load the driver then
        // skip it.
        if (isDriverAllowed(aDriver.driver, callerCL)) {
            try {
                println("    trying " + aDriver.driver.getClass().getName());
                Connection con = aDriver.driver.connect(url, info);
                if (con != null) {
                    // Success!
                    println("getConnection returning " + aDriver.driver.getClass().getName());
                    return (con);
                }
            } catch (SQLException ex) {
                if (reason == null) {
                    reason = ex;
                }
            }

        } else {
            println("    skipping: " + aDriver.driver.getClass().getName());
        }

    }

    ... 생략
}
```
DriverManager는 JDBC Driver들을 관리할 수 있는 객체이고 DriverManager를 통해 DB Connection을 얻을 수 있다.
위 메서드는 DriverManager 객체 내의 private static getConnection(...) 메서드로 public static getConnection(...)가 최종적으로 호출하게 되는 메서드이다.
로직을 살펴보면 등록된 Driver들을 순회하며 connection을 맺어보고 가장 먼저 맺어진 Connection을 반환한다. (여러 Driver가 등록된 경우)  
<br></br>

```java
public static void main(String[] args) throws SQLException {
    String url = "jdbc:mysql://localhost:3306/study_db";
    String user = "root";
    String password = "1234";

    try (Connection connection = DriverManager.getConnection(url, user, password)) {

        // 정적 SQL 실행을 위한 객체
        Statement statement = connection.createStatement();

        // 질의 결과 테이블 객체
        // 실제 DB 질의도 ResultSet 객체가 하게 된다. (단순히 질의 결과를 가지는 객체가 아님)
        ResultSet rs = statement.executeQuery("SELECT * FROM users");
        while (rs.next()) {
            System.out.println(rs.getString("name"));
        }
    }
}
```
앞서 살펴봤듯이 DriverManager는 url, user, password값으로 DB Connection을 맺어주는 기능을 제공한다.
하지만 위 코드를 보면 알 수 있듯이 DriverManager는 DB 연결을 Util 클래스에 가깝다.
또한 매번 DB 접근을 위해 Connection을 맺고 끊어줘야 한다는 것도 DB 접근이 빈번한 Application 입장에서는 큰 낭비일 것이다.
실제로 DriverManager.getConnection(url, user, password) 수행속도를 확인해보니 부분의 10회 평균이 0.25초였다.
API 요청에서 DB 접근을 위한 Connection 생성에 0.25초를 소비한다면 그 API의 성능은.. 더 말하지 않아도 될 것 같다.   
<br></br>

### (2) DataSource
```java
public interface DataSource  extends CommonDataSource, Wrapper {

  Connection getConnection() throws SQLException;

  Connection getConnection(String username, String password)
    throws SQLException;
    
  ... 생략
}
```
주석으로 DataSource 설명을 대신하자면 Datasource는 DB Connection을 생성하는 팩토리이다.
DriverManager의 대안으로 탄생했고 DB Connection을 획득하기 위한 메서드들이 정의되어 있다.
JDBC에서는 따로 구현체를 제공하지는 않는다. 때문에 개발자는 DataSource의 여러 구현체 중 원하는 걸 사용해 DB 접근 방식을 선택할 수 있다.   
<br></br>

## HikariCP
---
```text
Spring Boot uses the following algorithm for choosing a specific implementation:

1. We prefer HikariCP for its performance and concurrency. If HikariCP is available, we always choose it.
2. Otherwise, if the Tomcat pooling DataSource is available, we use it.
3. Otherwise, if Commons DBCP2 is available, we use it.
4. If none of HikariCP, Tomcat, and DBCP2 are available and if Oracle UCP is available, we use it.

(https://docs.spring.io/spring-boot/docs/current/reference/html/data.html#data.sql.datasource)
```
HikariCP는 고성능 JDBC Connection Pool이자 Java 진영에서 DB Connection Pool을 사용할 때 가장 먼저 고려되는 library이다.
위 글은 spring boot 공식 문서인데 Default DataSource로 사용하는 것이 HikariCP이다. 1번 글만 읽어봐도 HikariCP를 얼마나 신뢰하는 지를 알 수 있다.
<br></br>


```java
public static void main(String[] args) throws SQLException {
    HikariConfig config = new HikariConfig();
    config.setJdbcUrl("jdbc:mysql://localhost:3306/study_db");
    config.setUsername("root");
    config.setPassword("1234");

    try (HikariDataSource ds = new HikariDataSource(config)) {
        Connection connection = ds.getConnection();

        // 정적 SQL 실행을 위한 객체
        Statement statement = connection.createStatement();
        
        // 질의 결과 테이블 객체
        // 실제 DB 질의도 ResultSet 객체가 하게 된다. (단순히 질의 결과를 가지는 객체가 아님)
        ResultSet rs = statement.executeQuery("SELECT * FROM users");
        while (rs.next()) {
            System.out.println(rs.getString("name"));
        }

    }
}
```
먼저 HikariCP 사용 코드부터 살펴보자. 이름에서도 알 수 있듯이 HikariCP는 DataSource 구현체인 HikariDataSource를 제공한다.
HikariDataSource는 DataSource의 구현체이지만 추가적으로 Closeable 인터페이스를 구현하고 있기도 하다. 때문에 위 코드처럼 try with resource 구문과 함께 사용할 수 있다.
HikariCP는 스스로를 빠르다고 소개하는데 정말 빠른 걸까? 10번을 실행해봤을 때 Connection connection = ds.getConnection()의 수행 시간은 평균 1 MilliSecond이다.
이는 DriverManager를 사용했을 때보다 250배 빨라진 수치이다. 어떻게 HikariCP는 DriverManager에 비해 250배 빠른 성능을 낼 수 있는 것일까?
<br></br>

### (1) Pooling 기법
HikariCP의 CP는 Connection Pool의 약어이다. 말 그대로 Connection을 미리 생성해두고 Pool에 보관한 후 필요할 때 꺼내서 쓰는 방식이다.
이러한 방식은 DriverManger를 활용해 필요시에 DB와 Connection을 생성하고 사용 후 Connection을 닫는 방식에 비해 성능과 자원 사용 측면에서 모두 효율적이다.
<br></br>

### (2) Delegates 최적화
대다수의 사람들이 HikariCP가 고성능인 이유는 Pooling 기법에 있다고 생각할 것이고 이는 틀린 말은 아니다.
하지만 다른 Connection Pool 기반의 DataSource와 비교했을 때에도 HikariCP가 뛰어나다는 건 다른 이유들도 분명 있다는 뜻일 것이다.
[Down the Rabbit Hole](https://github.com/brettwooldridge/HikariCP/wiki/Down-the-Rabbit-Hole) 글에서는 HikariCP가 어떻게 고성능을 달성했는지 설명해주며
Connection, Statement 등을 감싼 Delegates의 최적화가 큰 역할을 한다고 말한다. 간단한 예시로 ConnectionProxy는 ArrayList\<Statement> 객체를 가지고 있는데 Statement를 생성하고 ArrayList에 담은 후 사용 후에는 제거를 해주게 된다.
이때 remove() 메서드는 Head to tail 순서로 원소를 찾는다. 하지만 대개 사용 직후 Statement가 제가된다는 것을 remove()를 Tail to head 순서로 구현한 FastList 자료 구조를 만들어 사용한다고 한다.
이러한 최적화는 큰 성능 개선은 아니라 말하지만 이정도 수준을 시작으로 JIT 컴파일러를 잘 활용할 수 있도록 바이트코드 수준의 엔지니어링까지 적용되어 고성능을 달성했다고 설명해준다.
<br></br>

## 정리
--- 
Spring Data JPA나 Spring Data JDBC처럼 개발자가 편하게 사용할 수 있는 라이브러리로 개발을 하다 보니 DB Connection과 그 주변부에 대해 생각하지 않고 개발을 해왔다는 생각이 든다.
게다가 회사 운영에서 DB Connection과 관련한 문제 상황을 겪어보지 못해 더 신경을 못썼던 것 같다.
하지만 JDBC, DataSource, HikariCP라는 DB 접근의 기반 기술을 알아보고 나니 개발했던 API들의 동작을 좀 더 세밀하게 알게된 것 같아 좋았고, 무엇보다 문제가 생겼을 떄 해결 과정에서 큰 힘이되지 않을까 싶다.





