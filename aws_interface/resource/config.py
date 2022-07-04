
MAX_N_GRAM = 3  # 1~MAX_N_GRAM 까지 N Gram 인덱스를 생성
SK_DIGIT_FIT = 40  # sort key 의 자리 맞춤 총 문자열 개수임.
SK_FLOAT_DEC_FIT = 16  # SK_DIGIT_FIT 에서 소숫점 자리가 차지하는 부분, 데시멀 (10진수)임

# base64 'z' * SK_DIGIT_FIT 로 표현할 수 있는 최대 범위 // 2
HALF_REP_NUMBER_B64 = 883423532389192164791648750371459257913741948437809479060803100646309887
MAX_REP_NUMBER_B64 = HALF_REP_NUMBER_B64 * 2

# 숫자를 base64 형태로 변환하여 표현
BASE64_LETTERS = "+/0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

STR_META_INFO_PARTITION = 'meta-info#partition'


if __name__ == '__main__':
    BASE64_LETTERS = sorted(BASE64_LETTERS)
    print(''.join(BASE64_LETTERS))