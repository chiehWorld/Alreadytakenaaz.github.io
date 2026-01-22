import os
import re
import html
import textwrap

# ================= 配置 =================
TARGET_DIR = "generated_posts"
# =======================================

def fix_code_block(match):
    """
    正则回调函数：处理每一个匹配到的代码块
    """
    # 1. 获取代码块的完整内容
    full_block = match.group(0)
    
    # 2. 分离头部(```python)、内容、尾部(```)
    # 捕获组: group(1)=缩进+```语言, group(2)=代码内容, group(3)=```
    # 注意：为了兼容性，我们手动拆分行更稳妥
    
    lines = full_block.split('\n')
    
    # 获取首行 (```language) 和 尾行 (```)
    first_line = lines[0].strip() # 去除首行可能存在的缩进
    last_line = lines[-1].strip() # 去除尾行可能存在的缩进
    
    # 获取中间的代码内容
    if len(lines) > 2:
        code_content_lines = lines[1:-1]
    else:
        # 如果代码块只有一行或两行（空的），直接返回标准化结果
        return f"{first_line}\n{last_line}"

    # 3. 核心修复：去除公共缩进 (Dedent)
    # 将列表转为字符串以便使用 textwrap
    code_text = "\n".join(code_content_lines)
    
    # textwrap.dedent 会移除所有行共有的前导空白符
    dedented_text = textwrap.dedent(code_text)
    
    # 4. 修复 HTML 实体 (例如把 &lt; 转回 <)
    # 很多爬虫下来的代码块里包含转义字符，导致代码不可用
    decoded_text = html.unescape(dedented_text)
    
    # 5. 清理首尾多余的空行
    decoded_text = decoded_text.strip()
    
    # 6. 重新组装
    # 确保首尾各有一个换行符，符合 Markdown 标准
    return f"{first_line}\n{decoded_text}\n{last_line}"

def process_file(filepath):
    """处理单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 正则表达式说明：
        # (?ms) 开启多行模式和点号匹配换行
        # ^\s*```.*?``` 匹配以 ``` 开头的代码块（允许 ``` 前有空格）
        # 非贪婪匹配 .*? 直到遇到下一个 ```
        
        # 匹配模式：
        # 1. ^\s*```  : 行首，任意空格，后跟 ```
        # 2. (.*?)    : 代码内容 (Group 1)
        # 3. ^\s*```  : 行首，任意空格，后跟 ``` 结束
        pattern = re.compile(r'(^\s*```[^\n]*\n)(.*?)(\n\s*```)', re.DOTALL | re.MULTILINE)
        
        # 替换操作：将匹配到的代码块传入 fix_code_block 进行处理
        new_content = pattern.sub(lambda m: fix_code_block_logic(m), content)

        # 写入文件（仅当内容发生变化时）
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        return False

    except Exception as e:
        print(f"处理出错: {filepath} | {e}")
        return False

def fix_code_block_logic(match):
    """
    具体的处理逻辑
    match.group(1): 开始标记 (如 "  ```python\n")
    match.group(2): 代码内容
    match.group(3): 结束标记 (如 "\n  ```")
    """
    head = match.group(1).strip() # 去除 ``` 前面的空格
    body = match.group(2)
    tail = match.group(3).strip() # 去除 ``` 前面的空格

    # 1. 智能去缩进
    # expandtabs 确保 tab 也能被正确计算长度
    body = textwrap.dedent(body)

    # 2. HTML 反转义
    body = html.unescape(body)

    # 3. 去除行尾空格
    body_lines = [line.rstrip() for line in body.split('\n')]
    
    # 4. 去除首尾空行 (保留中间空行)
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)
    while body_lines and not body_lines[-1].strip():
        body_lines.pop()
        
    body = "\n".join(body_lines)

    return f"{head}\n{body}\n{tail}"

def main():
    # 获取脚本所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.join(base_dir, TARGET_DIR)

    if not os.path.exists(target_path):
        print(f"错误：找不到目录 {target_path}")
        return

    print(f"=== 开始修复 Markdown 代码块缩进 ===")
    print(f"目标目录: {target_path}")

    count = 0
    modified_count = 0
    
    for filename in os.listdir(target_path):
        if filename.endswith(".md"):
            filepath = os.path.join(target_path, filename)
            count += 1
            if process_file(filepath):
                print(f"✅ 已修复: {filename}")
                modified_count += 1
            else:
                # print(f"   跳过: {filename} (无需修复)")
                pass

    print(f"\n=== 处理完成 ===")
    print(f"扫描文件: {count}")
    print(f"修复文件: {modified_count}")

if __name__ == "__main__":
    main()