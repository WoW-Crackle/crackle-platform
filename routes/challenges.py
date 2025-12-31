from flask import Blueprint, jsonify, request, abort
from models.challenge import Challenge
from extensions import db

challenges_bp = Blueprint('challenges', __name__)

# 문제 목록 조회
@challenges_bp.route('/challenges', methods=['GET'])
def get_challenges():
    try:
        challenges = Challenge.query.all()

        result = [
            {
                'id': challenge.id,
                'title': challenge.title,
                'difficulty': challenge.difficulty,
                'tags': challenge.tags
            }
            for challenge in challenges
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 문제 상세정보 조회
@challenges_bp.route('/challenges/<int:id>', methods=['GET'])
def get_challenge_detail(id):
    try:
        challenge = Challenge.query.get(id)
        if not challenge:
            abort(404, description="Challenge not found")

        result = {
            'id': challenge.id,
            'title': challenge.title,
            'description': challenge.description,
            'difficulty': challenge.difficulty,
            'tags': challenge.tags,
            'author': challenge.author
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500