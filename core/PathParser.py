import pathlib
import re
import subprocess
import platform

class PathParser:
    """
    VFX 파이프라인 경로 분석을 위한 베이스 클래스.
    경로 문자열을 입력받아 프로젝트, 태스크, 버전 등의 정보를 추출합니다.
    parts의 인덱스를 숫자로 했는데 나중에 템플릿 변경하거나 Lucidity 로 변경해보기.
    """

    def __init__(self, path_string):
        """
        인스턴스 초기화 및 기본 경로 정보 추출.
        
        Args:
            path_string (str): 분석할 파일의 전체 경로
        """
        self.path = pathlib.Path(path_string)
        self.parts = self.path.parts

        # 기본 경로 속성
        self.filename = self.path.name
        self.stem = self.path.stem
        self.ext = self.path.suffix

        # 경로 구조 분석 (인덱스 기반)
        # 주의: 폴더 구조가 변경될 경우 아래 인덱스를 수정해야 합니다.
        try:
            self.project = self.parts[2] if len(self.parts) > 2 else None
            self.task = self.parts[-4] if len(self.parts) > 3 else None
            self.status = self.parts[-3] if len(self.parts) > 2 else None
            self.dcc = self.parts[-2] if len(self.parts) > 1 else None
        except IndexError:
            self.project = self.task = self.status = self.dcc = None

        self.version = self._extract_version()

    @classmethod
    def create(cls, path_string):
        """
        경로 키워드를 분석하여 AssetPath 또는 ShotPath 인스턴스를 자동으로 생성합니다.
        
        Returns:
            PathParser|AssetPath|ShotPath: 경로 유형에 맞는 객체
        """
        if "/assets/" in path_string:
            return AssetPath(path_string)
        elif "/shots/" in path_string:
            return ShotPath(path_string)
        return cls(path_string)

    def _extract_version(self):
        """파일명에서 '_v001' 형식의 패턴을 찾아 정수형 버전을 반환합니다."""
        version_pattern = r'_v(\d+)'
        current_version = re.search(version_pattern, self.filename)
        return int(current_version.group(1)) if current_version else None

    def open_folder(self):
        """파일이 위치한 폴더를 운영체제별 탐색기에서 엽니다. (Windows는 파일 선택 상태)"""
        folder_path = self.path.parent
        if not folder_path.exists():
            print(f"ERROR: Directory does not exist: {folder_path}")
            return

        current_os = platform.system()
        if current_os == "Linux":
            subprocess.Popen(['caja', str(folder_path)])
        elif current_os == "Windows":
            # explorer /select 옵션으로 파일 하이라이트 실행
            subprocess.Popen(['explorer', '/select,', str(self.path)])

    def get_version_str(self):
        """정수형 버전을 'v001' 형태의 문자열로 반환합니다. 버전이 없으면 'v000' 반환."""
        if self.version is None:
            return "v000"
        return f"v{self.version:03d}"


class AssetPath(PathParser):
    """에셋 경로 전용 파서 클래스 (예: .../assets/prop/bag/...)"""
    
    def __init__(self, path_string):
        super().__init__(path_string)
        try:
            self.asset_type = self.parts[4]
            self.asset_name = self.parts[5]
        except IndexError:
            self.asset_type = self.asset_name = None


class ShotPath(PathParser):
    """샷 경로 전용 파서 클래스 (예: .../shots/EP01/S01/0010/...)"""
    
    def __init__(self, path_string):
        super().__init__(path_string)
        try:
            self.episode = self.parts[4]
            self.sequence = self.parts[5]
            self.shot_name = self.parts[6]
        except IndexError:
            self.episode = self.sequence = self.shot_name = None