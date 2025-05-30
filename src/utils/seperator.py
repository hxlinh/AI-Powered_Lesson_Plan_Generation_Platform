import re
import pypdf
import fitz  # PyMuPDF
import os
import shutil
from pypdf import PdfWriter

def chiasach(text,pdf_path,output_dir):
    lines = text.split('\n')
    extracted_numbers = []
    last_number = None
    check = None
    start = None  # Biến lưu số trang tìm được

    for line in lines:
        if re.search(r'\b\d+\.\d+\b', line):  # Kiểm tra xem có xuất hiện định dạng 1.1, 1.2, ... không
            matches = re.findall(r'\d+', line)  # Tìm tất cả các số trong dòng
            if matches:
                selected_number = int(matches[-1])  # Chọn số cuối cùng trong danh sách số tìm thấy
                
                if check is None:
                    check = selected_number  # Lưu số đầu tiên phát hiện được
                
                if last_number is not None and (selected_number - last_number) >= 0:
                    extracted_numbers.append(selected_number - last_number)
                
                last_number = selected_number  # Cập nhật last_number để dùng cho vòng lặp tiếp theo
    
    def find_exact_number_page(pdf_path, check):
        """Duyệt từng trang PDF để kiểm tra dòng nào chỉ chứa số = check"""
        start = None  # Biến lưu số trang tìm được

        with open(pdf_path, "rb") as file:
            reader = pypdf.PdfReader(file)
            total_pages = len(reader.pages)

            pattern = rf"^\s*{re.escape(str(check))}(?!\d)"  # Kiểm tra check xuất hiện đầu dòng và không có số cuối dòng
            invalid_end_pattern = r"\d$"  # Kiểm tra nếu dòng kết thúc bằng số
            for page_num in range(total_pages):
                text = reader.pages[page_num].extract_text()
                
                if text:  # Kiểm tra nếu có nội dung
                    lines = text.strip().split("\n")
                    
                    if lines:
                        first_line = lines[0].strip()
                        second_line = lines[1].strip() if len(lines) > 1 else ""
                        last_line = lines[-1].strip()
                        
                        # Kiểm tra check chỉ xuất hiện đầu dòng không có khoảng trắng trước đó
                        # và dòng không kết thúc bằng số
                        if ((re.match(pattern, first_line) and not re.search(invalid_end_pattern, first_line)) or
                            (re.match(pattern, second_line) and not re.search(invalid_end_pattern, second_line)) or
                            (re.match(pattern, last_line) and not re.search(invalid_end_pattern, last_line))):
                            return page_num  # Trả về số trang tìm thấy

        print(f"Số {check} không được tìm thấy trong file PDF.")
        return start  # Trả về None nếu không tìm thấy
    
    start = find_exact_number_page(pdf_path,check) -1  

    # def parse_toc(text):
    #     lines = text.strip().split("\n")
    #     merged_lines = []
    #     buffer = ""

    #     # Ghép các dòng xuống dòng vào cùng một mục
    #     for line in lines:
    #         line = line.strip()
    #         if re.search(r'\d+$', line):  # Nếu dòng có số trang ở cuối, lưu lại
    #             buffer += " " + line
    #             merged_lines.append(buffer.strip())
    #             buffer = ""
    #         else:  # Nếu chưa có số trang, ghép vào dòng trước đó
    #             buffer += " " + line

    #     # Đảm bảo dòng đầu tiên là chương 1 nếu chưa có số
    #     if not re.match(r"^\d", merged_lines[0]):
    #         merged_lines[0] = "1 " + merged_lines[0]

    #     corrected_lines = []
    #     for line in merged_lines:
    #         # Sửa lỗi dính số vào chữ (2.1Tools → 2.1 Tools)
    #         line = re.sub(r"^(\d+\.\d+)([A-Z])", r"\1 \2", line)
    #         line = re.sub(r"^(\d+)([A-Z])", r"\1 \2", line)  # Sửa lỗi chương chính
    #         line = re.sub(r"\s+[.\-]\s+(\d+)$", r" \1", line)  # Bỏ dấu "." hoặc "-" giữa tên và số trang

    #         # Xử lý lỗi dính nhiều mục trên cùng một dòng
    #         split_lines = re.split(r'(\d+\.\d+\s+.+?\s+\d+)', line)
    #         corrected_lines.extend([s.strip() for s in split_lines if s.strip()])

    #     # Mẫu regex nhận diện mục lục
    #     pattern = re.compile(r"^(\d+\.\d+)\s+.+?\s+(\d+)$")

    #     toc = []
    #     for line in corrected_lines:
    #         match = pattern.search(line)
    #         if match:
    #             section = match.group(1)  # Số mục con
    #             page = int(match.group(2))  # Trang
    #             toc.append((section, page))

    #     return toc
    def parse_toc(text):
        # Hàm TOC để xử lý các giá trị
        def toc(numbers):
            toc_list = []
            for number in numbers:
                parts = number.split(".")  # Tách các phần của số (VD: "1.1.2" → ["1", "1", "2"])
                parts = [int(p) for p in parts]  # Chuyển từng phần từ str → int

                if len(parts) == 2:  # Nếu có 2 phần (VD: 1.1)
                    toc_list.append((f"{parts[0]}.{parts[1]}", parts[1]))  
                elif len(parts) == 3:  # Nếu có 3 phần (VD: 1.1.1)
                    toc_list.append((f"{parts[0]}.{parts[1]}", parts[2]))

            return toc_list

        # Duyệt qua từng dòng và tìm các số có dạng 1.1, 1.2, 1.3,...
        lines = text.split("\n")
        numbers = []

        for line in lines:
            if re.search(r'\b\d+\.\d+\b', line):  # Kiểm tra xem có số dạng 1.1, 1.2, ... không
                matches = re.findall(r'\d+', line)  # Tìm tất cả các số trong dòng
                if matches:
                    number_str = ".".join(matches)  # Chuyển danh sách số thành chuỗi có dấu chấm (VD: "1.1")
                    numbers.append(number_str)  # Lưu vào danh sách

        # Gọi hàm toc để xử lý danh sách số và trả kết quả
        return toc(numbers)


    # Chạy thử với mục lục của bạn
    toc_list = parse_toc(text)
    print(toc_list)

    # Chia file PDF theo chương và mục con
    def split_pdf(pdf_path, toc, output_folder):
        doc = fitz.open(pdf_path)
        os.makedirs(output_folder, exist_ok=True)
        for i in range(len(toc)):
            section, start_page = toc[i]
            start_page = start - toc[0][1] + start_page +1  # Điều chỉnh theo chỉ mục PDF
            end_page = start -toc[0][1] + toc[i+1][1] + 1  if i + 1 < len(toc) else len(doc) - 1  # Xác định trang cuối

            # Kiểm tra nếu start_page hợp lệ
            if start_page >= len(doc):
                print(f"Bỏ qua {section}: start_page ({start_page}) vượt quá số trang PDF.")
                continue

            # Điều chỉnh end_page không vượt quá phạm vi của PDF
            end_page = min(end_page, len(doc) - 1)

            new_doc = fitz.open()
            for page_num in range(start_page, end_page + 1):
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

            # Kiểm tra nếu new_doc có trang trước khi lưu
            if new_doc.page_count == 0:
                print(f"Bỏ qua {section}: Không có trang nào được trích xuất.")
                new_doc.close()
                continue

            # Xác định thư mục cha
            main_section = section.split(".")[0]
            main_folder = os.path.join(output_folder, main_section)
            os.makedirs(main_folder, exist_ok=True)

            output_pdf = os.path.join(main_folder, f"{section}.pdf")
            new_doc.save(output_pdf)
            new_doc.close()
            print(f"Đã lưu: {output_pdf}")

    split_pdf(pdf_path, toc_list, output_dir)


