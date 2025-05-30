from src.utils.retriever_storage import save_retriever, load_retriever, delete_retriever, list_retrievers
from src.utils.lesson_generator import get_sumarize, chat_lesson, generate_lesson_plan
from flask import jsonify
import os

def test(lesson_pdf_path, course_id, lesson_number):
    retriever, text_summaries = get_sumarize(lesson_pdf_path)
            
    # Đảm bảo retriever có các thuộc tính cần thiết trước khi lưu
    if not hasattr(retriever, 'vectorstore') or not hasattr(retriever, 'docstore'):
        return jsonify({"error": f"Invalid retriever for lesson {lesson_number}"}), 500

    # Lưu retriever
    save_success = save_retriever(course_id, lesson_number, retriever, text_summaries)
    if not save_success:
        return jsonify({"error": f"Failed to save retriever for lesson {lesson_number}"}), 500
    

test("/Users/admin/Code/AI_CHAT/lesson_plan/src/assets/book/50/chiabuoi/Buoi_1.pdf", "1", "1")
test("/Users/admin/Code/AI_CHAT/lesson_plan/src/assets/book/50/chiabuoi/Buoi_2.pdf", "1", "2")