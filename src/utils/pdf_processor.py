from openai import OpenAI
from marker.converters.pdf import PdfConverter
from marker.config.parser import ConfigParser
from marker.models import create_model_dict
from marker.output import text_from_rendered
import fitz
import os
import cv2
import numpy as np
import tensorflow as tf
import shutil
from tensorflow.keras.models import load_model
from paddleocr import PaddleOCR # main OCR dependencies
from matplotlib import pyplot as plt # plot images
import re
import openai
import pypdf
import pytesseract
from PIL import Image

MODEL_PATH = os.path.join(os.path.dirname(__file__), "/Users/admin/Code/AI_CHAT/lesson_plan/src/models/classifier/model.h5")

# client = OpenAI(base_url="http://192.168.100.80:1234/v1", api_key="lm_studio")
# MODEL = "meta=llama-3.1-8b-instruct-finetuned"
# def convert_pdf(pdf_path):
#     config = {
#         "page_range": [0, 1, 2, 3, 4],
#         "processors": "torch.mps",
#         "output_format": "markdown",
#     }
#     config_parser = ConfigParser(config)
#     converter = PdfConverter(
#         config={
#         "page_range": [0, 1, 2, 3, 4],
#         "processors": "torch.mps",
#         "output_format": "markdown",
#         },
#         artifact_dict=create_model_dict(),
#         renderer=config_parser.get_renderer(),
#         llm_service=config_parser.get_llm_service()
#     )
#     rendered = converter(pdf_path)
#     text, _, images = text_from_rendered(rendered)
#     return text

# def get_book_name(path):
#     page=convert_pdf(path)
#     message = [
#         {
#             "role": "system",
#             "content": "You are a helpful assistant that give me title and author of the book."
#         },
#     ]
#     user_input = f"""Give me the title and author of the book in this structure: [name of the book] by [author of the book].
# {page}"""
#     message.append({"role": "user", "content": user_input})
#     try:
#         response = client.chat.completions.create(model=MODEL, messages=message)
#     except Exception as e:
#         print("Loi roi")
#         exit(1)
#     return response.choices[0].message.content

def get_book_name(pdf_path):
    # Set API key
    openai.api_key = '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'
    def detect_toc(text):
        prompt = (
            "You are an AI assistant. I will provide a text passage, please identify and extract only the Title and Author from it. Do not include any other content."
            "Respond strictly in the following format: name of the book by author of the book."
            "If no title or author is found, say 'No title or author found."
            f"Text passage:\n{text}"
        )
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content

    # # Định nghĩa đường dẫn thư mục
    # correct_dir = "./correct/"
    # # Đảm bảo thư mục đích tồn tại
    # os.makedirs(correct_dir, exist_ok=True)

    # doc = fitz.open(pdf_path)
    # # Khởi tạo model OCR
    # ocr_model = PaddleOCR(lang='en',use_angle_cls=True)
    # extracted_texts = ""
    # for i in range(5):
    #     page = doc.load_page(i)
    #     pix = page.get_pixmap()
    #     pix.save(f"./correct/{page.number}.png")
    #     img_path = os.path.join('.', f'./correct/{i}.png')
        
    #     # Kiểm tra xem ảnh có tồn tại không
    #     if os.path.exists(img_path):
    #         result = ocr_model.ocr(img_path)
            
    #         # Trích xuất và định dạng văn bản OCR
    #         extracted_texts += '\n'.join([line[1][0] for line in result[0]]) + "\n"

    pdf_reader = pypdf.PdfReader(pdf_path)
    extracted_texts = ""
    for page in range(5):
        page = pdf_reader.pages[page]
        extracted_texts += page.extract_text() + "\n"
    
    sample = detect_toc(extracted_texts)

    return sample

