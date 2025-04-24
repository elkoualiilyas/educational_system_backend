# Bawabati School Management System - Project Report

## 1. Project Overview

### Name and Purpose
**Bawabati** is a comprehensive school management system designed to streamline educational administration processes. The platform facilitates interaction between administrators, teachers, and students through a unified web interface, enabling course management, content sharing, and student enrollment.

### Technologies Used
- **Backend**: Python 3.11, Django 5.2
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5
- **Form Processing**: Crispy Forms with Bootstrap5
- **Database**: MySQL
- **Development Tools**: Django Debug Toolbar
- **Authentication**: Django's built-in authentication system

### Folder Structure
```
educational_system/bawabati/
├── bawabati/ (Project settings)
│   ├── settings.py (Configuration)
│   ├── urls.py (Main URL routing)
│   └── wsgi.py (WSGI configuration)
├── bawabati_app/ (Main application)
│   ├── migrations/ (Database migrations)
│   ├── templates/ (HTML templates)
│   │   └── bawabati_app/ (App-specific templates)
│   ├── models.py (Data models)
│   ├── views.py (View functions/classes)
│   ├── urls.py (URL routing)
│   ├── forms.py (Form definitions)
│   └── signals.py (Django signals)
├── students/ (Student-specific app)
├── teachers/ (Teacher-specific app)
├── courses/ (Course management app)
├── grades/ (Grades management app)
└── manage.py (Django command-line utility)
```

## 2. User Roles & Access

### Role: Admin
**Functions:**
- User management (create, view, edit, delete users)
- Course management (create, assign teachers, monitor)
- System-wide monitoring and administration
- Role assignment and permission management

**Views:**
- Admin dashboard with system statistics
- User management interface
- Course creation and management
- System configuration options

### Role: Teacher
**Functions:**
- Create and manage assigned courses
- Upload course materials (notes)
- View enrolled students
- Manage course content

**Views:**
- Teacher dashboard showing assigned courses
- Course detail view with student lists
- Note upload interface
- Profile management

### Role: Student
**Functions:**
- Enroll in available courses
- View course materials
- Download notes
- View personal enrollment information

**Views:**
- Student dashboard showing enrolled courses
- Course browsing interface
- Course detail view with materials
- Profile management

## 3. Main Features

### Authentication
- **Login/Register**: Custom implementation with role-based fields
- **Role-based Redirection**: After login, users are directed to role-specific dashboards
- **Password Management**: Secure password handling and reset functionality
- **Profile Management**: Users can update their profile information

### Course Management
- **Course Creation**: Admin and teachers can create new courses
- **Course Assignment**: Admin can assign teachers to courses
- **Course Editing**: Update course details including title, description, and teacher assignment
- **Course Listing**: Filtered views based on user roles

### Note Upload/Download
- **Secure File Storage**: Server-side storage of educational materials
- **File Type Restriction**: System validates file types for security
- **Metadata Storage**: Notes include upload date, uploader info, and description
- **Controlled Access**: Students can only download notes from enrolled courses

### Enrollment System
- **Self-enrollment**: Students can enroll themselves in available courses
- **Enrollment Management**: Teachers and admins can view enrolled students
- **Enrollment Statistics**: Dashboard displays enrollment metrics
- **Enrollment Restrictions**: Business logic defines enrollment rules

## 4. Database Models

### UserProfile
- **Extension of Django's User model** (OneToOneField)
- **Fields**:
  - `user`: OneToOneField to Django's User model
  - `role`: CharField with choices ('student', 'teacher', 'admin')
  - `profile_picture`: ImageField for user avatars
  - `bio`: TextField for user description
- **Relationships**: Connected to User model via OneToOne relationship

### Course
- **Core educational unit in the system**
- **Fields**:
  - `title`: CharField for course name
  - `code`: CharField for unique course code
  - `description`: TextField for course details
  - `assigned_teacher`: ForeignKey to User model
  - `created_at`: DateTimeField (auto-added)
- **Relationships**: 
  - Connected to User (teacher) via ForeignKey
  - Referenced by Note and Enrollment models

### Note
- **Educational materials attached to courses**
- **Fields**:
  - `title`: CharField for note title
  - `course`: ForeignKey to Course model
  - `file`: FileField for the actual document
  - `uploaded_by`: ForeignKey to User model
  - `upload_date`: DateTimeField (auto-added)
  - `description`: TextField (optional)
