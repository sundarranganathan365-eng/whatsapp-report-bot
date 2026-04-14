const API_BASE = window.location.hostname === 'localhost' ? "http://localhost:8000/api/admin" : "/api/admin";

export const api = {
  getStudents: async (search = "") => {
    let url = `${API_BASE}/students/?_v=${Date.now()}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    const res = await fetch(url);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to fetch");
    return data.data;
  },
  
  addStudent: async (student) => {
    const res = await fetch(`${API_BASE}/students/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(student)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to add");
    return data.data;
  },

  deleteStudent: async (rollNo, className) => {
    const res = await fetch(`${API_BASE}/students/${encodeURIComponent(rollNo)}?class_name=${encodeURIComponent(className)}`, {
      method: "DELETE"
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to delete");
    return data;
  },

  getAttendance: async (rollNo, className) => {
    const res = await fetch(`${API_BASE}/attendance/${encodeURIComponent(rollNo)}?class_name=${encodeURIComponent(className)}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to fetch");
    return data.data;
  },

  getMarks: async (sheetType, rollNo, className) => {
    const res = await fetch(`${API_BASE}/marks/${sheetType}/${encodeURIComponent(rollNo)}?class_name=${encodeURIComponent(className)}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to fetch");
    return data.data;
  },

  addAttendance: async (record) => {
    const res = await fetch(`${API_BASE}/attendance/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(record)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to add attendance");
    return data.data;
  },

  addMark: async (sheetType, record) => {
    const res = await fetch(`${API_BASE}/marks/${sheetType}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(record)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to add mark");
    return data.data;
  },

  previewReport: async (rollNo, className) => {
    let url = `${API_BASE}/reports/preview/${encodeURIComponent(rollNo)}`;
    if (className) {
      url += `?class_name=${encodeURIComponent(className)}`;
    }
    const res = await fetch(url);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to fetch");
    return data.data;
  },

  getBotConfig: async () => {
    const res = await fetch(`${API_BASE}/bot/config`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to fetch");
    return data.data;
  },

  updateBotConfig: async (config) => {
    const res = await fetch(`${API_BASE}/bot/config`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(config)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to update");
    return data.data;
  },

  addAttendanceBulk: async (records) => {
    const res = await fetch(`${API_BASE}/attendance/bulk`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ records })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to add bulk attendance");
    return data.data;
  },

  addMarksBulk: async (sheetType, records) => {
    const res = await fetch(`${API_BASE}/marks/${sheetType}/bulk`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ records })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to add bulk marks");
    return data.data;
  }
};
