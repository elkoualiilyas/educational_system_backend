import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

const GradeList = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [grades, setGrades] = useState([]);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [course, setCourse] = useState(null);
  const [isTeacher, setIsTeacher] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState('');
  const [selectedSemester, setSelectedSemester] = useState(1);
  const [selectedAssessment, setSelectedAssessment] = useState('control_1');

  useEffect(() => {
    if (!id) {
      setError('Course ID is missing');
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      try {
        const [courseRes, gradesRes] = await Promise.all([
          axios.get(`/api/courses/${id}/`),
          axios.get(`/api/courses/${id}/grades/`)
        ]);
        
        setCourse(courseRes.data);
        setGrades(gradesRes.data.grades);
        setReports(gradesRes.data.reports);
        setIsTeacher(courseRes.data.current_user?.userprofile?.role === 'teacher' || 
                    courseRes.data.current_user?.userprofile?.role === 'admin');
      } catch (err) {
        setError('Failed to load grades');
        console.error('Error loading grades:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  const getAssessmentTypeLabel = (type) => {
    const types = {
      'control_1': 'Premier Contrôle',
      'control_2': 'Deuxième Contrôle',
      'exam': 'Examen Final'
    };
    return types[type] || type;
  };

  const getSemesterLabel = (semester) => {
    return semester === 1 ? 'First Semester' : 'Second Semester';
  };

  const handleAddGrade = () => {
    if (!selectedStudent) {
      alert('Please select a student');
      return;
    }
    navigate(`/courses/${id}/students/${selectedStudent}/grades/${selectedSemester}/${selectedAssessment}/add`);
  };

  if (loading) return <div className="container mt-4">Loading...</div>;
  if (error) return (
    <div className="container mt-4">
      <div className="alert alert-danger">{error}</div>
      <button className="btn btn-secondary" onClick={() => navigate(-1)}>
        <i className="fas fa-arrow-left me-2"></i> Go Back
      </button>
    </div>
  );
  if (!course) return (
    <div className="container mt-4">
      <div className="alert alert-warning">Course not found</div>
      <button className="btn btn-secondary" onClick={() => navigate(-1)}>
        <i className="fas fa-arrow-left me-2"></i> Go Back
      </button>
    </div>
  );

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Grades for {course.title}</h2>
        <button className="btn btn-secondary" onClick={() => navigate(-1)}>
          <i className="fas fa-arrow-left me-2"></i> Back to Course
        </button>
      </div>
      
      {/* Grade Reports Summary */}
      <div className="card mb-4">
        <div className="card-header">
          <h4>Grade Reports</h4>
        </div>
        <div className="card-body">
          <div className="table-responsive">
            <table className="table">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Semester</th>
                  <th>Continuous Assessment</th>
                  <th>Exam Grade</th>
                  <th>Final Average</th>
                </tr>
              </thead>
              <tbody>
                {reports.map(report => (
                  <tr key={report.id}>
                    <td>{report.student.first_name} {report.student.last_name}</td>
                    <td>{getSemesterLabel(report.semester)}</td>
                    <td>{report.continuous_assessment_average || '-'}</td>
                    <td>{report.exam_grade || '-'}</td>
                    <td>{report.final_average || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Detailed Grades */}
      <div className="card">
        <div className="card-header d-flex justify-content-between align-items-center">
          <h4>Detailed Grades</h4>
          {isTeacher && (
            <button 
              className="btn btn-primary" 
              onClick={() => setShowAddModal(true)}
            >
              <i className="fas fa-plus me-2"></i> Add Grade
            </button>
          )}
        </div>
        <div className="card-body">
          <div className="table-responsive">
            <table className="table">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Semester</th>
                  <th>Assessment</th>
                  <th>Written (70%)</th>
                  <th>Participation (15%)</th>
                  <th>Homework (15%)</th>
                  <th>Final Grade</th>
                  <th>Comments</th>
                  {isTeacher && <th>Actions</th>}
                </tr>
              </thead>
              <tbody>
                {grades.map(grade => (
                  <tr key={grade.id}>
                    <td>{grade.student.first_name} {grade.student.last_name}</td>
                    <td>{getSemesterLabel(grade.semester)}</td>
                    <td>{getAssessmentTypeLabel(grade.assessment_type)}</td>
                    <td>{grade.written_grade}</td>
                    <td>{grade.participation || '-'}</td>
                    <td>{grade.homework || '-'}</td>
                    <td>{grade.final_grade}</td>
                    <td>{grade.comments || '-'}</td>
                    {isTeacher && (
                      <td>
                        <Link 
                          to={`/courses/${id}/grades/${grade.id}/edit`}
                          className="btn btn-sm btn-primary me-2"
                        >
                          <i className="fas fa-edit me-1"></i> Edit
                        </Link>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Add Grade Modal */}
      {showAddModal && (
        <div className="modal show d-block" tabIndex="-1">
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Add New Grade</h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => setShowAddModal(false)}
                ></button>
              </div>
              <div className="modal-body">
                <div className="mb-3">
                  <label className="form-label">Student</label>
                  <select 
                    className="form-select" 
                    value={selectedStudent} 
                    onChange={(e) => setSelectedStudent(e.target.value)}
                  >
                    <option value="">Select a student</option>
                    {course.enrolled_students?.map(student => (
                      <option key={student.id} value={student.id}>
                        {student.first_name} {student.last_name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="mb-3">
                  <label className="form-label">Semester</label>
                  <select 
                    className="form-select" 
                    value={selectedSemester} 
                    onChange={(e) => setSelectedSemester(parseInt(e.target.value))}
                  >
                    <option value={1}>First Semester</option>
                    <option value={2}>Second Semester</option>
                  </select>
                </div>
                <div className="mb-3">
                  <label className="form-label">Assessment Type</label>
                  <select 
                    className="form-select" 
                    value={selectedAssessment} 
                    onChange={(e) => setSelectedAssessment(e.target.value)}
                  >
                    <option value="control_1">Premier Contrôle</option>
                    <option value="control_2">Deuxième Contrôle</option>
                    <option value="exam">Examen Final</option>
                  </select>
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setShowAddModal(false)}
                >
                  Cancel
                </button>
                <button 
                  type="button" 
                  className="btn btn-primary" 
                  onClick={handleAddGrade}
                >
                  Continue
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      {showAddModal && <div className="modal-backdrop show"></div>}
    </div>
  );
};

export default GradeList; 