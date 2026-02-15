# Лабораторная работа 1. Реализация удаленного импорта
## Задание:
>Разместите представленный ниже код локально на компьютере и реализуйте механизм удаленного импорта. Продемонстрируйте в виде скринкаста или в текстовом отчете с несколькими скриншотами работу удаленного импорта.

>По шагам:

>Создайте файл `myremotemodule.py`, который будет импортироваться, разместите его в каталоге, который далее будет "корнем сервера" (допустим, создайте его в папке rootserver).
>Разместите в нём следующий код:
```
def myfoo():
    author = "" # Здесь обознаться своё имя (авторство модуля)
    print(f"{author}'s module is imported")
```
>Создайте файл Python с содержимым функций `url_hook` и классов `URLLoader`, `URLFinder` из текста конспекта лекции со всеми необходимыми библиотеками (допустим, `activation_script.py`).
>Далее, чтобы продемонстрировать работу импорта из удаленного каталога, мы должны запустить сервер http так, чтобы наш желаемый для импорта модуль "лежал" на сервере (например, в корневой директории сервера). Откроем каталог rootserver с файлом myremotemodule.py и запустим там сервер:
```
python3 -m http.server
```
>После этого мы запускаем файл, в котором содержится код, размещенный выше (обязательно добавление в `sys.path_hooks`).
```
python3 -i activation_script.py
```
>Теперь, если мы попытаемся импортировать файл `myremotemodule.py`, в котором размещена наша функция myfoo будет выведен `ModuleNotFoundError: No module named 'myremotemodule'`, потому что такого модуля пока у нас нет (транслятор про него ничего не знает).
Однако, как только мы выполним код:
```
sys.path.append("http://localhost:8000")
```
>добавив путь, где располагается модуль, в `sys.path`, будет срабатывать наш "кастомный" `URLLoader`. В path_hooks будет содержатся наша функция `url_hook`.

>Протестируйте работу удаленного импорта, используя в качестве источника модуля другие "хостинги" (например, repl.it, github pages, beget, sprinthost).
>Переписать содержимое функции `url_hook`, класса `URLLoader` с помощью модуля requests (см. комменты).
>Задание со звездочкой (*): реализовать обработку исключения в ситуации, когда хост (где лежит модуль) недоступен.
>Задание про-уровня (***): реализовать загрузку пакета, разобравшись с аргументами функции `spec_from_loader` и внутренним устройством импорта пакетов.

-------

## Решение:

Проделали все шаги по инструкции

