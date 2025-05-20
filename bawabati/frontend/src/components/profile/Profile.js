import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getCSRFToken } from '../../utils/csrf';

const Profile = ({ user }) => {
  const [formData, setFormData] = useState({
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    email: user.email || '',
    phone_number: user.userprofile?.phone_number || '',
    bio: user.userprofile?.bio || '',
    specialisation: user.userprofile?.specialisation || ''
  });
  const [message, setMessage] = useState({ type: '', text: '' });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await axios.put('/api/users/profile/', formData, {
        headers: {
          'X-CSRFToken': getCSRFToken(),
        }
      });
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
      // Update the user data in the parent component
      if (response.data) {
        // You might want to add a callback prop to update the user data in App.js
        console.log('Profile updated:', response.data);
      }
    } catch (error) {
      setMessage({ 
        type: 'danger', 
        text: error.response?.data?.error || 'Failed to update profile. Please try again.' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <h2>Profile</h2>
      {message.text && (
        <div className={`alert alert-${message.type}`} role="alert">
          {message.text}
        </div>
      )}
      <form onSubmit={handleSubmit}>
        <div className="row">
          <div className="col-md-6">
            <div className="form-group mb-3">
              <label htmlFor="first_name">First Name</label>
              <input
                type="text"
                className="form-control"
                id="first_name"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                required
              />
            </div>
          </div>
          <div className="col-md-6">
            <div className="form-group mb-3">
              <label htmlFor="last_name">Last Name</label>
              <input
                type="text"
                className="form-control"
                id="last_name"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                required
              />
            </div>
          </div>
        </div>

        <div className="form-group mb-3">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            className="form-control"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group mb-3">
          <label htmlFor="phone_number">Phone Number</label>
          <input
            type="tel"
            className="form-control"
            id="phone_number"
            name="phone_number"
            value={formData.phone_number}
            onChange={handleChange}
          />
        </div>

        <div className="form-group mb-3">
          <label htmlFor="bio">Bio</label>
          <textarea
            className="form-control"
            id="bio"
            name="bio"
            rows="3"
            value={formData.bio}
            onChange={handleChange}
          ></textarea>
        </div>

        {(user.userprofile?.role === 'teacher' || user.userprofile?.role === 'admin') && (
          <div className="form-group mb-3">
            <label htmlFor="specialisation">Specialisation</label>
            <input
              type="text"
              className="form-control"
              id="specialisation"
              name="specialisation"
              value={formData.specialisation}
              onChange={handleChange}
            />
          </div>
        )}

        <button 
          type="submit" 
          className="btn btn-primary" 
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Updating...
            </>
          ) : 'Update Profile'}
        </button>
      </form>
    </div>
  );
};

export default Profile; 