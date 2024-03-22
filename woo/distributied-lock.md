# Distributed Lock 구현
## Lock이란?
- 운영체제에서 Lock은 공유 자원을 하나의 Thread가 점유할 때 다른 Thread에서 접근하지 못하도록 막는 장치로 정의한다.
- API를 구현하며 Lock을 사용하는 것도 마찬가지이다.
- 특정 API 기능의 작업에서 특정 자원에 동시에 접근하는 것을 막는 장치이다.


## Distributed Lock이란?
- Lock은 공유 자원을 대표하는 key값을 두고 key값에 접근한 Thread(혹은 요청)이 있는지를 확인하는 방식으로 동작한다.
- 서버 대수를 2개 이상으로 가져간다면 key값을 기반으로 공유 자원에 접근한 Thread가 존재하는지 여부를 저장할 수 있는 외부 저장소가 필요하다.
- 이처럼 Application 외부 저장소를 기반으로 Lock을 구현하여 Scale Out 시에도 Lock 동작에 유효하도록 구현한 것을 Distributed Lock


## Distributed Lock 개발 시 주의점과 해결 방법