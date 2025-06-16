#!/usr/bin/env python3
"""
OpenRouter MCP Client
Клиент для подключения MCP сервера к OpenRouter API
"""

import json
import asyncio
import subprocess
import sys
from typing import Dict, List, Any, Optional
import aiohttp
import os
from datetime import datetime
from dotenv import load_dotenv

class OpenRouterMCPClient:
    """Клиент для интеграции MCP сервера с OpenRouter"""
    
    def __init__(self, api_key: str, model: str = "anthropic/claude-3.5-sonnet"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.mcp_process = None
        self.available_tools = []
        self.conversation_history = []
        
    async def start_mcp_server(self):
        """Запуск MCP сервера в subprocess"""
        try:
            self.mcp_process = subprocess.Popen(
                [sys.executable, "standard_mcp_server.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            # Инициализация MCP соединения
            await self.initialize_mcp()
            
        except Exception as e:
            print(f"❌ Ошибка запуска MCP сервера: {e}")
            raise
    
    async def initialize_mcp(self):
        """Инициализация MCP соединения"""
        # Отправляем initialize запрос
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "OpenRouter MCP Client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await self.send_mcp_request(init_request)
        
        # Получаем список доступных инструментов
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        tools_response = await self.send_mcp_request(tools_request)
        if tools_response and "result" in tools_response:
            self.available_tools = tools_response["result"].get("tools", [])
    
    async def send_mcp_request(self, request: Dict) -> Optional[Dict]:
        """Отправка запроса к MCP серверу"""
        try:
            if not self.mcp_process:
                raise Exception("MCP сервер не запущен")
            
            # Проверяем, что процесс еще жив
            if self.mcp_process.poll() is not None:
                stderr_output = self.mcp_process.stderr.read()
                raise Exception(f"MCP сервер завершился с ошибкой: {stderr_output}")
            
            # Отправляем запрос
            request_str = json.dumps(request) + "\n"
            self.mcp_process.stdin.write(request_str)
            self.mcp_process.stdin.flush()
            
            # Читаем ответ
            response_str = self.mcp_process.stdout.readline()
            
            if response_str and response_str.strip():
                try:
                    response = json.loads(response_str.strip())
                    return response
                except json.JSONDecodeError as e:
                    print(f"❌ Ошибка парсинга ответа MCP: {e}", file=sys.stderr)
                    return None
            else:
                print("❌ Пустой ответ от MCP сервера", file=sys.stderr)
                return None
            
        except Exception as e:
            print(f"❌ Ошибка MCP запроса: {e}", file=sys.stderr)
            return None
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> str:
        """Вызов инструмента через MCP"""
        # Проверяем состояние процесса
        if not self.mcp_process or self.mcp_process.poll() is not None:
            return "❌ MCP сервер не активен"
        
        tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        response = await self.send_mcp_request(tool_request)
        if response and "result" in response:
            content = response["result"].get("content", [])
            if content and len(content) > 0:
                return content[0].get("text", "Нет результата")
        elif response and "error" in response:
            error = response["error"]
            return f"❌ Ошибка сервера: {error.get('message', 'Неизвестная ошибка')}"
        
        return "❌ Ошибка выполнения инструмента"
    
    def format_tools_for_openrouter(self) -> List[Dict]:
        """Форматирование инструментов для OpenRouter API"""
        formatted_tools = []
        
        for tool in self.available_tools:
            tool_def = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            
            # Добавляем параметры если они есть
            if "inputSchema" in tool:
                schema = tool["inputSchema"]
                if "properties" in schema:
                    tool_def["function"]["parameters"]["properties"] = schema["properties"]
                if "required" in schema:
                    tool_def["function"]["parameters"]["required"] = schema["required"]
            
            formatted_tools.append(tool_def)
        
        return formatted_tools
    
    async def chat_with_openrouter(self, message: str) -> str:
        """Отправка запроса к OpenRouter с поддержкой инструментов"""
        
        # Добавляем сообщение пользователя
        self.conversation_history.append({
            "role": "user",
            "content": message
        })
        
        # Подготавливаем запрос
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost:3000",
            "X-Title": "MCP Demo Client"
        }
        
        payload = {
            "model": self.model,
            "messages": self.conversation_history,
            "tools": self.format_tools_for_openrouter(),
            "tool_choice": "auto"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    return f"❌ Ошибка OpenRouter: {response.status} - {error_text}"
                
                try:
                    result = await response.json()
                except json.JSONDecodeError as e:
                    return f"❌ Ошибка парсинга ответа OpenRouter: {e}"
                
                if "choices" not in result or len(result["choices"]) == 0:
                    return "❌ Пустой ответ от OpenRouter"
                
                choice = result["choices"][0]
                message_result = choice["message"]
                
                # Добавляем ответ ассистента в историю
                self.conversation_history.append(message_result)
                
                # Проверяем, нужно ли вызвать инструменты
                if "tool_calls" in message_result:
                    tool_results = []
                    
                    for tool_call in message_result["tool_calls"]:
                        func_name = tool_call["function"]["name"]
                        func_args_str = tool_call["function"]["arguments"]
                        
                        try:
                            # Обрабатываем пустые аргументы
                            if not func_args_str or func_args_str.strip() == "":
                                func_args = {}
                            else:
                                func_args = json.loads(func_args_str)
                        except json.JSONDecodeError as e:
                            tool_result = f"❌ Ошибка парсинга аргументов: {e}"
                        else:
                            # Вызываем инструмент через MCP
                            tool_result = await self.call_tool(func_name, func_args)
                        
                        tool_results.append(f"Результат {func_name}: {tool_result}")
                        
                        # Добавляем результат инструмента в историю
                        self.conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": tool_result
                        })
                    
                    # Получаем финальный ответ после выполнения инструментов
                    final_payload = {
                        "model": self.model,
                        "messages": self.conversation_history
                    }
                    
                    async with session.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=final_payload
                    ) as final_response:
                        
                        if final_response.status == 200:
                            try:
                                final_result = await final_response.json()
                                
                                if "choices" in final_result and len(final_result["choices"]) > 0:
                                    final_message = final_result["choices"][0]["message"]["content"]
                                    self.conversation_history.append({
                                        "role": "assistant",
                                        "content": final_message
                                    })
                                    return final_message
                                else:
                                    return "❌ Пустой финальный ответ"
                            except json.JSONDecodeError as e:
                                return f"❌ Ошибка парсинга финального ответа: {e}"
                        else:
                            return f"❌ Ошибка финального запроса: {final_response.status}"
                
                return message_result.get("content", "Нет ответа")
    
    async def interactive_chat(self):
        """Интерактивный чат с пользователем"""
        print("\n" + "="*50)
        print("🤖 Personal Assistant MCP готов к работе!")
        print(f"📡 Модель: {self.model}")
        print(f"🔧 Доступно инструментов: {len(self.available_tools)}")
        print("💬 Введите 'quit' для выхода")
        print("="*50)
        
        while True:
            try:
                user_input = input("\n👤 Вы: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 До свидания!")
                    break
                
                if not user_input:
                    continue
                
                print("🤔 Думаю...")
                response = await self.chat_with_openrouter(user_input)
                print(f"\n🤖 ИИ: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
    
    async def cleanup(self):
        """Очистка ресурсов"""
        if self.mcp_process:
            self.mcp_process.terminate()
            self.mcp_process = None

async def main():
    """Главная функция"""
    
    # Загружаем переменные из .env файла
    load_dotenv()
    
    # Проверяем API ключ
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Не найден API ключ OpenRouter!")
        print("💡 Создайте .env файл в папке проекта с содержимым:")
        print("   OPENROUTER_API_KEY=ваш_api_ключ")
        print("💡 Получить ключ можно на: https://openrouter.ai/keys")
        return
    
    # Создаем клиент
    client = OpenRouterMCPClient(
        api_key=api_key,
        model="anthropic/claude-3.5-sonnet"  # можно поменять модель
    )
    
    try:
        # Запускаем MCP сервер
        await client.start_mcp_server()
        
        # Запускаем интерактивный чат
        await client.interactive_chat()
        
    finally:
        # Очищаем ресурсы
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 