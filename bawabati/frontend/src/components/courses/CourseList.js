import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const CourseList = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedSpecialisation, setSelectedSpecialisation] = useState('');
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetchCourses();
  }, [selectedSpecialisation]);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      setError('');
      const url = selectedSpecialisation 
        ? `/api/courses/?specialisation=${selectedSpecialisation}`
        : '/api/courses/';
      const response = await axios.get(url);
      setCourses(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to load courses. Please try again.');
      console.error('Error fetching courses:', error);
      setCourses([]);
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async (courseId) => {
    try {
      await axios.post(`/api/courses/${courseId}/enroll/`);
      // Refresh the courses list
      fetchCourses();
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to enroll in course. Please try again.');
      console.error('Error enrolling in course:', error);
    }
  };

  if (loading) {
    return (
      <div className="text-center mt-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Courses</h2>
        <Link to="/courses/add" className="btn btn-primary">
          <i className="fas fa-plus me-2"></i> Add Course
        </Link>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      <div className="card mb-4">
        <div className="card-body">
          <div className="row align-items-center">
            <div className="col-md-6">
              <label htmlFor="specialisationFilter" className="form-label">Filter by Specialisation:</label>
              <select
                id="specialisationFilter"
                className="form-select"
                value={selectedSpecialisation}
                onChange={(e) => setSelectedSpecialisation(e.target.value)}
              >
                <option value="">All Specialisations</option>
                <option value="computer_science">Computer Science</option>
                <option value="mathematics">Mathematics</option>
                <option value="physics">Physics</option>
                <option value="chemistry">Chemistry</option>
                <option value="biology">Biology</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {courses.length === 0 ? (
        <div className="alert alert-info" role="alert">
          No courses found.
        </div>
      ) : (
        <div className="row">
          {courses.map(course => (
            <div key={course.id} className="col-md-6 col-lg-4 mb-4">
              <div className="card h-100">
                <div className="card-body">
                  <h5 className="card-title">{course.title}</h5>
                  <h6 className="card-subtitle mb-2 text-muted">
                    {course.assigned_teacher?.first_name} {course.assigned_teacher?.last_name}
                  </h6>
                  <p className="card-text">{course.description}</p>
                  <div className="mb-3">
                    <span className="badge bg-primary me-2">{course.specialisation}</span>
                    <span className="badge bg-info">Capacity: {course.capacity}</span>
                  </div>
                  <div className="d-flex justify-content-between align-items-center">
                    <Link to={`/courses/${course.id}`} className="btn btn-primary">
                      <i className="fas fa-eye me-2"></i> View Details
                    </Link>
                    {course.can_enroll && (
                      <button
                        className="btn btn-success"
                        onClick={() => handleEnroll(course.id)}
                      >
                        <i className="fas fa-user-plus me-2"></i> Enroll
                      </button>
                    )}
                    {/* Edit button for admins */}
                    {user && user.userprofile.role === 'admin' && (
                      <Link to={`/courses/${course.id}/edit`} className="btn btn-warning ms-2">
                        <i className="fas fa-edit me-2"></i> Edit
                      </Link>
                    )}
                  </div>
                </div>
                <div className="card-footer text-muted">
                  Start Date: {new Date(course.start_date).toLocaleDateString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CourseList; 