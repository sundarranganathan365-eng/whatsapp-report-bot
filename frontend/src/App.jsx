import React from 'react';
import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { LayoutDashboard, Users, CalendarCheck, BookOpen, FileText } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import StudentsModule from './pages/StudentsModule';
import AttendanceModule from './pages/AttendanceModule';
import MarksModule from './pages/MarksModule';
import ReportPreview from './pages/ReportPreview';

const Sidebar = () => {
  return (
    <div className="sidebar">
      <h2>Admin Portal</h2>
      <div className="nav-links">
        <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <LayoutDashboard size={20} /> Dashboard
        </NavLink>
        <NavLink to="/students" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Users size={20} /> Students
        </NavLink>
        <NavLink to="/attendance" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <CalendarCheck size={20} /> Attendance
        </NavLink>
        <NavLink to="/marks" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <BookOpen size={20} /> Tests & Exams
        </NavLink>
        <NavLink to="/reports" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <FileText size={20} /> Report Preview
        </NavLink>
      </div>
    </div>
  );
};

const Layout = ({ children }) => {
  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-content">
        {children}
      </div>
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/students" element={<StudentsModule />} />
          <Route path="/attendance" element={<AttendanceModule />} />
          <Route path="/marks" element={<MarksModule />} />
          <Route path="/reports" element={<ReportPreview />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
