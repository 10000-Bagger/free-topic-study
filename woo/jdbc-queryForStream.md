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

## 다시 queryForStream으로
```java
public <T> Stream<T> queryForStream(PreparedStatementCreator psc, @Nullable PreparedStatementSetter pss, RowMapper<T> rowMapper) throws DataAccessException {
    return (Stream)result((Stream)this.execute(psc, (ps) -> {
        if (pss != null) {
            pss.setValues(ps);
        }

        ResultSet rs = ps.executeQuery();
        Connection con = ps.getConnection();
        return (Stream)(new ResultSetSpliterator(rs, rowMapper)).stream().onClose(() -> {
            JdbcUtils.closeResultSet(rs);
            if (pss instanceof ParameterDisposer parameterDisposer) {
                parameterDisposer.cleanupParameters();
            }

            JdbcUtils.closeStatement(ps);
            DataSourceUtils.releaseConnection(con, this.getDataSource());
        });
    }, false));
}
```
- 잠시 Java의 Stream을 알아봤다.
- 다시 JdbcTemplate의 queryForStream() 메서드로 돌아오자.
- 위 코드는 5개의 queryForStream() 중 전신이 되는 메서드인데 이 메서드를 알아보면 queryForStream의 동작 방식을 알 수 있을 것 같다.
- 이 코드를 타고 차근 차근 파헤쳐보자

```java
ResultSet rs = ps.executeQuery();
Connection con = ps.getConnection();

return (Stream)(new ResultSetSpliterator(rs, rowMapper)).stream().onClose(() -> {
    JdbcUtils.closeResultSet(rs);
    if (pss instanceof ParameterDisposer parameterDisposer) {
        parameterDisposer.cleanupParameters();
    }

    JdbcUtils.closeStatement(ps);
    DataSourceUtils.releaseConnection(con, this.getDataSource());
});
```
- 위 코드는 queryForStream() 내부에서 SQL 결과를 Stream으로 변환하는 부분만 추려낸 것이다.
- 코드를 보면 SQL 결과와 메서드 인자 rowMapper 그리고 ResultSetSpliterator를 활용해 Stream을 생성하는 것을 확인할 수 있다.
- 그렇다면 ResultSetSpliterator가 뭐지?

## ResultSetSpliterator란?
```java
private static class ResultSetSpliterator<T> implements Spliterator<T> {
    private final ResultSet rs;
    private final RowMapper<T> rowMapper;
    private int rowNum = 0;

    public ResultSetSpliterator(ResultSet rs, RowMapper<T> rowMapper) {
        this.rs = rs;
        this.rowMapper = rowMapper;
    }

    public boolean tryAdvance(Consumer<? super T> action) {
        try {
            if (this.rs.next()) {
                action.accept(this.rowMapper.mapRow(this.rs, this.rowNum++));
                return true;
            } else {
                return false;
            }
        } catch (SQLException var3) {
            throw new InvalidResultSetAccessException(var3);
        }
    }

    @Nullable
    public Spliterator<T> trySplit() {
        return null;
    }

    public long estimateSize() {
        return Long.MAX_VALUE;
    }

    public int characteristics() {
        return 16;
    }

    public Stream<T> stream() {
        return StreamSupport.stream(this, false);
    }
}
```
- ResultSetSpliterator는 JdbcTemplate의 내부 클래스로 JdbcTemplate 내부에서만 사용되는 클래스이다.
- 또한 Spliterator를 implememts하고 있어 Spliterator 역할을 하는 것으로 보인다.
- stream() 메서드를 통해 클래스 자신을 활용해 stream을 생성해주는 역할을 하는 것으로 보이는데...
- 그럼 Spliterator는 뭐지??

## Spliterator란?
```java
public interface Spliterator<T> {
    boolean tryAdvance(Consumer<? super T> action);
    Spliterator<T> trySplit();
    long estimateSize();
    int characteristics();
    ...
}
```
- 기본적으로 Spliterator는 여러 개의 data source를 순회하거나 파티셔닝하기 위한 인터페이스이다.
- Stream의 파이프라이닝 처리를 위한 필수적인 인터페이스이다.
- 주요 method
  - tryAdvance : 요소를 하나씩 소비하면서 탐색해야 할 요소가 남아있으면 매개변수로 주어진 action을 수행하고 true 반환
  - trySplit : 일부 요소를 분할해서 두 번째 Spliterator를 생성 (ResultSetSpliterator에서는 사용하지 않는 메서드임)
  - estimateSize : 탐색해야 할 요소의 수 제공 (전체 데이터 수 - 탐색한 데이터 수)
  - characteristics : Spliterator 객체에 포함된 모든 특성값의 합을 반환

## 다시 queryForStream으로
```java
ResultSet rs = ps.executeQuery();
Connection con = ps.getConnection();

return (Stream)(new ResultSetSpliterator(rs, rowMapper)).stream().onClose(() -> {
    JdbcUtils.closeResultSet(rs);
    if (pss instanceof ParameterDisposer parameterDisposer) {
        parameterDisposer.cleanupParameters();
    }

    JdbcUtils.closeStatement(ps);
    DataSourceUtils.releaseConnection(con, this.getDataSource());
});
```
- ResultSetSpliterator와 Spliterator에 대해 간략히 알아보고 다시 queryForStream()으로 돌아왔다.
- 이제 어느 정도 코드가 이해된다.
- JdbcTemplate 내부 클래스인 ResultSetSpliterator를 활용해 ResultSet을 1건씩 Stream으로 변환하는 작업을 한다.

### 다시 원점에서 생각해보기
- 현재 queryForStream()을 알아보고 있는 이유는 대용량 DB 조회 -> 엑셀 파일 처리를 위해 queryForStream()를 사용했고 
- 어떤 방식으로 동작하기에 이 메서드를 사용한 것인지 알아보기 위해서이다.
- 현재까지 알아본 queryForStream() 동작의 큰 흐름은 아래와 같다.
  - executeQuery()로 대용량 데이터 조회 및 ResultSet 반환 -> ResultSet.next()를 활용해 1건씩 Stream으로 변환
- 지금까지는 SQL 결과를 어떻게 Stream으로 변환하는지를 파악했다.
- 하지만 executeQuery()를 통해 대용량 데이터를 한번에 조회하면 Stream을 사용하는 이유가 전혀 없을 것이다.
- 추측해보자면 executeQuery()에서도 대용량 건의 경우 데이터를 나눠서 가져오고, Stream으로 변화하고, 처리하고의 과정을 반복해야 Stream을 사용한 의미가 있을 것이다.
- 그렇다면 대용량 데이터를 조회할 때 `ResultSet rs = ps.executeQuery();` 이 코드가 어떻게 동작하는지를 알아봐야 할 것 같다..

## 