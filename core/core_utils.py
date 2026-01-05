# -*- coding: utf-8 -*-
import configparser
import os

def get_config_value(config_path, section, option, fallback=None):
    """
    .config 또는 .ini 파일에서 특정 설정 값을 읽어옵니다.

    :param config_path: 설정 파일의 전체 경로
    :param section: 값을 가져올 섹션 이름
    :param option: 값을 가져올 옵션(키) 이름
    :param fallback: 값을 찾지 못했을 때 반환할 기본값
    :return: 설정 값 또는 fallback 값
    :rtype: str or None
    """
    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        return fallback
    
    config.read(config_path)
    return config.get(section, option, fallback=fallback)
