import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Sidebar = ({ user }) => {
  const location = useLocation();
  
  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };
  
  return (
    <div className="sidebar bg-dark text-white" style={{ width: '250px', minHeight: 'calc(100vh - 56px)', position: 'fixed', top: '56px', left: 0 }}>
      <div className="p-3">
        <div className="text-center mb-3">
          <div className="mb-2">
            <i className="fas fa-user-circle fa-3x"></i>
          </div>
          <h6>{user.first_name || user.username}</h6>
          <small className="text-muted">
            {user.userprofile.role === 'admin' ? 'Administrator' :
             user.userprofile.role === 'teacher' ? 'Teacher' : 'Student'}
          </small>
        </div>
        <hr className="my-2" />
        <ul className="nav flex-column">
          <li className="nav-item">
            <Link 
              to="/" 
              className={`nav-link ${isActive('/') ? 'active bg-primary' : 'text-white-50'}`}
            >
              <i className="fas fa-tachometer-alt me-2"></i> Dashboard
            </Link>
          </li>
          <li className="nav-item">
            <Link 
              to="/courses" 
              className={`nav-link ${isActive('/courses') ? 'active bg-primary' : 'text-white-50'}`}
            >
              <i className="fas fa-book me-2"></i> Courses
            </Link>
          </li>
          
          {user.userprofile.role === 'admin' && (
            <li className="nav-item">
              <Link 
                to="/users" 
                className={`nav-link ${isActive('/users') ? 'active bg-primary' : 'text-white-50'}`}
              >
                <i className="fas fa-users me-2"></i> Users
              </Link>
            </li>
          )}
          
          {(user.userprofile.role === 'teacher' || user.userprofile.role === 'admin') && (
            <li className="nav-item">
              <Link 
                to="/notes/add" 
                className={`nav-link ${isActive('/notes/add') ? 'active bg-primary' : 'text-white-50'}`}
              >
                <i className="fas fa-file-upload me-2"></i> Upload Note
              </Link>
            </li>
          )}
          
          <li className="nav-item">
            <Link 
              to="/profile" 
              className={`nav-link ${isActive('/profile') ? 'active bg-primary' : 'text-white-50'}`}
            >
              <i className="fas fa-user-circle me-2"></i> Profile
            </Link>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default Sidebar; 