import "../styles/chatPage.css";
import botImg from "../assets/images/bot_img.jpg";
import { useParams } from "react-router-dom";
import { useState, useEffect, useRef } from "react";

// Component for loading PDF files
const loadPdfFiles = () => {
  const context = require.context("../assets/book", true, /\.pdf$/);
  let pdfMap = {};

  context.keys().forEach((key) => {
    const parts = key.split("/");
    if (parts.length >= 4 && parts[2] === "book_origin") {
      const folderName = parts[1];
      pdfMap[folderName] = context(key);
    }
  });

  return pdfMap;
};

const pdfFiles = loadPdfFiles();

// Message component to reduce repetition
const Message = ({ message, selectedTitle, onLike, isProcessingSessions, messages }) => {
  const { role, content, isLoading, liked, timestamp } = message;
  const messageRef = useRef(null);
  
  // Kiểm tra xem có tin nhắn nào đã được like trong cùng loại chat không
  const hasLikedMessage = (selectedTitle === "CLOs" || selectedTitle === "Course Syllabus") && 
    messages.some(msg => msg.role === "assistant" && msg.liked);
  
  // Sử dụng useEffect để render công thức toán học sau khi component được render
  useEffect(() => {
    if (messageRef.current && window.MathJax && !isLoading) {
      window.MathJax.typesetPromise([messageRef.current])
        .catch(err => console.error('MathJax error:', err));
    }
  }, [content, isLoading]);

  return (
    <div className={`message ${role === "assistant" ? "received" : "sent"}`}>
      {role === "assistant" && (
        <div className="message-avatar">
          <img src={botImg} alt="avatar" />
        </div>
      )}
      <div className="message-content">
        {isLoading ? (
          <p className="message-text">
            <span className="loading-dots">...</span>
          </p>
        ) : (
          <div 
            ref={messageRef}
            className="message-text"
            dangerouslySetInnerHTML={{ __html: content }}
          />
        )}
        
        {timestamp && (
          <div className="message-timestamp">{timestamp}</div>
        )}
        
        {/* Phần code nút Like giữ nguyên */}
        {selectedTitle === "CLOs" && role === "assistant" && (
          liked ? (
            <button 
              className="like-button liked"
              disabled={true}
              aria-label="Liked this CLO"
            >
              <i className="fa-solid fa-thumbs-up"></i>
            </button>
          ) : !hasLikedMessage && (
            <button 
              className="like-button"
              onClick={() => onLike(content, "CLOs")}
              aria-label="Like this CLO"
            >
              <i className="fa-regular fa-thumbs-up"></i>
            </button>
          )
        )}
        
        {/* Phần code nút Like cho Course Syllabus giữ nguyên */}
        {selectedTitle === "Course Syllabus" && role === "assistant" && (
          liked ? (
            <button 
              className="like-button liked"
              disabled={true}
              aria-label="Liked this syllabus"
            >
              <i className="fa-solid fa-thumbs-up"></i>
            </button>
          ) : !hasLikedMessage && (
            <button 
              className="like-button"
              onClick={() => onLike(content, "Syllabus")}
              disabled={isProcessingSessions}
              aria-label="Like this syllabus"
            >
              <i className="fa-regular fa-thumbs-up"></i>
            </button>
          )
        )}
      </div>
    </div>
  );
};

// Loading indicator component
const LoadingIndicator = () => (
  <div className="loading-container">
    <div className="loading-spinner-large"></div>
    <p>Đang tải...</p>
  </div>
);

// Error message component
const ErrorMessage = ({ message }) => (
  <div className="error-container">
    <i className="fa-solid fa-circle-exclamation"></i>
    <p>{message}</p>
  </div>
);

