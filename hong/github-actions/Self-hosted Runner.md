# Github Action Runner

로컬에서 Github Action를 테스트 해보기 위해 공부했습니다. 
공부하다보니 로컬에서 CI를 실행하는 건 맞지만 "테스트용"이 아닌 "Github Action"을 로컬에서 실행하는 거 더라구요..
CI 수정할 때 PR에 올리기 전에 내부에서 먼저 실행해보고 싶었는데, 아직 관련 대안은 없는 것 같습니다..

링크: https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners/about-github-hosted-runners

### Github Action: GitHub-hosted runners

> GitHub offers hosted virtual machines to run workflows. The virtual machine contains an environment of tools, packages, and settings available for GitHub Actions to use.
> 
- Runner는 GithHub Actions workflow를 실행하는 작업을 위한virtual machine.
- Runner는 repository를 machine에 clone하고 테스트를 위한 소프트웨어를 설치하고, 커맨드를 실행할 수 있는 기능을 제공.
- GitHub에서 runner를 제공하긴 하지만, 공식 문서에 따르면 runner를 직접 hosting해서 사용할 수 있음.
- 관련 링크: [About self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners)

### Github Actions Self-hosted Runner

> You can host your own runners and customize the environment used to run jobs in your GitHub Actions workflows.
> 
- Self-hosted Runner란 Github Actions에서 사용자가 지정하는 로컬 컴퓨팅 자원으로 빌드를 수행하도록 설정하는 기능.
- 주로 배포 작업이 많아 배포가 지체되거나 서버 비용이 부담되는 경우 사용됨.
- self-host runner는 관리 측면에서 커스터 마이징이 가능함.
    - Repository-level: 단일 저장소에서 작업 수행 가능
    - Organization-level: 조직 내 여러 저장소에 걸쳐 작업 수행 가능.
    - Enterprise-level: 엔터프라이즈 계정 내 여러 조직에 할당되어 사용될 수 있음.
- 연결 방식은 오픈 소스 [runner](https://github.com/actions/runner) 애플리케이션을 사용하여 Github과 연결해서 사용됨.
- Self-hosted runner는 Github Actions과의 연결이 14일 이상 없으면 Github에서 자동으로 삭제됨.

### GitHub-host runner와 Self-host runner의 차이점

GitHub-host runner는 빠르고 간편한 워크플로우 실행 방법을 제공. 반면 self-hosted runner는 사용자의 사용자 정의 환경에서 워크플로우를 실행할 수 있도록 유연한 구성을 제공.

GitHub-host runner:

- 운영 체제, 사전 설치된 패키지 및 도구, runner 애플리케이션 자동 업데이트
- Github에 의해 관리 및 유지보수됨.
- 각 작업 실행에 대한 깨끗한 인스턴스를 보장해줌.
- Github Plan에서의 무료 분을 사용하고, 무료 분이 초과된 경우 분당 요금을 책정.

Self-host runner:

- 자동으로 runner 애플리케이션 업데이트를 수행할 수도 있고, 비활성화할 수도 있음.
- 운영체제 및 다른 소프트웨어의 업데이트는 사용자에게 책임이 있음.
- 클라우드 서비스나 사용자가 이미 지불하는 로컬 머신을 사용할 수 있음.
- 하드웨어, 운영 체제, 소프트웨어 및 보안 요구 사항에 맞게 사용자 정의 가능.
- 각 작업 실행을 위한 깨끗한 인스턴스를 보장하지 않음.
- Github Actions에서 무료로 사용 가능, Runner를 실행하는 머신의 유지 비용만 사용자가 따로 지불.

### Self-hosted runner 설정 방법

1. Github Actions을 사용하고자 하는 저장소에서 Settings - Actions - Runners로 이동.

<img width="1050" alt="Screenshot 2024-06-17 at 3 04 33 AM" src="https://github.com/10000-Bagger/free-topic-study/assets/34956359/92298b57-d78e-45b0-9495-57d28803c8d6">
    
2. 설정하고자 하는 로컬 머신에 해당되는 OS를 선택
    - OS 별로 설정하는 방법은 Download, Configure 내용을 따라 하면 됨.

<img width="706" alt="Screenshot 2024-06-17 at 3 24 29 AM" src="https://github.com/10000-Bagger/free-topic-study/assets/34956359/a6cb14ee-9fdd-474a-b6b5-def4c1d54735">

3. repository의 workflows 디렉토리 안에서 yaml 파일 생성 시 아래와 같이 설정을 추가하면 self-hosted runner로 실행이 됨.

<img width="696" alt="Screenshot 2024-06-17 at 3 25 53 AM" src="https://github.com/10000-Bagger/free-topic-study/assets/34956359/b9d3997d-83ad-4b74-8c83-034373eaef57">