def extract_contents_from_image(pdf_path,model_path):
    openai.api_key = 'your key'
    def detect_toc(text):
        prompt = (
            "You are an AI assistant. I will provide a text passage, "
            "please identify and extract only the main chapter headings (e.g., 1, 2, 3) "
            "and their subheadings (e.g., 1.1, 1.2, 1.3) along with their associated page numbers if available. "
            "Do not include any other content. "
            "Respond in a structured format listing only the relevant headings and subheadings. "
            "If no table of contents is found, say 'No table of contents found'.\n\n"
            "Do not use character '-' in the response."
            f"Text passage:\n{text}"
        )
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI assistant that helps identify table of contents in text."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    
    # Định nghĩa đường dẫn thư mục
    correct_dir = "./correct/"
    # Đảm bảo thư mục đích tồn tại
    os.makedirs(correct_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    for i in range(30):
        page = doc.load_page(i)
        pix = page.get_pixmap()
        pix.save(f"./correct/{page.number}.png")

    # Load mô hình đã được huấn luyện
    model = load_model(model_path)

    # Lấy danh sách tất cả ảnh trong thư mục correct
    image_files = [f for f in os.listdir(correct_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    max=-1
    min=100
    # Duyệt qua từng ảnh
    for img_name in image_files:
        img_path = os.path.join(correct_dir, img_name)

        # Đọc ảnh bằng OpenCV
        img = cv2.imread(img_path)
        if img is None:
            print(f"Không thể đọc {img_name}")
            continue

        # Chuyển đổi ảnh sang RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Chuyển ảnh thành tensor và resize
        img_tensor = tf.convert_to_tensor(img, dtype=tf.float32)
        img_resized = tf.image.resize(img_tensor, (256, 256))

        # Chuẩn hóa ảnh về khoảng [0,1] và thêm batch dimension
        img_input = np.expand_dims(img_resized / 255.0, axis=0)

        # Dự đoán với model
        yhat = model.predict(img_input)

        # Kiểm tra kết quả dự đoán và di chuyển file nếu cần
        if yhat[0][0] > 0.5:
            os.remove(img_path)
        else:
            num = int(img_name.split('.')[0])
            if max < num:
                max = num
            if min > num:
                min = num

    # Khởi tạo model OCR
    ocr_model = PaddleOCR(lang='en', use_angle_cls=True, use_gpu=False)
    # Lưu kết quả OCR vào danh sách
    ocr_results = []

    extracted_texts = ""

    for i in range(min, max + 1):
        img_path = os.path.join('.', f'./correct/{i}.png')
        
        # Kiểm tra xem ảnh có tồn tại không
        if os.path.exists(img_path):
            # Mở ảnh bằng PIL (Pillow)
            img = Image.open(img_path)
            # Sử dụng Tesseract OCR để nhận diện văn bản
            test = pytesseract.image_to_string(img)
            if test.strip():
                result = ocr_model.ocr(img_path)
                # Trích xuất và định dạng văn bản OCR
                extracted_texts += '\n'.join([line[1][0] for line in result[0]]) + "\n"

    def merge_numeric_lines(text):
        lines = text.split('\n')
        merged_lines = []
        pattern_number = re.compile(r'\d+$')  # Chỉ chứa số
        pattern_section = re.compile(r'\d+\.\d+')  # Định dạng số như 1.1, 2.1
        pattern_subsection = re.compile(r'\d+\.\d+\.\d+')  # Định dạng số như 1.2.1, 2.3.1
        pattern_chapter = re.compile(r'Chapter \d+$')  # Định dạng "Chapter X"
        pattern_CHAPTER = re.compile(r'CHAPTER \d+$')  # Định dạng "Chapter X"
        remove_keywords = {"CONTENTS", "Contents", "Table of Contents", "Preface", "preface", "PREFACE", "page ", "Page",
                            "Online Resources", "ONLINE RESOURCES", "About the Author", "ABOUT THE AUTHOR"}

        # Xóa các dòng có từ khóa đặc biệt trong 8 dòng đầu tiên
        filtered_lines = [line for line in lines if not any(keyword in line for keyword in remove_keywords)]
        
        for i, line in enumerate(filtered_lines):
            if pattern_number.fullmatch(line.strip()):
                if merged_lines:
                    merged_lines[-1] += ' ' + line.strip()
            elif pattern_section.fullmatch(line.strip()) or pattern_subsection.fullmatch(line.strip()):
                merged_lines.append(line)
            elif i > 0 and (pattern_section.fullmatch(filtered_lines[i - 1].strip()) or pattern_subsection.fullmatch(filtered_lines[i - 1].strip())):
                merged_lines[-1] += ' ' + line.strip()
            else:
                merged_lines.append(line)
            # Xóa số thứ hai nếu có hai số cuối dòng
        refined_lines = [re.sub(r'(\d+) (\d+)$', r'\1', line) for line in merged_lines]
        # Nếu dòng có dạng "Chapter X", thụt dòng tiếp theo
        final_lines = []
        i = 0
        while i < len(refined_lines):
            if (pattern_chapter.fullmatch(refined_lines[i].strip()) and i + 1 < len(refined_lines)) or (pattern_CHAPTER.fullmatch(refined_lines[i].strip()) and i + 1 < len(refined_lines)):
                final_lines.append(refined_lines[i] + ' ' + refined_lines[i + 1])
                i += 2  # Bỏ qua dòng tiếp theo vì đã được gộp
            else:
                final_lines.append(refined_lines[i])
                i += 1
        # Xóa dấu chấm ở cuối dòng
        final_lines = [re.sub(r'\.$', '', line) for line in final_lines]

        # Trích xuất số cuối mỗi dòng và tính toán giá trị mới
        extracted_numbers = []
        last_number = None
        check = None
        for line in final_lines:
            match = re.search(r' (\d+)$', line)
            if match:
                current_number = int(match.group(1))
                if check is None:
                    check = current_number  # Lưu số đầu tiên phát hiện được
                if (last_number is not None) and (current_number - last_number) >=0 :
                    extracted_numbers.append((current_number - last_number))
                last_number = current_number

        return '\n'.join(final_lines),extracted_numbers , check

    def clean_text(text):
        lines = text.split("\n")  # Tách văn bản thành các dòng
        cleaned_lines = [line for line in lines if line.strip()]  # Loại bỏ các dòng trống
        return "\n".join(cleaned_lines)  # Ghép lại thành chuỗi mới
    

    sample = merge_numeric_lines(extracted_texts)
    shutil.rmtree(correct_dir)
    sample1 = detect_toc(sample)
    result = clean_text(sample1)
    return result

def process_pdf(pdf_path):
    try:
        book_info = get_book_name(pdf_path)
        content = extract_contents_from_image(pdf_path, MODEL_PATH)
        result = {
            "book": book_info,
            "content": content
        }

        return result
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None
    

def test(pdf):
    book_info = get_book_name(pdf)
    content = extract_contents_from_image(pdf, MODEL_PATH)

    print(f"Title: {book_info}")
    print(f"Content: {content}")

# test("/Users/admin/Code/AI_CHAT/lesson_plan/src/utils/William- Elementary differential equations and boundary value problems-7ed.pdf")

# book_info = get_book_name("/Users/admin/Code/AI_CHAT/lesson_plan/src/utils/a.pdf")
# print(book_info)

# content = extract_contents_from_image("/Users/admin/Code/AI_CHAT/lesson_plan/src/utils/William- Elementary differential equations and boundary value problems-7ed.pdf", MODEL_PATH)
# print(content)
