"""parser 모듈의 설정 오류."""


class ParserConfigError(Exception):
    """설정 파일이나 모듈 이름이 잘못됐을 때 사용한다. CLI는 이 오류를 메시지만 출력하고 종료한다."""
