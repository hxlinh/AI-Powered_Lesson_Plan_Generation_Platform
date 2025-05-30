// export const updateJsonFile = (updatedCourses) => {
//     return fetch('http://localhost:5000/update-data', {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify(updatedCourses),
//     })
//     .then(response => response.json())
//     .catch(error => console.error('Lỗi khi cập nhật JSON:', error));
//   };

export const deleteCourse = async (courseId) => {
  try {
    const response = await fetch(`http://127.0.0.1:5000/delete-course/${courseId}`, {
      method: 'DELETE'
    });
    return response.json();
  } catch (error) {
    console.error('Error deleting course:', error);
    throw error;
  }
};