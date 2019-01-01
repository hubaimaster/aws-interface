# AWS-Interface

**AWS 인터페이스** 는 Amazon Web Services (AWS)에서 제공하는 IAM, DynamoDB, Lambda, API Gateway 등의 서비스를 추상화하여 손쉽게 사용할 수 있게 해주는 인터페이스입니다.

새로운 서비스를 제작할 때, 주로 확장성과 초기 투자 비용 사이의 trade-off를 고민하게 됩니다. 처음에는 EC2 인스턴스를 하나 파서 웹 프레임워크와 함께 서버 안에서 돌려도 되지만, 서비스가 커지면 AWS DynamoDB와 같은 서비스를 고려해야 합니다. 사실 DynamoDB도 확장성 좋고 쓰기 쉬운 서비스라고 만들었겠지만, 정작 능숙하게 다룰줄 아는 개발자가 몇명이나 될까요?

AWS 인터페이스는 이런 문제를 해결하기 위해서 레시피 (Recipe)라는 추상적인 개념으로 DB를 구성할 수 있도록 합니다. 레시피를 작성하면 실제 백엔드를 담당하는 AWS 등의 IaaS 서비스가 자동으로 구성되고 이와 손쉽게 통신할 수 있는 플랫폼별 SDK가 만들어집니다. DB를 관리할 수 있는 대시보드 또한 AWS 인터페이스에서 제공됩니다.

## 서비스 구성 (사용자 입장)

### Recipe (레시피)
서비스하고자 하는 앱의 백엔드 및 DB 단에 들어갈 요소를 설정하는 단위입니다.

### Sauce (소스)
레시피를 구성하는 요소로, 서비스에서 제공할 추상화된 기능을 말합니다. 초기에는 4가지 소스를 지원할 예정입니다.

- Auth: 로그인 및 사용자 인증
- Database: 각종 데이터
- Push: 앱 및 웹 푸시 알림
- Email: 이메일 알림

### Dashboard (대시보드)
레시피를 구성하고, DB를 관리할 수 있는 웹 인터페이스를 대시보드라고 부릅니다. aws-interface.com에서  IAM 정보를 입력해서 계정을 만들거나 로컬에서 호스팅된 대시보드에 IAM 정보를 등록한 후에 이용 가능합니다. 웹 인터페이스는 Django 프레임워크를 기반으로 합니다.

### Backend (백엔드)
실제 뒷단에서 사용하는 IaaS 서비스를 말합니다. 현재는 AWS 백엔드만 제공하지만 향후에는 Google Cloud Platform, Naver Cloud Platform, 테스트용 Local Deployment 등을 추가적으로 지원할 예정입니다.

### Client SDK
레시피를 기반으로 자동으로 구성된 백엔드를 클라이언트 앱에서 접근하기 위한 SDK를 말합니다. SDK는 Python, Swift, Java 등 다양한 플랫폼에서 지원하는 언어로 자동 생성됩니다.

## 서비스 설계 (개발자 입장)

### Recipe, Sauce Abstract Class
상술한 바와 같이 Sauce는 서비스에서 제공할 추상화된 기능을 말합니다. 기능에 따라 소스 추상 클래스를 상속한 AuthSauce, DatabaseSauce 등이 구현됩니다. Recipe는 이러한 소스를 담고 있는 컨테이너 클래스로, 특정 서비스의 백엔드/DB 구조를 담는 객체라고 볼 수 있습니다.

### ServiceController Class
레시피에 명시된 바에 따라 Backend (뒷단의 IaaS 서비스)를 조작하는 컨트롤러입니다. 예컨대, AuthSauce가 담긴 Recipe를 ServiceController (이하 sc)에서 apply시키면, AWS DynamoDB 상에서 관련 테이블이 만들어지고 그것을 조작할 수 있는 Lambda 함수와 API Gateway 설정이 만들어집니다. Client SDK 또한 sc에서 생성됩니다. 관리자로서 서비스를 관리하는 기능 또한 sc에서 제공됩니다. 예컨대 Auth 소스가 들어간 서비스의 경우, sc를 통해 현재 접속한 사용자를 확인하는 등의 기능이 제공됩니다.

