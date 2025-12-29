from flask import Blueprint, jsonify, request
from models.challenge import Challenge
from extensions import db

challenges_bp = Blueprint('challenges', __name__)

# 문제 목록 조회
@challenges_bp.route('/challenges', methods=['GET'])
def get_challenges():
    try:
        # 데이터베이스에서 문제 목록 가져오기
        challenges = Challenge.query.all()
        
        # 문제 목록을 JSON 형태로 변환
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
        # 특정 문제 가져오기
        challenge = Challenge.query.get(id)
        
        if not challenge:
            return jsonify({'error': 'Challenge not found'}), 404

        # 문제 상세정보를 JSON 형태로 변환
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