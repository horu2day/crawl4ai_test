import asyncio
import re
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse
from crawl4ai import AsyncWebCrawler


async def fetch_and_save_markdown(crawler, url, output_dir):
    """
    웹 페이지를 가져와서 markdown 파일로 저장하는 비동기 함수입니다.
    """
    try:
        result = await crawler.arun(url=url)
        if result and result.markdown:
            # 파일명 생성 (URL에서 유효하지 않은 문자 제거)
            parsed_url = urlparse(url)

            # URL 경로를 올바르게 처리하여 파일 이름 생성
            file_path_parts = parsed_url.path.strip("/").split("/")
            file_name = "_".join(file_path_parts)
            if not file_name:
                file_name = "index"  # 경로가 없는 경우
            file_name = parsed_url.netloc + "_" + file_name + ".md"

            file_path = Path(output_dir) / file_name

            # 파일 저장
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result.markdown)
            print(f"Saved: {url} to {file_path}")
        else:
            print(f"Failed to fetch or no markdown content: {url}")

    except Exception as e:
        print(f"Error fetching or saving {url}: {e}")


async def crawl(start_url, output_dir, crawler):
    """
    웹사이트를 크롤링하고 결과를 markdown 파일로 저장하는 비동기 함수입니다.
    """

    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)

    visited_urls = set()
    urls_to_visit = {start_url}  # 중복 체크용 set으로 변경

    while urls_to_visit:
        current_url = urls_to_visit.pop()

        if current_url in visited_urls:
            continue
        visited_urls.add(current_url)

        print(f"Crawling: {current_url}")

        # 현재 페이지를 markdown 파일로 저장
        await fetch_and_save_markdown(crawler, current_url, output_dir)

        # 현재 페이지에서 링크 추출
        try:
            result = await crawler.arun(url=current_url)
            if result and result.markdown:
                # 개선된 링크 추출 정규식 (상대 경로 및 절대 경로 추출)
                link_pattern = r'<a[^>]*href="([^"]*)"'
                links = re.findall(link_pattern, result.markdown)

                for link in links:
                    # /docs/ 중복 제거
                    if "/docs/" in link and link.count("/docs/") > 1:
                        link = link.replace("/docs/", "/").replace("/docs", "")

                   # 링크가 https:// 로 시작하는 경우 처리
                    if link.startswith("https://"):
                        full_link = link
                    # 상대 경로 처리
                    else:
                        full_link = urljoin(current_url, link)

                    parsed_link = urlparse(full_link)
                    # 같은 도메인인지 확인
                    if parsed_link.netloc == urlparse(start_url).netloc and parsed_link.scheme in ["http", "https"]:
                        urls_to_visit.add(full_link)
        except Exception as e:
            print(f"Error extracting links from {current_url}: {e}")


async def main():
    """
    메인 비동기 함수입니다.
    """
    start_url = "https://github.com/supabase/supabase-py"  # 시작 URL 설정
    output_dir = "output_markdowns"  # 출력 디렉토리 설정

    async with AsyncWebCrawler(verbose=True) as crawler:
        await crawl(start_url, output_dir, crawler)

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
