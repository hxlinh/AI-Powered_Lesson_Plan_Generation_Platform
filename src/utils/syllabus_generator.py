from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm_studio")
MODEL = "meta=llama-3.1-8b-instruct-PLO-finetuned"

def chat_syllabus(conversation_history, user_input):
    system_message = """
Bạn là một trợ lý chuyên nghiệp giúp giảng viên soạn thảo kế hoạch bài giảng(Course Syllabus) cho một môn học dựa trên nội dung sách được cung cấp và tuân thủ cấu trúc đầu ra dưới đây:
Cấu trúc đầu ra:
# Buổi 1 (thời lượng buổi 1):
## Nội dung:
### Chương 1: [Tiêu đề chương]
[Số chương Tiêu đề chương ví dụ: 1.1 Giới thiệu]
## Hoạt động dạy và học:
### Giảng dạy:
[Nội dung giảng dạy]
### Học trên lớp:
[Hoạt động học trên lớp]
### Tự học:
[Hoạt động tự học]
## CLOs:
[Liệt kê các CLOs mà buổi học này hướng đến theo CLOs đầu vào]
...
# Buổi n (thời lượng buổi n):
## Nội dung:
### [Tiêu đề chương]
[Số chương Nội dung chương ví dụ: 1.1 Giới thiệu]
## Hoạt động dạy và học:
### Giảng dạy:
[Nội dung giảng dạy]
### Học trên lớp:
[Hoạt động học trên lớp]
### Tự học:
[Hoạt động tự học]
## CLOs:
[Liệt kê các CLOs mà buổi học này hướng đến]
Yêu cầu:
Phải bao gồm số chương và Tiêu đề của chương.
Phải phản hồi theo cấu trúc đầu ra.
Luôn phản hồi bằng tiếng Việt.
Chỉ nêu CLOs nào có trong buổi học đó.
"""

    messages = [
        {"role": "system", "content": system_message},
        *conversation_history,
    ]
    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(model=MODEL, messages=messages)
        return response.choices[0].message.content
    except Exception as e:
        exit(1)