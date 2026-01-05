# -*- coding: utf-8 -*-
import logging
import os

def get_logger(logger_name, log_file_path, stream_level=logging.INFO, file_level=logging.DEBUG):
    """
    지정된 이름과 경로로 로거(Logger)를 생성하고 설정합니다.

    이 함수는 두 개의 핸들러를 가진 로거를 반환합니다:
    1. StreamHandler: 콘솔에 로그를 출력합니다.
    2. FileHandler: 지정된 파일에 로그를 기록합니다.

    :param logger_name: 로거의 이름 (일반적으로 __name__ 사용)
    :type logger_name: str
    :param log_file_path: 로그를 저장할 파일의 전체 경로
    :type log_file_path: str
    :param stream_level: 콘솔에 출력할 최소 로그 레벨 (기본값: logging.INFO)
    :type stream_level: int
    :param file_level: 파일에 기록할 최소 로그 레벨 (기본값: logging.DEBUG)
    :type file_level: int
    :return: 설정이 완료된 로거 객체
    :rtype: logging.Logger
    """
    # 1. 로거 생성 및 레벨 설정
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # 로거 자체는 가장 낮은 레벨(DEBUG)부터 모든 메시지를 받도록 설정
    logger.propagate = False # 상위 로거로 메시지가 전파되지 않도록 방지

    # 2. 핸들러 중복 추가 방지 (리로드 시 중요)
    if logger.hasHandlers():
        logger.handlers.clear()

    # 3. 포매터 생성
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 4. 스트림 핸들러 (콘솔 출력용) 설정
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(stream_level)
    logger.addHandler(stream_handler)

    # 5. 파일 핸들러 (파일 저장용) 설정
    # 로그 파일이 저장될 디렉토리가 없으면 생성
    log_dir = os.path.dirname(log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(file_level)
    logger.addHandler(file_handler)

    return logger
