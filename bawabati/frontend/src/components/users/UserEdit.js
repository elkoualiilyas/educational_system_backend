import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { getCSRFToken } from '../../utils/csrf';

const UserEdit = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    role: 'student',
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchUser();
    // eslint-disable-next-line
  }, [id]);

  const fetchUser = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`/api/users/${id}/`);
      setFormData({
        username: res.data.username || '',
        email: res.data.email || '',
        first_name: res.data.first_name || '',
        last_name: res.data.last_name || '',
        role: res.data.userprofile?.role || 'student',
      });
    } catch (err) {
      setError('Failed to load user data.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      // Prevent admin role change
      if (formData.role === 'admin') {
        setError('Cannot set user role to admin through this form.');
        setLoading(false);
        return;
      }
      await axios.put(`/api/users/${id}/`, formData, {
        headers: { 'X-CSRFToken': getCSRFToken() }
      });
      setSuccess('User updated successfully!');
      setTimeout(() => navigate('/users'), 1000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update user.');
    } finally {
      setLoading(false);
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
    <div className="container mt-4">
      <h2>Edit User</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label">Username</label>
          <input type="text" className="form-control" name="username" value={formData.username} readOnly />
        </div>
        <div className="mb-3">
          <label className="form-label">Email</label>
          <input type="email" className="form-control" name="email" value={formData.email} onChange={handleChange} required />
        </div>
        <div className="mb-3">
          <label className="form-label">First Name</label>
          <input type="text" className="form-control" name="first_name" value={formData.first_name} onChange={handleChange} required />
        </div>
        <div className="mb-3">
          <label className="form-label">Last Name</label>
          <input type="text" className="form-control" name="last_name" value={formData.last_name} onChange={handleChange} required />
        </div>
        <div className="mb-3">
          <label className="form-label">Role</label>
          <select className="form-select" name="role" value={formData.role} onChange={handleChange} required>
            <option value="student">Student</option>
            <option value="teacher">Teacher</option>
          </select>
        </div>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Saving...' : 'Update User'}
        </button>
      </form>
    </div>
  );
};

export default UserEdit; 