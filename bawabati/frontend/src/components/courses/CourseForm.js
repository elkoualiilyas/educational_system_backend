import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { getCSRFToken } from '../../utils/csrf';

const CourseForm = ({ isEdit = false }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    specialisation: '',
    capacity: 30,
    assigned_teacher: '',
    students: [],
    end_date: ''
  });
  const [teachers, setTeachers] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchTeachers();
    fetchStudents();
    if (isEdit && id) {
      fetchCourse();
    }
    // eslint-disable-next-line
  }, [id, isEdit]);

  const fetchTeachers = async () => {
    try {
      const res = await axios.get('/api/teachers/');
      setTeachers(res.data);
    } catch (err) {
      setError('Failed to load teachers.');
    }
  };

  const fetchStudents = async () => {
    try {
      const res = await axios.get('/api/students/');
      setStudents(res.data);
    } catch (err) {
      setError('Failed to load students.');
    }
  };

  const fetchCourse = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`/api/courses/${id}/`);
      setFormData({
        title: res.data.title || '',
        description: res.data.description || '',
        specialisation: res.data.specialisation || '',
        capacity: res.data.capacity || 30,
        assigned_teacher: res.data.assigned_teacher?.id || '',
        students: res.data.enrolled_students ? res.data.enrolled_students.map(s => s.id) : [],
        end_date: res.data.end_date || ''
      });
    } catch (err) {
      setError('Failed to load course data.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, selectedOptions } = e.target;
    if (type === 'select-multiple') {
      setFormData({
        ...formData,
        [name]: Array.from(selectedOptions, option => option.value)
      });
    } else {
      setFormData({
        ...formData,
        [name]: value
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const payload = {
        ...formData,
        capacity: Number(formData.capacity),
        assigned_teacher_id: Number(formData.assigned_teacher),
        student_ids: formData.students.map(Number),
      };
      delete payload.assigned_teacher;
      delete payload.students;
      let response;
      if (isEdit && id) {
        response = await axios.put(`/api/courses/${id}/edit/`, payload, {
          headers: { 'X-CSRFToken': getCSRFToken() }
        });
      } else {
        response = await axios.post('/api/courses/add/', payload, {
          headers: { 'X-CSRFToken': getCSRFToken() }
        });
      }
      setSuccess('Course saved successfully!');
      setTimeout(() => navigate('/courses'), 1000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to save course.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-4">
      <h2>{isEdit ? 'Edit Course' : 'Add New Course'}</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label">Title</label>
          <input type="text" className="form-control" name="title" value={formData.title} onChange={handleChange} required />
        </div>
        <div className="mb-3">
          <label className="form-label">Description</label>
          <textarea className="form-control" name="description" value={formData.description} onChange={handleChange} required />
        </div>
        <div className="mb-3">
          <label className="form-label">Specialisation</label>
          <input type="text" className="form-control" name="specialisation" value={formData.specialisation} onChange={handleChange} />
        </div>
        <div className="mb-3">
          <label className="form-label">Capacity</label>
          <input type="number" className="form-control" name="capacity" value={formData.capacity} onChange={handleChange} min="1" />
        </div>
        <div className="mb-3">
          <label className="form-label">End Date</label>
          <input type="date" className="form-control" name="end_date" value={formData.end_date ? formData.end_date.substring(0, 10) : ''} onChange={handleChange} />
        </div>
        <div className="mb-3">
          <label className="form-label">Assigned Teacher</label>
          <select className="form-select" name="assigned_teacher" value={formData.assigned_teacher} onChange={handleChange} required>
            <option value="">-- Select Teacher --</option>
            {teachers.map(teacher => (
              <option key={teacher.id} value={teacher.id}>{teacher.first_name} {teacher.last_name} ({teacher.username})</option>
            ))}
          </select>
        </div>
        <div className="mb-3">
          <label className="form-label">Enroll Students</label>
          <select className="form-select" name="students" value={formData.students} onChange={handleChange} multiple>
            {students.map(student => (
              <option key={student.id} value={student.id}>{student.first_name} {student.last_name} ({student.username})</option>
            ))}
          </select>
        </div>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Saving...' : (isEdit ? 'Update Course' : 'Create Course')}
        </button>
      </form>
    </div>
  );
};

export default CourseForm; 