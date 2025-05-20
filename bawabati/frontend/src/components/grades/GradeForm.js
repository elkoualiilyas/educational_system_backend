import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';

const GradeForm = ({ isEdit = false, initialData = {} }) => {
  const { courseId, studentId, semester, assessmentType } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    semester: initialData.semester || parseInt(semester) || 1,
    assessment_type: initialData.assessment_type || assessmentType || 'control_1',
    written_grade: initialData.written_grade || '',
    participation: initialData.participation || '',
    homework: initialData.homework || '',
    comments: initialData.comments || '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [student, setStudent] = useState(null);
  const [course, setCourse] = useState(null);

  useEffect(() => {
    // Fetch only the course details
    const fetchCourse = async () => {
      try {
        const courseRes = await axios.get(`/api/courses/${courseId}/`);
        setCourse(courseRes.data);
        // Find the student in the enrolled students list
        const foundStudent = courseRes.data.enrolled_students?.find(s => String(s.id) === String(studentId));
        if (foundStudent) {
          setStudent(foundStudent);
        } else {
          setError('Student not found in this course.');
        }
      } catch (err) {
        setError('Failed to load course or student details');
      }
    };
    fetchCourse();
  }, [studentId, courseId]);

  const handleChange = (e) => {
    const value = e.target.type === 'number' ? parseFloat(e.target.value) : e.target.value;
    setFormData({
      ...formData,
      [e.target.name]: value
    });
  };

  const validateForm = () => {
    if (!formData.written_grade || formData.written_grade < 0 || formData.written_grade > 20) {
      setError('Written grade must be between 0 and 20');
      return false;
    }
    if (formData.participation && (formData.participation < 0 || formData.participation > 20)) {
      setError('Participation grade must be between 0 and 20');
      return false;
    }
    if (formData.homework && (formData.homework < 0 || formData.homework > 20)) {
      setError('Homework grade must be between 0 and 20');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const csrfToken = document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];

      const config = {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        }
      };

      const url = isEdit 
        ? `/api/grades/${initialData.id}/`
        : `/api/courses/${courseId}/students/${studentId}/grades/`;

      const response = await axios[isEdit ? 'put' : 'post'](url, formData, config);
      
      setSuccess(isEdit ? 'Grade updated successfully' : 'Grade added successfully');
      setTimeout(() => navigate(`/courses/${courseId}`), 1500);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to save grade. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!student || !course) {
    return <div className="container mt-4">Loading...</div>;
  }

  return (
    <div className="container mt-4">
      <h2>{isEdit ? 'Edit Grade' : 'Add Grade'}</h2>
      <div className="mb-4">
        <h4>Course: {course.title}</h4>
        <h4>Student: {student.first_name} {student.last_name}</h4>
      </div>
      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label">Semester</label>
          <select 
            className="form-select" 
            name="semester" 
            value={formData.semester} 
            onChange={handleChange} 
            required
            disabled={isEdit}
          >
            <option value={1}>First Semester</option>
            <option value={2}>Second Semester</option>
          </select>
        </div>
        <div className="mb-3">
          <label className="form-label">Assessment Type</label>
          <select 
            className="form-select" 
            name="assessment_type" 
            value={formData.assessment_type} 
            onChange={handleChange} 
            required
            disabled={isEdit}
          >
            <option value="control_1">Premier Contrôle</option>
            <option value="control_2">Deuxième Contrôle</option>
            <option value="exam">Examen Final</option>
          </select>
        </div>
        <div className="mb-3">
          <label className="form-label">Written Grade (70%)</label>
          <input 
            type="number" 
            step="0.01" 
            min="0" 
            max="20" 
            className="form-control" 
            name="written_grade" 
            value={formData.written_grade} 
            onChange={handleChange} 
            required 
          />
        </div>
        <div className="mb-3">
          <label className="form-label">Participation (15%)</label>
          <input 
            type="number" 
            step="0.01" 
            min="0" 
            max="20" 
            className="form-control" 
            name="participation" 
            value={formData.participation} 
            onChange={handleChange} 
          />
        </div>
        <div className="mb-3">
          <label className="form-label">Homework (15%)</label>
          <input 
            type="number" 
            step="0.01" 
            min="0" 
            max="20" 
            className="form-control" 
            name="homework" 
            value={formData.homework} 
            onChange={handleChange} 
          />
        </div>
        <div className="mb-3">
          <label className="form-label">Comments</label>
          <textarea 
            className="form-control" 
            name="comments" 
            value={formData.comments} 
            onChange={handleChange} 
          />
        </div>
        <div className="d-flex gap-2">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Saving...' : (isEdit ? 'Update Grade' : 'Add Grade')}
          </button>
          <button 
            type="button" 
            className="btn btn-secondary" 
            onClick={() => navigate(-1)}
            disabled={loading}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default GradeForm; 