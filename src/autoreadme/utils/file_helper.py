import os
import fnmatch

def load_gitignore_patterns(directory):
    """加载.gitignore文件中的匹配模式"""
    gitignore_path = os.path.join(directory, '.gitignore')
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns

def is_path_ignored(rel_path, ignore_patterns):
    """检查相对路径是否应该被忽略"""
    for pattern in ignore_patterns:
        # 处理目录模式 (例如 'node_modules/')
        if pattern.endswith('/'):
            # 如果路径就是该目录，或者在该目录内，则匹配
            if rel_path == pattern.rstrip('/') or rel_path.startswith(pattern):
                return True
        # 处理文件/通配符模式
        elif fnmatch.fnmatch(rel_path, pattern):
            return True
        # 对于不包含斜杠的模式，也匹配基本名称
        elif '/' not in pattern and fnmatch.fnmatch(os.path.basename(rel_path), pattern):
            return True
    return False

def find_files(directory, patterns, ignore_patterns):
    """查找符合条件的文件"""
    filepaths = []
    for root, dirs, files in os.walk(directory, topdown=True):
        rel_root = os.path.relpath(root, directory)
        if rel_root == '.':
            rel_root = ''

        # 过滤目录
        dirs[:] = [d for d in dirs if not is_path_ignored(os.path.join(rel_root, d), ignore_patterns)]

        for f in files:
            rel_path = os.path.join(rel_root, f)
            if not is_path_ignored(rel_path, ignore_patterns):
                if any(fnmatch.fnmatch(f, p) for p in patterns):
                    filepaths.append(os.path.join(root, f))
    return filepaths

def get_project_structure(directory, ignore_patterns):
    """生成项目结构"""
    structure = []
    for root, dirs, files in os.walk(directory, topdown=True):
        rel_root = os.path.relpath(root, directory)
        if rel_root == '.':
            rel_root = ''
        
        # 跳过被忽略的根目录
        if rel_root and is_path_ignored(rel_root, ignore_patterns):
            dirs[:] = []
            continue

        # 过滤子目录
        dirs[:] = [d for d in dirs if not is_path_ignored(os.path.join(rel_root, d), ignore_patterns)]
        
        level = rel_root.count(os.sep) if rel_root else 0
        indent = ' ' * 4 * (level)
        # 如果不是起始目录，才添加缩进和目录名
        if rel_root:
            structure.append(f'{indent}{os.path.basename(root)}/')
        else:
            structure.append(f'{os.path.basename(root)}/')

        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            if not is_path_ignored(os.path.join(rel_root, f), ignore_patterns):
                structure.append(f'{sub_indent}{f}')
    return "\n".join(structure)