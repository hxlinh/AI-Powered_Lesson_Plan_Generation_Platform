from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm_studio")
MODEL = "lmstudio-community/meta-llama-3.1-8b-instruct-q8_0-finetuned-gguf/llama-3.1-8b-instruct-q8_0-plo-finetuned.gguf"

# def start_CLO(messages,s, book, tc): #book include title, author; tc include table of content, s include subject
#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 """Bạn là một trợ lý chuyên nghiệp giúp giảng viên soạn thảo các chuẩn đầu ra học phần (CLOs - Course Learning Outcomes) cho một môn học dựa trên nội dung sách được cung cấp và tuân thủ cấu trúc đầu ra dưới đây:
# Cấu trúc đầu ra:
# # Sau khi kết thúc học phần, sinh viên có khả năng:
# ## Chuẩn đầu ra học phần (CLOs): [CLO1]: [Mô tả cụ thể về khả năng hoặc kiến thức sinh viên đạt được sau khi học môn học phần này].
# ### Kiến thức: [Mô tả kiến thức nếu có, ví dụ: L1. Nhớ, L2. Hiểu, L3. Áp dụng, L4. Phân tích, L5. Đánh giá, L6. Sáng tạo].
# ### Kỹ năng: [Mô tả kỹ năng nếu có, ví dụ: L1. Bắt chước, L2. Thao tác, L3. Chính xác, L4. Phối hợp, L5. Thuần thục].
# ### Thái độ: [Mô tả thái độ nếu có, ví dụ: L1. Tiếp nhận, L2. Phản hồi, L3. Đánh giá, L4. Tổ chức, L5. Hình thành đặc điểm cá nhân].
# ...
# ## Chuẩn đầu ra học phần (CLOs): [CLOn]: [Mô tả cụ thể về khả năng hoặc kiến thức sinh viên đạt được sau khi học môn học phần này].
# ### Kiến thức: [Mô tả kiến thức nếu có, ví dụ: L1. Nhớ, L2. Hiểu, L3. Áp dụng, L4. Phân tích, L5. Đánh giá, L6. Sáng tạo].
# ### Kỹ năng: [Mô tả kỹ năng nếu có, ví dụ: L1. Bắt chước, L2. Thao tác, L3. Chính xác, L4. Phối hợp, L5. Thuần thục].
# ### Thái độ: [Mô tả thái độ nếu có, ví dụ: L1. Tiếp nhận, L2. Phản hồi, L3. Đánh giá, L4. Tổ chức, L5. Hình thành đặc điểm cá nhân].
# Yêu cầu:
# Phải phản hồi theo cấu trúc đầu ra.
# Luôn phản hồi bằng tiếng Việt.
# Mô tả CLO phải rõ ràng, cụ thể và liên quan đến nội dung học phần.
# Mỗi CLO phải có mã riêng (ví dụ: CLO1, CLO2, ...), mô tả của CLO và kiến thức, kỹ năng, thái độ.
# Mô tả của kiến thức, kỹ năng và thái độ có thể để trống nếu không áp dụng.
# """
#             ),
#         },
#     ]
#     user_input = f"""Hãy soạn thảo chuẩn đầu ra học phần (CLOs - Course Learning Outcomes) cho một môn học dựa trên nội dung sách được cung cấp.
# Môn học: {s}
# Tên sách: {book}
# Nội dung sách: 
# {tc}
# """
#     messages.append({"role": "user", "content": user_input})
#     try:
#         response = client.chat.completions.create(model=MODEL, messages=messages)
#         messages.append({"role": "system", "content": response.choices[0].message.content})
#     except Exception as e:
#         exit(1)
#     return response.choices[0].message.content

# def chat(messages,input):
#     messages.append({"role": "user", "content": input})
#     try:
#         response = client.chat.completions.create(model=MODEL, messages=messages)
#         messages.append({"role": "system", "content": response.choices[0].message.content})
#     except Exception as e:
#         exit(1)
#     return response.choices[0].message.content

def chat_CLO(conversation_history, user_input): 
    system_message = """Bạn là một trợ lý chuyên nghiệp giúp giảng viên soạn thảo các chuẩn đầu ra học phần (CLOs - Course Learning Outcomes) cho một môn học dựa trên nội dung sách được cung cấp và tuân thủ cấu trúc đầu ra dưới đây:
Cấu trúc đầu ra:
# Sau khi kết thúc học phần, sinh viên có khả năng:
## Chuẩn đầu ra học phần (CLOs): [CLO1]: [Mô tả cụ thể về khả năng hoặc kiến thức sinh viên đạt được sau khi học môn học phần này].
### Kiến thức: [Mô tả kiến thức nếu có, ví dụ: L1. Nhớ, L2. Hiểu, L3. Áp dụng, L4. Phân tích, L5. Đánh giá, L6. Sáng tạo].
### Kỹ năng: [Mô tả kỹ năng nếu có, ví dụ: L1. Bắt chước, L2. Thao tác, L3. Chính xác, L4. Phối hợp, L5. Thuần thục].
### Thái độ: [Mô tả thái độ nếu có, ví dụ: L1. Tiếp nhận, L2. Phản hồi, L3. Đánh giá, L4. Tổ chức, L5. Hình thành đặc điểm cá nhân].
### Chuẩn đầu ra chương trình đào tạo (PLOs): [Nêu PLO mà CLO này đóng góp vào ví dụ: PLOn].
...
## Chuẩn đầu ra học phần (CLOs): [CLOn]: [Mô tả cụ thể về khả năng hoặc kiến thức sinh viên đạt được sau khi học môn học phần này].
### Kiến thức: [Mô tả kiến thức nếu có, ví dụ: L1. Nhớ, L2. Hiểu, L3. Áp dụng, L4. Phân tích, L5. Đánh giá, L6. Sáng tạo].
### Kỹ năng: [Mô tả kỹ năng nếu có, ví dụ: L1. Bắt chước, L2. Thao tác, L3. Chính xác, L4. Phối hợp, L5. Thuần thục].
### Thái độ: [Mô tả thái độ nếu có, ví dụ: L1. Tiếp nhận, L2. Phản hồi, L3. Đánh giá, L4. Tổ chức, L5. Hình thành đặc điểm cá nhân].
### Chuẩn đầu ra chương trình đào tạo (PLOs): [Nêu PLO mà CLO này đóng góp vào ví dụ: PLOn].
Yêu cầu:
Phải phản hồi theo cấu trúc đầu ra.
Luôn phản hồi bằng tiếng Việt.
Mô tả CLO phải rõ ràng, cụ thể và liên quan đến nội dung học phần.
Mỗi CLO phải có mã riêng (ví dụ: CLO1, CLO2, ...), mô tả của CLO và kiến thức, kỹ năng, thái độ.
Mô tả của kiến thức, kỹ năng và thái độ có thể để trống nếu không áp dụng.
Mỗi CLO phải nêu PLO mà CLO này đóng góp vào, ngoài ra phải xem xét nội dung CLO có trong PLO đó không.
"""

    messages = [
        {"role": "system", "content": system_message},
        *conversation_history,
    ]
    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(model=MODEL, messages=messages)
        messages.append({"role": "assistant", "content": response.choices[0].message.content})
        print(conversation_history)
    except Exception as e:
        exit(1)
    return response.choices[0].message.content
