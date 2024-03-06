# jdbc - queryForStream
## 현재 상황
- 이커머스 판매자 사이트를 개발하며 주문 건들을 엑셀파일로 제공하는 기능이 있다
- 해당 기능은 대량의 주문건을 조회하여 엑셀 파일로 변환하는 작업을 수행한다.
- 팀원분이 대용량 조회를 고려하여 JdbcTemplate의 queryForStream()를 사용한 것 같은데 선택 이유를 좀 알아보려고 함

## JdbcTemplate - queryForStream
- JdbcTemplate 내에는 파라미터에 따라 총 5개의 queryForStream 메서드가 존재한다.
- 메서드 그대로 queryForStream은 Stream을 반환한다.
- 데이터를 Stream으로 반환하면 어떤 이점이 있을까?
```java
public class JdbcTemplate extends JdbcAccessor implements JdbcOperations {
    
    public <T> Stream<T> queryForStream(final String sql, final RowMapper<T> rowMapper) throws DataAccessException {
        // 생략...
    }
    
    public <T> Stream<T> queryForStream(PreparedStatementCreator psc, @Nullable PreparedStatementSetter pss, RowMapper<T> rowMapper) throws DataAccessException {
        // 생략...
    }
    
    public <T> Stream<T> queryForStream(PreparedStatementCreator psc, RowMapper<T> rowMapper) throws DataAccessException {
        // 생략...
    }

    public <T> Stream<T> queryForStream(String sql, @Nullable PreparedStatementSetter pss, RowMapper<T> rowMapper) throws DataAccessException {
        // 생략...
    }

    public <T> Stream<T> queryForStream(String sql, RowMapper<T> rowMapper, @Nullable Object... args) throws DataAccessException {
        // 생략...
    }
}
```

## Stream이란?
- 일련의 연속성을 가지는 흐름을 뜻하는 매우 추상적인 개념이다.
- 데이터가 출발지에서 도착지로 단일 방향으로 흘러가는 개념
- 예를 들어 유튜브에서 영상을 볼 때 영상 전체 파일을 한번에 제공하려 한다면 2가지 문제가 발생한다.
  - 용량이 큰 경우 엄청난 대기가 발생한다.
  - 대용량의 데이터를 한번에 처리하기 위해서는 큰 메모리 공간이 필요함.
- 위 문제점들을 해결하기 위해 영상 파일을 잘게 쪼개 연속적으로 전달하는 방식이 스트림의 한 예시이다


## Java의 Stream
### (1) 입력/출력 스트림(Input/Output Stream)
- Application과 외부에 미리 연결된 입출력 통로를 의미한다.
- 외부로부터 데이터를 받는 경우 Input Stream/ 보내는 경우 Output Stream이다.

#### Input Stream
```java
public static void main(String[] args) throws InterruptedException, IOException {

    // wow my name is woo가 적힌 파일
    InputStream inputStream = new FileInputStream("test.txt");
    byte[] bytesFromTxt = new byte[5]; // 5byte씩 참조로 고정

    while(0 < inputStream.available()) {
        inputStream.read(bytesFromTxt); // 읽어온 5byte를 bytesFromTxt에 담는다.

        System.out.println(new String(bytesFromTxt));
    }
    
    inputStream.close();
}

// wow m
// y nam
// e is 
// woo
```
- Input Stream의 강점은 외부 데이터를 원하는 양만큼만 참조하여 처리할 수 있다는 점이다.
- 즉, 데이터를 입력 받을 통로를 열어두고 원하는 양의 데이터를 가져오는 것이 핵심.
- 위 예시에서는 5byte씩 참조하여 처리하는 방식

#### Output Stream
```java
public static void main(String[] args) throws InterruptedException, IOException {
    FileOutputStream outputStream = new FileOutputStream("/Users/wkwon/test2.txt");

    byte[] bytes = "Hello, World".getBytes();

    for(byte b: bytes) {
        outputStream.write(b);
    }

    outputStream.close();
}
```
- 마찬가지로 Output Stream은 데이터를 내보낼 통로를 만들어두고 원하는 양만큼의 데이터를 전송할 때 사용한다.
- 위 예시에서는 1byte씩 데이터를 내보낸다.

### (2) 반복자 스트림(Stream)
- 컬렉션, 배열 등의 저장 요소를 하나씩 참조해서 람다식으로 처리할 수 있도록 해주는 기능이다.