import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { Search, Plus, Trash2 } from 'lucide-react';

const StudentsModule = () => {
  const [students, setStudents] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({ roll_no: '', name: '', class_name: '10' });
  const [filterClass, setFilterClass] = useState('All');

  const fetchStudents = async () => {
    setLoading(true);
    try {
      const data = await api.getStudents(search);
      setStudents(data);
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, [search]);

  const displayedStudents = students.filter(s => 
    filterClass === 'All' ? true : s.class_name === filterClass
  );

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      await api.addStudent(form);
      setForm({ roll_no: '', name: '', class_name: '' });
      fetchStudents();
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  const handleDelete = async (roll_no, class_name) => {
    if (!window.confirm(`Delete student Roll No ${roll_no} in Class ${class_name}?`)) return;
    try {
      await api.deleteStudent(roll_no, class_name);
      fetchStudents();
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Gradewise Student Management</h1>
        <p>Organization by 8th, 9th, and 10th Standards.</p>
      </div>

      <div className="card" style={{ marginBottom: '24px' }}>
        <h3 className="display-text">Add New Student</h3>
        <form onSubmit={handleAdd} style={{ display: 'flex', gap: '16px', marginTop: '16px', alignItems: 'flex-end' }}>
          <div className="input-group" style={{ margin: 0, flex: 1 }}>
            <label>Roll No</label>
            <input required value={form.roll_no} onChange={e => setForm({...form, roll_no: e.target.value})} placeholder="e.g. 23" />
          </div>
          <div className="input-group" style={{ margin: 0, flex: 2 }}>
            <label>Name</label>
            <input required value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="e.g. Rahul Kumar" />
          </div>
          <div className="input-group" style={{ margin: 0, flex: 1 }}>
            <label>Standard</label>
            <select required value={form.class_name} onChange={e => setForm({...form, class_name: e.target.value})}>
              <option value="8">8th</option>
              <option value="9">9th</option>
              <option value="10">10th</option>
            </select>
          </div>
          <button type="submit" className="btn-primary" style={{ height: '46px' }}><Plus size={18}/> Add</button>
        </form>
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 className="display-text">Student Database</h3>
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            <div className="input-group" style={{ margin: 0, width: '150px' }}>
              <select value={filterClass} onChange={e => setFilterClass(e.target.value)}>
                <option value="All">All Grades</option>
                <option value="8">8th Grade</option>
                <option value="9">9th Grade</option>
                <option value="10">10th Grade</option>
              </select>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', background: 'var(--surface-container-high)', padding: '8px 16px', borderRadius: 'var(--radius-full)' }}>
              <Search size={18} color="var(--on-surface-variant)" />
              <input 
                style={{ border: 'none', background: 'none', boxShadow: 'none', padding: '0 8px', width: '200px' }} 
                placeholder="Search..." 
                value={search} 
                onChange={e => setSearch(e.target.value)} 
              />
            </div>
          </div>
        </div>

        <div className="table-container">
          {loading ? <p>Loading...</p> : (
            <table>
              <thead>
                <tr>
                  <th>Roll No</th>
                  <th>Name</th>
                  <th>Class</th>
                  <th style={{ width: '100px' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {displayedStudents.map(s => (
                  <tr key={`${s.class_name}-${s.roll_no}`}>
                    <td>{s.roll_no}</td>
                    <td><b>{s.name}</b></td>
                    <td>
                      <span style={{ 
                        padding: '4px 12px', 
                        background: 'var(--surface-container-high)', 
                        color: 'var(--on-surface-variant)', 
                        borderRadius: 'var(--radius-full)', 
                        fontSize: '0.8rem',
                        fontWeight: '600'
                      }}>{s.class_name}th Grade</span>
                    </td>
                    <td>
                      <button onClick={() => handleDelete(s.roll_no, s.class_name)} className="btn-danger" style={{ display: 'flex', alignItems: 'center', padding: '8px' }}>
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
                {displayedStudents.length === 0 && (
                  <tr><td colSpan="4" style={{ textAlign: 'center', padding: '24px' }}>No records found.</td></tr>
                )}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default StudentsModule;
