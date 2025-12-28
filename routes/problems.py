from flask import Blueprint, jsonify, request
from models.challenge import Challenge
from extensions import db

problems_bp = Blueprint('problems', __name__)

# 문제 목록 조회
@problems_bp.route('/problems', methods=['GET'])
def get_problems():
    try:
        # 데이터베이스에서 문제 목록 가져오기
        problems = Challenge.query.all()
        
        # 문제 목록을 JSON 형태로 변환
        result = [
            {
                'id': problem.id,
                'title': problem.title,
                'difficulty': problem.difficulty,
                'tags': problem.tags
            }
            for problem in problems
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 문제 상세정보 조회
@problems_bp.route('/problems/<int:problem_id>', methods=['GET'])
def get_problem_detail(problem_id):
    try:
        # 특정 문제 가져오기
        problem = Challenge.query.get(problem_id)
        
        if not problem:
            return jsonify({'error': 'Problem not found'}), 404

        # 문제 상세정보를 JSON 형태로 변환
        result = {
            'id': problem.id,
            'title': problem.title,
            'description': problem.description,
            'difficulty': problem.difficulty,
            'tags': problem.tags,
            'author': problem.author
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500