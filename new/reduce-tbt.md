## 위키피디아의 TBT 개선하기

> 반디부디 때문에 성능 관련한 글을 자주 보게 되네요
>
> 위키피다아 모바일 사이트의 페이지 로딩 속도를 개선한 글에 대해 읽어서 공유드립니다!
> 
> 처음 페이지를 로드할 때 600ms 이상 걸리는 JS 작업이 있었는데, 두 단계에 거쳐 개선하였고, 그 결과 로딩 시간(TBT, Total Blocking Time)을 300ms 정도 줄일 수 있었다고 합니다


### TBT가 중요한 이유
![image](https://github.com/10000-Bagger/free-topic-study/assets/80238096/2f9d6747-9484-4724-8be7-af568fefdb33)

1. 600ms 자바스크립트 실행
2. 관련 핸들러 실행
3. 브라우저가 시각적으로 업데이트가 필요한 부분 수행

- 각 단계마다 실행시간이 오래 걸리면 사용자 인터랙션까지 시간이 오래 걸림
  - 구글에서는 `50ms`보다 오래 걸리면 `"long take"`라고 정의함
 
### TBT란
- FCP(첫번째 컨텐츠가 그려지는 시간) ~ TTI(사용자가 상호작용할 수 있는 시간) 사이에 브라우저의 메인 스레드에 있는 모든 긴 작업의 차단의 합

![image](https://github.com/10000-Bagger/free-topic-study/assets/80238096/201caf11-52c2-4eb0-8c13-75c744a48732)

- 80ms 작업은 50ms보다 30ms 더 길기 때문에 TBT에 30ms 포함
- 30ms 작업은 50ms보다 짧고 긴 작업이 아니므로 TBT에 포함 x
- 100ms 작업은 50ms보다 50ms 더 길기 때문에 TBT에 50ms 포함

=>  TBT: 30ms + 50ms = 80ms

### TBT 줄이기
#### 1. 불필요한 자바스크립트 줄이기
- 메인스레드에서 실행되는 작업인 HTML 파싱, 페인팅, 가비지 콜렉팅 등이 있지만
- 가장 로딩을 오래 걸리게 하는 것은 자바스크립트
  - [자바스크립트 프레임워크가 얼마나 많은 리소스를 사용하는지에 관련한 글](https://timkadlec.com/remembers/2020-04-21-the-cost-of-javascript-frameworks/)
 
#### 위키피디아 사례

<img src="https://github.com/10000-Bagger/free-topic-study/assets/80238096/fbb3d3f4-9be5-47aa-b377-ce91be875309" width="500px" />

- 위키피디아 모바일에서 `_enabled` 메서드의 실행 시간이 가장 길었음
- 이 메서드는 사이트 사이즈 조절을 수행
- 내부 제이쿼리의 `.on("click")` 호출이 오래 걸림

``` js
function _enable( $container, prefix, page, isClosed ) {
  ...

  var $link = $container.find("a:not(.reference a)");
  $link.on("click", function () {
    if (
      $link.attr("href") !== undefined &&
      $link.attr("href").indexOf("#") > -1
    ) {
      checkHash();
    }
  });
  util.getWindow().on("hashchange", function () {
    checkHash();
  });
}
```
- 대부분의 링크에 클릭 이벤트 리스너가 추가됨
- 링크가 많은 경우, 4000개의 링크가 열리고 200ms가 소요되는 경우가 있었음
- 결국 이 메서드를 삭제 했다고 함
  - 해결방식이 약간 짜침 🧑‍🦲 

#### 2. 자바스크립트 최적화하기

- 위키피디아 사례

<img src="https://github.com/10000-Bagger/free-topic-study/assets/80238096/5e81dbab-e784-470f-9523-0981fb994d63" width="500px" />

- `initMediaViewer` 메서드가 실행되는데 100ms가 소요
- 이 메서드는 썸네일에 클릭 이벤트 리스너를 추가해서, 클릭하면 미디어 뷰어가 열리는 동작을 수행

``` js
/**
 * Event handler for clicking on an image thumbnail
 *
 * @param {jQuery.Event} ev
 * @ignore
 */
function onClickImage(ev) {
  ev.preventDefault();
  routeThumbnail($(this).data("thumb"));
}
 
/**
 * Add routes to images and handle clicks
 *
 * @method
 * @ignore
 * @param {jQuery.Object} [$container] Optional container to search
 * within
 */
function initMediaViewer($container) {
  currentPageHTMLParser
    .getThumbnails($container)
    .forEach(function (thumb) {
      thumb.$el.off().data("thumb", thumb).on("click", onClickImage);
    });
}
```

- 위키백과 문서 편집자는 수천 개의 이미지가 포함된 문서를 만들 수 있음
- 이 코드를 실행하면 이미지가 많은 페이지의 경우 실행하는 데 100ms 이상이 걸리고 페이지의 TBT가 증가할 수 있음

- 해결 방식: 이벤트 위임 사용
   - 이벤트 위임: 이벤트 리스너를 부모에 부착
   - 즉, 모든 이미지가 포함된 하나의 컨테이너 요소에 하나의 클릭 이벤트 리스너를 추가하도록 initMediaViewer 메서드를 수정
 
### 결론
- 위키피디아는 위 두 단계를 거쳐 TBT가 200ms 감소

---

개인적으로 이 글을 읽으면서 느꼈던 점은
- 크게 엄청난 일을 하지 않았는데 성능이 변경된 점
- 사소한 변경 사항으로 웹사이트 전반적인 성능에 영향을 미칠 수 있었던 점
- 결국 측정을 잘하고 -> 어느 부분이 문제인지 인지 후 개선하는 것이 중요하다~
