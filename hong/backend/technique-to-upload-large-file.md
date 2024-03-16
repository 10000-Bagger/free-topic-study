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
