from flask import Blueprint, jsonify, request
from models.challenge import Challenge
from extensions import db
from sqlalchemy.exc import SQLAlchemyError

challenges_bp = Blueprint('challenges', __name__)

# 문제 목록 조회
@challenges_bp.route('/challenges', methods=['GET'])
def get_challenges():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        pagination = Challenge.query.paginate(page=page, per_page=per_page, error_out=False)
        
        result = [
            {
                'id': challenge.id,
                'title': challenge.title,
                'difficulty': challenge.difficulty,
                'tags': challenge.tags
            }
            for challenge in pagination.items
        ]
        return jsonify({
            'challenges': result,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 문제 상세정보 조회
@challenges_bp.route('/challenges/<int:id>', methods=['GET'])
def get_challenge_detail(id):
    try:
        challenge = Challenge.query.get_or_404(id)

        result = {
            'id': challenge.id,
            'title': challenge.title,
            'description': challenge.description,
            'difficulty': challenge.difficulty,
            'tags': challenge.tags,
            'author': challenge.author
        }
        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500