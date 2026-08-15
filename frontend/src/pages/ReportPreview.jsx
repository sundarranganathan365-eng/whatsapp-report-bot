import React, { useState } from 'react';
import { api, PDF_BASE } from '../api/client';
import { Search, Download, FileText, CheckCircle } from 'lucide-react';

const ReportPreview = () => {
    const [rollNo, setRollNo] = useState('');
    const [className, setClassName] = useState('');
    const [reportType, setReportType] = useState('weekly');
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(false);
  
    const handleGenerate = async (e) => {
      e?.preventDefault();
      if (!rollNo) return;
      setLoading(true);
      try {
        const data = await api.previewReport(rollNo, className, reportType);
        setReport(data);
      } catch (err) {
        alert("Error: " + err.message);
      } finally {
        setLoading(false);
      }
    };

    const handleTypeChange = async (type) => {
      setReportType(type);
      if (rollNo) {
        setLoading(true);
        try {
          const data = await api.previewReport(rollNo, className, type);
          setReport(data);
        } catch (err) {
          console.error(err);
        } finally {
          setLoading(false);
        }
      }
    };
  
    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div className="page-header">
          <h1>Report Preview</h1>
          <p>Preview live WhatsApp report text formats & PDF attachments before sending.</p>
        </div>
  
        <div className="card" style={{ marginBottom: '24px' }}>
          <form onSubmit={handleGenerate} style={{ display: 'flex', gap: '16px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
            <div className="input-group" style={{ margin: 0, flex: 1, minWidth: '140px', maxWidth: '220px' }}>
              <label>Student Roll No</label>
              <input value={rollNo} onChange={e => setRollNo(e.target.value)} placeholder="Enter Roll No" required />
            </div>
            <div className="input-group" style={{ margin: 0, flex: 1, minWidth: '140px', maxWidth: '220px' }}>
              <label>Class</label>
              <input value={className} onChange={e => setClassName(e.target.value)} placeholder="e.g. 10A (Optional)" />
            </div>

            <div className="input-group" style={{ margin: 0, minWidth: '220px' }}>
              <label>Report Format</label>
              <select value={reportType} onChange={e => handleTypeChange(e.target.value)} style={{ padding: '10px', borderRadius: '8px' }}>
                <option value="weekly">1️⃣ Weekly Report (7-Day Summary)</option>
                <option value="full">2️⃣ Full Academic Overview (All Details)</option>
              </select>
            </div>

            <button type="submit" className="btn-primary" style={{ height: '46px', whiteSpace: 'nowrap' }} disabled={loading}>
                {loading ? 'Generating...' : <><FileText size={18}/> Generate Preview</>}
            </button>
          </form>
        </div>
  
        {report && (
          <div style={{ display: 'flex', gap: '24px', flex: 1, overflow: 'hidden' }}>
            
            {/* Left side: WhatsApp Text Summary */}
            <div className="card" style={{ flex: 1, overflowY: 'auto' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h3 className="display-text">WhatsApp Text Format ({reportType === 'weekly' ? 'Option 1: Weekly' : 'Option 2: Full Overview'})</h3>
                </div>

                <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
                  <button 
                    onClick={() => handleTypeChange('weekly')} 
                    style={{ 
                      padding: '6px 12px', 
                      borderRadius: '6px', 
                      border: '1px solid var(--primary)', 
                      background: reportType === 'weekly' ? 'var(--primary)' : 'transparent',
                      color: reportType === 'weekly' ? '#fff' : 'var(--primary)',
                      cursor: 'pointer',
                      fontSize: '0.85rem'
                    }}>
                    1️⃣ Weekly Report
                  </button>
                  <button 
                    onClick={() => handleTypeChange('full')} 
                    style={{ 
                      padding: '6px 12px', 
                      borderRadius: '6px', 
                      border: '1px solid var(--primary)', 
                      background: reportType === 'full' ? 'var(--primary)' : 'transparent',
                      color: reportType === 'full' ? '#fff' : 'var(--primary)',
                      cursor: 'pointer',
                      fontSize: '0.85rem'
                    }}>
                    2️⃣ Full Academic Overview
                  </button>
                </div>

                <div style={{ 
                    background: '#0B141A', 
                    padding: '16px', 
                    borderRadius: '12px', 
                    color: '#E9EDEF',
                    fontFamily: 'monospace',
                    whiteSpace: 'pre-wrap',
                    lineHeight: '1.5',
                    fontSize: '0.9rem',
                    borderLeft: '4px solid #00A884'
                }}>
                    {report.summary}
                </div>
            </div>

            {/* Right side: PDF Viewer */}
            <div className="card" style={{ flex: 1.5, display: 'flex', flexDirection: 'column' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h3 className="display-text">PDF Attachment</h3>
                    <a href={`${PDF_BASE}${report.pdf_url}`} target="_blank" rel="noreferrer" className="btn-primary" style={{ textDecoration: 'none', padding: '6px 12px', fontSize: '0.875rem' }}>
                        <Download size={16} /> Download PDF
                    </a>
                </div>
                <div style={{ flex: 1, background: 'var(--surface-container-low)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
                    <iframe 
                        src={`${PDF_BASE}${report.pdf_url}`} 
                        width="100%" 
                        height="100%" 
                        style={{ border: 'none' }}
                        title="PDF Preview"
                    />
                </div>
            </div>

          </div>
        )}
      </div>
    );
  };

export default ReportPreview;
