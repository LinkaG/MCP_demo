#!/usr/bin/env python3
"""
Прямой тест MCP сервера
"""

import json
import subprocess
import sys
import time
import os

def test_mcp_server():
    print("🧪 Тестирование MCP сервера...")
    
    # Запускаем сервер с UTF-8 кодировкой
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    process = subprocess.Popen(
        [sys.executable, "standard_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        env=env
    )
    
    try:
        # Тест 1: Initialize
        print("🔄 Тест 1: Initialize")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "Test Client", "version": "1.0.0"}
            }
        }
        
        process.stdin.write(json.dumps(init_request, ensure_ascii=False) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        response_obj = json.loads(response)
        print(f"📥 Ответ: {json.dumps(response_obj, ensure_ascii=False, indent=2)}")
        
        # Тест 2: Tools list
        print("\n🔄 Тест 2: Tools list")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        process.stdin.write(json.dumps(tools_request, ensure_ascii=False) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        response_obj = json.loads(response)
        print(f"📥 Ответ: {json.dumps(response_obj, ensure_ascii=False, indent=2)}")
        
        # Тест 3: Generate password
        print("\n🔄 Тест 3: Generate password")
        tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "generate_password",
                "arguments": {"length": 12, "include_symbols": True}
            }
        }
        
        process.stdin.write(json.dumps(tool_request, ensure_ascii=False) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        response_obj = json.loads(response)
        print(f"📥 Ответ: {json.dumps(response_obj, ensure_ascii=False, indent=2)}")
        
        print("\n✅ Все тесты выполнены!")
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
    
    finally:
        # Закрываем процесс
        process.terminate()
        
        # Показываем stderr если есть
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"\n📋 Логи сервера:\n{stderr_output}")

if __name__ == "__main__":
    test_mcp_server() 