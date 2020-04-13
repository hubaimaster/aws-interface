import sys
import os

# cloud.libs 폴더 안에서는 cloud.libs 위치 기준으로 라이브러리 import 할 수 있게 sys.path 추가
path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path)

