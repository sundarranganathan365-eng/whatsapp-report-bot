import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { Users, Activity, Settings2, Save } from 'lucide-react';

const Dashboard = () => {
  const [stats, setStats] = useState({ totalStudents: 0 });
  const [botConfig, setBotConfig] = useState({ is_active: true, default_reply: '' });
  const [saving, setSaving] = useState(false);

  // Poll for stats and config
  useEffect(() => {
    api.getStudents().then(data => setStats({ totalStudents: data?.length || 0 })).catch(err => console.error(err));
    api.getBotConfig().then(data => setBotConfig(data)).catch(err => console.error(err));
  }, []);

  const handleSaveConfig = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.updateBotConfig(botConfig);
      alert("Bot settings updated successfully.");
    } catch(err) {
      alert("Config save error: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Overview of system metrics and bot status.</p>
      </div>

      <div className="card-grid">
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ padding: '16px', background: 'var(--surface-container-high)', borderRadius: '12px', color: 'var(--primary)' }}>
              <Users size={32} />
            </div>
            <div style={{ flex: 1 }}>
              <h3 style={{ color: 'var(--on-surface-variant)', fontSize: '0.875rem' }}>Total Students</h3>
              <p style={{ fontSize: '2rem', fontWeight: '700' }}>{stats.totalStudents}</p>
            </div>
            <button onClick={() => window.location.reload()} className="btn-primary" style={{ padding: '8px' }}>
              <Activity size={18} /> Sync
            </button>
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ padding: '16px', background: 'var(--surface-container-high)', borderRadius: '12px', color: 'var(--success)' }}>
              <Activity size={32} />
            </div>
            <div>
              <h3 style={{ color: 'var(--on-surface-variant)', fontSize: '0.875rem' }}>Bot Status</h3>
              <p style={{ fontSize: '1.5rem', fontWeight: '700', color: botConfig.is_active ? 'var(--success)' : 'var(--danger)' }}>
                {botConfig.is_active ? 'Active' : 'Paused'}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <Settings2 size={24} color="var(--primary)" />
            <h3>Bot Settings</h3>
        </div>
        <form onSubmit={handleSaveConfig} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div className="input-group" style={{ display: 'flex', alignItems: 'center', gap: '12px', flexDirection: 'row' }}>
                <input 
                    type="checkbox" 
                    checked={botConfig.is_active} 
                    onChange={e => setBotConfig({...botConfig, is_active: e.target.checked})}
                    style={{ width: '20px', height: '20px', cursor: 'pointer', boxShadow: 'none' }}
                />
                <label style={{ margin: 0, fontWeight: 'bold', color: 'var(--on-surface)' }}>Bot Engine Active</label>
            </div>
            <div className="input-group">
                <label>Default Reply Message</label>
                <textarea 
                    value={botConfig.default_reply}
                    onChange={e => setBotConfig({...botConfig, default_reply: e.target.value})}
                    style={{ width: '100%', minHeight: '120px', resize: 'vertical' }}
                />
            </div>
            <button type="submit" className="btn-primary" style={{ alignSelf: 'flex-start' }} disabled={saving}>
                <Save size={18} /> {saving ? 'Saving...' : 'Save Settings'}
            </button>
        </form>
      </div>
    </div>
  );
};

export default Dashboard;