def chiabuoi(text,pdf_root_folder,output_folder):
    # Đảm bảo thư mục đầu ra tồn tại
    os.makedirs(output_folder, exist_ok=True)
    lines = text.split('\n')
    
    current_session = None  # Biến lưu tên buổi hiện tại
    pdf_merger = None  # Đối tượng hợp nhất PDF
    
    for line in lines:
        line = line.strip()
        # print(line)
        
        # Xác định dòng chứa "Buổi X"
        match_session = re.search(r'Buổi (\d+)', line)
        if match_session:
            # Nếu đã có một phiên làm việc trước đó, lưu lại file PDF đã gộp
            if current_session and pdf_merger:
                if pdf_merger.pages:
                    merged_pdf_path = os.path.join(output_folder, f"{current_session}.pdf")
                    pdf_merger.write(merged_pdf_path)
                    pdf_merger.close()
                    print(f"Đã tạo: {merged_pdf_path}")
                else:
                    print(f"Không có tệp PDF hợp lệ cho {current_session}")
            
            # Khởi tạo buổi mới
            current_session = f"Buoi_{match_session.group(1)}"
            pdf_merger = PdfWriter()
            continue
        
        # Nếu có danh sách file PDF (dạng 1.1, 1.2,...)
        match_pdf = re.search(r'(\d+\.\d+)', line)
        if match_pdf and current_session:
            pdf_file = f"{match_pdf.group(1)}.pdf"
            
            # Tìm file trong thư mục chương tương ứng
            chapter_number = match_pdf.group(1).split('.')[0]
            chapter_folder = os.path.join(pdf_root_folder, chapter_number)
            pdf_path = os.path.join(chapter_folder, pdf_file)
            
            # Kiểm tra và thêm file vào merger
            print(f"Đang kiểm tra tệp: {pdf_path}")
            if os.path.exists(pdf_path):
                pdf_merger.append(pdf_path)
                print(f"Đã thêm vào {current_session}: {pdf_file}")
            else:
                print(f"Không tìm thấy: {pdf_path}")
    
    # Lưu lại file PDF của buổi cuối cùng
    if current_session and pdf_merger:
        if pdf_merger.pages:
            merged_pdf_path = os.path.join(output_folder, f"{current_session}.pdf")
            pdf_merger.write(merged_pdf_path)
            pdf_merger.close()
            print(f"Đã tạo: {merged_pdf_path}")
        else:
            print(f"Không có tệp PDF hợp lệ cho {current_session}")


