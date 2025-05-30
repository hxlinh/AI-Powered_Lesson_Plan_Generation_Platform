from flask import Flask, jsonify, request
import json
from flask_cors import CORS
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime
import shutil
from src.utils.pdf_processor import process_pdf
from src.utils.clo_generator import chat_CLO
from src.utils.syllabus_generator import chat_syllabus
from src.utils.seperator import chiasach, chiabuoi
from src.utils.lesson_generator import get_sumarize, chat_lesson, generate_lesson_plan
from src.utils.retriever_storage import save_retriever, load_retriever, delete_retriever, list_retrievers

# lesson_retrievers = {}
# lesson_summarize = {}

app = Flask(__name__)
CORS(app)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'src', 'assets', 'content', 'data.json')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'src', 'assets', 'book')


# Đảm bảo thư mục upload tồn tại
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def read_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as file:
        return json.load(file)


def write_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


@app.route('/courses', methods=['GET'])
def get_courses():
    return jsonify(read_data())


@app.route('/update-data', methods=['POST'])
def update_data():
    data = request.json
    write_data(data)
    return jsonify({'message': 'Cập nhật thành công'})

@app.route('/process-pdf', methods=['POST'])
def process_pdf_endpoint():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Không tìm thấy file"}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "Không có file nào được chọn"}), 400
            
        # Save file temporarily
        temp_path = os.path.join(UPLOAD_FOLDER, "temp_process.pdf")
        file.save(temp_path)
        
        # Process PDF
        pdf_info = process_pdf(temp_path)
        
        # Xóa file tạm sau khi xử lý
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify({
            "success": True,
            "book": pdf_info["book"],
            "content": pdf_info["content"]
        })
    
    except Exception as e:
        print(f"Error in process_pdf_endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/create-course', methods=['POST'])
def create_course():
    try:
        file = request.files['file']
        subject = request.form['subject']
        number_lesson = request.form['numberLesson']
        duration_lesson = request.form['durationLesson']
        
        # Nhận thông tin đã được chỉnh sửa
        book_name = request.form.get('bookName', '')
        book_content = request.form.get('bookContent', '')
        
        # Save file temporarily
        temp_path = os.path.join(UPLOAD_FOLDER, "temp.pdf")
        file.save(temp_path)
        
        # Nếu không có thông tin sách đã chỉnh sửa, xử lý PDF để lấy thông tin
        if not book_name or not book_content:
            pdf_info = process_pdf(temp_path)
        else:
            pdf_info = {
                "book": book_name,
                "content": book_content
            }
        # _,max=process_pdf(temp_path)
        # max=max-1
        # Get current courses and generate new ID
        courses = read_data()
        new_id = max([course['id'] for course in courses], default=0) + 1
        
        # Create directory for the new course
        course_dir = os.path.join(UPLOAD_FOLDER, str(new_id), "book_origin")
        os.makedirs(course_dir, exist_ok=True)
        
        # Move PDF to final location
        final_path = os.path.join(course_dir, secure_filename(file.filename))
        shutil.move(temp_path, final_path)

        chiasach_dir = os.path.join(UPLOAD_FOLDER, str(new_id), "chiasach")
        chiasach(pdf_info['content'], final_path, chiasach_dir)

        initial_prompt = f"""Hãy soạn thảo chuẩn đầu ra học phần (CLOs - Course Learning Outcomes) cho một môn học dựa trên nội dung sách được cung cấp.
# Môn học: {subject}
# Chuẩn đầu ra chương trình đào tạo (PLO - Program Learning Outcomes): Người học tốt nghiệp Chương trình đào tạo kỹ sư CLC Việt-Pháp (PFIEV), chuyên ngành Công nghệ phần mềm - Công nghệ thông tin, Trường Đại học Bách khoa - Đại học Đà Nẵng đáp ứng yêu cầu chuẩn đầu ra bậc 7 theo Khung trình độ quốc gia Việt Nam:
PLO1. Có kiến thức và hiểu biết chuyên sâu về toán học, khoa học và các nguyên lý kỹ thuật để xác định, trình bày và giải quyết các vấn đề mới, phức tạp trong lĩnh vực Công nghệ thông tin, chuyên ngành công nghệ phần mềm và các lĩnh vực liên quan khác;
PLO2. Có khả năng áp dụng thiết kế kỹ thuật phù hợp nhất hoặc sử dụng sự sáng tạo của cá nhân để đưa ra các giải pháp đáp ứng với các yêu cầu thực tiễn về sức khỏe cộng đồng, an ninh, phúc lợi cũng như các yếu tố liên quan đến toàn cầu, văn hoá, xã hội, môi trường và kinh tế;
PLO3. Có khả năng truyền đạt kiến thức bằng nhiều phương pháp khác nhau, khả năng giao tiếp rõ ràng với người nghe trong chuyên ngành và không thuộc chuyên ngành;
PLO4. Có khả năng nhận thức trách nhiệm đạo đức và nghề nghiệp trong các tình huống kỹ thuật và trong việc đưa ra những đánh giá sáng suốt có xem xét tác động của các giải pháp kỹ thuật trong bối cảnh toàn cầu, kinh tế, môi trường và xã hội;
PLO5. Có khả năng hoạt động hiệu quả trong bối cảnh quốc gia và quốc tế, thiết lập mục tiêu, lập kế hoạch nhiệm vụ và đáp ứng các mục tiêu, với vai trò là thành viên nhóm hoặc lãnh đạo trong nhóm, tạo ra môi trường hợp tác toàn diện đa dạng về văn hóa;
PLO6. Có khả năng thu thập thông tin, tiến hành thử nghiệm nâng cao, phân tích và giải thích dữ liệu, tạo ra được sự mô phỏng và sử dụng phán đoán kỹ thuật để có được khảo sát chi tiết và nghiên cứu các vấn đề kỹ thuật phức tạp hoặc đưa ra kết luận
PLO7. Có khả năng tự tích luỹ và áp dụng kiến thức mới khi cần thiết, sử dụng các chiến lược học tập phù hợp;
PLO8. Có khả năng thể hiện tư duy phản biện, đổi mới sáng tạo, tổ chức, quản lý, quản trị hoạt động nghề nghiệp tiên tiến; có tư duy khởi nghiệp;
PLO9. Có trình độ tiếng Anh là TOEIC 600 hoặc tương đương; có trình độ tiếng Pháp là DELF B1 hoặc tương đương.
# Tên sách: {pdf_info['book']}
# Nội dung sách: 
{pdf_info['content']}
        """

        # Thêm timestamp cho tin nhắn
        current_time = datetime.now().strftime("%H:%M:%S")

        # Generate CLOs
        initial_clo = chat_CLO(
            conversation_history=[],
            user_input = initial_prompt
        )

        # Create new course data
        new_course = {
            "id": new_id,
            "subject": subject,
            "date": datetime.now().strftime("%d-%m-%Y"),
            "book": pdf_info["book"],
            "content": pdf_info["content"],
            "number_lesson": int(number_lesson),
            "duration_lesson": int(duration_lesson),
            "message_CLOs": [
                {"role": "user", "content": initial_prompt, "timestamp": current_time},
                {"role": "assistant", "content": initial_clo, "timestamp": datetime.now().strftime("%H:%M:%S")}
            ]
        }
        
        # Update JSON file
        courses.append(new_course)
        write_data(courses)
        
        return jsonify({"success": True, "id": new_id})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/delete-course/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    try:
        # Read current data
        courses = read_data()
        
        # Remove course from data
        courses = [course for course in courses if course['id'] != course_id]
        
        # Save updated data
        write_data(courses)
        
        # Delete course folder
        course_folder = os.path.join(UPLOAD_FOLDER, str(course_id))
        if os.path.exists(course_folder):
            shutil.rmtree(course_folder)
        
        # Delete all retrievers for this course
        delete_retriever(course_id)
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error deleting course: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/initialize-syllabus', methods=['POST'])
def initialize_syllabus():
    try:
        data = request.json
        course_id = data['courseId']
        selected_clo = data['selectedCLO']
        
        courses = read_data()
        course = next((c for c in courses if c['id'] == course_id), None)
        
        if not course:
            return jsonify({"error": "Course not found"}), 404
            
        initial_prompt = f"""Hãy soạn thảo kế hoạch giảng dạy và học tập (Course Syllabus) cho một môn học dựa trên những nội dung được cung cấp
        #Môn học: {course['subject']}
        #Chuẩn đầu ra học phần (CLOs):
        {selected_clo}
        #Tên sách: {course['book']}
        #Nội dung sách: 
        {course['content']}
        #Thời lượng khóa học: {course['number_lesson']} buổi, mỗi buổi: {course['duration_lesson']} giờ.
        """

        # Thêm timestamp cho tin nhắn
        current_time = datetime.now().strftime("%H:%M:%S")

        # Generate Course Syllabus with empty conversation history
        initial_response = chat_syllabus([], initial_prompt)
        
        # Đánh dấu CLO đã được like
        for i, msg in enumerate(course['message_CLOs']):
            if msg['role'] == 'assistant' and msg['content'] == selected_clo:
                course['message_CLOs'][i]['liked'] = True
        
        course['message_CS'] = [
            {"role": "user", "content": initial_prompt, "timestamp": current_time},
            {"role": "assistant", "content": initial_response, "timestamp": datetime.now().strftime("%H:%M:%S")}
        ]
        
        write_data(courses)
        
        return jsonify({
            "success": True,
            "message": initial_response,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        course_id = data['courseId']
        user_message = data['message']
        chat_type = data['chatType']
        
        # Đọc dữ liệu hiện tại
        courses = read_data()
        course = next((c for c in courses if c['id'] == course_id), None)
        
        if not course:
            return jsonify({"error": "Course not found"}), 404
            
        # Xác định trường message và hàm chat tương ứng
        if chat_type == "CLOs":
            message_field = "message_CLOs"
            chat_function = chat_CLO
        elif chat_type == "Course Syllabus":
            message_field = "message_CS"
            chat_function = chat_syllabus
        else:
            return jsonify({"error": "Invalid chat type"}), 400
            
        # Lấy lịch sử chat
        conversation_history = [
            {"role": m["role"], "content": m["content"]} 
            for m in course[message_field]
        ]
        
        # Thêm timestamp cho tin nhắn người dùng
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Gọi hàm chat tương ứng
        response = chat_function(conversation_history, user_message)
        
        # Cập nhật lịch sử chat với timestamp
        course[message_field].extend([
            {"role": "user", "content": user_message, "timestamp": current_time},
            {"role": "assistant", "content": response, "timestamp": datetime.now().strftime("%H:%M:%S")}
        ])
        
        write_data(courses)
        
        return jsonify({
            "success": True,
            "message": response,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/split-sessions', methods=['POST'])
def split_sessions():
    try:
        data = request.json
        course_id = data['courseId']
        message_content = data['message']
        
        # Đọc dữ liệu hiện tại
        courses = read_data()
        course = next((c for c in courses if c['id'] == course_id), None)
        
        if not course:
            return jsonify({"error": "Course not found"}), 404
        
        # Đánh dấu Syllabus đã được like
        for i, msg in enumerate(course['message_CS']):
            if msg['role'] == 'assistant' and msg['content'] == message_content:
                course['message_CS'][i]['liked'] = True
        
        # Xác định đường dẫn thư mục
        pdf_root_folder = os.path.join(UPLOAD_FOLDER, str(course_id), "chiasach")
        output_folder = os.path.join(UPLOAD_FOLDER, str(course_id), "chiabuoi")
        
        # Đảm bảo thư mục đầu ra tồn tại
        os.makedirs(output_folder, exist_ok=True)
        
        # Gọi hàm chiabuoi
        chiabuoi(
            text=message_content,
            pdf_root_folder=pdf_root_folder,
            output_folder=output_folder
        )
        
        # Khởi tạo các buổi học với trạng thái chưa tải
        number_of_lessons = course.get('number_lesson', 0)
        
        for i in range(1, number_of_lessons + 1):
            lesson_key = f"message_L{i}"
            # Kiểm tra xem buổi học đã tồn tại chưa
            if lesson_key not in course:
                course[lesson_key] = []
            
            # Thêm trạng thái tải cho buổi học
            course[f"lesson_{i}_loaded"] = False
        
        # Cập nhật dữ liệu
        write_data(courses)
        
        return jsonify({
            "success": True, 
            "message": "Đã tạo các buổi học thành công"
        })
        
    except Exception as e:
        print(f"Error in split_sessions: {str(e)}")
        return jsonify({"error": str(e)}), 500



@app.route('/initialize-lesson', methods=['POST'])
def initialize_lesson():
    try:
        data = request.json
        course_id = data['courseId']
        lesson_number = data['lessonNumber']
        
        # Đọc dữ liệu hiện tại
        courses = read_data()
        course = next((c for c in courses if c['id'] == course_id), None)
        
        if not course:
            return jsonify({"error": "Course not found"}), 404
        
        # Kiểm tra xem buổi học đã được tải chưa
        lesson_loaded_key = f"lesson_{lesson_number}_loaded"
        if lesson_loaded_key in course and course[lesson_loaded_key]:
            # Nếu đã tải, trả về kế hoạch bài giảng hiện có
            message_key = f"message_L{lesson_number}"
            if message_key in course and course[message_key] and course[message_key][0]["role"] == "assistant":
                return jsonify({
                    "success": True,
                    "message": course[message_key][0]["content"],
                    "timestamp": course[message_key][0].get("timestamp", datetime.now().strftime("%H:%M:%S")),
                    "alreadyLoaded": True
                })
        
        # Đường dẫn đến file PDF của buổi học
        lesson_pdf_path = os.path.join(UPLOAD_FOLDER, str(course_id), "chiabuoi", f"Buoi_{lesson_number}.pdf")
        print("lesson pdf path: ", lesson_pdf_path)
        # Kiểm tra xem file PDF có tồn tại không
        if not os.path.exists(lesson_pdf_path):
            return jsonify({"error": f"PDF for lesson {lesson_number} not found"}), 404
        
        session_id = str(uuid.uuid4())
        # Tạo retriever mới
        retriever, text_summaries = get_sumarize(lesson_pdf_path, session_id)
        # Đảm bảo retriever có các thuộc tính cần thiết trước khi lưu
        if not hasattr(retriever, 'vectorstore') or not hasattr(retriever, 'docstore'):
            return jsonify({"error": f"Invalid retriever for lesson {lesson_number}"}), 500
        
        # Lưu retriever
        save_success = save_retriever(course_id, lesson_number, retriever, text_summaries)
        if not save_success:
            return jsonify({"error": f"Failed to save retriever for lesson {lesson_number}"}), 500
        
        # Tạo kế hoạch bài giảng
        message_key = f"message_L{lesson_number}"
        lesson_plan = generate_lesson_plan(text_summaries, course['duration_lesson'])
        
        # Thêm timestamp cho tin nhắn
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Cập nhật hoặc tạo mới message cho buổi học
        if message_key not in course:
            course[message_key] = []
        
        # Thêm tin nhắn đầu tiên với role "assistant" và timestamp
        course[message_key] = [{"role": "assistant", "content": lesson_plan, "timestamp": current_time}]
        
        # Đánh dấu buổi học đã được tải
        course[lesson_loaded_key] = True
        
        # Lưu dữ liệu
        write_data(courses)
        
        return jsonify({
            "success": True,
            "message": lesson_plan,
            "timestamp": current_time
        })
        
    except Exception as e:
        print(f"Error initializing lesson: {str(e)}")
        return jsonify({"error": str(e)}), 500

    
@app.route('/chat-lesson', methods=['POST'])
def handle_chat_lesson():
    try:
        data = request.json
        course_id = data['courseId']
        lesson_number = data['lessonNumber']
        user_message = data['message']
        
        # Đọc dữ liệu hiện tại
        courses = read_data()
        course = next((c for c in courses if c['id'] == course_id), None)
        
        if not course:
            return jsonify({"error": "Course not found"}), 404
        
        # Thêm timestamp cho tin nhắn
        current_time = datetime.now().strftime("%H:%M:%S")

        # Tải retriever
        retriever, _ = load_retriever(course_id, lesson_number)
        
        # Nếu không tìm thấy retriever, tạo mới
        if retriever is None:
            # Đường dẫn đến file PDF của buổi học
            lesson_pdf_path = os.path.join(UPLOAD_FOLDER, str(course_id), "chiabuoi", f"Buoi_{lesson_number}.pdf")
            
            # Kiểm tra xem file PDF có tồn tại không
            if not os.path.exists(lesson_pdf_path):
                return jsonify({"error": f"PDF for lesson {lesson_number} not found"}), 404
            
            # Tạo retriever mới
            retriever, text_summaries = get_sumarize(lesson_pdf_path)
            
            # Đảm bảo retriever có các thuộc tính cần thiết trước khi lưu
            if not hasattr(retriever, 'vectorstore') or not hasattr(retriever, 'docstore'):
                return jsonify({"error": f"Invalid retriever for lesson {lesson_number}"}), 500
            
            # Lưu retriever
            save_success = save_retriever(course_id, lesson_number, retriever, text_summaries)
            if not save_success:
                return jsonify({"error": f"Failed to save retriever for lesson {lesson_number}"}), 500
                
            # Đánh dấu buổi học đã được tải
            lesson_loaded_key = f"lesson_{lesson_number}_loaded"
            course[lesson_loaded_key] = True
        
        # Gọi hàm chat_lesson để lấy phản hồi
        response = chat_lesson(user_message, retriever)
        
        # Cập nhật lịch sử chat
        message_key = f"message_L{lesson_number}"
        if message_key not in course:
            course[message_key] = []
            
        course[message_key].extend([
            {"role": "user", "content": user_message, "timestamp": current_time},
            {"role": "assistant", "content": response, "timestamp": datetime.now().strftime("%H:%M:%S")}
        ])
        
        # Lưu dữ liệu
        write_data(courses)
        
        return jsonify({
            "success": True,
            "message": response,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
    except Exception as e:
        print(f"Error in chat_lesson: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/list-retrievers', methods=['GET'])
def get_retrievers_list():
    try:
        retrievers = list_retrievers()
        return jsonify({
            "success": True,
            "retrievers": retrievers
        })
    except Exception as e:
        print(f"Error listing retrievers: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/delete-retriever', methods=['POST'])
def remove_retriever():
    try:
        data = request.json
        course_id = data['courseId']
        lesson_number = data.get('lessonNumber')  # None để xóa tất cả
        
        success = delete_retriever(course_id, lesson_number)
        
        return jsonify({
            "success": success,
            "message": "Đã xóa retriever thành công" if success else "Lỗi khi xóa retriever"
        })
    except Exception as e:
        print(f"Error deleting retriever: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)