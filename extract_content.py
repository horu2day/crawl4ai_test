import re
import os
from pathlib import Path


def extract_main_content(markdown_file):
    """
    Obsidian Publish 마크다운 파일에서 본문만 추출합니다.
    앞쪽의 네비게이션 링크와 뒤쪽의 메타데이터를 제거합니다.
    """
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 본문 시작을 찾기: 첫 번째 # 헤더가 나타나는 위치
    # (네비게이션 링크 다음에 본문 제목이 나옴)
    lines = content.split('\n')

    start_idx = 0
    end_idx = len(lines)

    # 본문 시작 찾기: 첫 번째 실질적인 # 헤더
    for i, line in enumerate(lines):
        # # 으로 시작하는 실제 제목 라인 찾기 (링크가 아닌)
        if line.strip().startswith('#') and not line.startswith('['):
            start_idx = i
            break

    # 본문 끝 찾기: "Links to this page" 섹션부터 모두 제거
    for i in range(start_idx, len(lines)):
        line = lines[i].strip()
        if line == "Links to this page":
            end_idx = i
            break

    # 본문만 추출
    main_content = '\n'.join(lines[start_idx:end_idx])

    # 불필요한 빈 줄 정리
    main_content = re.sub(r'\n{3,}', '\n\n', main_content)

    return main_content.strip()


def process_all_files(input_dir, output_dir):
    """
    입력 디렉토리의 모든 마크다운 파일을 처리하여 본문만 추출합니다.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Obsidian 파일만 처리 (로컬 HTML 파일 제외)
    md_files = [f for f in input_path.glob("*.md")
                if "publish.obsidian.md" in f.name]

    for md_file in md_files:
        print(f"Processing: {md_file.name}")

        try:
            # 본문 추출
            main_content = extract_main_content(md_file)

            # 출력 파일명 (간소화)
            output_file = output_path / f"clean_{md_file.name}"

            # 저장
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(main_content)

            print(f"  [OK] Saved to: {output_file.name}")
            print(f"    Original: {os.path.getsize(md_file)} bytes")
            print(f"    Cleaned:  {os.path.getsize(output_file)} bytes")

        except Exception as e:
            print(f"  [ERROR] {e}")


if __name__ == "__main__":
    input_dir = "output_markdowns"
    output_dir = "output_markdowns/cleaned"

    print("=" * 60)
    print("Obsidian Publish 본문 추출기")
    print("=" * 60)

    process_all_files(input_dir, output_dir)

    print("\n완료!")