# mucluc = """1. Functions and Models
#    1.1 Four Ways to Represent a Function, p. 8
#    1.2 Mathematical Models: A Catalog of Essential Functions, p. 21
#    1.3 New Functions from Old Functions p. 36
#    1.4 Exponential Functions, p. 45
#    1.5 Inverse Functions and Logarithms p. 54
#    Review, p. 67
#    Principles of Problem Solving, p. 70
# 2. Limits and Derivatives
#    2.1 The Tangent and Velocity Problems, p. 78
#    2.2 The Limit of a Function, p. 83
#    2.3 Calculating Limits Using the Limit Laws p. 94
#    2.4 The Precise Definition of a Limit, p. 105
#    2.5 Continuity, p. 115
#    2.6 Limits at Infinity; Horizontal Asymptotes, p. 127
#    2.7 Derivatives and Rates of Change, p. 140
#    The Derivative as a Function, p. 153
#    Review, p. 166
#    Problems Plus, p. 171
# 3. Differentiation Rules
#    3.1 Derivatives of Polynomials and Exponential Functions, p. 174
#    3.2 The Product and Quotient Rules, p. 185
#    3.3 Derivatives of Trigonometric Functions, p. 191
#    3.4 The Chain Rule, p. 199
#    3.5 Implicit Differentiation, p. 209
#    3.6 Derivatives of Logarithmic and Inverse Trigonometric Functions, p. 217
#    3.7 Rates of Change in the Natural and Social Sciences, p. 225
#    3.8 Exponential Growth and Decay, p. 239
#    3.9 Related Rates, p. 247
#    3.10 Linear Approximations and Differentials, p. 254
#    3.11 Hyperbolic Functions, p. 261
#    Review, p. 269
#    Problems Plus, p. 274
# 4. Applications of Differentiation
#    4.1 Maximum and Minimum Values, p. 280
#    4.2 The Mean Value Theorem, p. 290
#    4.3 What Derivatives Tell Us about the Shape of a Graph, p. 296
#    4.4 Indeterminate Forms and L'Hospital's Rule, p. 309
#    4.5 Summary of Curve Sketching, p. 320
#    4.6 Graphing with Calculus and Technology, p. 329
#    4.7 Optimization Problems, p. 336
#    4.8 Newton's Method, p. 351
#    4.9 Antiderivatives
#    Review, p. 364
#    Problems Plus, p. 369
# 5. Integrals
#    5.1 The Area and Distance Problems, p. 372
#    5.2 The Definite Integral, p. 384
#    5.3 The Fundamental Theorem of Calculus, p. 399
#    5.4 Indefinite Integrals and the Net Change Theorem, p. 409
#    5.5 The Substitution Rule, p. 419
#    Review, p. 428
#    Problems Plus, p. 432
# 6. Applications of Integration
#    6.1 Areas Between Curves, p. 436
#    6.2 Volumes, p. 446
#    6.3 Volumes by Cylindrical Shells, p. 460
#    6.4 Work, p. 467
#    6.5 Average Value of a Function, p. 473
#    Review, p. 478
#    Problems Plus, p. 481
# 7. Techniques of Integration
#    7.1 Integration by Parts, p. 486
#    7.2 Trigonometric Integrals, p. 493
#    7.3 Trigonometric Substitution, p. 500
#    7.4 Integration of Rational Functions by Partial Fractions, p. 507
#    7.5 Strategy for Integration, p. 517
#    7.6 Integration Using Tables and Technology, p. 523
#    7.7 Approximate Integration, p. 529
#    Improper Integrals, p. 542
#    Review, p. 552
#    Problems Plus, p. 556
# 8. Further Applications of Integration
#    8.1 Arc Length, p. 560
#    8.2 Area of a Surface of Revolution, p. 567
#    8.3 Applications to Physics and Engineering, p. 576
#    8.4 Applications to Economics and Biology, p. 587
#    8.5 Probability, p. 592
#    Review, p. 600
#    Problems Plus, p. 602
# 9. Differential Equations
#    9.1 Modeling with Differential Equations, p. 606
#    9.2 Direction Fields and Euler's Method, p. 612
#    9.3 Separable Equations, p. 621
#    9.4 Models for Population Growth, p. 631
#    9.5 Linear Equations, p. 641
#    9.6 Predator-Prey Systems, p. 649
#    Review, p. 656
#    Problems Plus, p. 659
# 10. Parametric Equations and Polar Coordinates
#     10.1 Curves Defined by Parametric Equations, p. 662
#     10.2 Calculus with Parametric Curves, p. 673
#     10.3 Polar Coordinates, p. 684
#     10.4 Calculus in Polar Coordinates, p. 694
#     10.5 Conic Sections, p. 702
#     10.6 Conic Sections in Polar Coordinates, p. 711
#     Review, p. 719
#     Problems Plus, p. 722
# 11. Sequences, Series, and Power Series
#     11.1 Sequences, p. 724
#     11.2 Series, p. 738
#     11.3 The Integral Test and Estimates of Sums, p. 751
#     11.4 The Comparison Tests, p. 760
#     11.5 Alternating Series and Absolute Convergence, p. 765
#     11.6 The Ratio and Root Tests, p. 774
#     11.7 Strategy for Testing Series, p. 779
#     11.8 Power Series, p. 781
#     11.9 Representations of Functions as Power Series, p. 787
#     11.10 Taylor and Maclaurin Series, p. 795
#     11.11 Applications of Taylor Polynomials
#     Review, p. 821
#     Problems Plus, p. 825
# 12. Vectors and the Geometry of Space
#     12.1 Three-Dimensional Coordinate Systems, p. 830
#     12.2 Vectors, p. 836
#     12.3 The Dot Product, p. 847
#     12.4 The Cross Product, p. 855
#     12.5 Equations of Lines and Planes, p. 864
#     12.6 Cylinders and Quadric Surfaces, p. 875
#     Review, p. 883
#     Problems Plus, p. 887
# 13. Vector Functions
#     13.1 Vector Functions and Space Curves, p. 890
#     13.2 Derivatives and Integrals of Vector Functions, p. 898
#     13.3 Arc Length and Curvature, p. 904
#     13.4 Motion in Space: Velocity and Acceleration, p. 916
#     Review, p. 927
#     Problems Plus
# 14. Partial Derivatives
#     14.1 Functions of Several Variables, p. 934
#     14.2 Limits and Continuity, p. 951
#     14.3 Partial Derivatives, p. 961
#     14.4 Tangent Planes and Linear Approximations, p. 974
#     14.5 The Chain Rule, p. 985
#     14.6 Directional Derivatives and the Gradient Vector, p. 994
#     14.7 Maximum and Minimum Values, p. 1008
#     14.8 Lagrange Multipliers, p. 1020
#     Review, p. 1031
#     Problems Plus, p. 1035
# 15. Multiple Integrals
#     15.1 Double Integrals over Rectangles, p. 1038
#     15.2 Double Integrals over General Regions, p. 1051
#     15.3 Double Integrals in Polar Coordinates, p. 1062
#     15.4 Applications of Double Integrals, p. 1069
#     15.5 Surface Area, p. 1079
#     15.6 Triple Integrals, p. 1082
#     15.7 Triple Integrals in Cylindrical Coordinates, p. 1095
#     15.8 Triple Integrals in Spherical Coordinates, p. 1102
#     15.9 Change of Variables in Multiple Integrals, p. 1109
#     Review, p. 1117
#     Problems Plus, p. 1121
# 16. Vector Calculus
#     16.1 Vector Fields, p. 1124
#     16.2 Line Integrals, p. 1131
#     16.3 The Fundamental Theorem for Line Integrals, p. 1144
#     16.4 Green's Theorem, p. 1154
#     16.5 Curl and Divergence, p. 1161
#     16.6 Parametric Surfaces and Their Areas, p. 1170
#     16.7 Surface Integrals, p. 1182
#     16.8 Stokes Theorem, p. 1195
#     16.9 The Divergence Theorem, p. 1201
#     16.10 Summary, p. 1208
#     Review, p. 1209
#     Problems Plus, p. 1213
# Appendixes
#     A. Numbers, Inequalities, and Absolute Values, A2
#     B. Coordinate Geometry and Lines, A10
#     C. Graphs of Second-Degree Equations, A16
#     D. Trigonometry, A24
#     E. Sigma Notation, A36
#     F. Proofs of Theorems, A41
# The Logarithm Defined as an Integral, A53
# Answers to Odd-Numbered Exercises, A61
# Index, A143"""
# pdf_path = "/Users/admin/Code/AI_CHAT/lesson_plan/src/utils/cal9th.pdf"
# markdown_path="/Users/admin/Code/AI_CHAT/lesson_plan/src/utils/plan_XLTH.md"
# output_dir = "/Users/admin/Code/AI_CHAT/lesson_plan/src/utils/output"
# output_folder = "/Users/admin/Code/AI_CHAT/lesson_plan/src/utils/output_folder"
# chiasach(mucluc, pdf_path, output_dir) 
# -> cac file pdf chia sach trong output_dir

