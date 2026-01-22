import os
import re
import html
import datetime
import requests
import lxml.html
import urllib3
import textwrap
from bs4 import BeautifulSoup, NavigableString, Tag
from newspaper import Article, Config
from urllib.parse import urljoin
from markdownify import markdownify as md

# ================= 配置区域 =================
BOOKMARK_FILE = "favorites_2026_1_22.html"
TARGET_FOLDERS = ["技术", "面经"]
AUTHOR = "Chieh"
OUTPUT_DIR = "generated_posts"
ASSETS_DIR_NAME = "assets"
# ===========================================

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 全局请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# ================= 智能标签映射 =================
TAG_MAPPING = {
    "Java": ["java", "jdk", "spring", "mybatis", "maven", "netty"],
    "Python": ["python", "pip", "flask", "django", "pandas", "numpy"],
    "C++": ["c++", "cpp", "stl", "cmake", "qt"],
    "JavaScript": ["javascript", "js", "node", "npm", "vue", "react", "jquery"],
    "Frontend": ["前端", "html", "css", "dom", "ui"],
    "Backend": ["后端", "server", "api", "sql", "mysql", "redis", "linux"],
    "Algorithm": ["算法", "leetcode", "排序", "查找"],
    "Tools": ["git", "vscode", "idea", "nas", "unraid"]
}

def analyze_tags(title, original_folder, native_tags=None):
    tags = set()
    tags.add(original_folder)
    if native_tags:
        for t in native_tags:
            if t and len(t.strip()) > 1: tags.add(t.strip())
    title_lower = title.lower()
    for tag_name, keywords in TAG_MAPPING.items():
        for kw in keywords:
            if kw in title_lower:
                tags.add(tag_name)
                break
    if "面经" in original_folder: tags.add("Interview")
    return list(tags)

def sanitize_filename(title):
    safe_title = re.sub(r'[\\/*?:"<>|]', '', title)
    safe_title = re.sub(r'\s+', '-', safe_title).strip()
    return safe_title[:80]

def check_file_exists(directory, title_keyword):
    if not os.path.exists(directory): return False
    for filename in os.listdir(directory):
        if filename.endswith(".md") and title_keyword and title_keyword in filename:
            return True
    return False

def download_image(img_url, file_prefix, suffix, save_dir):
    try:
        if not img_url or img_url.startswith("data:"): return None
        lower_url = img_url.lower()
        if '.png' in lower_url: ext = '.png'
        elif '.gif' in lower_url: ext = '.gif'
        elif '.webp' in lower_url: ext = '.webp'
        elif '.svg' in lower_url: return None
        else: ext = '.jpg'
        
        img_filename = f"{file_prefix}_{suffix}{ext}"
        save_path = os.path.join(save_dir, img_filename)
        if os.path.exists(save_path): return f"{ASSETS_DIR_NAME}/{img_filename}"
            
        response = requests.get(img_url, headers=HEADERS, timeout=15, verify=False)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return f"{ASSETS_DIR_NAME}/{img_filename}"
    except: pass
    return None

def extract_text_preserving_indent(element):
    """
    核心函数：提取文本并保留缩进和换行
    递归遍历 DOM 树，遇到 <br> / <div> / <p> 插入换行符，
    遇到文本节点则保留其原始空白符（空格/Tab）。
    """
    text_parts = []
    
    for child in element.children:
        if isinstance(child, NavigableString):
            # 保留原始文本，包括前导空格
            text_parts.append(str(child))
        elif isinstance(child, Tag):
            # 处理换行标签
            if child.name == 'br':
                text_parts.append('\n')
            # 递归处理子元素
            else:
                # 如果是块级元素，前后可能需要换行（视情况而定，简单处理为后换行）
                if child.name in ['div', 'p', 'li', 'tr']:
                    text_parts.append(extract_text_preserving_indent(child))
                    text_parts.append('\n') # 块级元素后追加换行
                else:
                    # 行内元素 (span, b, i, a...) 直接拼接
                    text_parts.append(extract_text_preserving_indent(child))
    
    return "".join(text_parts)

