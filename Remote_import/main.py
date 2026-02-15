import sys
import os


sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rootserver'))


from activation_script import url_hook

sys.path_hooks.append(url_hook)


def demo_remote_import():
    """Демонстрация удаленного импорта"""

    print("=== ДЕМОНСТРАЦИЯ УДАЛЕННОГО ИМПОРТА ===\n")

    # Добавляем локальный сервер
    local_host = "http://localhost:8000"
    sys.path.append(local_host)
    print(f"Добавлен хост: {local_host}")

    # 1. Импорт простого модуля
    print("\n1. Импорт простого модуля:")
    try:
        import myremotemodule
        result = myremotemodule.myfoo()
        print(f"Результат: {result}")

        # Тестируем вычисления
        calc_result = myremotemodule.remote_calc(10, 5)
        print(f"Вычисления: {calc_result}")
    except Exception as e:
        print(f"Ошибка: {e}")

    # 2. Тестирование недоступного хоста
    print("\n2. Тестирование недоступного хоста:")
    try:
        sys.path.append("http://nonexistent-domain-12345.com")
        import some_module
    except Exception as e:
        print(f"Ожидаемая ошибка: {e}")
        sys.path.remove("http://nonexistent-domain-12345.com")

    # 3. Демонстрация с разными хостами
    print("\n3. Запустите отдельно test_hosts.py для тестирования разных хостов")
    print("   python rootserver/test_hosts.py")


if __name__ == "__main__":
    demo_remote_import()