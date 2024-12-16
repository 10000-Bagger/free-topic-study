import os

def count_md_files(directory):
    md_count = 0
    for root, dirs, files in os.walk(directory):
        md_count += sum(1 for file in files if file.endswith('.md'))
    return md_count


if __name__ == "__main__":
    root = os.getcwd()
    md_file_count = count_md_files(root) - 1  # README.md 파일 제외
    readme_path = os.path.join(root, 'README.md')

    with open(readme_path, 'r', encoding='utf-8') as file:
        readme_contents = file.readlines()

    for i, line in enumerate(readme_contents):
        if line.startswith("### 전체 아티클 갯수:"):
            readme_contents[i] = f"### 전체 아티클 갯수: {md_file_count}개\n"
            break

    with open(readme_path, 'w', encoding='utf-8') as file:
        file.writelines(readme_contents)

    print(f"Updated the README.md with total article count: {md_file_count}")