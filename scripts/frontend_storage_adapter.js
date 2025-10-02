// Small adapter to replace localStorage with API-backed storage when available.
// Usage: call StorageAdapter.load('some.key') or StorageAdapter.save('some.key', value)

const API_BASE = '/api';

async function safeFetch(url, options={}){
  try{
    const res = await fetch(url, options);
    if(!res.ok) throw new Error('Fetch failed '+res.status);
    return await res.json();
  }catch(e){
    // propagate error to caller to allow fallback
    throw e;
  }
}

const StorageAdapter = {
  async loadSetting(key){
    // tries GET /api/settings/?key=key and returns value or null
    try{
      const data = await safeFetch(`${API_BASE}/settings/?key=${encodeURIComponent(key)}`);
      if(Array.isArray(data) && data.length) return data[0].value;
      return null;
    }catch(e){
      // fallback to localStorage
      try{
        const raw = localStorage.getItem(key);
        return raw ? JSON.parse(raw) : null;
      }catch(_){ return null; }
    }
  },

  async saveSetting(key, value){
    try{
      const payload = { key, value };
      const res = await fetch(`${API_BASE}/settings/upsert/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if(!res.ok) throw new Error('api save failed');
      return await res.json();
    }catch(e){
      // fallback
      try{ localStorage.setItem(key, JSON.stringify(value)); return { fallback: true }; }catch(_){ throw e; }
    }
  },

  async loadUIState(key){
    try{
      const data = await safeFetch(`${API_BASE}/ui-state/?key=${encodeURIComponent(key)}`);
      if(Array.isArray(data) && data.length) return data[0].state;
      return null;
    }catch(e){
      try{ const raw = localStorage.getItem(key); return raw ? JSON.parse(raw) : null; }catch(_){ return null; }
    }
  },

  async saveUIState(key, state){
    try{
      const payload = { key, state };
      const res = await fetch(`${API_BASE}/ui-state/upsert/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if(!res.ok) throw new Error('api save failed');
      return await res.json();
    }catch(e){
      try{ localStorage.setItem(key, JSON.stringify(state)); return { fallback: true }; }catch(_){ throw e; }
    }
  }
};

export default StorageAdapter;
