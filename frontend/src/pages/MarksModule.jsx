import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { Search, Save, Users, Target } from 'lucide-react';

const MarksModule = () => {
  const [mode, setMode] = useState('bulk'); // 'single' or 'bulk'
  
  // Single mode state
  const [sheetType, setSheetType] = useState('tests');
  const [rollNo, setRollNo] = useState('');
  const [singleClass, setSingleClass] = useState('10');
  const [records, setRecords] = useState([]);
  const [singleForm, setSingleForm] = useState({ date: '', subject: '', marks: 0 });

  // Bulk mode state
  const [classes, setClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState('');
  const [bulkDate, setBulkDate] = useState('');
  const [bulkSubject, setBulkSubject] = useState('');
  const [classStudents, setClassStudents] = useState([]);
  const [bulkData, setBulkData] = useState({}); // { roll_no: marks }
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
      const data = await api.getMarks(sheetType, rollNo, singleClass);
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
      
      const initialData = {};
      filtered.forEach(s => { initialData[s.roll_no] = ''; });
      setBulkData(initialData);
    } catch(err) {
      alert("Error loading class: " + err.message);
    }
  };

  const handleAddSingle = async (e) => {
    e.preventDefault();
    try {
      await api.addMark(sheetType, {
        roll_no: rollNo, 
        date: singleForm.date, 
        subject: singleForm.subject, 
        marks: parseFloat(singleForm.marks), 
        class_name: singleClass
      });
      fetchSingleRecords();
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  const handleSaveBulk = async () => {
    if (!bulkDate || !bulkSubject) {
        alert("Please select a date and subject.");
        return;
    }
    setSaving(true);
    
    const recordsToSave = classStudents.map(s => ({
        roll_no: s.roll_no,
        date: bulkDate,
        subject: bulkSubject,
        marks: parseFloat(bulkData[s.roll_no]) || 0,
        class_name: s.class_name
    }));

    try {
        await api.addMarksBulk(sheetType, recordsToSave);
        alert(`Successfully uploaded marks for ${recordsToSave.length} students!`);
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
          <h1>Test & Exam Marks</h1>
        </div>
        <div style={{ display: 'flex', background: 'var(--surface-container-high)', borderRadius: 'var(--radius-full)', padding: '4px' }}>
          <button 
            type="button" 
            onClick={() => setMode('bulk')} 
            style={{ 
              padding: '8px 16px', borderRadius: 'var(--radius-full)', background: mode === 'bulk' ? 'var(--surface-container-lowest)' : 'transparent', color: mode === 'bulk' ? 'var(--primary)' : 'var(--on-surface-variant)', boxShadow: mode === 'bulk' ? 'var(--shadow-ambient)' : 'none' 
            }}
          >Bulk Upload</button>
          <button 
            type="button" 
            onClick={() => setMode('single')} 
            style={{ 
              padding: '8px 16px', borderRadius: 'var(--radius-full)', background: mode === 'single' ? 'var(--surface-container-lowest)' : 'transparent', color: mode === 'single' ? 'var(--primary)' : 'var(--on-surface-variant)', boxShadow: mode === 'single' ? 'var(--shadow-ambient)' : 'none' 
            }}
          >Single Student</button>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '24px' }}>
          <div className="input-group" style={{ margin: 0 }}>
            <label>Exam Type</label>
            <select value={sheetType} onChange={e => setSheetType(e.target.value)} style={{ width: '100%', maxWidth: '300px' }}>
              <option value="tests">Weekly Tests</option>
              <option value="exams">Term Exams</option>
            </select>
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
            <div className="card">
              <h3 className="display-text">Add New Mark</h3>
              <form onSubmit={handleAddSingle} style={{ display: 'flex', gap: '16px', marginTop: '16px', alignItems: 'flex-end' }}>
                <div className="input-group" style={{ margin: 0, flex: 1 }}>
                  <label>Date</label>
                  <input type="date" value={singleForm.date} onChange={e => setSingleForm({...singleForm, date: e.target.value})} required />
                </div>
                <div className="input-group" style={{ margin: 0, flex: 1 }}>
                  <label>Subject</label>
                  <input value={singleForm.subject} onChange={e => setSingleForm({...singleForm, subject: e.target.value})} placeholder="e.g. Math" required />
                </div>
                <div className="input-group" style={{ margin: 0, flex: 1 }}>
                  <label>Marks</label>
                  <input type="number" value={singleForm.marks} onChange={e => setSingleForm({...singleForm, marks: e.target.value})} required />
                </div>
                <button type="submit" className="btn-primary" style={{ height: '46px' }}>Save</button>
              </form>
  
              <div className="table-container" style={{ marginTop: '24px' }}>
                <table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Subject</th>
                      <th>Marks</th>
                    </tr>
                  </thead>
                  <tbody>
                    {records.map((r, i) => (
                      <tr key={i}>
                        <td>{r.Date}</td>
                        <td>{r.Subject}</td>
                        <td>
                          <span style={{ 
                            color: 'var(--on-surface-variant)',
                            background: 'var(--surface-container-high)',
                            padding: '6px 12px', borderRadius: 'var(--radius-full)', fontSize: '0.85rem', fontWeight: 'bold'
                          }}>{r.Marks}</span>
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
            <h3 className="display-text" style={{ marginBottom: '16px' }}>Bulk {sheetType === 'tests' ? 'Tests' : 'Exams'} Entry</h3>
            <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-end', marginBottom: '24px', flexWrap: 'wrap' }}>
                <div className="input-group" style={{ flex: 1, minWidth: '200px' }}>
                    <label>Select Class</label>
                    <select value={selectedClass} onChange={e => setSelectedClass(e.target.value)}>
                        {classes.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                </div>
                <div className="input-group" style={{ flex: 1, minWidth: '200px' }}>
                    <label>Date</label>
                    <input type="date" value={bulkDate} onChange={e => setBulkDate(e.target.value)} required />
                </div>
                <div className="input-group" style={{ flex: 1, minWidth: '200px' }}>
                    <label>Subject</label>
                    <input value={bulkSubject} onChange={e => setBulkSubject(e.target.value)} placeholder="e.g. Science" required />
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
                                <th style={{ width: '150px' }}>Marks Scored</th>
                            </tr>
                        </thead>
                        <tbody>
                            {classStudents.map(s => (
                                <tr key={s.roll_no}>
                                    <td>{s.roll_no}</td>
                                    <td>{s.name}</td>
                                    <td>
                                        <input 
                                            type="number" 
                                            placeholder="0"
                                            value={bulkData[s.roll_no] || ''}
                                            onChange={e => setBulkData({...bulkData, [s.roll_no]: e.target.value})}
                                            style={{ 
                                                width: '100px',
                                                padding: '8px 12px', borderRadius: 'var(--radius-default)',
                                                border: '1px solid var(--surface-container-highest)',
                                                background: 'var(--surface-container-lowest)',
                                                color: 'var(--on-surface)'
                                             }}
                                        />
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'flex-end' }}>
                    <button className="btn-primary" onClick={handleSaveBulk} disabled={saving}>
                        <Save size={18} /> {saving ? 'Saving to Google Sheets...' : `Upload ${classStudents.length} Marks`}
                    </button>
                </div>
                </>
            )}
        </div>
      )}

    </div>
  );
};
export default MarksModule;
