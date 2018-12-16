# AWSInterface
**AWSInterface** 는 AWS(아마존웹서비스) 내의 IAM, DynamoDB, Lambda, API Gateway 등의 서비스들을 추상화하여
손쉽게 사용할 수 있게 해주는 인터페이스입니다. AWSInterface 추상 서비스 'Auth' 가 작동하는 단계는 다음과 같습니다.
1. AWSInterface는 사용자로부터 추상 서비스 정보를 입력받습니다.
2. 입력 받은 정보로부터 DynamoDB 에서 단일 테이블을 만들고 그 안에 사용자 모델을 빌드합니다. 
3. 이어서 사용자 모델들을 읽고 쓸 수 있는 Lambda 함수를 작성합니다.
4. 작성된 Lambda 함수를 외부에서 이용할 수 있게 API Gateway 로 배포합니다.
5. 추가적으로 API Gateway에서 배포된 API에 접근할 수 있는 SDK를 Java, Python, Swift 등의 언어로 자동 생성하여 빌드합니다.
6. 사용자는 클라이언트 어플리케이션에 자동 생성된 SDK를 임포트하여 AWS 리소스를 이용합니다.

이 6가지 단계는 AWSInterface에 의해 자동으로 실행되고, 결과적으로 사용자는 AWS의 서비스의 작동방식을 이해하지 못해도 AWSInterface를 통해 사용자 인증 서비스를 손쉽게 구현할 수 있습니다.

AWS Interface 에서 제공하는 추상서비스 목록. (2018.12.15)
1. Auth
2. Database
3. Push
4. Email
5. SDK Generater

## 실행방법
*AWSInterface는 Python 3.6 환경에서 작성되었습니다. 따라서 Python 3.x 환경에서 실행하는것을 권장합니다*

**요구사항**
* AWS Interface 를 이용하기위해선 AWS 계정에 접속할 수 있는 관리자권한이 필요합니다. 계정이 없다면 [AWS 계정 만들기](https://aws.amazon.com/ko/premiumsupport/knowledge-center/create-and-activate-aws-account/)를 참조하세요.
[IAM 사용자 생성](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/id_users_create.html) 후 IAM User의 Access Key 와 Secret Access Key 를 기록해둡니다.


**종속성 라이브러리 설치**
* 다음은 콘솔창에서 AWSInterface 가 의존하고 있는 라이브러리를 설치하는 방법입니다. 
* 명령을 실행하기전 requirements.txt 파일이 있는 AWSInterface 루트 폴더로 이동해주세요. ```cd AWSInterface```
```shell
$ pip install -r requirements.txt
```

## Contribution 가이드라인

**버그리포팅과 피드백을 받기 위해 [깃허브 이슈](https://github.com/hubaimaster/AWSInterface/issues)를 사용하고 있습니다.**
* 클라이언트 SDK 자동 생성 언어 확장 관련 Contribution 환영합니다.
* AWSInterface 프로젝트는 Apache 2.0 라이센스를 따릅니다.
