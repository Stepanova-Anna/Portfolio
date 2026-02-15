# Лабораторная работа №5. RPC. gRPC. Protobuf

### Задание
> Создать полный глоссарий употребляемых терминов по какой-то области (допустим, Python) и спроектировать доступ к нему в виде  Web API в докер-контейнере по образцу brendanburns/dictionary-server (или в иной форме отчуждения/контейнеризации, допускающей быстрое развёртывание на произвольной платформе).

**Система состоит из двух основных микросервисов:**

Glossary Service (сервис глоссария)

- Реализован на gRPC.
- Предоставляет CRUD-операции для работы с терминами.
- Использует Protocol Buffers для сериализации данных.

API Gateway (шлюз)

- Реализован на Python (Flask/FastAPI).
- Предоставляет RESTful API для взаимодействия с клиентами.
- Преобразует HTTP-запросы в gRPC-вызовы к Glossary Service.

*Успешная сборка*

 ![Лабораторная работа 5](https://github.com/Stepanova-Anna/Prog-5-LR-5/blob/main/7.png)

 ![Лабораторная работа 5](https://github.com/Stepanova-Anna/Prog-5-LR-5/blob/main/1.png)

 
**Примеры работы**

Health check

 ![Лабораторная работа 5](https://github.com/Stepanova-Anna/Prog-5-LR-5/blob/main/5.png)

Поиск термина "gRPC"

  ![Лабораторная работа 5](https://github.com/Stepanova-Anna/Prog-5-LR-5/blob/main/4.png)

Список всех терминов

 ![Лабораторная работа 5](https://github.com/Stepanova-Anna/Prog-5-LR-5/blob/main/2.png)

Поиск первого термина

 ![Лабораторная работа 5](https://github.com/Stepanova-Anna/Prog-5-LR-5/blob/main/3.png)

Потоковая передача терминов (SSE)

![Лабораторная работа 5](https://github.com/Stepanova-Anna/Prog-5-LR-5/blob/main/6.png)
