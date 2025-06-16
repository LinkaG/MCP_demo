#!/usr/bin/env python3
"""
Personal Assistant MCP Server
Демонстрационный проект, показывающий возможности MCP протокола
"""

import json
import random
import string
import hashlib
from datetime import datetime
from typing import Dict, List, Any
from mcp.server.fastmcp import FastMCP

# Создаем MCP сервер
mcp = FastMCP("Personal Assistant")

# Хранилище данных в памяти (в реальном проекте использовалась бы БД)
tasks_storage: List[Dict[str, Any]] = []
calculator_history: List[Dict[str, Any]] = []

# =============================================================================
# TOOLS (Инструменты)
# =============================================================================

@mcp.tool()
def add_task(title: str, description: str = "", priority: str = "medium") -> str:
    """Добавить новую задачу в список дел.
    
    Args:
        title: Название задачи
        description: Описание задачи (необязательно)
        priority: Приоритет задачи (low, medium, high)
    """
    if priority not in ["low", "medium", "high"]:
        return "Ошибка: приоритет должен быть low, medium или high"
    
    task = {
        "id": len(tasks_storage) + 1,
        "title": title,
        "description": description,
        "priority": priority,
        "completed": False,
        "created_at": datetime.now().isoformat()
    }
    
    tasks_storage.append(task)
    return f"✅ Задача '{title}' добавлена с приоритетом {priority}"

@mcp.tool()
def get_tasks(status: str = "all") -> str:
    """Получить список задач.
    
    Args:
        status: Фильтр по статусу (all, completed, pending)
    """
    if not tasks_storage:
        return "📝 Список задач пуст"
    
    filtered_tasks = tasks_storage
    if status == "completed":
        filtered_tasks = [t for t in tasks_storage if t["completed"]]
    elif status == "pending":
        filtered_tasks = [t for t in tasks_storage if not t["completed"]]
    
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

@mcp.tool()
def complete_task(task_id: int) -> str:
    """Отметить задачу как выполненную.
    
    Args:
        task_id: ID задачи для завершения
    """
    for task in tasks_storage:
        if task["id"] == task_id:
            if task["completed"]:
                return f"⚠️ Задача #{task_id} уже выполнена"
            
            task["completed"] = True
            task["completed_at"] = datetime.now().isoformat()
            return f"🎉 Задача #{task_id} '{task['title']}' отмечена как выполненная!"
    
    return f"❌ Задача с ID {task_id} не найдена"

@mcp.tool()
def calculate(expression: str) -> str:
    """Выполнить математическое вычисление.
    
    Args:
        expression: Математическое выражение для вычисления
    """
    try:
        # Безопасное вычисление только математических выражений
        allowed_chars = set("0123456789+-*/()., ")
        if not all(c in allowed_chars for c in expression):
            return "❌ Разрешены только числа и базовые математические операции"
        
        result = eval(expression)
        
        # Сохраняем в историю
        history_entry = {
            "expression": expression,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        calculator_history.append(history_entry)
        
        return f"🧮 {expression} = {result}"
    
    except Exception as e:
        return f"❌ Ошибка вычисления: {str(e)}"

@mcp.tool()
def generate_password(length: int = 12, include_symbols: bool = True) -> str:
    """Сгенерировать безопасный пароль.
    
    Args:
        length: Длина пароля (от 4 до 64 символов)
        include_symbols: Включать ли специальные символы
    """
    if length < 4 or length > 64:
        return "❌ Длина пароля должна быть от 4 до 64 символов"
    
    # Составляем набор символов
    chars = string.ascii_letters + string.digits
    if include_symbols:
        chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
    
    # Генерируем пароль
    password = ''.join(random.choice(chars) for _ in range(length))
    
    # Вычисляем силу пароля
    strength = "Слабый"
    if length >= 8 and include_symbols:
        strength = "Сильный"
    elif length >= 6:
        strength = "Средний"
    
    return f"🔐 Сгенерированный пароль: {password}\n💪 Сила пароля: {strength}"

@mcp.tool()
def text_stats(text: str) -> str:
    """Получить статистику по тексту.
    
    Args:
        text: Текст для анализа
    """
    if not text.strip():
        return "❌ Текст не может быть пустым"
    
    words = text.split()
    chars = len(text)
    chars_no_spaces = len(text.replace(" ", ""))
    sentences = len([s for s in text.split(".") if s.strip()])
    paragraphs = len([p for p in text.split("\n\n") if p.strip()])
    
    # Самые частые слова
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

# =============================================================================
# RESOURCES (Ресурсы)
# =============================================================================

@mcp.resource("tasks://list")
def tasks_resource() -> str:
    """Ресурс для доступа к списку всех задач в JSON формате."""
    return json.dumps(tasks_storage, ensure_ascii=False, indent=2)

@mcp.resource("calculator://history")
def calculator_history_resource() -> str:
    """Ресурс для доступа к истории вычислений."""
    return json.dumps(calculator_history, ensure_ascii=False, indent=2)

# =============================================================================
# PROMPTS (Промпты)
# =============================================================================

@mcp.prompt()
def task_summary() -> str:
    """Создать сводку по задачам для ИИ помощника."""
    total = len(tasks_storage)
    completed = len([t for t in tasks_storage if t["completed"]])
    pending = total - completed
    
    high_priority = len([t for t in tasks_storage if t["priority"] == "high" and not t["completed"]])
    
    return f"""Ты персональный помощник по продуктивности. Вот текущая ситуация с задачами пользователя:

📊 Статистика задач:
- Всего задач: {total}
- Выполнено: {completed}
- В ожидании: {pending}
- Высокий приоритет (не выполнено): {high_priority}

Дай краткий анализ продуктивности и советы по управлению задачами."""

@mcp.prompt()
def productivity_tips(focus_area: str = "general") -> str:
    """Промпт для получения советов по продуктивности.
    
    Args:
        focus_area: Область фокуса (general, time_management, task_organization)
    """
    prompts = {
        "general": "Дай 3-5 универсальных советов по повышению продуктивности",
        "time_management": "Дай советы по эффективному управлению временем",
        "task_organization": "Дай советы по организации и приоритизации задач"
    }
    
    base_prompt = prompts.get(focus_area, prompts["general"])
    
    return f"""Ты эксперт по продуктивности и личной эффективности. 

{base_prompt}. 

Сделай ответ практичным, с конкретными действиями, которые можно применить сегодня."""

# =============================================================================
# ЗАПУСК СЕРВЕРА
# =============================================================================

if __name__ == "__main__":
    print("🚀 Запуск Personal Assistant MCP Server...")
    print("📋 Доступные инструменты:")
    print("   • add_task - добавить задачу")
    print("   • get_tasks - получить список задач")
    print("   • complete_task - завершить задачу")
    print("   • calculate - калькулятор")
    print("   • generate_password - генератор паролей")
    print("   • text_stats - анализ текста")
    print()
    print("📦 Доступные ресурсы:")
    print("   • tasks://list - список задач")
    print("   • calculator://history - история вычислений")
    print()
    print("💡 Доступные промпты:")
    print("   • task_summary - сводка по задачам")
    print("   • productivity_tips - советы по продуктивности")
    print()
    
    mcp.run() 