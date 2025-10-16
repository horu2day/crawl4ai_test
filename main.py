import asyncio
import re
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode


def extract_main_content(markdown_content):
    """
    마크다운 콘텐츠에서 본문만 추출 (네비게이션 링크 제거)
    """
    lines = markdown_content.split('\n')
    start_idx = 0
    end_idx = len(lines)

    # 본문 시작 찾기: 첫 번째 # 헤더
    for i, line in enumerate(lines):
        if line.strip().startswith('#') and not line.startswith('['):
            start_idx = i
            break

    # 본문 끝 찾기: "Links to this page" 섹션
    for i in range(start_idx, len(lines)):
        if lines[i].strip() == "Links to this page":
            end_idx = i
            break

    # 본문만 추출
    main_content = '\n'.join(lines[start_idx:end_idx])

    # 불필요한 빈 줄 정리
    main_content = re.sub(r'\n{3,}', '\n\n', main_content)

    return main_content.strip()


async def fetch_and_save_markdown(crawler, url, output_dir, save_clean=True):
    """
    웹 페이지를 크롤링하여 markdown 파일로 저장

    Args:
        crawler: AsyncWebCrawler 인스턴스
        url: 크롤링할 URL
        output_dir: 출력 디렉토리
        save_clean: True면 원본과 본문만 추출한 파일 둘다 저장, False면 원본만 저장
    """
    try:
        # 로컬 파일인 경우와 웹 페이지 구분
        if url.startswith("file://"):
            result = await crawler.arun(url=url)
        else:
            # JavaScript 렌더링을 위한 크롤러 설정 (Obsidian Publish용)
            crawler_config = CrawlerRunConfig(
                wait_until="networkidle",
                wait_for="css:.published-container",
                delay_before_return_html=2.0,
                page_timeout=90000,
                cache_mode=CacheMode.BYPASS,
                js_code=["window.scrollTo(0, 100);", "window.scrollTo(0, 0);"]
            )
            result = await crawler.arun(url=url, config=crawler_config)

        if result and result.markdown:
            # 파일명 생성
            parsed_url = urlparse(url)

            if url.startswith("file://"):
                file_name = Path(parsed_url.path).stem + ".md"
            else:
                file_path_parts = parsed_url.path.strip("/").split("/")
                file_name = "_".join(file_path_parts)
                if not file_name:
                    file_name = "index"
                file_name = parsed_url.netloc + "_" + file_name + ".md"

            # 원본 저장
            file_path = Path(output_dir) / file_name
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result.markdown)
            print(f"[원본] {file_path}")

            # 본문만 추출하여 저장
            if save_clean and not url.startswith("file://"):
                clean_content = extract_main_content(result.markdown)
                clean_path = Path(output_dir) / f"clean_{file_name}"
                with open(clean_path, "w", encoding="utf-8") as f:
                    f.write(clean_content)
                print(f"[본문] {clean_path}")
        else:
            print(f"Failed: {url}")

    except Exception as e:
        print(f"Error: {url}: {e}")


async def crawl(start_url, output_dir, crawler, max_pages=5):
    """
    웹사이트를 크롤링하고 결과를 markdown 파일로 저장하는 비동기 함수입니다.
    """

    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)

    visited_urls = set()
    urls_to_visit = {start_url}  # 중복 체크용 set으로 변경

    while urls_to_visit and len(visited_urls) < max_pages:
        current_url = urls_to_visit.pop()

        if current_url in visited_urls:
            continue
        visited_urls.add(current_url)

        print(f"Crawling ({len(visited_urls)}/{max_pages}): {current_url}")

        # 현재 페이지를 markdown 파일로 저장
        await fetch_and_save_markdown(crawler, current_url, output_dir)

        # 최대 페이지 수에 도달하면 링크 추출 중단
        if len(visited_urls) >= max_pages:
            break

        # 현재 페이지에서 링크 추출
        try:
            # 로컬 파일과 웹 페이지 구분
            if current_url.startswith("file://"):
                result = await crawler.arun(url=current_url)
            else:
                crawler_config = CrawlerRunConfig(
                    wait_until="networkidle",
                    wait_for="css:.published-container",
                    delay_before_return_html=2.0,
                    page_timeout=90000,
                    cache_mode=CacheMode.BYPASS,
                    js_code=["window.scrollTo(0, 100);", "window.scrollTo(0, 0);"]
                )
                result = await crawler.arun(url=current_url, config=crawler_config)
            if result and result.html:
                # HTML에서 직접 href 링크 추출
                href_pattern = r'href="(https://publish\.obsidian\.md/followtheidea/Content/[^"]+)"'
                links = re.findall(href_pattern, result.html)

                # 중복 제거
                unique_links = list(set(links))
                print(f"Found {len(unique_links)} unique links")

                for link in unique_links[:10]:  # 처음 발견한 10개 링크만 추가
                    print(f"  Adding: {link}")
                    urls_to_visit.add(link)

        except Exception as e:
            print(f"Error extracting links from {current_url}: {e}")


async def main():
    """
    메인 비동기 함수입니다.
    """
    # 로컬 HTML 파일에서 시작하여 링크된 페이지 5개 크롤링
    start_url = "file://C:/Users/USER/Downloads/Content - follow the idea - Obsidian Publish.html"
    output_dir = "output_markdowns"  # 출력 디렉토리 설정

    # SPA용 브라우저 설정
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True,
        viewport_width=1280,
        viewport_height=1024,
        java_script_enabled=True
    )

    async with AsyncWebCrawler(config=browser_config, verbose=True) as crawler:
        await crawl(start_url, output_dir, crawler, max_pages=5)

if __name__ == "__main__":
    asyncio.run(main())

# import asyncio
# import re
# from crawl4ai import *

# async def main():
#     async with AsyncWebCrawler() as crawler:
#         result = await crawler.arun(
#             url="https://flet.dev/docs/",
#         )
#         print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
#         print(result.markdown)
#         print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


#     # async with AsyncYoutubeCrawler() as crawler:
#     #     result = await crawler.arun(
#     #         url="https://www.youtube.com/@namespaces/videos",
#     #     )
#     #     print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
#     #     print(result.markdown)
#     #     print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

#     #     # 정규 표현식을 사용하여 '/watch?v=...' 패턴 찾기
#     #     pattern = r"/watch\?v=[a-zA-Z0-9_-]+"
#     #     matches = re.findall(pattern, result.markdown)

#     #     # 찾은 패턴을 사용하여 전체 URL 생성
#     #     base_url = "https://www.youtube.com"
#     #     youtube_urls = [f"{base_url}{match}" for match in matches]

#     #     # 중복 제거 및 순서 유지
#     #     unique_urls = []
#     #     seen = set()
#     #     for url in youtube_urls:
#     #         if url not in seen:
#     #             unique_urls.append(url)
#     #             seen.add(url)

#     #     # 결과 출력
#     #     print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
#     #     print("YouTube URLs:")
#     #     for url in unique_urls:
#     #         print(url)
#     #     print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


# if __name__ == "__main__":
#     asyncio.run(main())
