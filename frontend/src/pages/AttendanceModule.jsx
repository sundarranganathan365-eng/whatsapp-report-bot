import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { Search, Save, Users } from 'lucide-react';

const AttendanceModule = () => {
  const [mode, setMode] = useState('bulk'); // 'single' or 'bulk'
  
  // Single mode state
  const [rollNo, setRollNo] = useState('');
  const [singleClass, setSingleClass] = useState('10');
  const [records, setRecords] = useState([]);
  const [singleForm, setSingleForm] = useState({ date: '', status: 'Present' });

  // Bulk mode state
  const [classes, setClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState('');
  const [bulkDate, setBulkDate] = useState('');
  const [classStudents, setClassStudents] = useState([]);
  const [bulkData, setBulkData] = useState({}); // { roll_no: 'Present'|'Absent' }
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    // Fetch unique classes for the dropdown
    api.getStudents().then(data => {
      const uniqueClasses = [...new Set(data.map(s => s.class_name).filter(Boolean))];
      setClasses(uniqueClasses);
      if (uniqueClasses.length > 0) setSelectedClass(uniqueClasses[0]);
    }).catch(console.error);
  }, []);

  const fetchSingleRecords = async (e) => {
    e?.preventDefault();
    if (!rollNo) return;
    try {
      const data = await api.getAttendance(rollNo, singleClass);
      setRecords(data);
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  const loadBulkClass = async () => {
    try {
      const data = await api.getStudents();
      const filtered = data.filter(s => s.class_name === selectedClass);
      setClassStudents(filtered);
      
      // Default everyone to present
      const initialData = {};
      filtered.forEach(s => { initialData[s.roll_no] = 'Present'; });
      setBulkData(initialData);
    } catch(err) {
      alert("Error loading class: " + err.message);
    }
  };

  const handleAddSingle = async (e) => {
    e.preventDefault();
    try {
      await api.addAttendance({ 
        roll_no: rollNo, 
        date: singleForm.date, 
        status: singleForm.status, 
        class_name: singleClass
      });
      fetchSingleRecords();
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  const handleSaveBulk = async () => {
    if (!bulkDate) {
        alert("Please select a date for the attendance.");
        return;
    }
    setSaving(true);
    
    const records = classStudents.map(s => ({
        roll_no: s.roll_no,
        date: bulkDate,
        status: bulkData[s.roll_no],
        class_name: s.class_name
    }));

    try {
        await api.addAttendanceBulk(records);
        alert(`Successfully marked attendance for ${records.length} students!`);
        setClassStudents([]); // Reset
    } catch (err) {
        alert("Failed to save: " + err.message);
    } finally {
        setSaving(false);
    }
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Attendance Management</h1>
        </div>
        <div style={{ display: 'flex', background: 'var(--surface-container-high)', borderRadius: 'var(--radius-full)', padding: '4px' }}>
          <button 
            type="button" 
            onClick={() => setMode('bulk')} 
            style={{ 
              padding: '8px 16px', borderRadius: 'var(--radius-full)', background: mode === 'bulk' ? 'var(--surface-container-lowest)' : 'transparent', color: mode === 'bulk' ? 'var(--primary)' : 'var(--on-surface-variant)', boxShadow: mode === 'bulk' ? 'var(--shadow-ambient)' : 'none' 
            }}
          >Bulk Entry</button>
          <button 
            type="button" 
            onClick={() => setMode('single')} 
            style={{ 
              padding: '8px 16px', borderRadius: 'var(--radius-full)', background: mode === 'single' ? 'var(--surface-container-lowest)' : 'transparent', color: mode === 'single' ? 'var(--primary)' : 'var(--on-surface-variant)', boxShadow: mode === 'single' ? 'var(--shadow-ambient)' : 'none' 
            }}
          >Single View</button>
        </div>
      </div>

      {mode === 'single' && (
        <>
          <div className="card" style={{ marginBottom: '24px' }}>
            <form onSubmit={fetchSingleRecords} style={{ display: 'flex', gap: '16px', alignItems: 'flex-end' }}>
              <div className="input-group" style={{ margin: 0, flex: 2 }}>
                <label>Student Roll No</label>
                <input value={rollNo} onChange={e => setRollNo(e.target.value)} placeholder="Enter Roll No" />
              </div>
              <div className="input-group" style={{ margin: 0, flex: 1 }}>
                <label>Standard</label>
                <select value={singleClass} onChange={e => setSingleClass(e.target.value)}>
                    <option value="8">8th Grade</option>
                    <option value="9">9th Grade</option>
                    <option value="10">10th Grade</option>
                </select>
              </div>
              <button type="submit" className="btn-primary" style={{ height: '46px' }}><Search size={18}/> Fetch</button>
            </form>
          </div>

          {records.length > 0 && (
            <div className="card" style={{ marginBottom: '24px' }}>
              <h3 className="display-text">Add Attendance</h3>
              <form onSubmit={handleAddSingle} style={{ display: 'flex', gap: '16px', marginTop: '16px', alignItems: 'flex-end' }}>
                <div className="input-group" style={{ margin: 0, flex: 1 }}>
                  <label>Date</label>
                  <input type="date" value={singleForm.date} onChange={e => setSingleForm({...singleForm, date: e.target.value})} required />
                </div>
                <div className="input-group" style={{ margin: 0, flex: 1 }}>
                  <label>Status</label>
                  <select value={singleForm.status} onChange={e => setSingleForm({...singleForm, status: e.target.value})}>
                    <option>Present</option>
                    <option>Absent</option>
                  </select>
                </div>
                <button type="submit" className="btn-primary" style={{ height: '46px' }}>Mark</button>
              </form>

              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {records.map((r, i) => (
                      <tr key={i}>
                        <td>{r.Date}</td>
                        <td>
                          <span style={{ 
                            color: r.Status === 'Present' ? 'var(--on-surface-variant)' : 'var(--danger)',
                            background: r.Status === 'Present' ? 'var(--surface-container-high)' : 'rgba(239, 68, 68, 0.1)',
                            padding: '6px 12px', borderRadius: 'var(--radius-full)', fontSize: '0.85rem', fontWeight: 'bold'
                          }}>{r.Status}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {mode === 'bulk' && (
        <div className="card">
            <h3 className="display-text" style={{ marginBottom: '16px' }}>Bulk Class Entry</h3>
            <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-end', marginBottom: '24px' }}>
                <div className="input-group" style={{ flex: 1 }}>
                    <label>Select Class</label>
                    <select value={selectedClass} onChange={e => setSelectedClass(e.target.value)}>
                        {classes.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                </div>
                <div className="input-group" style={{ flex: 1 }}>
                    <label>Date</label>
                    <input type="date" value={bulkDate} onChange={e => setBulkDate(e.target.value)} required />
                </div>
                <button type="button" className="btn-primary" style={{ height: '46px' }} onClick={loadBulkClass}>
                    <Users size={18}/> Load Roster
                </button>
            </div>

            {classStudents.length > 0 && (
                <>
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Roll No</th>
                                <th>Name</th>
                                <th style={{ width: '150px' }}>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {classStudents.map(s => (
                                <tr key={s.roll_no}>
                                    <td>{s.roll_no}</td>
                                    <td>{s.name}</td>
                                    <td style={{ display: 'flex', gap: '8px' }}>
                                        <button 
                                            onClick={() => setBulkData({...bulkData, [s.roll_no]: 'Present'})}
                                            style={{ 
                                                padding: '6px 12px', borderRadius: 'var(--radius-full)',
                                                background: bulkData[s.roll_no] === 'Present' ? 'var(--primary)' : 'var(--surface-container-high)',
                                                color: bulkData[s.roll_no] === 'Present' ? 'white' : 'var(--on-surface-variant)'
                                             }}
                                        >P</button>
                                        <button 
                                            onClick={() => setBulkData({...bulkData, [s.roll_no]: 'Absent'})}
                                            style={{ 
                                                padding: '6px 12px', borderRadius: 'var(--radius-full)',
                                                background: bulkData[s.roll_no] === 'Absent' ? 'var(--danger)' : 'var(--surface-container-high)',
                                                color: bulkData[s.roll_no] === 'Absent' ? 'white' : 'var(--on-surface-variant)'
                                             }}
                                        >A</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'flex-end' }}>
                    <button className="btn-primary" onClick={handleSaveBulk} disabled={saving}>
                        <Save size={18} /> {saving ? 'Saving to Google Sheets...' : `Save ${classStudents.length} Records`}
                    </button>
                </div>
                </>
            )}
        </div>
      )}

    </div>
  );
};
export default AttendanceModule;
