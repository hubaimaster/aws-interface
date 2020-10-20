

def safe_to_run_code():
    """
    코드가 서버에서 실행되도 안전한지 체크합니다.
    Lambda 에 업로드된 패키지지인 경우
    core.environment_flag 패키지가 존재하지 않습니다.
    따라서 Safe to run code 합니다.
    :return:
    """
    try:
        import core.environment_flag
        return False
    except Exception as _:
        return True
