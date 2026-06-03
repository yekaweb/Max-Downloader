#!/usr/bin/env python3
import ast
import sys

try:
    with open("bot/loader_professional_enhanced.py", "r", encoding="utf-8") as f:
        code = f.read()
    ast.parse(code)
    print("✅ Syntax OK")
    sys.exit(0)
except SyntaxError as e:
    print(f"❌ Syntax Error: {e}")
    sys.exit(1)
