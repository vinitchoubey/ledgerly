import React, { useState, useEffect } from 'react';

// Make sure VITE_API_URL is set in your host (like Render or Vercel)
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const today = () => new Date().toISOString().split('T')[0];

// Format date to MM/DD/YYYY to match input behavior
const formatDate = (rawDate) => {
  if (!rawDate) return '-';
  const [year, month, day] = rawDate.split('-');
  return `${month}/${day}/${year}`;
};

// Global colors
const themeBlue = '#2563eb';
const themeRed = '#dc2626';

// Reusable inline styles so we don't clutter the JSX too much
const inputStyle = { padding: '7px 9px', border: '1px solid #999', fontSize: '0.9rem' };
const btnStyle = { padding: '8px 14px', border: `1px solid ${themeBlue}`, background: '#fff', color: themeBlue, cursor: 'pointer', fontSize: '0.9rem' };
const btnDanger = { ...btnStyle, border: `1px solid ${themeRed}`, color: themeRed };
const btnPrimary = { padding: '8px 14px', border: 'none', background: themeBlue, color: '#fff', cursor: 'pointer', fontSize: '0.9rem' };
const cardStyle = { padding: '16px', border: '1px solid #999' };

function App() {
  // auth stuff
  const [userToken, setUserToken] = useState(localStorage.getItem('token') || null);
  const [isLoginMode, setIsLoginMode] = useState(true); 
  const [credentials, setCredentials] = useState({ email: '', password: '' });
  const [errorMessage, setErrorMessage] = useState('');

  // main app state
  const [newExpense, setNewExpense] = useState({ item: '', amount: '', category: '', date: today() });
  const [budgetInput, setBudgetInput] = useState('');
  const [receiptFile, setReceiptFile] = useState(null);
  const [receiptDate, setReceiptDate] = useState(today());
  
  // data from backend
  const [dashboardData, setDashboardData] = useState(null);
  const [monthlyData, setMonthlyData] = useState(null);
  
  // ui state
  const [isUploading, setIsUploading] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard');
  const [openToggles, setOpenToggles] = useState({});

  const headers = { Authorization: `Bearer ${userToken}` };

  const handleLoginSignup = async (e) => {
    e.preventDefault();
    setErrorMessage('');

    try {
      if (!isLoginMode) {
        // Handle Signup
        const response = await fetch(`${API_URL}/signup`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(credentials),
        });
        
        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          setErrorMessage(errData.detail || 'Signup failed. Try again.');
          return;
        }
        const data = await response.json();
        saveSession(data.access_token);
      } else {
        // Handle Login (using URLSearchParams for form data)
        const formParams = new URLSearchParams();
        formParams.append('username', credentials.email);
        formParams.append('password', credentials.password);

        const response = await fetch(`${API_URL}/login`, { method: 'POST', body: formParams });
        
        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          setErrorMessage(errData.detail || 'Incorrect email or password');
          return;
        }
        const data = await response.json();
        saveSession(data.access_token);
      }
    } catch (err) {
      setErrorMessage(`Network error: ${err.message}`);
    }
  };

  const saveSession = (token) => {
    localStorage.setItem('token', token);
    setUserToken(token);
  };

  const logoutUser = () => {
    localStorage.removeItem('token');
    setUserToken(null);
    setDashboardData(null);
    setMonthlyData(null);
  };

  const loadDashboard = async () => {
    const res = await fetch(`${API_URL}/optimize`, { headers });
    if (res.status === 401) return logoutUser();
    setDashboardData(await res.json());
  };

  const loadMonthly = async () => {
    const res = await fetch(`${API_URL}/monthly-summary`, { headers });
    if (res.status === 401) return logoutUser();
    const data = await res.json();
    setMonthlyData(data.monthly_summary);
  };

  // Fetch data when token changes
  useEffect(() => {
    if (userToken) { 
      loadDashboard(); 
      loadMonthly(); 
    }
  }, [userToken]);

  const submitManualExpense = async (e) => {
    e.preventDefault();
    await fetch(`${API_URL}/manual-entry`, {
      method: 'POST',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...newExpense, amount: parseFloat(newExpense.amount) }),
    });
    // reset form
    setNewExpense({ item: '', amount: '', category: '', date: today() });
    loadDashboard();
    loadMonthly();
  };

  const updateBudget = async (e) => {
    e.preventDefault();
    await fetch(`${API_URL}/update-budget`, {
      method: 'POST',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ budget: parseFloat(budgetInput) }),
    });
    setBudgetInput('');
    loadDashboard();
  };

  const wipeAllData = async () => {
    // Adding a warning so users don't accidentally nuke their account
    if (window.confirm("Are you sure you want to reset everything? This is permanent.")) {
      await fetch(`${API_URL}/reset-all`, { method: 'POST', headers });
      loadDashboard();
      loadMonthly();
    }
  };

  const uploadReceipt = async (e) => {
    e.preventDefault();
    if (!receiptFile) return;
    
    setIsUploading(true);
    try {
      const payload = new FormData();
      payload.append('file', receiptFile);
      
      const res = await fetch(`${API_URL}/process-receipt?override_date=${receiptDate}`, {
        method: 'POST',
        headers,
        body: payload,
      });
      
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      
      setReceiptFile(null);
      loadDashboard();
      loadMonthly();
    } catch (err) {
      alert(`Oops, upload failed: ${err.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const toggleTransaction = (index) => {
    setOpenToggles(prev => ({ ...prev, [index]: !prev[index] }));
  };

  // Render Login screen if no token
  if (!userToken) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', fontFamily: 'Arial, sans-serif', background: '#fff' }}>
        <div style={{ width: '300px', padding: '24px', border: '1px solid #999' }}>
          <h2 style={{ textAlign: 'center', margin: '0 0 16px', color: '#000' }}>Ledgerly</h2>

          <form onSubmit={handleLoginSignup} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <input type="email" placeholder="Email address" required style={inputStyle}
              value={credentials.email} onChange={e => setCredentials({ ...credentials, email: e.target.value })} />
            <input type="password" placeholder="Password" required style={inputStyle}
              value={credentials.password} onChange={e => setCredentials({ ...credentials, password: e.target.value })} />

            {errorMessage && <p style={{ color: themeRed, fontSize: '0.85rem', margin: 0 }}>{errorMessage}</p>}

            <button type="submit" style={btnPrimary}>
              {isLoginMode ? 'Log In' : 'Sign Up'}
            </button>
          </form>

          <p style={{ textAlign: 'center', fontSize: '0.85rem', marginTop: '12px' }}>
            {isLoginMode ? "Need an account?" : "Already registered?"}{' '}
            <span
              onClick={() => { setIsLoginMode(!isLoginMode); setErrorMessage(''); }}
              style={{ textDecoration: 'underline', cursor: 'pointer', color: themeBlue, fontWeight: '600' }}
            >
              {isLoginMode ? 'Sign up' : 'Log in'}
            </span>
          </p>
        </div>
      </div>
    );
  }

  // Helper for tab styling
  const getTabStyle = (tabName) => ({
    padding: '8px 18px', border: 'none', background: 'none', cursor: 'pointer',
    borderBottom: currentView === tabName ? `2px solid ${themeBlue}` : '2px solid transparent',
    fontWeight: currentView === tabName ? '700' : '400',
    color: currentView === tabName ? themeBlue : '#444',
    fontSize: '0.9rem',
  });

  return (
    <div style={{ padding: '24px', fontFamily: 'Arial, sans-serif', maxWidth: '900px', margin: 'auto', color: '#222' }}>

      {/* Top Nav */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
        <h1 style={{ margin: 0, fontSize: '1.4rem', color: '#000' }}>Ledgerly</h1>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button onClick={logoutUser} style={btnStyle}>Log Out</button>
          <button onClick={wipeAllData} style={btnDanger}>Reset All</button>
        </div>
      </div>

      <div style={{ borderBottom: '1px solid #ccc', marginBottom: '20px', display: 'flex' }}>
        <button style={getTabStyle('dashboard')} onClick={() => setCurrentView('dashboard')}>Dashboard</button>
        <button style={getTabStyle('monthly')} onClick={() => setCurrentView('monthly')}>Monthly Report</button>
      </div>

      {currentView === 'dashboard' && (
        <>
          <div style={{ ...cardStyle, marginBottom: '20px' }}>
            <form onSubmit={updateBudget} style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <strong>Monthly Budget: $</strong>
              <input type="number" value={budgetInput} onChange={e => setBudgetInput(e.target.value)}
                placeholder={dashboardData?.monthly_budget || '3000'} required style={{ ...inputStyle, width: '110px' }} />
              <button type="submit" style={btnStyle}>Save</button>
            </form>
          </div>

          <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}>
            {/* Manual Entry Form */}
            <div style={{ ...cardStyle, flex: 1, minWidth: '260px' }}>
              <h3 style={{ margin: '0 0 12px', fontSize: '1rem', color: '#000' }}>Manual Entry</h3>
              <form onSubmit={submitManualExpense} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <input placeholder="What did you buy?" value={newExpense.item} onChange={e => setNewExpense({ ...newExpense, item: e.target.value })} required style={inputStyle} />
                <input placeholder="Cost" type="number" step="0.01" value={newExpense.amount} onChange={e => setNewExpense({ ...newExpense, amount: e.target.value })} required style={inputStyle} />
                <input placeholder="Category (e.g., Food)" value={newExpense.category} onChange={e => setNewExpense({ ...newExpense, category: e.target.value })} required style={inputStyle} />
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <label style={{ fontSize: '0.85rem' }}>Date:</label>
                  <input type="date" value={newExpense.date} onChange={e => setNewExpense({ ...newExpense, date: e.target.value })} style={{ ...inputStyle, flex: 1 }} />
                  <span style={{ fontSize: '0.75rem', color: '#666' }}>{formatDate(newExpense.date)}</span>
                </div>
                <button type="submit" style={btnPrimary}>Add to Ledger</button>
              </form>
            </div>

            {/* Receipt Scanner */}
            <div style={{ ...cardStyle, flex: 1, minWidth: '260px' }}>
              <h3 style={{ margin: '0 0 12px', fontSize: '1rem', color: '#000' }}>Scan Receipt</h3>
              <form onSubmit={uploadReceipt} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <input type="file" accept="image/*" onChange={e => setReceiptFile(e.target.files[0])} required style={inputStyle} />
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <label style={{ fontSize: '0.85rem' }}>Date:</label>
                  <input type="date" value={receiptDate} onChange={e => setReceiptDate(e.target.value)} style={{ ...inputStyle, flex: 1 }} />
                  <span style={{ fontSize: '0.75rem', color: '#666' }}>{formatDate(receiptDate)}</span>
                </div>
                
                <p style={{ margin: 0, fontSize: '0.75rem', color: '#666' }}>We usually pull the date from the receipt, but you can override it here.</p>
                <button type="submit" disabled={isUploading} style={{ ...btnPrimary, background: isUploading ? '#999' : themeBlue, cursor: isUploading ? 'not-allowed' : 'pointer' }}>
                  {isUploading ? 'Scanning...' : 'Upload File'}
                </button>
              </form>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            {/* Quick Stats */}
            <div style={{ ...cardStyle, flex: 1, minWidth: '240px' }}>
              <h2 style={{ margin: '0 0 12px', fontSize: '1.05rem', color: '#000' }}>Current Status</h2>
              {dashboardData ? (
                <>
                  <p style={{ margin: '4px 0' }}>Budget: ${dashboardData.monthly_budget?.toFixed(2)}</p>
                  <p style={{ margin: '4px 0' }}>Spent so far: ${dashboardData.total_spent?.toFixed(2)}</p>
                  
                  {dashboardData.status === 'OVER_BUDGET' ? (
                    <>
                      <p style={{ margin: '4px 0', color: themeRed }}>Overdrawn by: ${Math.abs(dashboardData.remaining_budget).toFixed(2)}</p>
                      <p style={{ margin: '8px 0 0', fontWeight: '700', color: themeRed }}>Daily Limit: $0.00</p>
                    </>
                  ) : (
                    <>
                      <p style={{ margin: '4px 0' }}>Left to spend: ${dashboardData.remaining_budget?.toFixed(2)}</p>
                      <p style={{ margin: '8px 0 0', fontWeight: '700', color: themeBlue }}>Daily Limit: ${dashboardData.optimized_daily_limit?.toFixed(2)}</p>
                    </>
                  )}
                </>
              ) : <p style={{ color: '#666' }}>Loading stats...</p>}
            </div>

            {/* History Feed */}
            <div style={{ ...cardStyle, flex: 1.4, minWidth: '300px' }}>
              <h2 style={{ margin: '0 0 12px', fontSize: '1.05rem', color: '#000' }}>Transactions</h2>
              <div style={{ maxHeight: '320px', overflowY: 'auto' }}>
                
                {dashboardData?.history?.length > 0 ? dashboardData.history.map((tx, idx) => (
                  <div key={idx} style={{ border: '1px solid #ccc', marginBottom: '8px' }}>
                    
                    {/* Collapsible Header */}
                    <div onClick={() => toggleTransaction(idx)} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px', cursor: 'pointer', background: '#f5f5f5' }}>
                      <div>
                        <strong style={{ color: '#000', fontSize: '0.95rem' }}>{tx.shop}</strong>
                        <span style={{ fontSize: '0.78rem', color: '#000', marginLeft: '8px' }}>{formatDate(tx.date)}</span>
                        <span style={{ fontSize: '0.75rem', color: '#000', marginLeft: '8px' }}>
                          ({tx.items?.length || 0} items) {openToggles[idx] ? '-' : '+'}
                        </span>
                      </div>
                      <strong style={{ color: '#000', fontSize: '0.95rem' }}>${Number(tx.total).toFixed(2)}</strong>
                    </div>
                    
                    {/* Items Dropdown */}
                    {openToggles[idx] && tx.items?.map((item, j) => (
                      <div key={j} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 16px', borderTop: '1px solid #ccc', fontSize: '0.85rem', color: '#000' }}>
                        <span>{item.item} ({item.category})</span>
                        <span>${Number(item.amount).toFixed(2)}</span>
                      </div>
                    ))}

                  </div>
                )) : <p style={{ color: '#666', fontStyle: 'italic' }}>Nothing here yet. Add an expense above.</p>}
                
              </div>
            </div>
          </div>
        </>
      )}

      {currentView === 'monthly' && (
        <div>
          <h2 style={{ margin: '0 0 16px', fontSize: '1.1rem', color: '#000' }}>History (Last 12 Months)</h2>
          
          {monthlyData ? (
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'left', borderBottom: `2px solid ${themeBlue}`, padding: '8px 6px' }}>Month</th>
                  <th style={{ textAlign: 'right', borderBottom: `2px solid ${themeBlue}`, padding: '8px 6px' }}>Spent</th>
                  <th style={{ textAlign: 'right', borderBottom: `2px solid ${themeBlue}`, padding: '8px 6px' }}>+/- Budget</th>
                </tr>
              </thead>
              <tbody>
                {[...monthlyData].reverse().map((monthInfo, index) => {
                  const currentBudget = dashboardData?.monthly_budget || 3000;
                  const difference = currentBudget - monthInfo.total;
                  const isCurrentMonth = index === 0;
                  
                  return (
                    <tr key={monthInfo.month} style={{ borderBottom: '1px solid #ddd' }}>
                      <td style={{ padding: '7px 6px', fontWeight: isCurrentMonth ? '700' : '400', color: isCurrentMonth ? themeBlue : '#222' }}>
                        {monthInfo.label}{isCurrentMonth ? ' (current)' : ''}
                      </td>
                      <td style={{ padding: '7px 6px', textAlign: 'right' }}>
                        {monthInfo.total > 0 ? `$${monthInfo.total.toFixed(2)}` : '-'}
                      </td>
                      <td style={{ padding: '7px 6px', textAlign: 'right', color: difference >= 0 ? '#16a34a' : themeRed }}>
                        {monthInfo.total > 0 ? (difference >= 0 ? `+$${difference.toFixed(2)}` : `-$${Math.abs(difference).toFixed(2)}`) : '-'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : <p style={{ color: '#666' }}>Fetching reports...</p>}
        </div>
      )}

    </div>
  );
}

export default App;