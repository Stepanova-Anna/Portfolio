import grpc
import glossary_pb2
import glossary_pb2_grpc


def run():
    # Подключение к серверу
    channel = grpc.insecure_channel('localhost:50051')
    stub = glossary_pb2_grpc.GlossaryServiceStub(channel)

    print("=== Python Glossary gRPC Client ===\n")

    # 1. Получить все термины
    print("1. Получение всех терминов:")
    all_terms = stub.GetAllTerms(glossary_pb2.Empty())
    for term in all_terms.terms:
        print(f"  - {term.name} ({term.category})")
    print(f"Всего терминов: {all_terms.total_count}\n")

    # 2. Получить конкретный термин
    print("2. Получение термина по ID:")
    term = stub.GetTerm(glossary_pb2.TermRequest(id="1"))
    print(f"  Название: {term.name}")
    print(f"  Определение: {term.definition}")
    print(f"  Примеры: {', '.join(term.examples)}\n")

    # 3. Поиск терминов
    print("3. Поиск терминов:")
    search_results = stub.SearchTerms(
        glossary_pb2.SearchRequest(query="stream", limit=3)
    )
    for result in search_results.terms:
        print(f"  - {result.name}: {result.definition[:50]}...")
    print(f"Найдено: {search_results.total_count}\n")

    # 4. Добавление нового термина
    print("4. Добавление нового термина:")
    new_term = stub.AddTerm(
        glossary_pb2.AddTermRequest(
            name="Microservices",
            definition="Архитектурный стиль, при котором приложение состоит из небольших независимых сервисов.",
            category="Architecture",
            examples=["gRPC communication", "Docker containers"],
            synonyms=["distributed services", "service-oriented architecture"]
        )
    )
    print(f"  Результат: {new_term.message}")
    print(f"  ID нового термина: {new_term.term_id}\n")

    # 5. Потоковая передача терминов
    print("5. Потоковая передача терминов:")
    stream_request = glossary_pb2.StreamRequest(batch_size=2)
    stream = stub.StreamTerms(stream_request)

    count = 0
    for term in stream:
        count += 1
        print(f"  Получен термин {count}: {term.name}")
        if count >= 5:  # Ограничим вывод
            break

    # 6. Удаление термина
    print(f"\n6. Удаление термина:")
    if new_term.term_id:
        delete_result = stub.DeleteTerm(
            glossary_pb2.TermRequest(id=new_term.term_id)
        )
        print(f"  Результат удаления: {delete_result.message}")


if __name__ == '__main__':
    run()