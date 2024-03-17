# Multipart Upload to Upload Large Objects

## 배경

> java.lang.OutOfMemoryError: Required array size too large

5GB 이상의 파일을 업로드하려고 하면 위와 같은 에러가 발생한다. 이는 JVM의 Heap Size가 부족하기 때문에 발생하는 에러이다. 최대 20GB 까지의 파일을 업로드할 수 있어야 하기 때문에, 서버의 메모리 자원을 올려주는 방식으로는 적합하지 않을 것이라 판단하여 대안을 찾아보았다.

## Multipart Upload

> A multipart upload allows an application to upload a large object as a set of smaller parts uploaded in parallel. Upon completion, combines the smaller pieces into the original large object.

Multipart Upload는 큰 파일을 여러 개의 작은 파일로 나누어 병렬로 업로드하는 방식이다. 이 방식을 사용하면, 큰 파일을 업로드할 때 발생하는 여러 문제를 해결할 수 있다.

- 단일 HTTP connection으로 파일 업로드를 처리할 때 발생하는 TCP 처리량 제한을 우회하고 병렬처리로 인한 가용 network bandwidth를 최대한으로 사용.
- 파일 업로드 중에 문제 발생 시, 문제가 발생한 부분만 재시도함으로써 효율 증대.
- 작은 파일로 쪼개어 한번에 처리되는 서버의 메모리 자원을 최소화하여, 서버의 메모리 부족 문제 해결.

## Multipart Upload 적용 대표 사례: Amazon S3

> Amazon S3 can be ideal to store large objects due to its 5TB object size maximum along with its support for reducing upload times via multipart uploads and transfer acceleration.

S3의 multipart upload와 transfer acceleration 사용 전/후 업로드 소요 시간 비교 (485 MB 파일 업로드 시)

| Multipart Upload | Transfer Acceleration | Upload Time | Improvement |
| :--------------: | :-------------------: | :---------: | :---------: |
|        No        |          No           |     72s     |      -      |
|       Yes        |          No           |     43s     |     40%     |
|        No        |          Yes          |     45s     |     38%     |
|       Yes        |          Yes          |     28s     |     61%     |

