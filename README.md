# aws-interface

**aws-interface** 는 AWS(아마존웹서비스) 내의 IAM, DynamoDB, Lambda, API Gateway 등의 서비스들을 한번에 묶어
손쉽게 사용할 수 있게 해주는 인터페이스입니다. aws-interface 가 작동하는 단계는 다음과 같습니다.
1. aws-interface 의 view 로부터어플리케이션 모델 정보를 입력받습니다. 
2. 입력 받은 정보로부터 DynamoDB 에서 단일 테이블을 만들고 그 안에 사용자 모델을 빌드합니다. 
3. 이어서 사용자 모델들을 읽고 쓸 수 있는 Lambda 함수를 작성합니다.
4. 작성된 Lambda 함수를 외부에서 이용할 수 있게 API Gateway 로 배포합니다.
5. 추가적으로 API Gateway에서 배포된 API에 접근할 수 있는 SDK를 Java, Python, Swift 등의 언어로 자동 생성하여 빌드합니다.
6. 사용자는 클라이언트 어플리케이션에 자동 생성된 SDK를 임포트하여 AWS 리소스를 이용합니다.

이 6가지 단계는 aws-interface에 의해 자동으로 실행되고, 결과적으로 사용자는 AWS의 서비스의 작동방식을 이해하지 못해도 aws-interface를 통해 어플리케이션 서비스 모델을 손쉽게 구현할 수 있습니다.


## 실행방법
*aws-interface는 Python 3.6 환경에서 작성되었습니다. 따라서 Python 3.x 환경에서 실행하는것을 권장합니다*

**AWS 기본 설정**
* AWS 리소스를 이용하기위해선 AWS 계정에 접속할 수 있는 관리자권한이 필요합니다. 계정이 없으시다면 [AWS 계정 만들기](https://aws.amazon.com/ko/premiumsupport/knowledge-center/create-and-activate-aws-account/)를 참조하세요.
[IAM 사용자 생성](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/id_users_create.html) 후 IAM User의 Access Key 와 Secret Access Key 를 기록해둡니다.


**종속성 라이브러리 설치**
* 다음은 콘솔창에서 AWSInterface 가 의존하고 있는 라이브러리를 설치하는 방법입니다. 
* 명령을 실행하기전 requirements.txt 파일이 있는 AWSInterface 루트 폴더로 이동해주세요. ```cd aws-interface```
```shell
$ pip install -r requirements.txt
```


**aws-interface 실행**
* 아래 명령을 실행하여 aws-interface 를 사용자가 로컬 호스트 혹은 외부에서 특정 포트로 접근할 수 있도록 합니다.
* python run.py "port"
```shell
$ python run.py 80
```

**aws-interface 접속**
* 위의 과정을 거쳐 로컬 컴퓨터 브라우저 주소창에 localhost 를 입력하여 
aws-interface 를 사용할 수 있습니다.
* 이전 단계에서 기록 해놓은 Access Key와 Secret Key를 이용하여 로그인할 수 있습니다.

## Contribution 가이드라인

**버그리포팅과 피드백을 받기 위해 [깃허브 이슈](https://github.com/hubaimaster/aws-interface/issues)를 사용하고 있습니다.**
* 클라이언트 SDK 자동 생성 언어 확장 관련 Contribution 환영합니다.
* aws-interface 프로젝트는 Apache 2.0 라이센스를 따릅니다.
