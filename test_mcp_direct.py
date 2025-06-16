#!/usr/bin/env python3
"""
Прямой тест MCP сервера
"""

import json
import subprocess
import sys
import time

def test_mcp_server():
    print("🧪 Тестирование MCP сервера...")
    
    # Запускаем сервер
    process = subprocess.Popen(
        [sys.executable, "standard_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
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
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        print(f"📥 Ответ: {response.strip()}")
        
        # Тест 2: Tools list
        print("\n🔄 Тест 2: Tools list")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        print(f"📥 Ответ: {response.strip()}")
        
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
        
        process.stdin.write(json.dumps(tool_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        print(f"📥 Ответ: {response.strip()}")
        
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