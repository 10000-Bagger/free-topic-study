# Preflight Request: CORS

![Screenshot 2024-06-10 at 1 27 13 AM](https://github.com/10000-Bagger/free-topic-study/assets/34956359/1815fde0-6550-437d-b304-f6ef151c5853)

CORS (Cross-Origin Resource Sharing, 교차 출처 리소스 공유)

- Preflight request를 이해하기 위해선 CORS에 대해서 알아야한다. CORS는 “다른 출처”에 리소스를 요청할 때 지켜야하는 정책이다. 여기서 “출처(Origin)”은 url에서 protocol, host, port 까지를 포함한다.
- Cross-Domain 환경에서는 CORS 정책으로 인증이나 쿠키같은 민감한 정보의 교환이 까다롭다.
- 예를 들어, API를 요청하는 client와 요청을 받는 backend의 url이 다르면 (port 포함) CORS policy에 위반해서 `CORS error` 를 status로 전달한다.

CORS가 발생하는 예시:

- 백엔드는 EC2로 배포하고, 프론트는 로컬에서 작업하는 경우
- 백엔드와 프론트를 다른 url로 배포하는 경우

참고: CORS는 “브라우저 정책”이기 때문에 웹 개발 시에만 발생함.

참고: 해결방법은 개발 환경에서는 브라우저에서 Access-Control-Allow-Origin 설정을 해주는 [extension](https://chromewebstore.google.com/detail/allow-cors-access-control/lhobafahddgcelffkeicbaginigeejlf)을 사용하거나 백엔드에서 CORS 설정에 프론트쪽 url을 추가해주는 방식으로 해결 가능.  

# CORS의 동작 원리

동작 원리는 크게 세가지가 있다.

- 단순 요청을 보내는 것 (Simple Request)
- 예비 요청을 보내서 확인하는 것 (Preflight)
- 인증된 요청을 사용하는 방식 (Credential Request)

## Simple Request

예비 요청 없이 서버에 바로 요청을 보내는 방법.

서버에 바로 본 요청을 보낸 뒤, 서버는 해더에 `Access-Control-Allow-Origin` 값 등을 붙여서 보내주면 브라우저가 CORS 정책 위반 여부를 검사한다.

### 조건

- `GET`, `HEAD` 요청
- `Content-Type` 헤더가 다음과 같은 `POST` 요청
    - `application/x-www-form-urlencoded`
    - `multipart/form-data`
    - `text/plain`
- `Accept`, `Accept-Language`, `Content-Language`, `Content-Type`, `DPR`, `Downlink`, `Save-Data`, `Viewpoint-Width`, `Width`를 제외한 헤더를 사용하면 안된다.
- 대체로 REST API가 `Content-Type` 으로 `application/json` 을 사용하기 때문에 사실상 지켜지기 어려운 조건. 따라서 대부분 Preflight 방식으로 처리함.

## Preflight Request

서버로 바로 요청을 보내는 Simple Request와 다르게, 지금 보내는 요청이 유효한지 확인하기 위해 `OPTIONS` 메서드로 예비 요청을 보낸다.

이 과정이 필요한 이유는 서버의 부하를 줄이기 위함이다. 예를 들어, 요청에 대한 전달 데이터의 크기가 큰 리소스를 요청한다고 했을 때, 서버는 요청 데이터를 담아서 client에 전달한다. 하지만 이 요청이 CORS 정책을 위반하는 요청이라면 브라우저에서 해당 요청을 에러로 판단하기 때문에 서버에서는 불필요하게 데이터를 전달한 상황이 된다.

따라서 이런 상황을 방지하기 위해 예비 요청을 먼저 날려서 이 요청이 유효한 요청인지 먼저 확인하는 것이다.

![Screenshot 2024-06-10 at 2 19 09 AM](https://github.com/10000-Bagger/free-topic-study/assets/34956359/0f286d3d-517b-45fa-a6c4-545c053e9b78)

### 조건

1. `OPTIONS`: 브라우저에서 OPTIONS를 던져 해당 사이트에서 사용 가능한 methods 정보를 가져오게 될 때, preflight가 일어난다.
2. `Simple Request` : 사용자 정의 Header 정보를 추가 수정하게 되면 preflight가 발생한다. 예외적으로 사용자 정의 Header가 `Content-Type` 이 위에서 정의한 타입인 경우에만 preflight가 일어나지 않는다.
3. `Cookie setting` : 내 쿠키를 다른 써드파티에 보내고 싶을 때, with Credential을 이용하게 되는데, 이때 preflight가 발생한다.

## net::ERR_CONNECTION_REFUSED

이 에러는 클라이언트 축에서 서버로의 연결이 거부되었을 때 발생함.

대부분의 경우, 서버 주소나 포트 설정 문제, 서버의 CORS 설정, 서버가 올바르게 실행되지 않고 있거나 네트워크 문제로 인해 나타날 수 있음.