[Uploading large objects to Amazon S3 using multipart upload and transfer acceleration](https://aws.amazon.com/blogs/compute/uploading-large-objects-to-amazon-s3-using-multipart-upload-and-transfer-acceleration/) 에서 확인할 수 있듯이, Multipart Upload를 사용하면 업로드 시간을 최대 61%까지 단축할 수 있다.

- Single Part upload로 파일 업로드 시 `72초`가 소요됨.
- 위 파일은 Multipart upload와 transfer acceleration를 함께 사용했을 때 28초 (61% 개선) 만에 업로드가 완료됨.

## Multipart Upload 적용 방법

Multipart Upload 방식을 구현하는 순서는 아래와 같다.

1. **initialize upload request:**
    - client는 업로드할 파일 이름, 파일 사이즈 정보와 함께 업로드 초기화 요청을 보낸다.
    - 서버에서는 사용자의 요청 파일 이름으로 중복 파일이 있는지 검사하고, 없으면 Unique Slide ID를 생성하여 사용자, 요청 파일 정보와 함께 DB에 저장한다.
    - 해당 Slide ID와 파일 이름으로 지정된 저장 공간에 Parts를 저장할 폴더를 생성한다.
    - 파일의 사이즈를 기반으로 parts로 받을 파일의 최대 사이즈와 client가 전달해줘야 하는 총 part의 수를 계산한다.
    - Response로 위 과정에서 생성한 Slide ID, maxPartSize, numberOfParts 정보를 전달한다.
2. **upload part request (in parallel):**
    - 초기화 요청으로부터 전달받은 값을 기반으로 원본 파일에서 maxPartSize 만큼의 byte를 Slide ID, part number 정보와 함께 서버에 전달한다.
    - 위 요청을 numberOfParts의 수 만큼 수행한다.
    - 위 요청을 병렬로 처리하여 성능 향상을 이끌어 낸다.
    - 서버에서는 초기화 단계에서 생성한 저장 공간 위치에 파트의 넘버 정보를 포함한 파일 이름으로 파트를 저장한다.
    - 에러 상황 발생 시 client에 에러 정보를 전달하여 client가 해당 파트 요청을 다시 수행할 수 있도록 가이드한다.
3. **Complete upload request:**
    - 모든 파트 전송 요청이 성공했다면, client는 완료 검증을 위한 Slide ID, numberOfParts, 파일 이름 정보와 함께 업로드 완료 요청을 보낸다.
    - 서버는 위 정보를 기반으로 해당 슬라이드의 파일 이름과 생성된 파일 수를 확인한다.
    - 검증이 완료되면 파트를 순서대로 병합하여 하나의 파일. 즉, 원본 파일을 만든다.
    - 병합이 완료되면 파트를 삭제하고, 업로드 완료 상태를 client에 전달한다.

### 테스트 방법

구현한 Multipart Upload 방식이 정상 동작하는지 테스트하고, 전체 파일을 한번에 업로드하는 방식과 성능 차이를 확인하기 위해 아래와 같은 API를 생성했다.

- `createMultipartUpload` : 1단계. 초기화 요청을 수행하는 API
- `uploadPart`: 2단계. 파트 업로드 요청을 수행하는 API
- `completeMultipartUpload` : 3단계. 최종 파트를 최종 결과물로 병합하는 API
- `uploadSingleFile` : 성능 측정으로 위한 전체 파일을 한번에 업로딩하는 API

### 테스트 결과

- Multipart upload 방식으로 파일을 업로드 할 경우, 20GB 크기의 파일도 성공적으로 업로드할 수 있었다.
- Multipart upload 요청을 병렬로 요청할 경우, 파일 사이즈가 커질수록 뚜렷한 성능 차이를 확인할 수 있었다.
- 전체 파일을 한번에 업로드하는 방식은 5GB 업로드 시 Out Of Memory Error를 발생 (아래 사진 참고)시키며, 해당 에러는 JVM의 maxHeepSize를 늘려서 해결되지 않는다.
- 작은 파일인 경우, 전체 파일을 한번에 업로드하는 방식이 더 효율적이었지만, 파일 사이즈가 커질수록 multipart upload 방식으로 업로드하는 방식이 더 큰 효율을 내는 것을 확인할 수 있었다.

아래는 파일 사이즈에 따른 업로드 방식의 성능 테스트 결과이다.

**File Size: 488MB**

| Multipart upload | Parallel (Coroutine) | Upload time |
| --- | --- | --- |
| No | No | 1.5s |
| Yes | No | 4.7s |
| Yes | Yes | 4.7s |
- Single Upload 방식: 1.5초

    ![스크린샷 2024-03-17 154323](https://github.com/10000-Bagger/free-topic-study/assets/34956359/771f799d-3732-4ac6-aa90-945ff2d4f05d)

- multipart upload 방식 (sync): 4.7초

    ![스크린샷 2024-03-17 154412](https://github.com/10000-Bagger/free-topic-study/assets/34956359/59aa9d17-05b5-402a-b8dd-bac0c22542fc)

- multipart upload 방식 (Parallel): 4.7초

    ![스크린샷 2024-03-17 154541](https://github.com/10000-Bagger/free-topic-study/assets/34956359/90f098e5-ecec-4da5-8da2-4e7425e9f68d)


**File Size: 5GB**

| Multipart upload | Parallel (Coroutine) | Upload time |
| --- | --- | --- |
| No | No | - |
| Yes | No | 63s |
| Yes | Yes | 59s |
- Single Upload 방식: 확인 불가

![스크린샷 2024-03-17 150019](https://github.com/10000-Bagger/free-topic-study/assets/34956359/8ee0ab92-4734-41fa-a008-10a8254e9709)

- multipart upload 방식 (sync): 63초

    ![스크린샷 2024-03-17 154041](https://github.com/10000-Bagger/free-topic-study/assets/34956359/6c0a228e-47d5-4802-981a-a5fa6c76c814)


- multipart upload 방식 (Parallel): 59초
  
    ![스크린샷 2024-03-17 153814](https://github.com/10000-Bagger/free-topic-study/assets/34956359/b7c2bc4e-026b-491d-9232-2281bbee784f)
    

**File Size: 20GB**

| Multipart upload | Parallel (Coroutine) | Upload time |
| --- | --- | --- |
| No | No | - |
| Yes | No | 272s |
| Yes | Yes | 248s |

- multipart upload 방식 (sync): 4분 32초
  
    ![스크린샷 2024-03-17 152637](https://github.com/10000-Bagger/free-topic-study/assets/34956359/7eaf5ac6-07bd-489c-9249-a8055547ec8d)    

- multipart upload 방식 (Parallel): 4분 8초

    ![스크린샷 2024-03-17 153208](https://github.com/10000-Bagger/free-topic-study/assets/34956359/ae00c89d-c7b3-4cb7-a9a9-a96402ffd403)
