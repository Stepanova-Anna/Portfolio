import json
from datetime import datetime
from typing import Dict, List, Optional
import redis


class GlossaryStorage:
    def __init__(self, host='redis', port=6379, db=0):
        try:
            self.redis = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Проверка подключения
            self.redis.ping()
            print(f"Connected to Redis at {host}:{port}")
            self._initialize_data()
        except Exception as e:
            print(f"Error connecting to Redis: {e}")
            # Fallback: хранение в памяти
            self.in_memory_storage = {}
            self.redis = None
            self._initialize_in_memory()

    def _initialize_data(self):
        """Инициализация начальными данными о Python"""
        if not self.redis.exists('term:list'):
            print("Initializing glossary data in Redis...")
            initial_terms = self._get_initial_terms()

            for term in initial_terms:
                term_id = term['id']
                # Сериализуем списки в строки JSON перед сохранением
                term_copy = term.copy()
                if isinstance(term_copy.get('examples'), list):
                    term_copy['examples'] = json.dumps(term_copy['examples'])
                if isinstance(term_copy.get('synonyms'), list):
                    term_copy['synonyms'] = json.dumps(term_copy['synonyms'])

                self.redis.hset(f'term:{term_id}', mapping=term_copy)
                self.redis.sadd('term:list', term_id)
                self.redis.sadd(f'category:{term["category"]}', term_id)

            print(f"Initialized {len(initial_terms)} terms")

    def _initialize_in_memory(self):
        """Инициализация данных в памяти если Redis недоступен"""
        print("Using in-memory storage")
        self.in_memory_storage = {}
        initial_terms = self._get_initial_terms()
        for term in initial_terms:
            self.in_memory_storage[term['id']] = term

    def _get_initial_terms(self):
        """Получение начальных терминов"""
        now = datetime.now().isoformat()
        return [
            {
                'id': '1',
                'name': 'Protobuf',
                'definition': 'Механизм сериализации данных, разработанный компанией Google для эффективного обмена структурированными данными между системами.',
                'category': 'Data Serialization',
                'examples': ["gRPC communication", "configuration files"],
                'synonyms': ["Protocol Buffers", "protobuf"],
                'created_at': now,
                'updated_at': now
            },
            {
                'id': '2',
                'name': 'gRPC',
                'definition': 'Высокопроизводительный фреймворк для удаленного вызова процедур (RPC), использующий HTTP/2 и Protocol Buffers.',
                'category': 'RPC Framework',
                'examples': ["microservices communication", "streaming APIs"],
                'synonyms': ["Google RPC", "gRPC"],
                'created_at': now,
                'updated_at': now
            },
            {
                'id': '3',
                'name': 'Docker',
                'definition': 'Платформа для разработки, доставки и запуска приложений в контейнерах.',
                'category': 'Containerization',
                'examples': ["application deployment", "development environments"],
                'synonyms': ["Container platform", "Docker Engine"],
                'created_at': now,
                'updated_at': now
            },
            {
                'id': '4',
                'name': 'REST',
                'definition': 'Архитектурный стиль для разработки распределенных систем, использующий HTTP протокол.',
                'category': 'API Design',
                'examples': ["web APIs", "CRUD operations"],
                'synonyms': ["RESTful", "REST API"],
                'created_at': now,
                'updated_at': now
            },
            {
                'id': '5',
                'name': 'Streaming',
                'definition': 'Технология передачи данных в реальном времени в виде непрерывного потока.',
                'category': 'Data Transfer',
                'examples': ["video streaming", "real-time updates"],
                'synonyms': ["data streaming", "real-time streaming"],
                'created_at': now,
                'updated_at': now
            }
        ]

    def get_term(self, term_id: str) -> Optional[Dict]:
        """Получить термин по ID"""
        if self.redis:
            term_data = self.redis.hgetall(f'term:{term_id}')
            if term_data:
                # Десериализация JSON полей
                if 'examples' in term_data:
                    try:
                        term_data['examples'] = json.loads(term_data['examples'])
                    except:
                        term_data['examples'] = []
                if 'synonyms' in term_data:
                    try:
                        term_data['synonyms'] = json.loads(term_data['synonyms'])
                    except:
                        term_data['synonyms'] = []
            return term_data
        else:
            return self.in_memory_storage.get(term_id)

    def get_all_terms(self) -> List[Dict]:
        """Получить все термины"""
        if self.redis:
            term_ids = self.redis.smembers('term:list')
            terms = []
            for term_id in term_ids:
                term = self.redis.hgetall(f'term:{term_id}')
                if term:
                    # Десериализация JSON полей
                    if 'examples' in term:
                        try:
                            term['examples'] = json.loads(term['examples'])
                        except:
                            term['examples'] = []
                    if 'synonyms' in term:
                        try:
                            term['synonyms'] = json.loads(term['synonyms'])
                        except:
                            term['synonyms'] = []
                    terms.append(term)
            return terms
        else:
            return list(self.in_memory_storage.values())

    def search_terms(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """Поиск терминов"""
        results = []
        all_terms = self.get_all_terms()

        for term in all_terms:
            # Фильтр по категории
            if category and term.get('category') != category:
                continue

            # Поиск по названию и определению
            query_lower = query.lower()
            name = term.get('name', '').lower()
            definition = term.get('definition', '').lower()

            if query_lower in name or query_lower in definition:
                results.append(term)

        return results

    def add_term(self, term_data: Dict) -> str:
        """Добавить новый термин"""
        if self.redis:
            # Генерация ID
            term_id = str(self.redis.incr('term:counter', 1))
            if term_id == '1':  # Если счетчик только создан
                term_id = '6'  # Продолжаем с 6, так как у нас уже есть 1-5
        else:
            term_id = str(len(self.in_memory_storage) + 1)

        term_data['id'] = term_id
        term_data['created_at'] = datetime.now().isoformat()
        term_data['updated_at'] = datetime.now().isoformat()

        # Сериализация списков в JSON
        if 'examples' in term_data and isinstance(term_data['examples'], list):
            term_data['examples'] = json.dumps(term_data['examples'])
        if 'synonyms' in term_data and isinstance(term_data['synonyms'], list):
            term_data['synonyms'] = json.dumps(term_data['synonyms'])

        if self.redis:
            # Сохранение в Redis
            self.redis.hset(f'term:{term_id}', mapping=term_data)
            self.redis.sadd('term:list', term_id)
            self.redis.sadd(f'category:{term_data["category"]}', term_id)
        else:
            # Сохранение в памяти
            self.in_memory_storage[term_id] = term_data

        return term_id

    def delete_term(self, term_id: str) -> bool:
        """Удалить термин"""
        if self.redis:
            # Получаем данные термина для удаления из категории
            term = self.redis.hgetall(f'term:{term_id}')
            if not term:
                return False

            # Удаляем из всех коллекций
            self.redis.delete(f'term:{term_id}')
            self.redis.srem('term:list', term_id)
            category = term.get('category')
            if category:
                self.redis.srem(f'category:{category}', term_id)

            return True
        else:
            if term_id in self.in_memory_storage:
                del self.in_memory_storage[term_id]
                return True
            return False