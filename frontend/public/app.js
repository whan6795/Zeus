// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// State management
let authToken = null;
let currentUser = null;
let taskPollingIntervals = {};

// DOM Elements
const loginPage = document.getElementById('login-page');
const mainPage = document.getElementById('main-page');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const logoutBtn = document.getElementById('logout-btn');
const currentUsernameSpan = document.getElementById('current-username');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check if user is already logged in
    const savedToken = localStorage.getItem('authToken');
    if (savedToken) {
        authToken = savedToken;
        verifyTokenAndShowMainPage();
    }
    
    setupEventListeners();
});

function setupEventListeners() {
    // Login form
    loginForm.addEventListener('submit', handleLogin);
    
    // Logout button
    logoutBtn.addEventListener('click', handleLogout);
    
    // Tab buttons
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            switchTab(tabId);
        });
    });
    
    // Execute buttons
    const executeButtons = document.querySelectorAll('.execute-btn');
    executeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const module = button.getAttribute('data-module');
            executeModule(module);
        });
    });
}

async function handleLogin(e) {
    e.preventDefault();
    loginError.textContent = '';
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('登录失败: 用户名或密码错误');
        }
        
        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem('authToken', authToken);
        
        await loadUserInfo();
        showMainPage();
    } catch (error) {
        loginError.textContent = error.message;
    }
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    
    // Clear all polling intervals
    Object.keys(taskPollingIntervals).forEach(key => {
        clearInterval(taskPollingIntervals[key]);
    });
    taskPollingIntervals = {};
    
    showLoginPage();
}

async function verifyTokenAndShowMainPage() {
    try {
        await loadUserInfo();
        showMainPage();
    } catch (error) {
        handleLogout();
    }
}

async function loadUserInfo() {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
            'Authorization': `Bearer ${authToken}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to load user info');
    }
    
    currentUser = await response.json();
    currentUsernameSpan.textContent = `用户: ${currentUser.username}`;
    
    // Update UI based on permissions
    updateUIBasedOnPermissions();
}

function updateUIBasedOnPermissions() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Hide tabs without permission
    tabButtons.forEach((button, index) => {
        const module = button.getAttribute('data-tab');
        const hasPermission = currentUser.permissions.includes(module);
        
        if (!hasPermission) {
            button.style.display = 'none';
            tabContents[index].style.display = 'none';
        }
    });
    
    // Show first available tab
    const firstAvailableTab = Array.from(tabButtons).find(btn => 
        currentUser.permissions.includes(btn.getAttribute('data-tab'))
    );
    
    if (firstAvailableTab) {
        switchTab(firstAvailableTab.getAttribute('data-tab'));
    }
}

function showLoginPage() {
    loginPage.classList.add('active');
    mainPage.classList.remove('active');
}

function showMainPage() {
    loginPage.classList.remove('active');
    mainPage.classList.add('active');
}

function switchTab(tabId) {
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-tab') === tabId) {
            btn.classList.add('active');
        }
    });
    
    // Update tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
        if (content.id === tabId) {
            content.classList.add('active');
        }
    });
}

async function executeModule(module) {
    const button = document.querySelector(`[data-module="${module}"]`);
    const infoDiv = document.getElementById(`${module}-info`);
    
    button.disabled = true;
    infoDiv.innerHTML = '<div class="status pending"><span class="loading"></span>正在提交任务...</div>';
    infoDiv.classList.add('visible');
    
    try {
        const response = await fetch(`${API_BASE_URL}/modules/${module}/execute`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                module_name: module,
                parameters: {}
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '执行失败');
        }
        
        const data = await response.json();
        const taskId = data.task_id;
        
        infoDiv.innerHTML = `
            <h3>任务信息</h3>
            <div class="status pending">
                <span class="loading"></span>
                任务ID: ${taskId}<br>
                状态: 执行中...
            </div>
        `;
        
        // Start polling for task status
        pollTaskStatus(module, taskId);
    } catch (error) {
        infoDiv.innerHTML = `<div class="status failed">错误: ${error.message}</div>`;
        button.disabled = false;
    }
}

function pollTaskStatus(module, taskId) {
    // Clear existing interval for this module
    if (taskPollingIntervals[module]) {
        clearInterval(taskPollingIntervals[module]);
    }
    
    const infoDiv = document.getElementById(`${module}-info`);
    const button = document.querySelector(`[data-module="${module}"]`);
    
    taskPollingIntervals[module] = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/modules/tasks/${taskId}`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });
            
            if (!response.ok) {
                throw new Error('获取任务状态失败');
            }
            
            const taskStatus = await response.json();
            
            if (taskStatus.status === 'success') {
                clearInterval(taskPollingIntervals[module]);
                infoDiv.innerHTML = `
                    <h3>任务完成</h3>
                    <div class="status success">
                        任务ID: ${taskId}<br>
                        状态: 成功完成
                    </div>
                    <div class="result">
                        <strong>执行结果:</strong>
                        <pre>${JSON.stringify(taskStatus.result, null, 2)}</pre>
                    </div>
                `;
                button.disabled = false;
            } else if (taskStatus.status === 'failed') {
                clearInterval(taskPollingIntervals[module]);
                infoDiv.innerHTML = `
                    <h3>任务失败</h3>
                    <div class="status failed">
                        任务ID: ${taskId}<br>
                        状态: 失败<br>
                        错误: ${taskStatus.error}
                    </div>
                `;
                button.disabled = false;
            } else {
                // Still running
                infoDiv.innerHTML = `
                    <h3>任务信息</h3>
                    <div class="status pending">
                        <span class="loading"></span>
                        任务ID: ${taskId}<br>
                        状态: ${taskStatus.status}
                    </div>
                `;
            }
        } catch (error) {
            clearInterval(taskPollingIntervals[module]);
            infoDiv.innerHTML += `<div class="status failed">轮询错误: ${error.message}</div>`;
            button.disabled = false;
        }
    }, 2000); // Poll every 2 seconds
}
