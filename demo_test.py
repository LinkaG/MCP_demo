#!/usr/bin/env python3
"""
Демонстрационный скрипт для тестирования Personal Assistant MCP Server
"""

import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from personal_assistant import (
    add_task, get_tasks, complete_task, 
    calculate, generate_password, text_stats,
    tasks_resource, calculator_history_resource,
    task_summary, productivity_tips
)

def demo_tasks():
    """Демонстрация системы управления задачами"""
    print("🎯 ДЕМОНСТРАЦИЯ: Управление задачами")
    print("=" * 50)
    
    # Добавляем несколько задач
    print("➕ Добавляем задачи:")
    print(add_task("Изучить MCP протокол", "Прочитать документацию и примеры", "high"))
    print(add_task("Написать код", "Реализовать демо проект", "medium"))
    print(add_task("Протестировать", "Запустить все тесты", "low"))
    print()
    
    # Показываем все задачи
    print("📋 Все задачи:")
    print(get_tasks("all"))
    
    # Завершаем одну задачу
    print("✅ Завершаем задачу:")
    print(complete_task(1))
    print()
    
    # Показываем только невыполненные
    print("⏳ Невыполненные задачи:")
    print(get_tasks("pending"))

def demo_calculator():
    """Демонстрация калькулятора"""
    print("🧮 ДЕМОНСТРАЦИЯ: Калькулятор")
    print("=" * 50)
    
    expressions = [
        "2 + 2",
        "10 * 5 - 3",
        "(100 + 50) / 3",
        "2 ** 8"  # степень
    ]
    
    for expr in expressions:
        result = calculate(expr)
        print(f"🔢 {result}")
    print()

def demo_password():
    """Демонстрация генератора паролей"""
    print("🔐 ДЕМОНСТРАЦИЯ: Генератор паролей")
    print("=" * 50)
    
    print("🔑 Короткий пароль без символов:")
    print(generate_password(8, False))
    print()
    
    print("🔑 Длинный пароль с символами:")
    print(generate_password(16, True))
    print()

def demo_text_analysis():
    """Демонстрация анализа текста"""
    print("📊 ДЕМОНСТРАЦИЯ: Анализ текста")
    print("=" * 50)
    
    sample_text = """
    Это демонстрационный текст для анализа. 
    Текст содержит несколько предложений и разные слова.
    MCP протокол очень интересный и полезный инструмент.
    Протокол позволяет интегрировать различные сервисы с ИИ.
    """
    
    print("📝 Анализируемый текст:")
    print(sample_text.strip())
    print()
    
    print("📈 Результат анализа:")
    print(text_stats(sample_text))

def demo_resources():
    """Демонстрация ресурсов"""
    print("📦 ДЕМОНСТРАЦИЯ: Ресурсы")
    print("=" * 50)
    
    print("📋 Ресурс задач (JSON):")
    tasks_json = tasks_resource()
    print(tasks_json[:200] + "..." if len(tasks_json) > 200 else tasks_json)
    print()
    
    print("🧮 История калькулятора (JSON):")
    calc_json = calculator_history_resource()
    print(calc_json[:200] + "..." if len(calc_json) > 200 else calc_json)
    print()

def demo_prompts():
    """Демонстрация промптов"""
    print("💡 ДЕМОНСТРАЦИЯ: Промпты для ИИ")
    print("=" * 50)
    
    print("📊 Сводка по задачам:")
    print(task_summary())
    print()
    
    print("💪 Советы по продуктивности:")
    print(productivity_tips("time_management"))
    print()

def main():
    """Главная функция демонстрации"""
    print("🚀 Personal Assistant MCP Server - ДЕМОНСТРАЦИЯ")
    print("=" * 60)
    print()
    
    # Запускаем все демонстрации
    demo_tasks()
    print("\n" + "="*60 + "\n")
    
    demo_calculator()
    print("\n" + "="*60 + "\n")
    
    demo_password()
    print("\n" + "="*60 + "\n")
    
    demo_text_analysis()
    print("\n" + "="*60 + "\n")
    
    demo_resources()
    print("\n" + "="*60 + "\n")
    
    demo_prompts()
    
    print("✨ Демонстрация завершена!")
    print("🔧 Для запуска MCP сервера используйте: python personal_assistant.py")

if __name__ == "__main__":
    main() 