const ChatPage = () => {
  const { id } = useParams();
  const [course, setCourse] = useState(null);
  const [selectedMessages, setSelectedMessages] = useState([]);
  const [selectedTitle, setSelectedTitle] = useState("CLOs");
  const [pdfPath, setPdfPath] = useState(""); 
  const [inputMessage, setInputMessage] = useState('');
  const [isGeneratingSyllabus, setIsGeneratingSyllabus] = useState(false);
  const [isProcessingSessions, setIsProcessingSessions] = useState(false);
  const [sessionTabs, setSessionTabs] = useState([]);
  const [isInitializingLessonChat, setIsInitializingLessonChat] = useState(false);
  const [lessonPdfMap, setLessonPdfMap] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [loadingLesson, setLoadingLesson] = useState(null);
  
  // Refs
  const initializedLessons = useRef(new Set());
  const messagesContainerRef = useRef(null);

  // Scroll to bottom of messages when new messages are added
  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  }, [selectedMessages]);

  // Load lesson PDF
  const loadLessonPdf = (lessonNumber) => {
    try {
      const lessonPdfPath = require(`../assets/book/${id}/chiabuoi/Buoi_${lessonNumber}.pdf`);
      return lessonPdfPath;
    } catch (error) {
      console.error(`Error loading PDF for lesson ${lessonNumber}:`, error);
      return null;
    }
  };
  const handleInputChange = (e) => {
    setInputMessage(e.target.value);
  };
  
  // Thiết lập MathJax
  useEffect(() => {
    if (window.MathJax) {
      // Cấu hình MathJax
      window.MathJax.options = {
        ...window.MathJax.options,
        renderActions: {
          addMenu: [],
          checkLoading: []
        },
        processSectionDelay: 0 // Giảm độ trễ xuống 0
      };
    }
  }, []);

  // Handle sending a message
  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    
    const userMessage = inputMessage;
    setInputMessage('');
    
    // Thêm tin nhắn người dùng vào state với timestamp hiện tại
    const currentTime = new Date().toLocaleTimeString('en-US', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
    
    setSelectedMessages(prev => [
      ...prev,
      { role: 'user', content: userMessage, timestamp: currentTime }
    ]);
    
    // Thêm tin nhắn loading
    const loadingMessageId = Date.now();
    setSelectedMessages(prev => [
      ...prev,
      { id: loadingMessageId, role: 'assistant', content: '', isLoading: true }
    ]);
    
    try {
      let endpoint;
      let requestBody;
      
      if (selectedTitle === "CLOs" || selectedTitle === "Course Syllabus") {
        endpoint = 'http://127.0.0.1:5000/chat';
        requestBody = {
          courseId: parseInt(id),
          message: userMessage,
          chatType: selectedTitle
        };
      } else if (selectedTitle.startsWith("Buổi")) {
        const lessonNumber = selectedTitle.split(' ')[1];
        endpoint = 'http://127.0.0.1:5000/chat-lesson';
        requestBody = {
          courseId: parseInt(id),
          lessonNumber: parseInt(lessonNumber),
          message: userMessage
        };
      }
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Xóa tin nhắn loading và thêm tin nhắn thực từ bot
        setSelectedMessages(prev => 
          prev.filter(m => m.id !== loadingMessageId).concat({
            role: 'assistant',
            content: data.message,
            timestamp: data.timestamp // Sử dụng timestamp từ server
          })
        );
        
        // Cập nhật dữ liệu khóa học
        fetchCourseData();
      } else {
        throw new Error(data.error || 'Có lỗi xảy ra');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Xóa tin nhắn loading và thêm tin nhắn lỗi
      setSelectedMessages(prev => 
        prev.filter(m => m.id !== loadingMessageId).concat({
          role: 'assistant',
          content: 'Xin lỗi, có lỗi xảy ra khi xử lý tin nhắn của bạn. Vui lòng thử lại sau.',
          timestamp: new Date().toLocaleTimeString('en-US', { 
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
          })
        })
      );
      
      setError('Không thể gửi tin nhắn. Vui lòng thử lại sau.');
    }
  };

  // Handle like actions for both CLOs and Syllabus
  const handleLike = async (messageContent, type) => {
    if (type === "CLOs") {
      setIsGeneratingSyllabus(true);
      
      // Cập nhật UI ngay lập tức
      setSelectedMessages(prev => 
        prev.map(msg => 
          msg.role === "assistant" && msg.content === messageContent
            ? { ...msg, liked: true }
            : msg
        )
      );
  
      setCourse(prev => ({
        ...prev,
        message_CLOs: prev.message_CLOs.map(msg => 
          msg.role === "assistant" && msg.content === messageContent
            ? { ...msg, liked: true }
            : msg
        ),
        message_CS: []
      }));
  
      try {
        const response = await fetch(`http://127.0.0.1:5000/initialize-syllabus`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            courseId: parseInt(id),
            selectedCLO: messageContent
          })
        });
  
        const data = await response.json();
        if (data.success) {
          fetchCourseData();
        } else {
          throw new Error(data.error || 'Có lỗi xảy ra');
        }
      } catch (error) {
        console.error('Error generating syllabus:', error);
        setError('Không thể tạo syllabus. Vui lòng thử lại sau.');
      } finally {
        setIsGeneratingSyllabus(false);
      }
    } else if (type === "Syllabus") {
      setIsProcessingSessions(true);
      
      // Cập nhật UI ngay lập tức
      setSelectedMessages(prev => 
        prev.map(msg => 
          msg.role === "assistant" && msg.content === messageContent
            ? { ...msg, liked: true }
            : msg
        )
      );
  
      setCourse(prev => ({
        ...prev,
        message_CS: prev.message_CS.map(msg => 
          msg.role === "assistant" && msg.content === messageContent
            ? { ...msg, liked: true }
            : msg
        )
      }));
      
      try {
        // Create session tabs based on number of lessons
        if (course && course.number_lesson) {
          const numberOfLessons = course.number_lesson;
          const newSessionTabs = Array.from({ length: numberOfLessons }, (_, i) => `Buổi ${i + 1}`);
          setSessionTabs(newSessionTabs);
        }
        
        // Call API to run chiabuoi function
        const response = await fetch(`http://127.0.0.1:5000/split-sessions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            courseId: parseInt(id),
            message: messageContent
          })
        });
        
        const data = await response.json();
        if (data.success) {
          fetchCourseData();
          
          // Preload PDFs for lessons
          if (course && course.number_lesson) {
            const pdfMap = {};
            for (let i = 1; i <= course.number_lesson; i++) {
              const pdfPath = loadLessonPdf(i);
              if (pdfPath) {
                pdfMap[i] = pdfPath;
              }
            }
            setLessonPdfMap(pdfMap);
          }
        } else {
          throw new Error(data.error || 'Có lỗi xảy ra');
        }
      } catch (error) {
        console.error('Error processing sessions:', error);
        setError('Có lỗi xảy ra khi tạo các buổi học.');
      } finally {
        setIsProcessingSessions(false);
      }
    }
  };
  
  const initializeLesson = async (lessonNumber) => {
    try {
      setIsInitializingLessonChat(true);
      
      const response = await fetch(`http://127.0.0.1:5000/initialize-lesson`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          courseId: parseInt(id),
          lessonNumber: parseInt(lessonNumber)
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setSelectedMessages([{
          role: 'assistant',
          content: data.message,
          timestamp: data.timestamp
        }]);
        
        // Cập nhật dữ liệu khóa học
        fetchCourseData();
      } else {
        throw new Error(data.error || 'Có lỗi xảy ra');
      }
    } catch (error) {
      console.error('Error initializing lesson:', error);
      setError('Không thể khởi tạo buổi học. Vui lòng thử lại sau.');
    } finally {
      setIsInitializingLessonChat(false);
    }
  };

  // Fetch course data
  const fetchCourseData = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`http://127.0.0.1:5000/courses`);
      const data = await response.json();
      
      const currentCourse = data.find(c => c.id === parseInt(id));
      
      if (currentCourse) {
        setCourse(currentCourse);
        
        // Cập nhật tin nhắn dựa trên tab đã chọn
        if (selectedTitle === "CLOs" && currentCourse.message_CLOs) {
          setSelectedMessages(currentCourse.message_CLOs);
        } else if (selectedTitle === "Course Syllabus" && currentCourse.message_CS) {
          setSelectedMessages(currentCourse.message_CS);
        } else if (selectedTitle.startsWith("Buổi")) {
          const lessonNumber = selectedTitle.split(' ')[1];
          const messageKey = `message_L${lessonNumber}`;
          
          if (currentCourse[messageKey]) {
            setSelectedMessages(currentCourse[messageKey]);
          } else {
            // Khởi tạo buổi học nếu chưa có
            initializeLesson(lessonNumber);
          }
        }
        
        // Tạo tabs cho các buổi học nếu đã có syllabus được like
        if (currentCourse.number_lesson && 
            currentCourse.message_CS && 
            currentCourse.message_CS.some(msg => msg.liked)) {
          const numberOfLessons = currentCourse.number_lesson;
          const newSessionTabs = Array.from({ length: numberOfLessons }, (_, i) => `Buổi ${i + 1}`);
          setSessionTabs(newSessionTabs);
        }
      } else {
        setError('Không tìm thấy khóa học');
      }
    } catch (error) {
      console.error('Error fetching course data:', error);
      setError('Không thể tải dữ liệu khóa học');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle selecting a lesson
  const handleSelectLesson = async (lessonNumber) => {
    const lessonKey = `message_L${lessonNumber}`;
    const lessonTitle = `Buổi ${lessonNumber}`;
    const lessonLoadedKey = `lesson_${lessonNumber}_loaded`;
    
    // Kiểm tra xem buổi học đã được tải chưa
    const isLessonLoaded = course[lessonLoadedKey];
    
    if (!isLessonLoaded) {
      // Đánh dấu buổi học đang tải
      setLoadingLesson(lessonNumber);
      setIsInitializingLessonChat(true);
      
      try {
        // Call API to initialize retriever for this lesson
        const response = await fetch(`http://127.0.0.1:5000/initialize-lesson`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            courseId: parseInt(id),
            lessonNumber: lessonNumber
          })
        });
        
        const data = await response.json();
        if (data.success) {
          // Update course data
          await fetchCourseData();
        } else {
          throw new Error(data.error || 'Có lỗi xảy ra khi khởi tạo buổi học');
        }
      } catch (error) {
        console.error(`Error initializing lesson ${lessonNumber}:`, error);
        setError(`Có lỗi xảy ra khi khởi tạo buổi học ${lessonNumber}`);
      } finally {
        setIsInitializingLessonChat(false);
        setLoadingLesson(null);
      }
    } else {
    
    // Update displayed PDF
    if (lessonPdfMap[lessonNumber]) {
      setPdfPath(lessonPdfMap[lessonNumber]);
    } else {
      const pdfPath = loadLessonPdf(lessonNumber);
      if (pdfPath) {
        setPdfPath(pdfPath);
        setLessonPdfMap(prev => ({...prev, [lessonNumber]: pdfPath}));
      }
    }
    
    // Update messages and title
    if (course[lessonKey]?.length > 0) {
      setSelectedMessages(course[lessonKey]);
    } else {
      // Thêm timestamp cho tin nhắn chào mừng
      const currentTime = new Date().toLocaleTimeString('en-US', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
      
      setSelectedMessages([
        {
          role: "assistant", 
          content: `Chào mừng bạn đến với ${lessonTitle}! Bạn có thể đặt câu hỏi về nội dung buổi học này.`,
          timestamp: currentTime
        }
      ]);
    }
    setSelectedTitle(lessonTitle);}
  };

  // Add this useEffect to reprocess math when input changes
  useEffect(() => {
    if (window.MathJax && messagesContainerRef.current) {
      // Sử dụng requestAnimationFrame để đảm bảo nội dung được xử lý sau khi render
      const handleMathJax = () => {
        window.MathJax.typesetPromise([messagesContainerRef.current])
          .catch(err => console.error('MathJax error:', err));
      };
  
      requestAnimationFrame(handleMathJax);
    }
  }, [inputMessage, selectedMessages]);
  
  // Initial data loading
  useEffect(() => {
    fetchCourseData();
  }, [id]);

  // Find PDF file by id
  useEffect(() => {
    if (pdfFiles[id]) {
      setPdfPath(pdfFiles[id]);
    }
    
    // Preload PDFs for lessons
    if (course && course.number_lesson) {
      const pdfMap = {};
      for (let i = 1; i <= course.number_lesson; i++) {
        const pdfPath = loadLessonPdf(i);
        if (pdfPath) {
          pdfMap[i] = pdfPath;
        }
      }
      setLessonPdfMap(pdfMap);
    }
  }, [id, course?.number_lesson]);

  if (isLoading && !course) return <LoadingIndicator />;
  if (error) return <ErrorMessage message={error} />;
  if (!course) return <ErrorMessage message="Không tìm thấy khóa học" />;

  // Check if a syllabus has been liked
  const hasSyllabusLiked = course.message_CS && course.message_CS.some(msg => msg.liked);

  return (
    <div className="chat-page">
       <div className="chat-container row">
        <div className="chat-list col l-2">
          <div className="section-header">
            <h2>{course.subject}</h2>
          </div>
          <div className="chat-body">
            {course.message_CLOs?.length > 0 && (
              <div
                className={`user-item ${selectedTitle === "CLOs" ? "active" : ""}`}
                onClick={() => {
                  setSelectedMessages(course.message_CLOs);
                  setSelectedTitle("CLOs");
                  // Display original PDF when selecting CLOs
                  if (pdfFiles[id]) {
                    setPdfPath(pdfFiles[id]);
                  }
                }}
              >
                <h3>CLOs</h3>
              </div>
            )}
            
            {/* Only show Course Syllabus if it exists or is being generated */}
            {(course.message_CS?.length > 0 || isGeneratingSyllabus) && (
              <div
                className={`user-item ${selectedTitle === "Course Syllabus" ? "active" : ""} ${isGeneratingSyllabus ? "loading" : ""}`}
                onClick={() => {
                  if (!isGeneratingSyllabus) {
                    setSelectedMessages(course.message_CS);
                    setSelectedTitle("Course Syllabus");
                    // Display original PDF when selecting Course Syllabus
                    if (pdfFiles[id]) {
                      setPdfPath(pdfFiles[id]);
                    }
                  }
                }}
              >
                <h3>
                  Course Syllabus
                  {isGeneratingSyllabus && <span className="loading-spinner">...</span>}
                </h3>
              </div>
            )}
            
            {/* Only display session tabs if a syllabus has been liked */}
            {hasSyllabusLiked && sessionTabs.length > 0 && sessionTabs.map((tab, index) => {
          const lessonNumber = index + 1;
          const lessonLoadedKey = `lesson_${lessonNumber}_loaded`;
          const isLessonLoaded = course[lessonLoadedKey];
          const isLoading = loadingLesson === lessonNumber;
          
          return (
            <div
              key={`session-tab-${index}`}
              className={`user-item ${selectedTitle === tab ? "active" : ""} ${
                !isLessonLoaded && !isLoading ? "not-loaded" : ""
              }`}
              onClick={() => handleSelectLesson(lessonNumber)}
            >
              <div className="lesson-title-container">
                <h3>{tab}</h3>
                <span className="status-indicator">
                  {isLoading && (
                    <span className="loading-dots">...</span>
                  )}
                  {!isLessonLoaded && !isLoading && (
                    <i className="fa-solid fa-download"></i>
                  )}
                </span>
              </div>
            </div>
          );
        })}
            
            {/* Display lessons from course data that have messages */}
            {Object.keys(course)
              .filter(
                (key) => 
                  key.startsWith("message_L") && 
                  course[key]?.length > 0
              )
              .sort((a, b) => {
                const numA = parseInt(a.replace("message_L", ""));
                const numB = parseInt(b.replace("message_L", ""));
                return numA - numB;
              })
              .map((key) => {
                const lessonNumber = parseInt(key.replace("message_L", ""));
                const lessonTitle = `Buổi ${lessonNumber}`;
                
                // Skip if this lesson is already in sessionTabs
                if (sessionTabs.includes(lessonTitle)) {
                  return null;
                }
                
                return (
                  <div
                    key={key}
                    className={`user-item ${selectedTitle === lessonTitle ? "active" : ""}`}
                    onClick={() => handleSelectLesson(lessonNumber)}
                  >
                    <h3>{lessonTitle}</h3>
                  </div>
                );
              })}
          </div>
        </div>

        <div className="chat-messages col l-5">
          <div className="section-header">
            <h2>{selectedTitle}</h2>
            {isProcessingSessions && (
              <div className="processing-indicator">Đang xử lý buổi học...</div>
            )}
          </div>
          <div className="messages-container" ref={messagesContainerRef}>
            {selectedMessages.length > 0 ? (
              selectedMessages.map((message, index) => (
                <Message 
                  key={index}
                  message={message}
                  selectedTitle={selectedTitle}
                  onLike={handleLike}
                  isProcessingSessions={isProcessingSessions}
                  messages={selectedMessages}
                />
              ))
            ) : (
              <div className="empty-messages">
                <p>Chưa có tin nhắn nào. Hãy bắt đầu cuộc trò chuyện!</p>
              </div>
            )}
          </div>
          <div className="message-input">
            <input 
              type="text" 
              value={inputMessage}
              onChange={handleInputChange}
              placeholder="Nhập tin nhắn..." 
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              disabled={isInitializingLessonChat || isProcessingSessions}
            />
            <button 
              className="send-button" 
              onClick={handleSendMessage}
              disabled={isInitializingLessonChat || isProcessingSessions || !inputMessage.trim()}
            >
              <span>Gửi</span>
            </button>
          </div>
        </div>

        {/* Display PDF */}
        <div className="book col l-5">
          <div className="section-header">
            <h2>Sách</h2>
          </div>
          <div className="book-content">
            {pdfPath ? (
              <iframe
                src={pdfPath}
                width="100%"
                height="100%"
                style={{ border: "none" }}
                title="Course PDF"
              ></iframe>
            ) : (
              <div className="no-pdf">
                <p>Không tìm thấy sách.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
