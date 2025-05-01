import os
from pathlib import Path

# 현재 파일의 절대 경로
current_file = Path(__file__).resolve()

# 프로젝트 루트 디렉토리 (src 파일의 부모 디렉토리)
PROJECT_ROOT = current_file.parent.parent

# 출력 디렉토리
OUTPUT_DIR = PROJECT_ROOT / "output"

# 기타 필요한 경로 설정
OUTLINE_PATH = OUTPUT_DIR / "outline.json"
GUIDE_PATH = OUTPUT_DIR / "guide.md"

# 경로가 존재하지 않으면 생성
if not OUTPUT_DIR.exists():
    os.makedirs(OUTPUT_DIR)
