import React, { useState, useEffect } from 'react';
import '../../../styles/bookInfoModal.css';

const BookInfoModal = ({ isOpen, onClose, bookInfo, onConfirm, pdfFile }) => {
  const [bookName, setBookName] = useState('');
  const [bookContent, setBookContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [pdfUrl, setPdfUrl] = useState(null);

  // Cập nhật state khi bookInfo thay đổi
  useEffect(() => {
    if (bookInfo) {
      setBookName(bookInfo.book || '');
      setBookContent(bookInfo.content || '');
    }
  }, [bookInfo]);

  // Tạo URL cho file PDF
  useEffect(() => {
    if (pdfFile) {
      const url = URL.createObjectURL(pdfFile);
      setPdfUrl(url);
      
      // Cleanup function
      return () => {
        URL.revokeObjectURL(url);
      };
    }
  }, [pdfFile]);

  if (!isOpen) return null;

  const handleConfirm = () => {
    setIsLoading(true);
    onConfirm({
      book: bookName,
      content: bookContent
    });
  };

  return (
    <div className="book-info-modal-overlay">
      <div className="book-info-modal-container">
        <div className="book-info-modal-header">
          <h2>Xác nhận thông tin sách</h2>
          <button className="book-info-modal-close-btn" onClick={onClose}>×</button>
        </div>
        <div className="book-info-modal-content">
          <div className="book-info-form-section">
            <div className="book-info-form-group">
              <label>Tên sách:</label>
              <input
                type="text"
                value={bookName}
                onChange={(e) => setBookName(e.target.value)}
                className="book-info-form-control"
              />
            </div>
            <div className="book-info-form-group">
              <label>Mục lục:</label>
              <textarea
                value={bookContent}
                onChange={(e) => setBookContent(e.target.value)}
                className="book-info-form-control"
                rows={15}
              />
            </div>
          </div>
          
          <div className="book-info-pdf-preview">
            {pdfUrl ? (
              <iframe 
                src={pdfUrl} 
                title="PDF Preview" 
                className="pdf-iframe"
              />
            ) : (
              <div className="pdf-placeholder">
                Không thể hiển thị PDF
              </div>
            )}
          </div>
        </div>
        
        {isLoading ? (
          <div className="loading-spinner">
            <div className="spinner"></div>
          </div>
        ) : (
          <div className="book-info-modal-footer">
            <button className="book-info-cancel-btn" onClick={onClose}>Hủy</button>
            <button className="book-info-confirm-btn" onClick={handleConfirm}>Xác nhận</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default BookInfoModal;
