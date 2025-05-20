import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const AdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState({
    admin_count: 0,
    teacher_count: 0,
    student_count: 0,
    courses: [],
    users: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await axios.get('/api/dashboard/admin/');
        setDashboardData(response.data);
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
      <h1 className="mb-4">Admin Dashboard</h1>
      
      {/* Stats Cards */}
      <div className="row mb-4">
        <div className="col-md-4">
          <div className="card dashboard-card bg-primary text-white">
            <div className="card-body text-center">
              <i className="fas fa-user-shield card-icon"></i>
              <h5 className="card-title">Administrators</h5>
              <h2 className="card-text">{dashboardData.admin_count}</h2>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card dashboard-card bg-success text-white">
            <div className="card-body text-center">
              <i className="fas fa-chalkboard-teacher card-icon"></i>
              <h5 className="card-title">Teachers</h5>
              <h2 className="card-text">{dashboardData.teacher_count}</h2>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card dashboard-card bg-info text-white">
            <div className="card-body text-center">
              <i className="fas fa-user-graduate card-icon"></i>
              <h5 className="card-title">Students</h5>
              <h2 className="card-text">{dashboardData.student_count}</h2>
            </div>
          </div>
        </div>
      </div>
      
      {/* Recent Users */}
      <div className="table-container">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h3>Recent Users</h3>
          <Link to="/users" className="btn btn-primary">
            <i className="fas fa-users me-2"></i> View All Users
          </Link>
        </div>
        <div className="table-responsive">
          <table className="table table-striped">
            <thead>
              <tr>
                <th>Username</th>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
              </tr>
            </thead>
            <tbody>
              {dashboardData.users.slice(0, 5).map(user => (
                <tr key={user.id}>
                  <td>{user.username}</td>
                  <td>{user.first_name} {user.last_name}</td>
                  <td>{user.email}</td>
                  <td>
                    <span className={`badge ${
                      user.userprofile.role === 'admin' ? 'bg-danger' :
                      user.userprofile.role === 'teacher' ? 'bg-success' : 'bg-info'
                    }`}>
                      {user.userprofile.role}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* Recent Courses */}
      <div className="table-container">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h3>Recent Courses</h3>
          <Link to="/courses" className="btn btn-primary">
            <i className="fas fa-book me-2"></i> View All Courses
          </Link>
        </div>
        <div className="table-responsive">
          <table className="table table-striped">
            <thead>
              <tr>
                <th>Title</th>
                <th>Teacher</th>
                <th>Specialisation</th>
                <th>Capacity</th>
                <th>Start Date</th>
              </tr>
            </thead>
            <tbody>
              {dashboardData.courses.slice(0, 5).map(course => (
                <tr key={course.id}>
                  <td>
                    <Link to={`/courses/${course.id}`}>{course.title}</Link>
                  </td>
                  <td>{course.assigned_teacher.first_name} {course.assigned_teacher.last_name}</td>
                  <td>{course.specialisation}</td>
                  <td>{course.capacity}</td>
                  <td>{new Date(course.start_date).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard; 