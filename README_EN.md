![Language](https://img.shields.io/badge/Language-Python3.6-blue.svg)
![Language](https://img.shields.io/badge/NaverFest-Finalist-brightgreen.svg)

**[WE R Naver D2 Fest Finalists!](https://github.com/D2CampusFest/6th)**

# AWS-Interface

AWS-Interface lets you jump start your next big idea with a powerful and flexible backend. Configure a scalable backend for your service within minutes through a simple web interface. All services are based on AWS's powerful services including IAM, DynamoDB, Lambda, API Gateway etc.

Amazon's web services were meant to be easy and simple—but they're simply not ☹️. There are often too many services for us mere mortals to track. With AWS Interface, we take away the nitty-gritty and let you focus on your ideas and your business.

Here's how it works: register your AWS IAM credentials for us to work with. Then, select the Recipes that you need for your backend service and tweak them through our website. That's it! We've built an infinitely scalable backend for your service via AWS services, and an auto-generated SDK for the frontend platform of your choice.\


## How To Use AWS Interface?

### Recipe

서비스하고자 하는 앱의 백엔드 및 DB 단에 들어갈 요소를 설정하는 단위입니다. 서비스에 추가할 추상화된 기능이라고 생각할 수 있습니다. 초기에는 5가지 레시피를 지원할 예정입니다.

- Bill: 백엔드 요금 사용 내역 확인
- Auth: 로그인 및 사용자 인증
- Database: 각종 데이터
- Storage: 파일 저장 및 배포
- Logic : 서버리스 API 코드 생성 및 배포

### Dashboard (대시보드)
레시피를 구성하고, DB를 관리할 수 있는 웹 인터페이스를 대시보드라고 부릅니다. [aws-interface.com](http://aws-interface.com) 에서  IAM 정보를 입력해서 계정을 만들거나 로컬에서 호스팅된 대시보드에 IAM 정보를 등록한 후에 이용 가능합니다. 웹 인터페이스는 Django 프레임워크를 기반으로 합니다.

### Backend (백엔드)
실제 뒷단에서 사용하는 IaaS 서비스를 말합니다. 현재는 AWS 백엔드만 제공하지만 향후에는 Google Cloud Platform, Naver Cloud Platform, 테스트용 Local Deployment 등을 추가적으로 지원할 예정입니다.

### Client SDK
레시피를 기반으로 자동으로 구성된 백엔드를 클라이언트 앱에서 접근하기 위한 SDK를 말합니다. SDK는 Python, Swift, Java 등 다양한 플랫폼에서 지원하는 언어로 자동 생성됩니다.

## 서비스 설계 (개발자 입장)

### RecipeController Abstract Class
상술한 바와 같이 Recipe는 서비스에서 제공할 추상화된 기능을 말합니다. 기능에 따라 소스 추상 클래스를 상속한 AuthRecipeController, DatabaseRecipeController 등이 구현됩니다. RecipeController 클래스는 이러한 기능들을 구성하는 설정을 담은 dictionary 를 조작하는 역할을 하는 것으로 생각할 수 있습니다. 예컨대 로그인 및 사용자 관리를 담당하는 AuthRecipeController 에서는 사용자 그룹, 비밀번호 규칙 등을 설정할 수 있습니다.

### ServiceController Abstract Class
레시피에 명시된 바에 따라 Backend (뒷단의 IaaS 서비스)를 조작하는 컨트롤러입니다. 예컨대, AuthSauce가 담긴 Recipe를 ServiceController (이하 SC)에서 apply시키면, AWS DynamoDB 상에서 관련 테이블이 만들어지고 그것을 조작할 수 있는 Lambda 함수와 API Gateway 설정이 만들어집니다. Client SDK 생성 및 관리자 기능 또한 SC에서 제공됩니다. 예컨대 AuthSC에서는 현재 접속한 사용자를 확인하는 등의 기능이 제공됩니다. SC도 Recipe와 마찬가지로 AuthSC, DatabaseSC 등으로 상속되어 구현됩니다.

### Django
장고 웹 인터페이스 단에서는 위의 core 클래스들을 import해서 필요한 함수를 호출하는 방식으로 구현됩니다.

### AWS 상세 구현
대시보드에서 레시피를 설정하고 deploy하면 AWS 내의 DynamoDB와 API Gateway가 자동으로 설정되고, DB 내에 적절한 테이블이 생성됩니다. 이어 자동으로 생성된 SDK 는 API Gateway와 http 방식으로 통신을 하게 됩니다.

예를 들어, 아래는 Auth 레시피가 실제 구현되는 과정입니다.

1. (사용자) AWS IAM 인증 정보를 AWS 인터페이스에 등록합니다.
2. (사용자) Auth 레시피를 구성하고 deploy합니다.
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

### Git Commit 메시지
Commit 메시지는 [다음과 같은 형식](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)으로 해주세요. Reddit 유저 왈, "the defacto standard".

```
Capitalized, short (50 chars or less) summary

More detailed explanatory text, if necessary.  Wrap it to about 72
characters or so.  In some contexts, the first line is treated as the
subject of an email and the rest of the text as the body.  The blank
line separating the summary from the body is critical (unless you omit
the body entirely); tools like rebase can get confused if you run the
two together.

Write your commit message in the imperative: "Fix bug" and not "Fixed bug"
or "Fixes bug."  This convention matches up with commit messages generated
by commands like git merge and git revert.

Further paragraphs come after blank lines.

- Bullet points are okay, too

- Typically a hyphen or asterisk is used for the bullet, followed by a
  single space, with blank lines in between, but conventions vary here

- Use a hanging indent
```
