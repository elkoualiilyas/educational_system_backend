import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getCSRFToken } from '../../utils/csrf';

const NoteForm = ({ courseId, onNoteAdded }) => {
  const [formData, setFormData] = useState({
    title: '',
    file: null,
    course: courseId || ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    if (!courseId) {
      // Fetch courses for selection
      axios.get('/api/courses/').then(res => {
        setCourses(res.data);
      });
    }
  }, [courseId]);

  const handleChange = (e) => {
    if (e.target.name === 'file') {
      const file = e.target.files[0];
      if (file && file.size > 10 * 1024 * 1024) { // 10MB limit
        setError('File size should be less than 10MB');
        e.target.value = null;
        return;
      }
      setFormData({
        ...formData,
        file: file
      });
    } else {
      setFormData({
        ...formData,
        [e.target.name]: e.target.value
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('title', formData.title);
      formDataToSend.append('file', formData.file);
      const selectedCourseId = courseId || formData.course;
      if (!selectedCourseId) {
        setError('Please select a course.');
        setLoading(false);
        return;
      }
      const response = await axios.post(
        `/api/courses/${selectedCourseId}/notes/upload/`,
        formDataToSend,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'X-CSRFToken': getCSRFToken(),
          }
        }
      );
      setFormData({
        title: '',
        file: null,
        course: courseId || ''
      });
      setSuccess('Note uploaded successfully!');
      if (onNoteAdded) {
        onNoteAdded(response.data.note);
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to upload note. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card mb-4">
      <div className="card-body">
        <h5 className="card-title">Upload Note</h5>
        {error && (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        )}
        {success && (
          <div className="alert alert-success" role="alert">
            {success}
          </div>
        )}
        <form onSubmit={handleSubmit}>
          {!courseId && (
            <div className="mb-3">
              <label htmlFor="course" className="form-label">Select Course</label>
              <select
                className="form-select"
                id="course"
                name="course"
                value={formData.course}
                onChange={handleChange}
                required
              >
                <option value="">-- Select a course --</option>
                {courses.map(course => (
                  <option key={course.id} value={course.id}>{course.title}</option>
                ))}
              </select>
            </div>
          )}
          <div className="mb-3">
            <label htmlFor="title" className="form-label">Note Title</label>
            <input
              type="text"
              className="form-control"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
            />
          </div>
          <div className="mb-3">
            <label htmlFor="file" className="form-label">File (Max 10MB)</label>
            <input
              type="file"
              className="form-control"
              id="file"
              name="file"
              onChange={handleChange}
              required
            />
            <small className="text-muted">
              Supported formats: PDF, DOC, DOCX, TXT
            </small>
          </div>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !formData.title || !formData.file || (!courseId && !formData.course)}
          >
            {loading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Uploading...
              </>
            ) : 'Upload Note'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default NoteForm; 