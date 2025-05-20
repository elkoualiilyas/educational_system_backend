import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import NoteForm from '../notes/NoteForm';

const CourseDetail = () => {
  const { id } = useParams();
  const [course, setCourse] = useState(null);
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCourseDetails();
    fetchNotes();
  }, [id]);

  const fetchCourseDetails = async () => {
    try {
      const response = await axios.get(`/api/courses/${id}/`);
      setCourse(response.data);
    } catch (error) {
      setError('Failed to load course details. Please try again.');
      console.error('Error fetching course details:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchNotes = async () => {
    try {
      const response = await axios.get(`/api/courses/${id}/notes/`);
      setNotes(response.data);
    } catch (error) {
      console.error('Error fetching notes:', error);
    }
  };

  const handleEnroll = async () => {
    try {
      await axios.post(`/api/courses/${id}/enroll/`);
      // Refresh course details
      fetchCourseDetails();
    } catch (error) {
      setError('Failed to enroll in course. Please try again.');
      console.error('Error enrolling in course:', error);
    }
  };

  const handleNoteAdded = (newNote) => {
    setNotes([...notes, newNote]);
  };

  const handleDeleteNote = async (noteId) => {
    if (!window.confirm('Are you sure you want to delete this note?')) {
      return;
    }

    try {
      await axios.delete(`/api/notes/${noteId}/`);
      setNotes(notes.filter(note => note.id !== noteId));
    } catch (error) {
      setError('Failed to delete note. Please try again.');
      console.error('Error deleting note:', error);
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

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    );
  }

  if (!course) {
    return (
      <div className="alert alert-warning" role="alert">
        Course not found.
      </div>
    );
  }

  const canManageNotes = course.assigned_teacher?.id === course.current_user?.id || 
                        course.current_user?.userprofile?.role === 'admin';

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>{course.title}</h2>
        <div>
          <Link to={`/courses/${id}/grades`} className="btn btn-info me-2">
            <i className="fas fa-graduation-cap me-2"></i> View Grades
          </Link>
          <Link to="/courses" className="btn btn-secondary me-2">
            <i className="fas fa-arrow-left me-2"></i> Back to Courses
          </Link>
          {course.can_enroll && (
            <button className="btn btn-success" onClick={handleEnroll}>
              <i className="fas fa-user-plus me-2"></i> Enroll Now
            </button>
          )}
        </div>
      </div>

      <div className="row">
        <div className="col-md-8">
          <div className="card mb-4">
            <div className="card-body">
              <h5 className="card-title">Course Description</h5>
              <p className="card-text">{course.description}</p>
            </div>
          </div>

          <div className="card mb-4">
            <div className="card-body">
              <h5 className="card-title">Course Details</h5>
              <div className="row">
                <div className="col-md-6">
                  <p><strong>Teacher:</strong> {course.assigned_teacher?.first_name} {course.assigned_teacher?.last_name}</p>
                  <p><strong>Specialisation:</strong> {course.specialisation}</p>
                  <p><strong>Capacity:</strong> {course.capacity} students</p>
                </div>
                <div className="col-md-6">
                  <p><strong>Start Date:</strong> {new Date(course.start_date).toLocaleDateString()}</p>
                  <p><strong>End Date:</strong> {new Date(course.end_date).toLocaleDateString()}</p>
                  <p><strong>Created:</strong> {new Date(course.created_at).toLocaleDateString()}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-4">
          {canManageNotes && (
            <NoteForm courseId={course.id} onNoteAdded={handleNoteAdded} />
          )}

          <div className="card mb-4">
            <div className="card-body">
              <h5 className="card-title">Course Notes</h5>
              {notes.length > 0 ? (
                <div className="list-group">
                  {notes.map(note => (
                    <div key={note.id} className="list-group-item">
                      <div className="d-flex w-100 justify-content-between align-items-center">
                        <div>
                          <h6 className="mb-1">{note.title}</h6>
                          <small className="text-muted">
                            Uploaded by {note.uploaded_by.first_name} {note.uploaded_by.last_name}
                          </small>
                        </div>
                        <div>
                          <a
                            href={note.file}
                            className="btn btn-sm btn-primary me-2"
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            <i className="fas fa-download"></i>
                          </a>
                          {canManageNotes && (
                            <button
                              className="btn btn-sm btn-danger"
                              onClick={() => handleDeleteNote(note.id)}
                            >
                              <i className="fas fa-trash"></i>
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted">No notes available for this course.</p>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Enrolled Students</h5>
              {course.enrolled_students && course.enrolled_students.length > 0 ? (
                <div className="list-group">
                  {course.enrolled_students.map(student => (
                    <div key={student.id} className="list-group-item">
                      <div className="d-flex w-100 justify-content-between">
                        <h6 className="mb-1">{student.first_name} {student.last_name}</h6>
                        <small>Enrolled: {new Date(student.enrollment_date).toLocaleDateString()}</small>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted">No students enrolled in this course yet.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CourseDetail; 