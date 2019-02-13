![Language](https://img.shields.io/badge/Language-Python3.6-blue.svg)
![Language](https://img.shields.io/badge/NaverFest-Finalist-brightgreen.svg)

**[WE R Naver D2 Fest Finalists!](https://github.com/D2CampusFest/6th)**

# AWS-Interface

AWS-Interface lets you jump start your next big idea with a powerful and flexible backend. Amazon's web services were meant to be easy and simple—but they're simply not ☹️. There are often too many services for us mere mortals to track. With AWS Interface, we take away the nitty-gritty and let you focus on your ideas and your business.

Here's how it works: register your AWS IAM credentials for us to work with. Then, select the Recipes that you need for your backend service and tweak them through our website. That's it! We've built an infinitely scalable backend for your service via AWS services, and an auto-generated SDK for the frontend platform of your choice.\


## For Users

### Recipe

This is an abstraction of backend/DB components for you to use in your service. We will support these five recipes when we first kick off AWS Interface.

- **Bill**: Billing for your internal AWS account 
- **Auth**: Login/authentication of users
- **Database**: General-purpose *database stuff*
- **Storage**: File storage and distribution
- **Logic** : Deployment of server-less (state-less) logic

### Dashboard

This is where you can configure and manage your Recipes/internal database. You can access your dashboard via [aws-interface.com](http://aws-interface.com) or host your own dashboard on your local server. Make sure to register your AWS IAM credentials to start using AWS Interface. The Dashboard is currently build on the Django framework.
A
### Backend

The Backend refers to the AWS services that actually serve your Recipes. Currently, the Backend consists of AWS services such as DynamoDB, Lambda, API Gateways etc (which you don't need to care about). We plan do to support other Backends like Google Cloud Platform or Naver Cloud Platform (which you might care about). *Not for now*.

### Client SDK

You can use the auto-generated client SDK's within your client apps to communicate with the Backend. Client SDK's can be generated in the language or platform of your choice. We currently plan to support Python, Swift and Java.


## For Contributors

### RecipeController Abstract Class

You can think of Recipes as abstract features for your backend. Each abstract feature is implemented via a concrete child of RecipeController, such as the AuthRecipeController and DatabaseRecipeController. The main role of the RecipeController is to manage the dictionary that stores configuration info for each abstract feature. For example, the AuthRecipeController provides an interface to control user groups and password rules.

### ServiceController Abstract Class

The main role of the ServiceController is to configure the Backend (your AWS services) according to the provided Recipes. For example, when you apply your AuthRecipe, the AuthServiceController will create a table in AWS DynamoDB, and create the required interfaces via AWS Lambda and API Gateway.

The ServiceController also serves as an admin interface for your backend and also serves as the SDK generator. For example, the AuthServiceController allows you to manage your users, check who is online, etc.

### Dashboard

The dashboard provides a web interface based on Django. The dashboard communicates with the above core classes by via imports.


## Environment

### Python Version & Libraries

AWS Interface uses Python version 3.6.

When installing Python libraries, we recommend that you use a virtual environment [of your choice](https://stackoverflow.com/questions/41573587/what-is-the-difference-between-venv-pyvenv-pyenv-virtualenv-virtualenvwrappe).

This is how you use the venv module provided by Python 3.5+.

```bash
# Install Python on Linux Debian
sudo apt update
sudo apt install python3
sudo apt install python3-venv
```

```
python3 -m venv venv
source venv/bin/activate  # activate virtual environment
pip install -r requirements.txt  # install packages
# deactivate  # deactivate virtual environment
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