- **Relationships**: Connected to Course and User models via ForeignKeys

### Enrollment
- **Links students to courses**
- **Fields**:
  - `student`: ForeignKey to User model
  - `course`: ForeignKey to Course model
  - `enrollment_date`: DateTimeField (auto-added)
  - `status`: CharField with choices ('active', 'completed', 'dropped')
- **Relationships**: Connected to User (student) and Course models via ForeignKeys

## 5. Routing & Views

### Main URL Patterns
- `/`: Home page / dashboard (role-specific)
- `/login/`: Login page
- `/logout/`: Logout endpoint
- `/register/`: User registration
- `/profile/`: User profile management
- `/users/`: User management (admin only)
- `/courses/`: Course listing
- `/courses/<id>/`: Course details
- `/courses/add/`: Course creation
- `/courses/<id>/edit/`: Course editing
- `/courses/<id>/delete/`: Course deletion
- `/courses/<id>/enroll/`: Course enrollment endpoint
- `/notes/add/`: Note upload

### View Types
The application primarily uses **function-based views** with decorators for permission handling, although some more complex views utilize **class-based views** for features like form handling and CRUD operations.

Notable view patterns include:
- Role-based dashboard redirection
- Permission-decorated views for admin features
- Form handling for profile and course management
- Detail views with context-dependent content

## 6. Templates & UI

### Template Structure
```
templates/
└── bawabati_app/
    ├── base.html (Base template with common elements)
    ├── login.html (Authentication)
    ├── register.html (User registration)
    ├── dashboard/
    │   ├── admin_dashboard.html
    │   ├── teacher_dashboard.html
    │   └── student_dashboard.html
    ├── course_list.html (Course listing)
    ├── course_detail.html (Course details)
    ├── course_form.html (Course creation/editing)
    ├── note_form.html (Note upload)
    ├── user_list.html (User management)
    └── profile.html (Profile management)
```

### Role-based Template Usage
The system uses conditional rendering within templates and separate dashboard templates for different user roles. Template inheritance is utilized with `base.html` providing the common structure.

### UI Framework
- **Bootstrap 5**: Primary UI framework for responsive design
- **Crispy Forms**: Enhanced form rendering
- **FontAwesome**: Icon library
- **Custom CSS**: Additional styling for specific components

## 7. Security & Best Practices

### Role-based Permissions
- **View-level Checks**: Functions to verify user roles before allowing access
- **Template Conditionals**: UI elements shown/hidden based on user role
- **URL Protection**: Admin URLs protected from unauthorized access
- **Form Validation**: Server-side validation of form submissions

### Login Required
- `@login_required` decorator applied to secured views
- Automatic redirection to login page for unauthenticated users
- Session management for persistent authentication

### File Upload Security
- **File Type Validation**: Checks on uploaded note files
- **Size Limitations**: Prevents excessively large uploads
- **Access Controls**: Students can only access notes from enrolled courses
- **Storage Security**: Files stored in protected directories

## 8. Future Improvements

### Features to Add
1. **Grading System**: Comprehensive grade tracking and reporting
2. **Attendance Tracking**: Digital attendance management
3. **Messaging System**: In-app communication between users
4. **Calendar & Scheduling**: Course schedules and events
5. **Mobile Application**: Native mobile app for better accessibility
6. **Notifications**: Real-time alerts for important events
7. **Assignment Submission**: Online assignment handling
8. **Discussion Forums**: Course-specific discussion boards
9. **API Development**: RESTful API for integrations
10. **Reporting**: Advanced analytics and reporting

### UI Enhancement Ideas
1. **Dashboard Redesign**: More intuitive and data-rich dashboards
2. **Dark Mode**: Alternative color scheme option
3. **Customizable Themes**: User-selected visual preferences
4. **Responsive Enhancements**: Better small-screen compatibility
5. **Accessibility Improvements**: WCAG compliance features

### Deployment Considerations
1. **Containerization**: Docker deployment for easier scaling
2. **CI/CD Pipeline**: Automated testing and deployment
3. **Cloud Migration**: Moving to cloud infrastructure
4. **Load Balancing**: Handling increased user traffic
5. **Backup Systems**: Automated data backup and recovery

---

*This report was generated on April 23, 2025 for the Bawabati School Management System.* 