def clean_code_blocks(soup):
    """HTML 预处理：标准化代码块并保留缩进"""
    
    code_containers = []
    code_containers.extend(soup.find_all('pre'))
    code_containers.extend(soup.find_all(class_=re.compile(r'cnblogs_code|cnblogs_Highlighter|syntaxhighlighter|highlight|code')))

    for container in code_containers:
        if container.parent is None: continue
        
        # 1. 移除行号干扰
        for bad in container.select('.line-numbers-rows, .gutter, .ln-num, .b-line-num, .number, .index'):
            bad.decompose()

        # 2. 核心：使用保留缩进的提取算法
        raw_code = extract_text_preserving_indent(container)

        # 3. 修复非破坏性空格
        raw_code = raw_code.replace('\xa0', ' ')

        # 4. 去除多余空行 (保留最多2个连续换行)
        raw_code = re.sub(r'\n{3,}', '\n\n', raw_code)

        # 5. 重建结构
        new_pre = soup.new_tag("pre")
        new_code = soup.new_tag("code")
        # 自动转义 HTML (例如 <form> -> &lt;form&gt;)
        new_code.string = raw_code 
        new_pre.append(new_code)
        container.replace_with(new_pre)

    # Table 布局代码 (这类通常每一行在独立的 td 里，不需要复杂缩进处理，直接拼接即可)
    for table in soup.find_all('table'):
        if table.find('td', class_=re.compile(r'code|blob-code|content')):
            code_lines = []
            for td in table.find_all('td', class_=re.compile(r'code|blob-code|content')):
                # 这里 td.get_text() 可能会丢缩进，改用 extract
                code_lines.append(extract_text_preserving_indent(td).rstrip())
            if code_lines:
                raw_code = "\n".join(code_lines)
                new_pre = soup.new_tag("pre")
                new_code = soup.new_tag("code")
                new_code.string = raw_code
                new_pre.append(new_code)
                table.replace_with(new_pre)
    return soup

def process_html_content(html_content_str, article_url, file_title_prefix, assets_full_path):
    if not html_content_str: return ""
    # 预处理：将 &nbsp; 替换为普通空格，防止 parser 忽略
    html_content_str = html_content_str.replace('&nbsp;', ' ')
    
    soup = BeautifulSoup(html_content_str, 'lxml')
    soup = clean_code_blocks(soup)
    
    imgs = soup.find_all('img')
    for i, img in enumerate(imgs):
        src = img.get('data-src') or img.get('src')
        if not src: continue
        abs_url = urljoin(article_url, src)
        local_path = download_image(abs_url, file_title_prefix, f"img_{i+1}", assets_full_path)
        if local_path:
            img['src'] = local_path
            for attr in ['data-src', 'srcset', 'loading']:
                if img.has_attr(attr): del img[attr]

    for tag in soup.find_all(['script', 'style', 'iframe', 'noscript', 'meta', 'input', 'button']):
        tag.decompose()
            
    return str(soup)

def get_content_by_site(url, article_obj):
    try:
        if not article_obj.html: return None
        full_soup = BeautifulSoup(article_obj.html, 'lxml')
        content_tag = None
        if "cnblogs.com" in url: content_tag = full_soup.find(id="cnblogs_post_body")
        elif "csdn.net" in url: content_tag = full_soup.find(id="content_views")
        elif "jianshu.com" in url: content_tag = full_soup.find("article")
        elif "zhihu.com" in url: content_tag = full_soup.find(class_="Post-RichText")
        elif "juejin.cn" in url: content_tag = full_soup.find(class_="markdown-body")
        
        if content_tag: return str(content_tag)
        else: return lxml.html.tostring(article_obj.top_node, encoding='unicode') if article_obj.top_node is not None else article_obj.html
    except: return None

