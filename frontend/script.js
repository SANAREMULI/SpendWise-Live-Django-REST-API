const API_BASE = window.SPENDWISE_API_BASE || 'http://127.0.0.1:8000/api';
const state = { token: localStorage.getItem('spendwise_token'), category: '', search: '', next: null, previous: null, page: 1 };

const loginPanel = document.querySelector('#login-panel');
const appPanel = document.querySelector('#app-panel');
const loginStatus = document.querySelector('#login-status');
const expenseStatus = document.querySelector('#expense-status');

function showApp() { loginPanel.classList.add('hidden'); appPanel.classList.remove('hidden'); loadExpenses(); }
function showLogin() { appPanel.classList.add('hidden'); loginPanel.classList.remove('hidden'); }
function authHeaders() { return { 'Content-Type': 'application/json', Authorization: `Token ${state.token}` }; }

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers: { ...authHeaders(), ...(options.headers || {}) } });
  if (response.status === 401) { localStorage.removeItem('spendwise_token'); state.token = null; showLogin(); throw new Error('Your session has expired.'); }
  if (!response.ok) throw new Error((await response.json()).detail || 'Request failed.');
  return response.json();
}

async function loadExpenses(url = null) {
  const params = new URLSearchParams();
  if (state.category) params.set('category', state.category);
  if (state.search) params.set('search', state.search);
  params.set('ordering', '-created_at');
  try {
    const data = await api(url || `/expenses/?${params}`);
    state.next = data.next; state.previous = data.previous;
    document.querySelector('#page-label').textContent = `Page ${state.page}`;
    document.querySelector('#next').disabled = !state.next;
    document.querySelector('#previous').disabled = !state.previous;
    const list = document.querySelector('#expense-list');
    list.innerHTML = data.results.length ? data.results.map(expense => `<article class="expense"><div><h3>${escapeHtml(expense.description)}</h3><p>${escapeHtml(expense.category)} &middot; ${new Date(expense.created_at).toLocaleDateString()}</p></div><strong class="amount">$${expense.amount}</strong></article>`).join('') : '<p class="status">No expenses found.</p>';
  } catch (error) { expenseStatus.textContent = error.message; }
}

function escapeHtml(value) { const div = document.createElement('div'); div.textContent = value; return div.innerHTML; }

document.querySelector('#login-form').addEventListener('submit', async event => {
  event.preventDefault(); loginStatus.textContent = 'Signing in...';
  const response = await fetch(`${API_BASE}/login/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: document.querySelector('#username').value, password: document.querySelector('#password').value }) });
  if (!response.ok) { loginStatus.textContent = 'Invalid username or password.'; return; }
  state.token = (await response.json()).token; localStorage.setItem('spendwise_token', state.token); showApp();
});

document.querySelector('#expense-form').addEventListener('submit', async event => {
  event.preventDefault(); expenseStatus.textContent = 'Saving...';
  try {
    await api('/expenses/', { method: 'POST', body: JSON.stringify({ amount: document.querySelector('#amount').value, description: document.querySelector('#description').value, category: document.querySelector('#category').value }) });
    event.target.reset(); expenseStatus.textContent = 'Expense added.'; state.page = 1; await loadExpenses();
  } catch (error) { expenseStatus.textContent = error.message; }
});

document.querySelectorAll('[data-category]').forEach(button => button.addEventListener('click', () => {
  state.category = button.dataset.category; state.page = 1;
  document.querySelectorAll('[data-category]').forEach(item => item.classList.toggle('active', item === button)); loadExpenses();
}));
document.querySelector('#search').addEventListener('input', event => { state.search = event.target.value; state.page = 1; loadExpenses(); });
document.querySelector('#next').addEventListener('click', () => { state.page += 1; loadExpenses(state.next); });
document.querySelector('#previous').addEventListener('click', () => { state.page -= 1; loadExpenses(state.previous); });
document.querySelector('#logout').addEventListener('click', () => { localStorage.removeItem('spendwise_token'); state.token = null; showLogin(); });
if (state.token) showApp();