# markdown_path="""# Buổi 1 (3 giờ):
# ## Nội dung:
# ### Chương 1: Introduction 
# Lý thuyết:
# - 1.1 Hệ phương trình tuyến tính và ma trận hệ số. 
# -1.2 Vectors in space and the dot product.

# Bài tập:
# - Giải quyết vấn đề. 
# - Làm việc nhóm.
# ## Hoạt động dạy và học:
# ### Giảng dạy:
# - Ôn lại hệ phương trình tuyến tính từ môn Đại số giải quyết các bài toán có liên quan.
# - Giới thiệu ý nghĩa của phép tích trong không gian ba chiều.
# ### Học trên lớp:
# - Đặt vấn đề mới, tìm hiểu đặc điểm của vấn đề mới, thảo luận và đưa ra kết luận. 
# - Làm việc theo nhóm để chuẩn hóa một hệ phương trình tuyến tính cho bài tập.
# ### Tự học:
# - Ôn lại lý thuyết đã học.
# - Chuẩn bị bài trước khi đến lớp
# ## CLOs:
# CLO1, CLO2

# # Buổi 2 (3 giờ):
# ## Nội dung:
# ### Chương 1: Introduction 
# Lý thuyết:
# - 1.3Vectors in space and the dot product. 
# -1.4Equations of lines and planes.

