import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../../../styles/lessonTabs.css';

const LessonTabs = ({ courseId, onSelectLesson }) => {
  const [lessonsStatus, setLessonsStatus] = useState({});
  const [totalLessons, setTotalLessons] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Lấy tổng số buổi học
  useEffect(() => {
    const fetchCourseData = async () => {
      try {
        const response = await axios.get(`/courses`);
        const courses = response.data;
        const course = courses.find(c => c.id === courseId);
        
        if (course) {
          setTotalLessons(course.number_lesson || 0);
          
          // Khởi tạo trạng thái cho tất cả các buổi học
          const initialStatus = {};
          for (let i = 1; i <= course.number_lesson; i++) {
            const statusKey = `lesson_${i}_status`;
            initialStatus[i] = course[statusKey] || "pending";
          }
          setLessonsStatus(initialStatus);
        }
        
        setLoading(false);
      } catch (err) {
        setError("Không thể tải dữ liệu khóa học");
        setLoading(false);
      }
    };
    
    fetchCourseData();
  }, [courseId]);

  // Kiểm tra trạng thái các buổi học định kỳ
  useEffect(() => {
    const checkLessonsStatus = async () => {
      try {
        const response = await axios.get(`/check-lessons-status/${courseId}`);
        if (response.data.success) {
          setLessonsStatus(response.data.lessonsStatus);
          
          // Kiểm tra xem có buổi học nào đang loading không
          const hasLoadingLessons = Object.values(response.data.lessonsStatus).includes("loading");
          
          // Nếu có buổi học đang loading, tạo buổi học tiếp theo
          if (hasLoadingLessons) {
            // Tìm buổi học đầu tiên đang loading
            const nextLessonNumber = Object.keys(response.data.lessonsStatus).find(
              key => response.data.lessonsStatus[key] === "loading"
            );
            
            if (nextLessonNumber) {
              createLesson(parseInt(nextLessonNumber));
            }
          }
        }
      } catch (err) {
        console.error("Lỗi khi kiểm tra trạng thái buổi học:", err);
      }
    };
    
    // Kiểm tra trạng thái mỗi 2 giây nếu có ít nhất một buổi học
    if (totalLessons > 0) {
      const intervalId = setInterval(checkLessonsStatus, 2000);
      return () => clearInterval(intervalId);
    }
  }, [courseId, totalLessons, lessonsStatus]);

  // Hàm tạo một buổi học
  const createLesson = async (lessonNumber) => {
    try {
      await axios.post('/create-lesson', {
        courseId,
        lessonNumber
      });
    } catch (err) {
      console.error(`Lỗi khi tạo buổi học ${lessonNumber}:`, err);
    }
  };

  // Hàm xử lý khi người dùng nhấn vào nút Like trong Course Syllabus
  const handleSyllabusLike = async (message) => {
    try {
      setLoading(true);
      
      // Gọi API để chia buổi học
      const response = await axios.post('/split-sessions', {
        courseId,
        message
      });
      
      if (response.data.success) {
        // Cập nhật tổng số buổi học
        setTotalLessons(response.data.totalLessons);
        
        // Khởi tạo trạng thái loading cho tất cả các buổi học
        const initialStatus = {};
        for (let i = 1; i <= response.data.totalLessons; i++) {
          initialStatus[i] = "loading";
        }
        setLessonsStatus(initialStatus);
        
        // Bắt đầu tạo buổi học đầu tiên
        createLesson(1);
      }
      
      setLoading(false);
    } catch (err) {
      setError("Lỗi khi chia buổi học");
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading-spinner">Đang tải...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="lesson-tabs">
      {Array.from({ length: totalLessons }, (_, i) => i + 1).map(lessonNumber => {
        const status = lessonsStatus[lessonNumber] || "pending";
        
        return (
          <div 
            key={lessonNumber}
            className={`lesson-tab ${status}`}
            onClick={() => status === "completed" && onSelectLesson(lessonNumber)}
          >
            {status === "loading" ? (
              <>
                <span>Buổi {lessonNumber}</span>
                <span className="loading-dots">...</span>
              </>
            ) : status === "error" ? (
              <>
                <span>Buổi {lessonNumber}</span>
                <span className="error-icon">⚠️</span>
              </>
            ) : (
              <span>Buổi {lessonNumber}</span>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default LessonTabs;
