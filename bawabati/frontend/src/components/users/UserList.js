import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { getCSRFToken } from '../../utils/csrf';

const UserList = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedRole, setSelectedRole] = useState('');

  useEffect(() => {
    fetchUsers();
  }, [selectedRole]);

  const fetchUsers = async () => {
    try {
      const url = selectedRole 
        ? `/api/users/?role=${selectedRole}`
        : '/api/users/';
      const response = await axios.get(url);
      setUsers(response.data);
    } catch (error) {
      setError('Failed to load users. Please try again.');
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) {
      return;
    }

    try {
      await axios.delete(`/api/users/${userId}/`, {
        headers: { 'X-CSRFToken': getCSRFToken() }
      });
      setUsers(users.filter(user => user.id !== userId));
    } catch (error) {
      setError('Failed to delete user. Please try again.');
      console.error('Error deleting user:', error);
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
        <h2>Users</h2>
        <Link to="/users/add" className="btn btn-primary">
          <i className="fas fa-user-plus me-2"></i> Add User
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
              <label htmlFor="roleFilter" className="form-label">Filter by Role:</label>
              <select
                id="roleFilter"
                className="form-select"
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
              >
                <option value="">All Roles</option>
                <option value="admin">Administrators</option>
                <option value="teacher">Teachers</option>
                <option value="student">Students</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="table-responsive">
        <table className="table table-striped">
          <thead>
            <tr>
              <th>Username</th>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
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
                <td>
                  <Link to={`/users/${user.id}/update`} className="btn btn-sm btn-primary me-2">
                    <i className="fas fa-edit"></i>
                  </Link>
                  <button
                    className="btn btn-sm btn-danger"
                    onClick={() => handleDelete(user.id)}
                  >
                    <i className="fas fa-trash"></i>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default UserList; 