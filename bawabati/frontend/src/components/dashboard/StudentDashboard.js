import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const StudentDashboard = () => {
  const [enrollments, setEnrollments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await axios.get('/api/dashboard/student/');
        setEnrollments(response.data.enrollments);
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
      <h1 className="mb-4">Student Dashboard</h1>
      
      {/* Enrolled Courses */}
      <div className="table-container">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h3>My Enrolled Courses</h3>
          <Link to="/courses" className="btn btn-primary">
            <i className="fas fa-book me-2"></i> Browse Courses
          </Link>
        </div>
        <div className="table-responsive">
          <table className="table table-striped">
            <thead>
              <tr>
                <th>Course</th>
                <th>Teacher</th>
                <th>Enrollment Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {enrollments.map(enrollment => (
                <tr key={enrollment.id}>
                  <td>
                    <Link to={`/courses/${enrollment.course.id}`}>
                      {enrollment.course.title}
                    </Link>
                  </td>
                  <td>
                    {enrollment.course.assigned_teacher.first_name} {enrollment.course.assigned_teacher.last_name}
                  </td>
                  <td>{new Date(enrollment.enrollment_date).toLocaleDateString()}</td>
                  <td>
                    <Link to={`/courses/${enrollment.course.id}`} className="btn btn-sm btn-info">
                      <i className="fas fa-eye"></i> View Course
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

export default StudentDashboard; 