# Bài tập:
# - Giải quyết vấn đề.
# - Làm việc nhóm.
# ## Hoạt động dạy và học:
# ### Giảng dạy:
# - Tiếp tục giới thiệu các đặc điểm của phép tích trong không gian ba chiều, bao gồm cả phương trình xấp xỉ đa thức cho một sự biến đổi. 
# - Ôn lại khái niệm về đường thẳng và mặt phẳng trong không gian ba chiều.
# ### Học trên lớp:
# - Đặt vấn đề mới, tìm hiểu đặc điểm của vấn đề mới, thảo luận và đưa ra kết luận. 
# - Làm việc theo nhóm để giải quyết bài tập về xấp xỉ đa thức.
# ### Tự học:
# - Ôn lại lý thuyết đã học.
# - Chuẩn bị bài trước khi đến lớp
# ## CLOs:
# CLO1, CLO2

# # Buổi 3 (3 giờ):
# ## Nội dung:
# ### Chương 1: Introduction 
# Lý thuyết:
# - 1.5Equations of lines and planes. 
# - 1.6The vector space Rn.

# Bài tập:
# - Giải quyết vấn đề.
# - Làm việc nhóm.
# ## Hoạt động dạy và học:
# ### Giảng dạy:
# - Ôn lại phương trình của đường thẳng và mặt phẳng trong không gian ba chiều, bao gồm cả xấp xỉ đa thức cho một sự biến đổi. 
# - Giới thiệu không gian số n và các tính chất của nó, đặc biệt là phép cộng và bội lặp.
# ### Học trên lớp:
# - Đặt vấn đề mới, tìm hiểu đặc điểm của vấn đề mới, thảo luận và đưa ra kết luận. 
# - Làm việc theo nhóm để giải quyết bài tập về hệ phương trình tuyến tính có nhiều biến.  
# ### Tự học:
# - Ôn lại lý thuyết đã học.
# - Chuẩn bị bài trước khi đến lớp
# ## CLOs:
# CLO1, CLO2

