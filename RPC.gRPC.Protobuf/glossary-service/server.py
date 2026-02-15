import grpc
from concurrent import futures
import logging
from datetime import datetime

import glossary_pb2
import glossary_pb2_grpc
from glossary_data import GlossaryStorage


class GlossaryServicer(glossary_pb2_grpc.GlossaryServiceServicer):
    def __init__(self):
        self.storage = GlossaryStorage()

    def GetTerm(self, request, context):
        """Получить термин по ID"""
        term_id = request.id
        term_data = self.storage.get_term(term_id)

        if not term_data:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Term with id {term_id} not found")
            return glossary_pb2.Term()

        return self._dict_to_term_proto(term_data)

    def GetAllTerms(self, request, context):
        """Получить все термины"""
        terms_data = self.storage.get_all_terms()
        terms = [self._dict_to_term_proto(term) for term in terms_data]

        return glossary_pb2.TermList(
            terms=terms,
            total_count=len(terms)
        )

    def SearchTerms(self, request, context):
        """Поиск терминов"""
        terms_data = self.storage.search_terms(
            query=request.query,
            category=request.category if request.category else None
        )

        if request.limit > 0:
            terms_data = terms_data[:request.limit]

        terms = [self._dict_to_term_proto(term) for term in terms_data]

        return glossary_pb2.TermList(
            terms=terms,
            total_count=len(terms)
        )

    def AddTerm(self, request, context):
        """Добавить новый термин"""
        term_data = {
            'name': request.name,
            'definition': request.definition,
            'category': request.category,
            'examples': list(request.examples),
            'synonyms': list(request.synonyms)
        }

        try:
            term_id = self.storage.add_term(term_data)
            return glossary_pb2.OperationResponse(
                success=True,
                message="Term added successfully",
                term_id=term_id
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return glossary_pb2.OperationResponse(
                success=False,
                message=f"Error adding term: {str(e)}",
                term_id=""
            )

    def DeleteTerm(self, request, context):
        """Удалить термин"""
        success = self.storage.delete_term(request.id)

        if success:
            return glossary_pb2.OperationResponse(
                success=True,
                message="Term deleted successfully",
                term_id=request.id
            )
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return glossary_pb2.OperationResponse(
                success=False,
                message=f"Term with id {request.id} not found",
                term_id=request.id
            )

    def StreamTerms(self, request, context):
        """Потоковая передача терминов"""
        all_terms = self.storage.get_all_terms()

        # Фильтрация по категории
        if request.category:
            all_terms = [
                term for term in all_terms
                if term.get('category') == request.category
            ]

        batch_size = request.batch_size or 1

        for i in range(0, len(all_terms), batch_size):
            batch = all_terms[i:i + batch_size]
            for term_data in batch:
                yield self._dict_to_term_proto(term_data)

    def _dict_to_term_proto(self, term_dict):
        """Конвертация словаря в protobuf сообщение"""
        return glossary_pb2.Term(
            id=term_dict.get('id', ''),
            name=term_dict.get('name', ''),
            definition=term_dict.get('definition', ''),
            category=term_dict.get('category', ''),
            examples=term_dict.get('examples', []),
            synonyms=term_dict.get('synonyms', []),
            created_at=term_dict.get('created_at', ''),
            updated_at=term_dict.get('updated_at', '')
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    glossary_pb2_grpc.add_GlossaryServiceServicer_to_server(
        GlossaryServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Glossary gRPC Server started on port 50051")
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()