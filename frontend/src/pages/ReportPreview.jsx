import React, { useState } from 'react';
import { api } from '../api/client';
import { Search, Download, FileText } from 'lucide-react';

const ReportPreview = () => {
    const [rollNo, setRollNo] = useState('');
    const [className, setClassName] = useState('');
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(false);
  
    const handleGenerate = async (e) => {
      e?.preventDefault();
      if (!rollNo) return;
      setLoading(true);
      try {
        const data = await api.previewReport(rollNo, className);
        setReport(data);
      } catch (err) {
        alert("Error: " + err.message);
      } finally {
        setLoading(false);
      }
    };
  
    return (
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <div className="page-header">
          <h1>Report Preview</h1>
          <p>Generate and view the live WhatsApp report before sending.</p>
        </div>
  
        <div className="card" style={{ marginBottom: '24px' }}>
          <form onSubmit={handleGenerate} style={{ display: 'flex', gap: '16px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
            <div className="input-group" style={{ margin: 0, flex: 1, minWidth: '150px', maxWidth: '300px' }}>
              <label>Student Roll No</label>
              <input value={rollNo} onChange={e => setRollNo(e.target.value)} placeholder="Enter Roll No" required />
            </div>
            <div className="input-group" style={{ margin: 0, flex: 1, minWidth: '150px', maxWidth: '300px' }}>
              <label>Class</label>
              <input value={className} onChange={e => setClassName(e.target.value)} placeholder="e.g. 10A (Optional)" />
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
                    <h3 className="display-text">WhatsApp Output</h3>
                </div>
                <div style={{ 
                    background: 'var(--surface-container-high)', 
                    padding: '16px', 
                    borderRadius: 'var(--radius-md)', 
                    color: 'var(--on-surface)',
                    fontFamily: 'monospace',
                    whiteSpace: 'pre-wrap',
                    lineHeight: '1.5'
                }}>
                    {report.summary}
                </div>

                <h3 className="display-text" style={{ marginTop: '24px', marginBottom: '16px' }}>Last 7 Days Snapshot</h3>
                <div style={{ 
                    background: 'var(--surface-container-high)', 
                    padding: '16px', 
                    borderRadius: 'var(--radius-md)', 
                    color: 'var(--on-surface)',
                    fontFamily: 'monospace',
                    whiteSpace: 'pre-wrap',
                    lineHeight: '1.5'
                }}>
                    {report.weekly_snapshot}
                </div>
            </div>

            {/* Right side: PDF Viewer */}
            <div className="card" style={{ flex: 2, display: 'flex', flexDirection: 'column' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h3 className="display-text">PDF Attachment</h3>
                    <a href={`http://localhost:8000${report.pdf_url}`} target="_blank" rel="noreferrer" className="btn-primary" style={{ textDecoration: 'none', padding: '6px 12px', fontSize: '0.875rem' }}>
                        <Download size={16} /> Download
                    </a>
                </div>
                <div style={{ flex: 1, background: 'var(--surface-container-low)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
                    <iframe 
                        src={`http://localhost:8000${report.pdf_url}`} 
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
