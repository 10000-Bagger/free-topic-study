from collections import Counter
from datetime import datetime
import os


# def count_files():
#     files_info = []
#     total_file_count = 0
#     directory_list = [directory for directory in os.listdir("./") if "Folder" in directory]
#     for directory in directory_list:
#         file_list = os.listdir(f"./{directory}")
#         file_count = len(file_list)
#         temp = [directory, file_count]
#         files_info.append(temp)
#         total_file_count += file_count
#     return files_info, total_file_count

# def count_files():
#     files_info = []
#     total_file_count = 0
#     # "jin", "hong", "joon", "new", "woo" 중 하나라도 포함된 폴더 이름을 찾습니다.
#     directory_list = [directory for directory in os.listdir("./") if any(name in directory for name in ["jin", "hong", "joon", "new", "woo"])]
#     for directory in directory_list:
#         file_list = os.listdir(f"./{directory}")
#         file_count = len(file_list)
#         temp = [directory, file_count]
#         files_info.append(temp)
#         total_file_count += file_count
#     return files_info, total_file_count

def count_files_recursive(directory):
    total_file_count = 0
    # 현재 디렉토리의 내용을 나열합니다.
    for entry in os.scandir(directory):
        if entry.is_file():
            # 파일이면 카운트를 증가합니다.
            total_file_count += 1
        elif entry.is_dir():
            # 디렉토리(폴더)면 재귀적으로 이 함수를 호출합니다.
            total_file_count += count_files_recursive(entry.path)
    return total_file_count

def count_files():
    files_info = []
    directory_list = [directory for directory in os.listdir("./") if os.path.isdir(directory) and directory not in [".github", "utils"]]
    for directory in directory_list:
        file_count = count_files_recursive(f"./{directory}")
        temp = [directory, file_count]
        files_info.append(temp)
    return files_info, sum(info[1] for info in files_info)
  
  
def make_info(files_info, total_file_count):
    info = f"### 전체 아티클 갯수: {total_file_count}개 (자동 업데이트)"
    # for directory_files_info in files_info:
    #     temp = f"- {directory_files_info[0]}: {directory_files_info[1]}\n"
    #     info += temp
    return info
    
def make_read_me(info):
    return f"""# 자유 주제 스터디
{info}

<br>

### 진행 방식
- 각자 이름의 branch에서 각자 이름의 폴더에 공부 내용을 정리하여 한다.
- 일주일에 5번 main branch를 향하는 PR을 올린다.
  - 새벽 6시 전까지 올린 PR은 전날 올린 건으로 간주된다. (출근길 글 읽기를 위해)
- 매일 낮 12시 이전까지 스터디원이 올린 PR에 승인, 질문 등의 피드백을 남긴다.
- PR에 꼭 완성된 글을 올리지 않아도 된다.

<br>

### 누적 벌금 : 370,013 원
"""

#     return f"""# Self-Updating-Readme
# Push할 때마다 폴더 별 파일 수를 리드미에 자동으로 업데이트<br>
# Automatically update the number of files per folder to Readme whenever you push.<br><br>
# {info}
# """


def update_readme():
    files_info, total_file_count = count_files()
    info = make_info(files_info, total_file_count)
    readme = make_read_me(info)
    return readme


if __name__ == "__main__":
    readme = update_readme()
    with open("./README.md", 'w', encoding='utf-8') as f:
        f.write(readme)
