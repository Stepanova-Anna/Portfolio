from flask import Flask, request, jsonify
from flask_cors import CORS
import grpc
import json
import os
import sys

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем protobuf модули
try:
    import glossary_pb2
    import glossary_pb2_grpc

    print("Successfully imported protobuf modules")
except ImportError as e:
    print(f"Import error: {e}")
    print("Current directory:", os.getcwd())
    print("Files:", os.listdir('.'))
    raise

app = Flask(__name__)
CORS(app)

# Конфигурация gRPC канала
GRPC_SERVER = os.getenv('GRPC_SERVER', 'glossary-service:50051')
print(f"API Gateway starting, connecting to gRPC at: {GRPC_SERVER}")


def get_grpc_stub():
    """Создание gRPC подключения"""
    try:
        channel = grpc.insecure_channel(GRPC_SERVER)
        return glossary_pb2_grpc.GlossaryServiceStub(channel)
    except Exception as e:
        print(f"Error creating gRPC channel: {e}")
        return None


@app.route('/')
def index():
    """Главная страница"""
    return jsonify({
        "service": "Python Glossary API Gateway",
        "version": "1.0",
        "endpoints": {
            "/api/health": "GET - Health check",
            "/api/terms": "GET - Get all terms",
            "/api/terms/<id>": "GET - Get term by ID",
            "/api/terms/search?q=<query>": "GET - Search terms",
            "/api/terms": "POST - Add new term",
            "/api/terms/<id>": "DELETE - Delete term",
            "/api/terms/stream": "GET - Stream terms (SSE)"
        }
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервиса"""
    return jsonify({
        "status": "healthy",
        "service": "Python Glossary API Gateway",
        "grpc_server": GRPC_SERVER,
        "timestamp": "2024-01-01T00:00:00Z"  # В реальном приложении используйте datetime
    })


@app.route('/api/terms', methods=['GET'])
def get_all_terms():
    """Получить все термины"""
    print("GET /api/terms called")
    try:
        stub = get_grpc_stub()
        if not stub:
            return jsonify({'error': 'gRPC service unavailable'}), 503

        response = stub.GetAllTerms(glossary_pb2.Empty())

        terms_list = []
        for term in response.terms:
            terms_list.append({
                'id': term.id,
                'name': term.name,
                'definition': term.definition,
                'category': term.category,
                'examples': list(term.examples),
                'synonyms': list(term.synonyms),
                'created_at': term.created_at,
                'updated_at': term.updated_at
            })

        return jsonify({
            'terms': terms_list,
            'total': response.total_count
        })
    except Exception as e:
        print(f"Error in get_all_terms: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/terms/<term_id>', methods=['GET'])
def get_term(term_id):
    """Получить термин по ID"""
    print(f"GET /api/terms/{term_id} called")
    try:
        stub = get_grpc_stub()
        if not stub:
            return jsonify({'error': 'gRPC service unavailable'}), 503

        request_msg = glossary_pb2.TermRequest(id=term_id)
        term = stub.GetTerm(request_msg)

        if not term.id:
            return jsonify({'error': 'Term not found'}), 404

        return jsonify({
            'id': term.id,
            'name': term.name,
            'definition': term.definition,
            'category': term.category,
            'examples': list(term.examples),
            'synonyms': list(term.synonyms),
            'created_at': term.created_at,
            'updated_at': term.updated_at
        })
    except Exception as e:
        print(f"Error in get_term: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/terms/search', methods=['GET'])
def search_terms():
    """Поиск терминов"""
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    limit = int(request.args.get('limit', 10))
    print(f"GET /api/terms/search called: q={query}, category={category}")

    try:
        stub = get_grpc_stub()
        if not stub:
            return jsonify({'error': 'gRPC service unavailable'}), 503

        request_msg = glossary_pb2.SearchRequest(
            query=query,
            category=category,
            limit=limit
        )

        response = stub.SearchTerms(request_msg)

        terms_list = []
        for term in response.terms:
            terms_list.append({
                'id': term.id,
                'name': term.name,
                'definition': term.definition,
                'category': term.category,
                'examples': list(term.examples),
                'synonyms': list(term.synonyms)
            })

        return jsonify({
            'terms': terms_list,
            'total': response.total_count,
            'query': query
        })
    except Exception as e:
        print(f"Error in search_terms: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/terms', methods=['POST'])
def add_term():
    """Добавить новый термин"""
    print("POST /api/terms called")
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        stub = get_grpc_stub()
        if not stub:
            return jsonify({'error': 'gRPC service unavailable'}), 503

        request_msg = glossary_pb2.AddTermRequest(
            name=data.get('name', ''),
            definition=data.get('definition', ''),
            category=data.get('category', 'General'),
            examples=data.get('examples', []),
            synonyms=data.get('synonyms', [])
        )

        response = stub.AddTerm(request_msg)

        if response.success:
            return jsonify({
                'success': True,
                'message': response.message,
                'term_id': response.term_id
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': response.message
            }), 400
    except Exception as e:
        print(f"Error in add_term: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/terms/<term_id>', methods=['DELETE'])
def delete_term(term_id):
    """Удалить термин"""
    print(f"DELETE /api/terms/{term_id} called")
    try:
        stub = get_grpc_stub()
        if not stub:
            return jsonify({'error': 'gRPC service unavailable'}), 503

        request_msg = glossary_pb2.TermRequest(id=term_id)
        response = stub.DeleteTerm(request_msg)

        if response.success:
            return jsonify({
                'success': True,
                'message': response.message
            })
        else:
            return jsonify({
                'success': False,
                'error': response.message
            }), 404
    except Exception as e:
        print(f"Error in delete_term: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/terms/stream', methods=['GET'])
def stream_terms():
    """Потоковая передача терминов (SSE)"""
    category = request.args.get('category', '')
    batch_size = int(request.args.get('batch_size', 1))
    print(f"GET /api/terms/stream called: category={category}")

    def generate():
        try:
            stub = get_grpc_stub()
            if not stub:
                yield f"data: {json.dumps({'error': 'gRPC service unavailable'})}\n\n"
                return

            request_msg = glossary_pb2.StreamRequest(
                category=category,
                batch_size=batch_size
            )

            for term in stub.StreamTerms(request_msg):
                data_dict = {
                    'id': term.id,
                    'name': term.name,
                    'definition': term.definition[:100] + "..." if len(term.definition) > 100 else term.definition,
                    'category': term.category
                }
                yield f"data: {json.dumps(data_dict)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return app.response_class(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


if __name__ == '__main__':
    print(f"Starting Flask app on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)