# # Buổi 4 (3 giờ):
# ## Nội dung:
# ### Chương 1: Introduction 
# Lý thuyết:
# - The vector space Rn. 
# - Matrix operations.

# Bài tập:
# - Giải quyết vấn đề.
# - Làm việc nhóm.
# ## Hoạt động dạy và học:
# ### Giảng dạy:
# - Ôn lại không gian số n và các tính chất của nó, bao gồm cả xấp xỉ đa thức cho một sự biến đổi. 
# - Giới thiệu khái niệm về ma trận; các phép toán trên ma trận (chậm) - thêm, lấy trừ, bội lặp và đảo.
# ### Học trên lớp:
# - Đặt vấn đề mới, tìm hiểu đặc điểm của vấn đề mới, thảo luận và đưa ra kết luận. 
# - Làm việc theo nhóm để giải quyết bài tập về xấp xỉ đa thức cho một sự biến đổi có nhiều biến.
# ### Tự học:
# - Ôn lại lý thuyết đã học.
# - Chuẩn bị bài trước khi đến lớp
# ## CLOs:
# CLO1, CLO2

# # Buổi 5 (3 giờ):
# ## Nội dung:
# ### Chương 1: Introduction 
# Lý thuyết:
# - Matrix operations. 
# - Survey of technology tools.