def post_process_markdown(md_text):
    """
    MD 后期深度处理
    """
    md_text = re.sub(r'\n{3,}', '\n\n', md_text)

    def clean_code_block_logic(match):
        head = match.group(1).strip() # ```javascript
        content = match.group(2)
        tail = match.group(3).strip() # ```

        # 1. 移除干扰头
        content = re.sub(r'^代码语言：.*\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'^复制\n', '', content, flags=re.MULTILINE)
        
        # 2. 移除连续空行
        content = re.sub(r'\n\s*\n', '\n', content)
        
        # 3. 智能去缩进 (去除公共前导空格)
        # 这里的关键是：如果之前的 extract 保留了所有缩进，那么这里 dedent 会把整体缩进对其到最左侧
        # 但保留内部的相对缩进
        content = textwrap.dedent(content)
        
        # 4. 修复 HTML 标签被拆行的问题 (针对 JS/HTML 代码)
        # 将 < script > 这种修复为 <script>
        content = re.sub(r'<\s+([a-zA-Z/]+)', r'<\1', content)
        content = re.sub(r'([a-zA-Z"\'\-])\s+>', r'\1>', content)

        return f"\n{head}\n{content.strip()}\n{tail}\n"

    # 正则匹配代码块
    pattern = re.compile(r'(^\s*```[^\n]*\n)(.*?)(\n\s*```)', re.DOTALL | re.MULTILINE)
    md_text = pattern.sub(clean_code_block_logic, md_text)
    
    return md_text.strip()

def generate_markdown_file(item, base_output_path):
    url = item['url']
    original_folder = item['folder']
    original_title = item['original_title']
    
    safe_original_title = sanitize_filename(original_title)
    if check_file_exists(base_output_path, safe_original_title):
        print(f"⏩ [跳过] {safe_original_title}")
        return

    assets_path = os.path.join(base_output_path, ASSETS_DIR_NAME)
    if not os.path.exists(assets_path): os.makedirs(assets_path)

    try:
        print(f"正在抓取: {original_title[:30]}...")
        config = Config()
        config.browser_user_agent = HEADERS['User-Agent']
        config.fetch_images = False 
        config.request_args = {'timeout': 20, 'verify': False}

        article = Article(url, config=config, language='zh')
        article.download()
        article.parse()

        final_title = article.title if article.title else original_title
        file_title_safe = sanitize_filename(final_title)

        if file_title_safe != safe_original_title:
            if check_file_exists(base_output_path, file_title_safe):
                print(f"⏩ [跳过] {file_title_safe}")
                return

        header_img_path = ""
        if article.top_image:
            top_img_abs_url = urljoin(url, article.top_image)
            dl_header = download_image(top_img_abs_url, file_title_safe, "header", assets_path)
            if dl_header: header_img_path = dl_header
        
        html_content_str = get_content_by_site(url, article)
        
        native_tags = list(article.tags) if article.tags else []
        if article.meta_keywords: native_tags.extend(article.meta_keywords)
        
        content_md = ""
        pub_date = article.publish_date
        date_str = pub_date.strftime("%Y-%m-%d") if pub_date else datetime.datetime.now().strftime("%Y-%m-%d")

        if html_content_str and len(html_content_str.strip()) > 50:
            processed_html = process_html_content(html_content_str, url, file_title_safe, assets_path)
            content_md = md(processed_html, heading_style="ATX")
            content_md = post_process_markdown(content_md)
            filename = f"{date_str}-{file_title_safe}.md"
        else:
            content_md = f"> ⚠️ 无法自动抓取内容，请手动访问原文。"
            filename = f"待处理-{date_str}-{file_title_safe}.md"

        smart_tags = analyze_tags(final_title, original_folder, native_tags)
        tag_yaml = "\n".join([f"    - {t}" for t in smart_tags])
        
        md_output = f"""---
layout:     post
title:      "{final_title}"
subtitle:   "归档于：{original_folder}"
date:       {date_str}
author:     {AUTHOR}
header-img: {header_img_path}
catalog: true
tags:
{tag_yaml}
---

{content_md}

---
> 参考链接：[{url}]({url})
"""
        save_path = os.path.join(base_output_path, filename)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(md_output)
            
    except Exception as e:
        print(f"  [Failed] {url} : {e}")
        create_fallback_file(item, str(e), base_output_path)

def create_fallback_file(item, error_msg, base_output_path):
    safe_title = sanitize_filename(item['original_title'])
    if check_file_exists(base_output_path, safe_title): return
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"待处理-{date_str}-{safe_title}.md"
    smart_tags = analyze_tags(item['original_title'], item['folder'])
    tag_yaml = "\n".join([f"    - {t}" for t in smart_tags])

    md_output = f"""---
layout:     post
title:      "{item['original_title']}"
date:       {date_str}
author:     {AUTHOR}
header-img: 
tags:
{tag_yaml}
---

**系统提示：** 自动抓取内容失败。

错误信息：`{error_msg}`

---
> 参考链接：[{item['url']}]({item['url']})
"""
    try:
        with open(os.path.join(base_output_path, filename), 'w', encoding='utf-8') as f:
            f.write(md_output)
    except: pass

def parse_bookmarks(html_path):
    if not os.path.exists(html_path): return []
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'lxml')
    extracted_links = []
    all_headers = soup.find_all('h3')
    for header in all_headers:
        folder_name = header.get_text().strip()
        if folder_name in TARGET_FOLDERS:
            dl_tag = header.find_next('dl')
            if dl_tag:
                links = dl_tag.find_all('a')
                for link in links:
                    url = link.get('href')
                    title = link.get_text().strip() or "未命名文章"
                    if url and not url.startswith("javascript"):
                        if "csdn.net" in url or "zhidao.baidu.com" in url: continue
                        extracted_links.append({"url": url, "original_title": title, "folder": folder_name})
    return extracted_links

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, BOOKMARK_FILE)
    final_output_dir = os.path.join(base_dir, OUTPUT_DIR)
    
    if not os.path.exists(final_output_dir): os.makedirs(final_output_dir)
    
    print("=== 启动程序 v4.6 (Indent Preserved) ===")
    links = parse_bookmarks(html_path)
    
    if not links:
        print(f"未在 '{BOOKMARK_FILE}' 中找到目标文件夹链接。")
        return

    print(f"=== 待处理任务：{len(links)} 个 ===")
    for i, link_item in enumerate(links):
        print(f"[{i+1}/{len(links)}] ", end="")
        generate_markdown_file(link_item, final_output_dir)
        
    print("\n=== 全部处理完毕 ===")

if __name__ == "__main__":
    main()