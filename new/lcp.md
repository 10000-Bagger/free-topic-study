## LCP 최적화하기

> 반디부디가 느려터졌다는 이야기를 듣고
> 
> 사이트 성능 측정을 해보았습니다
> 
> 그리고 이 글을 작성하게 되는데...

### LCP
- 모든 웹 경험에서 중요한 공통 집합을 `Core Web Vitals` 이라고 하는데 그 중 하나
- [Large Contentful Paint](https://web.dev/articles/lcp?hl=ko)
- 페이지를 처음 로드 했을 때, 가장 큰 컨텐츠가 렌더링 되는 시점까지 걸리는 시간
   - 보통 LCP가 `0 - 2.5초`면 빠름
   - `2.5 ~ 4초`: 중간
   - `4초 이상`: 느림

#### 반디부디 LCP

<img width="400" alt="image" src="https://github.com/10000-Bagger/free-topic-study/assets/80238096/62370971-e805-444b-8dee-d16eea6668c5">

> LCP `4.8초` ..🗿


### LCP 개선하기
- 페이지 로딩 ~ LCP까지 대략적으로 아래 일들이 발생
   - DNS, TCP, TLS / 리다이렉트 / TTFB / First Paint / FCP
- 이 중 하나만 느려도 LCP에 영향을 미침

#### 1. 사이즈가 큰 이미지 제거하기

> 가장 큰 컨텐츠로 잡혔던 부분은 아래 이미지 내 빨간박스 영역

<img width="300" alt="image" src="https://github.com/10000-Bagger/free-topic-study/assets/80238096/c275aa9e-ed0a-486a-8ebb-b2aec0a7343e">

- LCP 측정 시간:`4830ms` 로 아주 오래 걸림
- 해결 방식: css로 변환
    - 그라데이션만 들어간 이미지이기 때문에 이미지 압축 및 변환 필요 없이 css로 변환 가능

#### 2. 

--

- 참고자료
   - [LCP](https://web.dev/articles/lcp?hl=ko) 