### AWS 상세 구현
대시보드에서 레시피를 설정하고 deploy하면 AWS 내의 DynamoDB와 API Gateway가 자동으로 설정되고, DB 내에 적절한 테이블이 생성됩니다. 이때 어댑터는 API Gateway와 http 방식으로 통신을 하게 됩니다.

예를 들어, 아래는 Auth 소스가 들어간 레시피가 실제 구현되는 과정입니다.

1. (사용자) AWS IAM 인증 정보를 AWS 인터페이스에 등록합니다.
2. (사용자) 레시피에 Auth 소스를 추가하고 레시피를 deploy합니다.
3. (AWS 인터페이스) DynamoDB에서 단일 테이블을 만들고 그 안에 사용자 모델을 빌드합니다. 
4. (AWS 인터페이스) 모델들을 읽고 쓸 수 있는 Lambda 함수를 작성합니다.
5. (AWS 인터페이스) 작성된 Lambda 함수를 외부에서 이용할 수 있게 API Gateway로 배포합니다.
6. (AWS 인터페이스) API Gateway에 배포한 API에 접근할 수 있는 SDK를 Java, Python, Swift 등으로 자동 생성합니다.
7. (사용자) 자동 생성된 SDK를 클라이언트 앱에서 불러와서 AWS 리소스와 통신합니다.

## 환경 설정

### Python 버젼 및 라이브러리

AWS 인터페이스는 Python 3.6에서 작성되었습니다. 

Python 모듈 설치는 프로젝트 단위로 독립적으로 하시면 좋아요! 요런걸 주로 virtual environment라고 부르는데, 방법은 정말 [다양](https://stackoverflow.com/questions/41573587/what-is-the-difference-between-venv-pyvenv-pyenv-virtualenv-virtualenvwrappe)합니다.

아래는 Python 3에서 제공하는 공식 패키지인 venv를 사용하는 방식입니다.

```bash
# Ubuntu 등에서 Python 설치
sudo apt update
sudo apt install python3
sudo apt install python3-venv
```

```
python3 -m venv venv
source venv/bin/activate  # virtual environment 작동
pip install -r requirements.txt  # 패키지 설치
# deactivate 이거는 virtual environment 해제
```

#### AWS EC2 (Ubuntu) 사용자를 위한 Python 버전 팁
Ubuntu 16.04에서 apt로 받을 수 있는 기본 Python3 버전은 3.5입니다. 다른 방식으로 Python 버전을 올릴 수는 있지만, 처음부터 EC2 인스턴스를 Ubuntu 18.04로 만드는 것을 추천드립니다.

### IAM 계정
AWS 인터페이스를 이용하기 위해서는 AWS 계정에 접속할 수 있는 관리자 권한이 필요합니다. 대시보드에 접근하기 위해서는 AWS 계정 내에서 관리자 권한을 가진 IAM User의 Access Key와 Secret Access Key를 입력해야 합니다.

#### 참고
- [AWS 계정 생성](https://aws.amazon.com/ko/premiumsupport/knowledge-center/create-and-activate-aws-account/)
- [IAM 계정 생성](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/id_users_create.html)

## 빠른 실행
다음 명령어를 이용해서 로컬 대시보드 서버를 호스팅하여 테스트해보실 수 있습니다.
```
# activate virtual environment
cd aws_interface
python3 manage.py migrate
python3 manage.py runserver
# open 127.0.0.1:8000 on your browser
```

## Contribution 가이드라인

버그 리포팅과 피드백을 받기 위해 [깃허브 이슈](https://github.com/hubaimaster/AWSInterface/issues)를 사용하고 있습니다.

- 클라이언트 SDK 자동 생성 언어 확장 관련 Contribution 환영합니다.
- AWSInterface 프로젝트는 Apache 2.0 라이센스를 따릅니다.