- [Файл `myremotemodule.py`](https://github.com/Stepanova-Anna/Programming-3/blob/main/LR1-5sem/rootserver/myremotemodule.py)
  
- [Файл `activation_script.py`](https://github.com/Stepanova-Anna/Programming-3/blob/main/LR1-5sem/rootserver/activation_script.py)

**Локальный импорт:**

![Лабораторная работа 1. Задание 1](https://github.com/Stepanova-Anna/Programming-3/blob/main/LR1-5sem/7.png)

![Лабораторная работа 1. Задание 1](https://github.com/Stepanova-Anna/Programming-3/blob/main/LR1-5sem/6.png)

-------

**Удаленный импорт на Repl.it:**

### [Repl.it](https://replit.com/@stepanna/LR1-prog-5)

![Лабораторная работа 1. Задание 1](https://github.com/Stepanova-Anna/Programming-3/blob/main/LR1-5sem/8.png)

> Переписать содержимое функции url_hook, класса URLLoader с помощью модуля requests

```
response = requests.get(some_str, timeout=5)
response.raise_for_status()

***

data = response.text
```

> Задание со звездочкой (*): реализовать обработку исключения в ситуации, когда хост (где лежит модуль) недоступен.
 Метод `_handle_exception` обрабатывает все возможные ошибки
```
def _handle_exception(self, exception, url):
    """Обрабатывает исключения и возвращает понятные ImportError"""
    
    # Таймаут соединения
    if isinstance(exception, requests.exceptions.Timeout):
        return ImportError(f"Таймаут подключения: сервер {url} не ответил в течение 10 секунд")
    
    # Ошибки соединения с детальным анализом
    elif isinstance(exception, requests.exceptions.ConnectionError):
        if "Name or service not known" in str(exception):
            return ImportError(f"Хост не найден: {urlparse(url).netloc} не существует")
        elif "Connection refused" in str(exception):
            return ImportError(f"Соединение отклонено: сервер {url} отверг подключение")
        else:
            return ImportError(f"Ошибка соединения: {exception}")
    
    # HTTP ошибки с конкретными кодами
    elif isinstance(exception, requests.exceptions.HTTPError):
        status_code = exception.response.status_code
        if status_code == 404:
            return ImportError(f"Файл не найден (404): {url}")
        elif status_code == 403:
            return ImportError(f"Доступ запрещен (403): {url}")
        elif status_code == 500:
            return ImportError(f"Ошибка сервера (500): {url}")
        else:
            return ImportError(f"HTTP ошибка {status_code}: {url}")
    
    # SSL ошибки
    elif isinstance(exception, requests.exceptions.SSLError):
        return ImportError(f"SSL ошибка: проблема с сертификатом для {url}")
    
    # Слишком много редиректов
    elif isinstance(exception, requests.exceptions.TooManyRedirects):
        return ImportError(f"Слишком много перенаправлений: {url}")
    
    # DNS ошибки
    elif isinstance(exception, socket.gaierror):
        return ImportError(f"Ошибка DNS: хост {urlparse(url).netloc} не найден")
    
    # Другие SSL ошибки
    elif isinstance(exception, ssl.SSLError):
        return ImportError(f"SSL ошибка: {exception}")
    
    # Любые другие неожиданные ошибки
    else:
        return ImportError(f"Неожиданная ошибка при загрузке {url}: {exception}")
```
Обработка в функции `url_hook`
```
# Проверяем доступность хоста с таймаутом
try:
    response = requests.get(
        some_str,
        timeout=8,  # Таймаут для проверки доступности
        headers={'User-Agent': 'Python-URLHook/1.0'},
        allow_redirects=True
    )
    response.raise_for_status()

except requests.exceptions.Timeout:
    raise ImportError(f"Хост недоступен: {some_str} не отвечает (таймаут 8с)")

except requests.exceptions.ConnectionError as e:
    # Детальный анализ ошибок соединения
    error_msg = str(e).lower()
    if "name or service not known" in error_msg:
        raise ImportError(f"DNS ошибка: хост {parsed_url.netloc} не существует")
    elif "connection refused" in error_msg:
        raise ImportError(f"Соединение отклонено: {some_str}")
    else:
        raise ImportError(f"Ошибка соединения: {some_str} - {e}")

except requests.exceptions.HTTPError as e:
    raise ImportError(f"HTTP ошибка {e.response.status_code}: {some_str}")
```

> Задание про-уровня (***): реализовать загрузку пакета, разобравшись с аргументами функции spec_from_loader и внутренним устройством импорта пакетов
```
def _create_package_spec(self, package_name):
    """Создает спецификацию для пакета"""
    package_url = f"{self.base_url}/{package_name}"

    loader = PackageLoader(package_url, package_name)

    return spec_from_loader(
        package_name,
        loader,
        origin=f"{package_url}/__init__.py",  # Указываем __init__.py
        is_package=True,  # Ключевой параметр!
        submodule_search_locations=[package_url]  # Пути для поиска подмодулей
    )
```
Обнаружение пакетов
```
def discover_packages_and_modules(url):
    # Ищем директории (пакеты)
    directories = re.findall(r'href="([a-zA-Z_][a-zA-Z0-9_]*)/"', data)
    packages.update({
        d for d in directories
        if not d.startswith(('.', '_')) and d not in ['static', 'templates', 'tests']
    })

    # Проверяем, какие пакеты действительно содержат __init__.py
    valid_packages = set()
    for package in packages:
        init_url = f"{url.rstrip('/')}/{package}/__init__.py"
        response = requests.head(init_url, timeout=3)
        if response.status_code == 200:  # __init__.py существует!
            valid_packages.add(package)
```
