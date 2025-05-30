import React, { useState, useEffect } from 'react';
import '../styles/homePage.css';
import { Link, useNavigate } from 'react-router-dom';
import CreateCourseModal from '../components/ui/common/CreateCourseModal';
import { deleteCourse } from '../components/core/handleJson';

const HomePage = () => {
  const [courses, setCourses] = useState([]);
  const [editCourseId, setEditCourseId] = useState(null);
  const [newSubject, setNewSubject] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetch(`http://127.0.0.1:5000/courses`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => setCourses(data))
      .catch(error => console.error('Lỗi tải dữ liệu:', error));
  }, []);

  const updateData = (updatedCourses) => {
    fetch(`http://127.0.0.1:5000/update-data`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updatedCourses),
    })
    .then(response => response.json())
    .then(() => setCourses(updatedCourses))
    .catch(error => console.error('Lỗi cập nhật dữ liệu:', error));
  };

  const handleEdit = (event, courseId) => {
    event.preventDefault();
    event.stopPropagation();
    const updatedCourses = courses.map(course =>
      course.id === courseId ? { ...course, subject: newSubject } : course
    );
    updateData(updatedCourses);
    setEditCourseId(null);
  };

  const handleDelete = async (event, courseId) => {
    event.preventDefault();
    event.stopPropagation();
  
    try {
      await deleteCourse(courseId);
      const updatedCourses = courses.filter(course => course.id !== courseId);
      setCourses(updatedCourses);
    } catch (error) {
      console.error('Error deleting course:', error);
    }
  };

  return (
    <div className='home-page'>
      <div className='grid wide'>
        <div className='home-page__header'>
          <h1>Chào mừng bạn đến với Scistu25</h1>
          <h2>Khóa học của tôi</h2>
        </div>
        <div className='home-page__body'>
        <button 
          className='create-btn' 
          onClick={() => setIsModalOpen(true)}
        >
          Tạo mới
        </button>
        <CreateCourseModal 
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
        />
          <div className='home-page__body__list row'>
            {courses.map(course => (
              <div key={course.id} className='course col l-3 m-4 c-6 box-item'>
                {editCourseId === course.id ? (
                  <div className='course__info'>
                    <input
                      type='text'
                      value={newSubject}
                      onChange={(e) => setNewSubject(e.target.value)}
                    />
                    <p>Ngày tạo: {course.date}</p>
                  </div>
                ) : (
                  <Link to={`/chat/${course.id}`}>
                    <div className='course__info'>
                      <h2>{course.subject}</h2>
                      <p>Ngày tạo: {course.date}</p>
                    </div>
                  </Link>
                )}
                <div className='course__action'>
                  {editCourseId === course.id ? (
                    <button className='save-btn' onClick={(e) => handleEdit(e, course.id)}>
                      Lưu
                    </button>
                  ) : (
                    <button className='edit-btn' onClick={(e) => { setEditCourseId(course.id); setNewSubject(course.subject); }}>
                      Sửa
                    </button>
                  )}
                  <button className='delete-btn' onClick={(e) => handleDelete(e, course.id)}>
                    Xóa
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
