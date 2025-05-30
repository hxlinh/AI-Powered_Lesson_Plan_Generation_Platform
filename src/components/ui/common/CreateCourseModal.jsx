import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../../../styles/modal.css';
import BookInfoModal from './BookInfoModal';

const CreateCourseModal = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const [subject, setSubject] = useState('');
  const [file, setFile] = useState(null);
  const [numberLesson, setNumberLesson] = useState();
  const [durationLesson, setDurationLesson] = useState();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Thêm state mới
  const [bookInfo, setBookInfo] = useState(null);
  const [showBookInfoModal, setShowBookInfoModal] = useState(false);

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!subject || !file || !numberLesson || !durationLesson) {
      setError('Vui lòng điền đầy đủ thông tin');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      // Tạo FormData để gửi file
      const formData = new FormData();
      formData.append('file', file);
      
      // Gọi API để xử lý PDF trước
      const response = await fetch('http://127.0.0.1:5000/process-pdf', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Có lỗi xảy ra khi xử lý file PDF');
      }
      
      // Lưu thông tin sách và hiển thị modal xác nhận
      setBookInfo({
        book: data.book,
        content: data.content
      });
      setShowBookInfoModal(true);
      setIsLoading(false);
      
    } catch (error) {
      setError(error.message);
      setIsLoading(false);
    }
  };
  
  const handleConfirmBookInfo = async (confirmedInfo) => {
    try {
      setIsLoading(true);
      
      // Tạo FormData để gửi thông tin
      const formData = new FormData();
      formData.append('file', file);
      formData.append('subject', subject);
      formData.append('numberLesson', numberLesson);
      formData.append('durationLesson', durationLesson);
      formData.append('bookName', confirmedInfo.book);
      formData.append('bookContent', confirmedInfo.content);
      
      // Gọi API để tạo khóa học
      const response = await fetch('http://127.0.0.1:5000/create-course', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Có lỗi xảy ra khi tạo khóa học');
      }
      
      // Chuyển hướng đến trang khóa học mới
      navigate(`/chat/${data.id}`);
      onClose();
      
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
      setShowBookInfoModal(false);
    }
  };

  return (
    <>
      <div className="modal-overlay">
        <div className="modal-content">
          <h2>Tạo khóa học mới</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Tên môn học:</label>
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Nhập tên môn học"
                required
              />
            </div>
            <div className="form-group">
              <label>Tài liệu:</label>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Số buổi học:</label>
              <input
                type="number"
                value={numberLesson}
                onChange={(e) => setNumberLesson(e.target.value)}
                placeholder="Nhập số buổi học"
                min="1"
                required
              />
            </div>
            <div className="form-group">
              <label>Thời lượng mỗi buổi (giờ):</label>
              <input
                type="number"
                value={durationLesson}
                onChange={(e) => setDurationLesson(e.target.value)}
                placeholder="Nhập thời lượng mỗi buổi"
                min="1"
                required
              />
            </div>
            {error && <div className="error-message">{error}</div>}
            
            {isLoading ? (
              <div className="loading-spinner">
                <div className="spinner"></div>
              </div>
            ) : (
              <div className="modal-actions">
                <button type="button" className="cancel-btn" onClick={onClose}>Hủy</button>
                <button type="submit" className="submit-btn">Tiếp tục</button>
              </div>
            )}
          </form>
        </div>
      </div>
      
      // Trong phần render, cập nhật BookInfoModal component
        {showBookInfoModal && (
          <BookInfoModal
            isOpen={showBookInfoModal}
            onClose={() => setShowBookInfoModal(false)}
            bookInfo={bookInfo}
            onConfirm={handleConfirmBookInfo}
            pdfFile={file}  // Truyền file PDF vào modal
          />
        )}
    </>
  );
};

export default CreateCourseModal;
