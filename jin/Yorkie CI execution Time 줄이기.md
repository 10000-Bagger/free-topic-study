# Yorkie CI execution Time 줄이기

Yorkie의 CI 시간을 줄이며 다양한 시도를 해보았다.
물론 도입하지 못한 방법이 훨씬 많지만, 시도한 방법들이 누군가에겐 도움이 될 것 같아 PR description을 글로 옮겨본다.
[Reduce CI test time by optimizing task execution #988](https://github.com/yorkie-team/yorkie/pull/988)


일단 기존의 CI Time은 아래와 같았다.


![as-is ci time](https://github.com/user-attachments/assets/1de7dc97-031a-48b7-bc91-ac32e06fe8b7)

<Br> <br>

그리고 모든 방법을 도입한다면 아래와 같이 줄일 수도 있다.


![result ci time](https://github.com/user-attachments/assets/3982e2fc-3e12-40f8-9916-90a22f143fe1)

- build: 약 2m 20s
- bench 약 1m 10s (그림에서 더 줄어 보이는 것은 캐싱하는 시간이 생략 되었기 때문이다)
- sharding-test: 약 1m 10s

<br> <br>
 같다.

오픈소스는 컨벤션이나 컨텍스트가 공유되기 어려운 상태로 수많은 사람들이 기여하게 된다.
따라서 컨벤션을 지키지 않는 것이 프로젝트에 위험이 되는 경우, 도입하지 않는 것이 권장된다.
또한 Go 생태계 자체가 무언가를 강제할 수 있는 장치가 적은 편이다.
따라서, 정말 확실한 것만 도입할 수 밖에 없었다.

<br>

# 시도한 방법들
나는 다양한 방법을 시도했다. 실제로 실험해본 것은 더 많지만, 유효한 것들 중 몇개만 남겨본다. <br> <br>

실제로 도입한 것도 있고, 실험만 진행하고 도입하지 않은 것도 있다. <br>
도입한 것은 **`도입`** 
도입하지 않은 것은 `도입하지 않음`로 표기했다.

1. (**`도입`**) **remove unnecessary 'Get tools dependencies' step from bench, sharding jobs.** 
   - Reduce 1m 20s from `bench`, and`sharding-test` jobs
   - **단점 없음**
2. (`도입하지 않음`) **integration test를 병렬로 수행** 
   - Reduce 1m 20s from build job.
   - `Disadvantage` **:** 현재 integration test를 위한 공유 변수 중에는 “동시에 Write 하는” 변수가 존재하고, `-race` option으로 인해 테스트가 실패한다. 
   바로 지금 Race Condition을 막는 것은 쉽다. 하지만, 앞으로도 없을 것이라고 보장하기는 어렵다. 고민이 필요하다. 아래에서 더 설명한다.
3. (`도입하지 않음`) **cache make tools result** 
   - Reduce 1m 20s from build job
   - `Disadvantage` : `go install` result를 cache하는 것은 쉽지만, 이를 활용하는 것은 불편하며, make tools의 방식이 변경되는 경우 깨지기 쉽다. 아래에서 더 설명한다.


## 1. 불필요한 의존성 step 제거
ci test를 관찰하던 중 불필요한 의존성 설치를 발견했다.
Yorkie는 Make file을 통해 간단하게 의존성을 설치하게 세팅 되어 있다.
```sh
tools: ## install tools for developing yorkie
	go install github.com/bufbuild/buf/cmd/buf@v1.28.1
	go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.31.0
	go install connectrpc.com/connect/cmd/protoc-gen-connect-go@v1.12.0
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@v1.55.1
	go install github.com/sudorandom/protoc-gen-connect-openapi@v0.5.5
```

이때, 이 의존성들은 build를 위한 test들에서만 필요하지 benchmark와 sharding-test에서는 필요 없었다. 그럼에도 매번 1m 20s를 들여 설치하고 있었다.
정말 많은 사람이 참여하지만, 관심있게 들여다 보지 않으면 알 수 없다는 사실을 다시 한번 체감했다.
이러한 문제를 어떻게 하면 더 쉽게 발견할 수 있을지도 고민해 보면 좋을 것 같다.

![image](https://github.com/user-attachments/assets/6e96086c-6032-4de2-a737-cf1468250764)

<br>

bench는 1m 20s만 줄었다. 3m 20s 만큼 적어 보이는 것은 bench 결과가 이전 ci에서 캐싱되어, 캐싱하는 시간이 표시되지 않은 것이다.

<br> <br>


## 2. parallel test in integration package
golang은 간단하게 test를 Parallel로 실행할 수 있는 도구를 제공해준다.

![image](https://github.com/user-attachments/assets/7d3cea20-50e7-4b77-a67c-25c112695c31)

<br> <br>

단지 testing에서 제공해주는 `t.Parallel()`를 호출하면 병렬 테스트를 수행할 수 있다.
정확히는 병렬로 설정하지 않은 모든 테스트들이 끝난 다음, `t.Parallel()`이 적용된 모든 테스트들이 병렬로 수행된다. <br>
기존 테스트들과 병렬적으로 수행되는 것은 아니므로, 유의해야 한다.

<br> <br>

integration package에 parallel test를 적용하면, we can reduce 1m 20s from build job.

하지만, 나는 적용하지 않았다.

이유는 아래와 같다.

1. **현재 integration test에는 test 환경 설정을 위한 공유 state가 있고 이 state에 Write를 하는 Test가 있다.** <br> 따라서 테스트만을 위한 환경 설정 과정에서 Race Condition이 발생하는데, Yorkie는 테스트시 `-race` 옵션을 적용해 실행한다. <br>  <br> `-race` 옵션은 test 중 발생하는 race condition을 검출하는 기능이다. Yorkie는 CRDT기반 동시 편집 라이브러리인 만큼 각 기능들에 Race Condition이 없는 것은 중요하다. **이 테스트 옵션인 `-race` 로 인해 test가 실패한다.** <br> <br>

2. 이러한 Race Condition을 막는 것은 가능하다. <br> 
공유 Write를 제거하거나, 동시에 쓰기를 시도하지 못하도록 golang이 제공해주는 Write Mutex인 `sync.RWMutex`와 같은 방법들을 활용하는 것이다. <br>

그리고 이러한 공유 Write의 제거는 필요하다고 생각한다. `-race` 옵션의 목적은 테스트 할 대상에서 발생하는 Race Condition을 검증하는 것이지, 테스트 Setting 과정에서 발생하는 Race Condtion을 검증하는 것이 목표가 아니기 때문이다.  <br>

하지만, 제거한 이후에도 여전히 다른 문제가 남아 있고, 더 생각해 봐야한다.

   1. Parallel test 도입 이후 integration package에 test를 작성하는 사람들이 이러한 race condition을 고려해야 한다 <br>
   2. **고려하더라도, 확실하게 공유 Write가 없다고 확신하기 어렵다!** <br> 왜냐하면 잠재적 Race condition은 **테스트를 항상 실패시키지 않는다.** 내 경험상 같은 코드임에도 오직 20 ~ 30번에 한번씩 build test가 실패했다. <br> <br>
   따라서 테스트를 작성하는 사람이 race condition을 피해 테스트를 잘 작성했는지는 초기에 알 수 없다. 나는 이 상황을 방지할 수 있는 테스트 방법을 찾는 중이고, 알게된다면 공유해보려 한다.  <br> <br>
   이러한 문제들이 해결된 이후, Parallel Test를 Yorkie의 오래 걸리는 Test들에 적용할 수 있다면, 유의미하게 CI 혹은 Test 시간을 줄일 수 있을 것이다. (Bench 또한 줄일 수도 있다)
    

따라서, 일단은 도입해본 parallel test를 제거했다.

추후 테스트 시간이 더 길어진다면, 도입을 고려해볼 수 있을 것 같다.

<br> 

## 3. make tools를 캐싱하지 않은 이유

기존 모든 ci job 에서 make tools를 호출하는 step이 있었다. <br> 
따라서 make tools 결과물의 캐싱을 시도했고, 모든 job에서 1m 20s의 절약이 가능했다. <br>

(cache hit시 아래 capture의 `make-tools` job의 수행 시간은 10초 이하이다.)

![image](https://github.com/user-attachments/assets/3217ae0b-cefc-4cb8-9e48-92fa1079e9e9)


<br> <br>

테스트 결과 -> [after make-tools cache result](https://github.com/binary-ho/yorkie/actions/runs/10652632833)

<br>

하지만 나는 make tools 캐싱의 도입을 포기했다. 그 이유는 아래와 같습니다.

- 장점
    - **cache hit시 build test에서 1m 20s를 절약할 수 있다.**
- 단점

### 단점 1. **압축된 cache는 약 250MB의 용량을 차지한다.**
압축된 cache는 약 250MB의 용량을 차지한다. <br>
또한 이 캐시를 따로 관리해 주어야 한다. Github Actions는 30일 이상 접근되지 않은 캐시를 지운다. <br> 
하지만, Github Actions Free Plan은 500MB만이 제공된다.
따로 관리를 위한 step을 추가할 수 있지만, ci 과정이 매우 복잡해졌었다. <Br> <br>


### 단점 2. **캐싱을 활용하기 어렵다.**
**캐싱을 활용하기 어렵다.** <br>
추후 make tools 과정에 `go install` 이 아닌 다른 방식의 의존성 설치가 추가된다면, 캐시 타겟을 변경해야 한다. <br>

`go install` 는 결과물 파일이 있더라도, 호출시 많은 시간을 소모한다. <br>
내 테스트 결과 make tools의 결과물을 `$GOPATH/bin` 과 `$GOPATH/pkg` 에 미리 설치하더라도, 약 1분의 시간이 소요된다. 이는 기존 1m 20s와 큰 차이가 나지 않는다.<br>

make tools step을 제거하면 캐시의 효과를 누릴 수 있다. 현재 make tools는 5번의 `go install` 만을 호출하기 때문이다. 하지만, 추후 `go install` 을 호출하는 방법이 아닌, 다른 방법의 의존성 설치 과정이 추가된다면 ci에 다른 폴더의 캐싱이 추가 되어야 한다.

### 단점 3. 캐싱으로 인해 yml 파일에 최소 하나의 job, 매우 많은 step이 추가될 수 있다.
캐싱으로 인해 yml 파일에 최소 하나의 job, 매우 많은 step이 추가될 수 있다.
이는 yml 의 가독성을 크게 저해하는데, 캐싱을 적용하는 경우 아래와 같은 job이 추가된다.

```yml
  make-tools:
    name: make-tools
    runs-on: ubuntu-latest

    needs: ci-target-check
    if: ${{ needs.ci-target-check.outputs.build == 'true' }}

    steps:
    - name: Set up Go ${{ env.GO_VERSION }}
      uses: actions/setup-go@v4
      with:
        go-version: ${{ env.GO_VERSION }}

    - name: Save GOPATH to environment variables
      run: echo "GOPATH=$(go env GOPATH)" >> $GITHUB_ENV

    - name: Check out code
      uses: actions/checkout@v4

    - name: Restore Go pkg cache
      uses: actions/cache@v3
      id: restore-pkg
      with:
        path: ${{ env.GOPATH }}/gopath.tar.zst
        key: ${{ runner.os }}-gopath-${{ hashFiles('Makefile') }}
        restore-keys: |
          ${{ runner.os }}-gopath-
    - name: Get tools dependencies if cache not exists
      run: make tools

    - name: Compress Go pkg if cache not exists
      if: steps.restore-pkg.outputs.cache-hit != 'true'
      run: |
        tar -I 'zstd -3' -cf $GOPATH/gopath.tar.zst -C $GOPATH pkg bin
    - name: Store Go pkg if cache not exists
      if: steps.restore-pkg.outputs.cache-hit != 'true'
      uses: actions/cache/save@v3
      with:
        path: ${{ env.GOPATH }}/gopath.tar.zst
        key: ${{ runner.os }}-gopath-${{ hashFiles('Makefile') }}
```

<br> <br>


또한 아래와 같이 기존의 job들에 몇개의 step이 추가된다.

```yml

    - name: Save GOPATH to environment variables
      run: echo "GOPATH=$(go env GOPATH)" >> $GITHUB_ENV

    ...생략

    - name: Restore Go pkg cache
      uses: actions/cache@v3
      with:
        path: ${{ env.GOPATH }}/gopath.tar.zst
        key: ${{ runner.os }}-gopath-${{ hashFiles('Makefile') }}
        restore-keys: |
          ${{ runner.os }}-gopath-
    
    - name: Decompress Go pkg if cache exists
      run: |
        if [ -f "$GOPATH/gopath.tar.zst" ]; then
          mkdir -p $GOPATH/pkg
          tar -I 'zstd -d' -xf $GOPATH/gopath.tar.zst -C $GOPATH
        fi

```

<br>

이런 식으로 기존 캐시를 불러오기 위해 환경 변수를 세팅하고, 압축을 푸는 step이 추가되는데, 이는 yml 파일 가독성을 크게 떨어뜨린다.


## 4. 끝
결론적으로 나는 다양한 방법을 시도했다.
1. 불필요한 step이나 job을 검토했다. (적용)
2. step이나 job의 수행 시간을 줄이는 방법을 찾아 보았다. (우리 ci.yml에선 없었다.)
3. 병렬 테스트를 시도했다. (적용 하지 않음)
4. 테스트 시간 자체를 줄이려 노력했다. (우리 테스트 코드에는 별로 없었는데, go의 `Wait` 대신 `sync.WaitGroups`을 활용하는 방법이 있다.)
5. 의존성 캐싱을 시도했다. - 가장 많이 해보는 시도이다. 우리도 기본적인 golang 의존성 캐싱은 존재하지만, make tools로 설치하는 추가적인 의존성이 문제가 되었다.
