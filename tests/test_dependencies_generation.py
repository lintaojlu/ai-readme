# tests/test_dependencies_generation.py
# 测试依赖生成功能

import pytest
import os
import tempfile
import json
from unittest.mock import MagicMock
from pathlib import Path
import sys

# 添加项目根目录到路径
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.readmecraft.core import ReadmeCraft


class TestDependenciesGeneration:
    """测试依赖生成功能"""

    def test_extract_imports(self):
        """测试import提取功能"""
        print("\n" + "=" * 60)
        print("🔍 测试: Import语句提取")
        print("=" * 60)
        
        craft = ReadmeCraft()
        
        # 测试代码示例
        test_code = """
import os
import sys
from flask import Flask, render_template
from requests import get
import numpy as np
from django.shortcuts import render
import json  # 内置模块
from datetime import datetime
import custom_module
# import commented_module
"""
        
        imports = craft._extract_imports(test_code)
        
        print(f"提取到的import语句: {len(imports)}个")
        for imp in sorted(imports):
            print(f"  - {imp}")
        
        # 验证提取结果
        expected_imports = {
            'import os',
            'import sys', 
            'from flask import Flask, render_template',
            'from requests import get',
            'import numpy',
            'from django.shortcuts import render',
            'import json',
            'from datetime import datetime',
            'import custom_module'
        }
        
        # 注意：numpy as np 会被提取为 import numpy
        assert len(imports) >= 8, f"应该提取到至少8个import，实际: {len(imports)}"
        print("✅ Import提取测试通过!")

    def test_dependencies_generation_with_existing_requirements(self):
        """测试有现有requirements.txt的依赖生成"""
        print("\n" + "=" * 60)
        print("📦 测试: 有现有requirements.txt的依赖生成")
        print("=" * 60)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建现有的requirements.txt
            existing_req = "flask==2.0.1\nrequests>=2.25.0\n"
            req_path = os.path.join(temp_dir, "requirements.txt")
            with open(req_path, 'w') as f:
                f.write(existing_req)
            
            # 创建测试Python文件
            test_files = {
                "app.py": """
import os
from flask import Flask
import pandas as pd
from numpy import array
""",
                "utils.py": """
import requests
from datetime import datetime
import matplotlib.pyplot as plt
"""
            }
            
            for filename, content in test_files.items():
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, 'w') as f:
                    f.write(content)
            
            # 创建ReadmeCraft实例
            craft = ReadmeCraft(project_dir=temp_dir)
            craft.output_dir = os.path.join(temp_dir, "output")
            os.makedirs(craft.output_dir, exist_ok=True)
            
            # Mock LLM响应
            mock_requirements = """flask>=2.0.1
requests>=2.25.0
pandas>=1.3.0
numpy>=1.20.0
matplotlib>=3.5.0"""
            
            craft.model_client.get_answer = MagicMock(return_value=mock_requirements)
            
            # 生成依赖
            result = craft._generate_project_dependencies()
            
            # 验证文件生成
            output_req_path = os.path.join(craft.output_dir, "requirements.txt")
            analysis_path = os.path.join(craft.output_dir, "dependencies_analysis.txt")
            
            assert os.path.exists(output_req_path), "requirements.txt应该生成"
            assert os.path.exists(analysis_path), "dependencies_analysis.txt应该生成"
            
            # 验证内容
            with open(output_req_path, 'r') as f:
                generated_content = f.read()
            
            assert "flask" in generated_content.lower(), "应该包含flask"
            assert "pandas" in generated_content.lower(), "应该包含pandas"
            
            print(f"✅ 生成的requirements.txt:")
            print(generated_content)
            print("✅ 有现有requirements.txt的依赖生成测试通过!")

    def test_dependencies_generation_no_existing_requirements(self):
        """测试无现有requirements.txt的依赖生成"""
        print("\n" + "=" * 60) 
        print("📦 测试: 无现有requirements.txt的依赖生成")
        print("=" * 60)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试Python文件（无现有requirements.txt）
            test_files = {
                "main.py": """
import os
import sys
from flask import Flask, jsonify
import requests
from sqlalchemy import create_engine
""",
                "models.py": """
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
import datetime
"""
            }
            
            for filename, content in test_files.items():
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, 'w') as f:
                    f.write(content)
            
            craft = ReadmeCraft(project_dir=temp_dir)
            craft.output_dir = os.path.join(temp_dir, "output")
            os.makedirs(craft.output_dir, exist_ok=True)
            
            # Mock LLM响应
            mock_requirements = """flask>=2.0.0
requests>=2.25.0
sqlalchemy>=1.4.0"""
            
            craft.model_client.get_answer = MagicMock(return_value=mock_requirements)
            
            # 生成依赖
            result = craft._generate_project_dependencies()
            
            # 验证结果
            output_req_path = os.path.join(craft.output_dir, "requirements.txt")
            assert os.path.exists(output_req_path), "requirements.txt应该生成"
            
            with open(output_req_path, 'r') as f:
                content = f.read()
            
            print(f"生成的requirements.txt:")
            print(content)
            
            assert "flask" in content.lower(), "应该包含flask"
            assert "sqlalchemy" in content.lower(), "应该包含sqlalchemy"
            print("✅ 无现有requirements.txt的依赖生成测试通过!")

    def test_clean_requirements_content(self):
        """测试requirements.txt内容清理功能"""
        print("\n" + "=" * 60)
        print("🧹 测试: Requirements内容清理")
        print("=" * 60)
        
        craft = ReadmeCraft()
        
        # 测试需要清理的内容
        messy_content = """
```
Based on the import statements, here is the requirements.txt:

flask>=2.0.0
requests>=2.25.0

numpy
pandas==1.3.0
```

Some extra text here
"""
        
        cleaned = craft._clean_requirements_content(messy_content)
        
        print("清理前:")
        print(messy_content)
        print("\n清理后:")
        print(cleaned)
        
        lines = cleaned.split('\n')
        assert "flask>=2.0.0" in lines, "应该保留flask"
        assert "requests>=2.25.0" in lines, "应该保留requests"
        assert "numpy>=1.0.0" in lines, "numpy应该添加默认版本"
        assert "pandas==1.3.0" in lines, "应该保留pandas"
        assert "```" not in cleaned, "应该移除markdown标记"
        
        print("✅ Requirements内容清理测试通过!")

    def test_empty_project_dependencies(self):
        """测试空项目的依赖生成"""
        print("\n" + "=" * 60)
        print("📂 测试: 空项目依赖生成")
        print("=" * 60)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 只创建非Python文件
            with open(os.path.join(temp_dir, "README.md"), 'w') as f:
                f.write("# Test Project")
            
            craft = ReadmeCraft(project_dir=temp_dir)
            craft.output_dir = os.path.join(temp_dir, "output")
            os.makedirs(craft.output_dir, exist_ok=True)
            
            # 生成依赖
            result = craft._generate_project_dependencies()
            
            # 验证结果
            assert "No Python files found" in result, "应该显示没有找到Python文件"
            
            output_req_path = os.path.join(craft.output_dir, "requirements.txt")
            assert os.path.exists(output_req_path), "requirements.txt应该生成"
            
            print("✅ 空项目依赖生成测试通过!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"]) 