# Bài tập:
# - Giải quyết vấn đề.
# - Làm việc nhóm.
# ## Hoạt động dạy và học:
# ### Giảng dạy:
# - Ôn lại các phép toán trên ma trận (chậm), bao gồm cả xấp xỉ đa thức cho một sự biến đổi. 
# - Giới thiệu các công cụ hỗ trợ công nghệ hiện đại.
# ### Học trên lớp:
# - Đặt vấn đề mới, tìm hiểu đặc điểm của vấn đề mới, thảo luận và đưa ra kết luận.  
# - Làm việc theo nhóm để áp dụng Google Colaboratory (Colab) để giải quyết bài tập về xấp xỉ đa thức cho một sự biến đổi có nhiều biến.
# ### Tự học:
# - Ôn lại lý thuyết đã học.
# - Chuẩn bị bài trước khi đến lớp
# ## CLOs:
# CLO1, CLO2

# # Buổi 6 (3 giờ):
# ## Nội dung:
# ### Chương 1: Introduction 
# Lý thuyết:
# - Survey of technology tools.  
# - Chapter review

# Bài tập:
# - Giải quyết vấn đề.
# - Làm việc nhóm.
# ## Hoạt động dạy và học:
# ### Giảng dạy:
# - Ôn lại các công cụ hỗ trợ công nghệ hiện đại, bao gồm cả Colab.  
# - Đặt bài đánh giá học phần; đưa ra hướng dẫn về đánh giá học phần.
# ### Học trên lớp:
# - Xử lý những thắc mắc từ bài tập, bài giảng trước. 
# - Làm việc theo nhóm để chuẩn hóa một hệ phương trình tuyến tính có nhiều biến cho bài tập về xấp xỉ đa thức cho một sự biến đổi.
# ### Tự học:
# - Ôn lại lý thuyết đã học.
# - Chuẩn bị bài trước khi đến lớp
# ## CLOs:
# CLO1, CLO2

# # Buổi 7 (3 giờ):
# ## Nội dung:
# ### Chương 2: MATRICES AND SYSTEMS OF LINEAR EQUATIONS 
# Lý thuyết:
# - Systems of Linear Equations; Matrices 29
# - Echelon Form and Gauss–Jordan Elimination 35
# - Consistent Systems of Linear Equations 40
# - Applications (Optional) 48
# - Matrix Operations 54

# Bài tập:
# - Giải quyết vấn đề.
# - Làm việc nhóm.
# ## Hoạt động dạy và học:
# ### Giảng đọc:
# - Ôn lại các hệ phương trình tuyến tính, bao gồm cả xấp xỉ đa thức cho một sự biến đổi.  
# - Giới thiệu khái niệm về hình bậc nhất và thuật toán xóa điết Gauss–Jordan để đưa ra dạng hình bậc nhất cho một hệ phương trình tuyến tính.
# ### Học trên lớp:
# - Đặt vấn đề mới, tìm hiểu đặc điểm của vấn đề mới, thảo luận và đưa ra kết luận. 
# - Làm việc theo nhóm để giải quyết bài tập về xấp xỉ đa thức cho một sự biến đổi có nhiều biến.
# ### Tự học:
# - Ôn lại lý thuyết đã học.
# - Chuẩn bị bài trước khi đến lớp
# ## CLOs:
# CLO1, CLO2
# """
# output_dir = "/Users/admin/Code/AI_CHAT/lesson_plan/src/assets/book/29/chiasach"
# output_folder = "/Users/admin/Code/AI_CHAT/lesson_plan/src/assets/book/29/chiabuoi"
# chiabuoi(markdown_path,output_dir,output_folder) 
# ->  cac file buoi hoc trong output_folder