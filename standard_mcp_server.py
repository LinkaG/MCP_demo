#!/usr/bin/env python3
"""
Standard MCP Server для Personal Assistant
Совместимый с официальным MCP протоколом
"""

import json
import sys
import random
import string
from datetime import datetime
from typing import Dict, List, Any

class StandardMCPServer:
    def __init__(self):
        self.tasks_storage: List[Dict[str, Any]] = []
        self.calculator_history: List[Dict[str, Any]] = []
        
    def add_task(self, title: str, description: str = "", priority: str = "medium") -> str:
        """Добавить новую задачу"""
        if priority not in ["low", "medium", "high"]:
            return "Ошибка: приоритет должен быть low, medium или high"
        
        task = {
            "id": len(self.tasks_storage) + 1,
            "title": title,
            "description": description,
            "priority": priority,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        
        self.tasks_storage.append(task)
        return f"✅ Задача '{title}' добавлена с приоритетом {priority}"

    def get_tasks(self, status: str = "all") -> str:
        """Получить список задач"""
        if not self.tasks_storage:
            return "📝 Список задач пуст"
        
        filtered_tasks = self.tasks_storage
        if status == "completed":
            filtered_tasks = [t for t in self.tasks_storage if t["completed"]]
        elif status == "pending":
            filtered_tasks = [t for t in self.tasks_storage if not t["completed"]]
        
        if not filtered_tasks:
            return f"📝 Нет задач со статусом '{status}'"
        
        result = f"📋 Список задач ({status}):\n\n"
        for task in filtered_tasks:
            status_icon = "✅" if task["completed"] else "⏳"
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[task["priority"]]
            
            result += f"{status_icon} {priority_icon} #{task['id']}: {task['title']}\n"
            if task["description"]:
                result += f"   📄 {task['description']}\n"
            result += f"   📅 Создана: {task['created_at'][:10]}\n\n"
        
        return result

    def complete_task(self, task_id: int) -> str:
        """Завершить задачу"""
        for task in self.tasks_storage:
            if task["id"] == task_id:
                if task["completed"]:
                    return f"⚠️ Задача #{task_id} уже выполнена"
                
                task["completed"] = True
                task["completed_at"] = datetime.now().isoformat()
                return f"🎉 Задача #{task_id} '{task['title']}' отмечена как выполненная!"
        
        return f"❌ Задача с ID {task_id} не найдена"

    def calculate(self, expression: str) -> str:
        """Калькулятор"""
        try:
            allowed_chars = set("0123456789+-*/()., ")
            if not all(c in allowed_chars for c in expression):
                return "❌ Разрешены только числа и базовые математические операции"
            
            result = eval(expression)
            
            history_entry = {
                "expression": expression,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            self.calculator_history.append(history_entry)
            
            return f"🧮 {expression} = {result}"
        
        except Exception as e:
            return f"❌ Ошибка вычисления: {str(e)}"

    def generate_password(self, length: int = 12, include_symbols: bool = True) -> str:
        """Генератор паролей"""
        if length < 4 or length > 64:
            return "❌ Длина пароля должна быть от 4 до 64 символов"
        
        chars = string.ascii_letters + string.digits
        if include_symbols:
            chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
        
        password = ''.join(random.choice(chars) for _ in range(length))
        
        strength = "Слабый"
        if length >= 8 and include_symbols:
            strength = "Сильный"
        elif length >= 6:
            strength = "Средний"
        
        return f"🔐 Сгенерированный пароль: {password}\n💪 Сила пароля: {strength}"

    def text_stats(self, text: str) -> str:
        """Анализ текста"""
        if not text.strip():
            return "❌ Текст не может быть пустым"
        
        words = text.split()
        chars = len(text)
        chars_no_spaces = len(text.replace(" ", ""))
        sentences = len([s for s in text.split(".") if s.strip()])
        paragraphs = len([p for p in text.split("\n\n") if p.strip()])
        
        word_freq = {}
        for word in words:
            word_clean = word.lower().strip(".,!?;:")
            word_freq[word_clean] = word_freq.get(word_clean, 0) + 1
        
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        result = f"""📊 Статистика текста:

📝 Символов: {chars}
🔤 Символов без пробелов: {chars_no_spaces}
📖 Слов: {len(words)}
📄 Предложений: {sentences}
📋 Абзацев: {paragraphs}

🔝 Самые частые слова:"""
        
        for word, count in top_words:
            result += f"\n   • {word}: {count} раз"
        
        return result

    def get_tools_list(self):
        """Список доступных инструментов"""
        return {
            "tools": [
                {
                    "name": "add_task",
                    "description": "Добавить новую задачу в список дел",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Название задачи"},
                            "description": {"type": "string", "description": "Описание задачи", "default": ""},
                            "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Приоритет задачи", "default": "medium"}
                        },
                        "required": ["title"],
                        "additionalProperties": False
                    }
                },
                {
                    "name": "get_tasks",
                    "description": "Получить список задач",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "enum": ["all", "completed", "pending"], "description": "Фильтр по статусу", "default": "all"}
                        },
                        "additionalProperties": False
                    }
                },
                {
                    "name": "complete_task",
                    "description": "Отметить задачу как выполненную",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task_id": {"type": "integer", "description": "ID задачи для завершения"}
                        },
                        "required": ["task_id"],
                        "additionalProperties": False
                    }
                },
                {
                    "name": "calculate",
                    "description": "Выполнить математическое вычисление",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string", "description": "Математическое выражение"}
                        },
                        "required": ["expression"],
                        "additionalProperties": False
                    }
                },
                {
                    "name": "generate_password",
                    "description": "Сгенерировать безопасный пароль",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "length": {"type": "integer", "description": "Длина пароля (4-64)", "default": 12},
                            "include_symbols": {"type": "boolean", "description": "Включать спецсимволы", "default": True}
                        },
                        "additionalProperties": False
                    }
                },
                {
                    "name": "text_stats",
                    "description": "Получить статистику по тексту",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Текст для анализа"}
                        },
                        "required": ["text"],
                        "additionalProperties": False
                    }
                }
            ]
        }

    def call_tool(self, name: str, arguments: Dict) -> Dict:
        """Вызов инструмента"""
        try:
            if name == "add_task":
                result = self.add_task(
                    arguments.get("title", ""),
                    arguments.get("description", ""),
                    arguments.get("priority", "medium")
                )
            elif name == "get_tasks":
                result = self.get_tasks(arguments.get("status", "all"))
            elif name == "complete_task":
                result = self.complete_task(arguments.get("task_id", 0))
            elif name == "calculate":
                result = self.calculate(arguments.get("expression", ""))
            elif name == "generate_password":
                result = self.generate_password(
                    arguments.get("length", 12),
                    arguments.get("include_symbols", True)
                )
            elif name == "text_stats":
                result = self.text_stats(arguments.get("text", ""))
            else:
                return {
                    "content": [{"type": "text", "text": f"❌ Неизвестный инструмент: {name}"}],
                    "isError": True
                }
            
            return {
                "content": [{"type": "text", "text": result}],
                "isError": False
            }
            
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"❌ Ошибка выполнения: {str(e)}"}],
                "isError": True
            }

    def handle_request(self, request: Dict) -> Dict:
        """Обработка JSON-RPC запроса"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "Personal Assistant MCP Server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": self.get_tools_list()
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                result = self.call_tool(tool_name, tool_args)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

def main():
    """Основной цикл сервера"""
    server = StandardMCPServer()
    
    # Сервер запущен и готов к работе
    
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            
            try:
                request = json.loads(line.strip())
                response = server.handle_request(request)
                response_str = json.dumps(response)
                print(response_str, flush=True)
                
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
                }
                print(json.dumps(error_response), flush=True)
    
    except KeyboardInterrupt:
        print("Сервер остановлен", file=sys.stderr)

if __name__ == "__main__":
    main() 