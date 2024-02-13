# TL;DR
- [플러터 iOS 배포 가이드](https://docs.flutter.dev/deployment/ios)에 잘 나와있지만
- 문서에 없는 내용이랑 트러블 슈팅 내용을 적어봤섭니다
- 인생 첫 앱 배포라 내용이 일부 틀릴 수 있음 🧑‍🦲

<br />

## Developer 계정 생성

1. https://developer.apple.com/account/
2. Apple Developer Program 등록
    - 1년에 12만원인가라고 했는데 회사에서 등록해줘서 잘 모르겠음


## Apple App Store Connect 앱 등록

- iOS 앱 배포를 위해서는 https://appstoreconnect.apple.com/ 에서 앱을 등록해줘야함

1. app store connect > 앱 선택
<img width="500" alt="image" src="https://github.com/10000-Bagger/free-topic-study/assets/80238096/a32a1a40-9b6f-4f45-b58c-650f3ede9806">



2. App Store Connect 내 앱 등록
<img width="500" alt="image" src="https://github.com/10000-Bagger/free-topic-study/assets/80238096/53ed27cc-66f5-43d2-968b-bd47f191f848">


-  Description(앱 이름)을 입력
- Explicit App ID 선택한 후에 번들 ID 입력
- 앱에서 사용할 기능을 선택한 다음 Continue

> 참고:  XCode 내에서 Team을 선택해놓으면 일부 정보들이 기입되어있음
>
> <img width="500" alt="image" src="https://github.com/10000-Bagger/free-topic-study/assets/80238096/84ae63ea-6c6a-49d5-8521-5cc0eab16fab">


4. 앱 등록 확인
<img width="393" alt="image" src="https://github.com/10000-Bagger/free-topic-study/assets/80238096/fac0eb75-9e54-4234-9064-bf7c2b9d756c">


## TestFlight 배포하기

<img width="393" alt="image" src="https://github.com/10000-Bagger/free-topic-study/assets/80238096/8a161496-b9d6-46ab-82da-a5359f5ba7a2">

### [TestFllight란](https://developer.apple.com/kr/testflight/)
- 앱 배포하기 전에 테스트해볼 수 있는 도구
- 앱 스토어는 배포 심사가 오래 걸리고 / 앱 배포 전에 베타 테스트를 하기 위해서 등을 위해 테스트 플라이트를 자주 사용함

### 배포하기
1. XCode에서 `Product > Archive`
2. `Distribute App`을 누르고 기도하기
    - 이 과정에서1차 심사 느낌으로 검증을 하는데 오류가 많이 뜸
    - 아래 트러블 슈팅에 몇 가지 정리함

<img width="500" alt="image" src="https://github.com/minkyung00/wiki/assets/80238096/69944b5d-e5da-40d4-8798-7685729c777d">



3. 배포를 완료하면

<img width="474" alt="image" src="https://github.com/10000-Bagger/free-topic-study/assets/80238096/be438e9d-81be-4fc4-a460-1e5836d8ce19">


<br />

---

<br />

## TroubleShooting

### 1. App Icon Asset
<img width="300" alt="image" src="https://github.com/10000-Bagger/free-topic-study/assets/80238096/dd31bdfc-c48f-4998-9348-e1d2757a6f5d">

#### 오류
- https://www.appicon.co/ 에서 앱 아이콘 이미지 생성을 했는데
- 배경이 투명한 png를 사용해서 오류 발생

#### 해결

<img width="300" alt="스크린샷 2024-02-12 오후 5 04 46" src="https://github.com/10000-Bagger/free-topic-study/assets/80238096/81150c53-7c86-48fe-9e58-5f83ba92ddd8">


- 미리보기 > 내보내기 > 알파 체크 해제
   - > `알파`: rgba에서 a를 의미하고, 투명도 정보를 전달하는데 사용해서 알파 == 투명도로 간주됨

근데 앱 아이콘이 png면 왜 안되는거지

- 추가로 보면 좋을 정보
    - [iOS 앱 아이콘 가이드](https://developer.apple.com/design/human-interface-guidelines/app-icons/)

### 2. SDK version
<img width="300" alt="image" src="https://github.com/10000-Bagger/free-topic-study/assets/80238096/f7dacf2b-0e3e-449a-a6ff-77b352106280">

#### 오류
- 2023년 4월부터 ios 정책이 변경됨
- XCode 15 버전 이상에서 iOS 17 이상으로 빌드해야한다고 함

```
- 현재 내 버전
  - XCode 14.3
  - iOS 16.4
  - macOS Ventura 13.4 
```

#### 해결
- 회사 노트북에 XCode 버전 올리면 안돼서 고물 맥북을 소노마로 업그레이드함
- 개발환경 세팅부터 다시 함 눈물 난다
