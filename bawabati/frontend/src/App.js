import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import './App.css';
import { getCSRFToken } from './utils/csrf'; // adjust path if needed

// Components
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import AdminDashboard from './components/dashboard/AdminDashboard';
import TeacherDashboard from './components/dashboard/TeacherDashboard';
import StudentDashboard from './components/dashboard/StudentDashboard';
import Profile from './components/profile/Profile';
import UserList from './components/users/UserList';
import CourseList from './components/courses/CourseList';
import CourseDetail from './components/courses/CourseDetail';
import NoteForm from './components/notes/NoteForm';
import CourseForm from './components/courses/CourseForm';
import UserCreate from './components/users/UserCreate';
import UserEdit from './components/users/UserEdit';
import GradeList from './components/grades/GradeList';
import GradeForm from './components/grades/GradeForm';

// API configuration
axios.defaults.baseURL = 'http://localhost:8000';
axios.defaults.withCredentials = true;

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const checkAuth = async () => {
      try {
        const response = await axios.get('/api/auth/user/');
        setUser(response.data);
      } catch (error) {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = async () => {
    try {
      await axios.post('/api/auth/logout/', {}, {
        headers: { 'X-CSRFToken': getCSRFToken() }
      });
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  if (loading) {
    return <div className="text-center mt-5"><div className="spinner-border" role="status"></div></div>;
  }

  return (
    <Router>
      <div className="app-container">
        {user && <Navbar user={user} onLogout={handleLogout} />}
        <div className="d-flex">
          {user && <Sidebar user={user} />}
          <div className={`content ${user ? 'with-sidebar' : ''}`}>
            <Routes>
              <Route path="/login" element={!user ? <Login onLogin={handleLogin} /> : <Navigate to="/" />} />
              <Route path="/register" element={!user ? <Register onLogin={handleLogin} /> : <Navigate to="/" />} />
              
              {/* Protected routes */}
              <Route path="/" element={user ? (
                user.userprofile.role === 'admin' ? <AdminDashboard /> :
                user.userprofile.role === 'teacher' ? <TeacherDashboard /> :
                <StudentDashboard />
              ) : <Navigate to="/login" />} />
              
              <Route path="/profile" element={user ? <Profile user={user} /> : <Navigate to="/login" />} />
              <Route path="/users" element={user && user.userprofile.role === 'admin' ? <UserList /> : <Navigate to="/" />} />
              <Route path="/users/add" element={user && user.userprofile.role === 'admin' ? <UserCreate /> : <Navigate to="/login" />} />
              <Route path="/users/:id/update" element={user && user.userprofile.role === 'admin' ? <UserEdit /> : <Navigate to="/login" />} />
              <Route path="/courses" element={user ? <CourseList /> : <Navigate to="/login" />} />
              <Route path="/courses/:id" element={user ? <CourseDetail /> : <Navigate to="/login" />} />
              <Route path="/courses/:id/grades" element={user ? <GradeList /> : <Navigate to="/login" />} />
              <Route path="/courses/:courseId/students/:studentId/grades/:semester/:assessmentType/add" 
                     element={user && (user.userprofile.role === 'admin' || user.userprofile.role === 'teacher') ? 
                     <GradeForm isEdit={false} /> : <Navigate to="/login" />} />
              <Route path="/courses/:courseId/grades/:gradeId/edit" 
                     element={user && (user.userprofile.role === 'admin' || user.userprofile.role === 'teacher') ? 
                     <GradeForm isEdit={true} /> : <Navigate to="/login" />} />
              <Route path="/notes/add" element={user && (user.userprofile.role === 'admin' || user.userprofile.role === 'teacher') ? <UploadNotePage /> : <Navigate to="/login" />} />
              <Route path="/courses/add" element={user && user.userprofile.role === 'admin' ? <CourseForm isEdit={false} /> : <Navigate to="/login" />} />
              <Route path="/courses/:id/edit" element={user && user.userprofile.role === 'admin' ? <CourseForm isEdit={true} /> : <Navigate to="/login" />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
}

function UploadNotePage() {
  // Optionally, get courseId from query params if needed
  return (
    <div className="container mt-4">
      <h2>Upload Note</h2>
      <NoteForm courseId={null} />
    </div>
  );
}

export default App;
