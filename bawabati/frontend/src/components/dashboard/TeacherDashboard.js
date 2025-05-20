import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const TeacherDashboard = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await axios.get('/api/dashboard/teacher/');
        setCourses(response.data.courses);
      } catch (error) {
        setError('Failed to load dashboard data. Please try again.');
        console.error('Dashboard data error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="text-center mt-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    );
  }

  return (
    <div>
      <h1 className="mb-4">Teacher Dashboard</h1>
      
      {/* Courses */}
      <div className="table-container">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h3>My Courses</h3>
          <Link to="/courses" className="btn btn-primary">
            <i className="fas fa-book me-2"></i> View All Courses
          </Link>
        </div>
        <div className="table-responsive">
          <table className="table table-striped">
            <thead>
              <tr>
                <th>Title</th>
                <th>Specialisation</th>
                <th>Capacity</th>
                <th>Start Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {courses.map(course => (
                <tr key={course.id}>
                  <td>
                    <Link to={`/courses/${course.id}`}>{course.title}</Link>
                  </td>
                  <td>{course.specialisation}</td>
                  <td>{course.capacity}</td>
                  <td>{new Date(course.start_date).toLocaleDateString()}</td>
                  <td>
                    <Link to={`/courses/${course.id}`} className="btn btn-sm btn-info me-2">
                      <i className="fas fa-eye"></i>
                    </Link>
                    <Link to={`/notes/add?course=${course.id}`} className="btn btn-sm btn-success">
                      <i className="fas fa-file-upload"></i>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default TeacherDashboard; 