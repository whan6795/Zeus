// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// State management
let authToken = null;
let currentUser = null;
let taskPollingIntervals = {};
let moduleData = null;

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
        await loadModulesAndScripts();
        showMainPage();
    } catch (error) {
        loginError.textContent = error.message;
    }
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    moduleData = null;
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
        await loadModulesAndScripts();
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
}

async function loadModulesAndScripts() {
    const response = await fetch(`${API_BASE_URL}/modules/list`, {
        headers: {
            'Authorization': `Bearer ${authToken}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to load modules');
    }
    
    const data = await response.json();
    moduleData = data.modules;
    
    // Render the UI
    renderModuleTabs();
    renderModuleContents();
}

function renderModuleTabs() {
    const tabsContainer = document.querySelector('.tabs');
    tabsContainer.innerHTML = '';
    
    moduleData.forEach((module, index) => {
        const button = document.createElement('button');
        button.className = 'tab-button' + (index === 0 ? ' active' : '');
        button.setAttribute('data-tab', module.id);
        button.textContent = module.name;
        button.addEventListener('click', () => switchTab(module.id));
        tabsContainer.appendChild(button);
    });
}

function renderModuleContents() {
    const container = document.querySelector('.container');
    
    // Remove old tab contents
    const oldContents = container.querySelectorAll('.tab-content');
    oldContents.forEach(content => content.remove());
    
    moduleData.forEach((module, index) => {
        const tabContent = document.createElement('div');
        tabContent.id = module.id;
        tabContent.className = 'tab-content' + (index === 0 ? ' active' : '');
        
        const heading = document.createElement('h2');
        heading.textContent = module.name;
        tabContent.appendChild(heading);
        
        const description = document.createElement('p');
        description.textContent = module.description;
        tabContent.appendChild(description);
        
        // Create scripts section
        const scriptsSection = document.createElement('div');
        scriptsSection.className = 'scripts-section';
        
        const scriptsHeading = document.createElement('h3');
        scriptsHeading.textContent = '可用脚本:';
        scriptsSection.appendChild(scriptsHeading);
        
        // Create script cards
        const scriptsGrid = document.createElement('div');
        scriptsGrid.className = 'scripts-grid';
        
        module.scripts.forEach(script => {
            const scriptCard = document.createElement('div');
            scriptCard.className = 'script-card';
            
            const scriptName = document.createElement('h4');
            scriptName.textContent = script.name;
            scriptCard.appendChild(scriptName);
            
            const scriptDesc = document.createElement('p');
            scriptDesc.textContent = script.description;
            scriptCard.appendChild(scriptDesc);
            
            const executeBtn = document.createElement('button');
            executeBtn.className = 'btn-primary execute-btn';
            executeBtn.textContent = '执行';
            executeBtn.setAttribute('data-module', module.id);
            executeBtn.setAttribute('data-script', script.id);
            executeBtn.addEventListener('click', () => executeScript(module.id, script.id));
            scriptCard.appendChild(executeBtn);
            
            scriptsGrid.appendChild(scriptCard);
        });
        
        scriptsSection.appendChild(scriptsGrid);
        tabContent.appendChild(scriptsSection);
        
        // Task info area
        const taskInfo = document.createElement('div');
        taskInfo.className = 'task-info';
        taskInfo.id = `${module.id}-info`;
        tabContent.appendChild(taskInfo);
        
        container.appendChild(tabContent);
    });
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

async function executeScript(moduleName, scriptName) {
    const infoDiv = document.getElementById(`${moduleName}-info`);
    const button = document.querySelector(`[data-module="${moduleName}"][data-script="${scriptName}"]`);
    
    button.disabled = true;
    infoDiv.innerHTML = '<div class="status pending"><span class="loading"></span>正在提交任务...</div>';
    infoDiv.classList.add('visible');
    
    try {
        const response = await fetch(`${API_BASE_URL}/modules/execute?module_name=${moduleName}&script_name=${scriptName}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                module_name: moduleName,
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
                脚本: ${scriptName}<br>
                任务ID: ${taskId}<br>
                状态: 执行中...
            </div>
        `;
        
        // Start polling for task status
        pollTaskStatus(moduleName, scriptName, taskId, button);
    } catch (error) {
        infoDiv.innerHTML = `<div class="status failed">错误: ${error.message}</div>`;
        button.disabled = false;
    }
}

function pollTaskStatus(moduleName, scriptName, taskId, button) {
    const pollKey = `${moduleName}-${scriptName}`;
    
    // Clear existing interval for this script
    if (taskPollingIntervals[pollKey]) {
        clearInterval(taskPollingIntervals[pollKey]);
    }
    
    const infoDiv = document.getElementById(`${moduleName}-info`);
    
    taskPollingIntervals[pollKey] = setInterval(async () => {
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
                clearInterval(taskPollingIntervals[pollKey]);
                infoDiv.innerHTML = `
                    <h3>任务完成</h3>
                    <div class="status success">
                        脚本: ${scriptName}<br>
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
                clearInterval(taskPollingIntervals[pollKey]);
                infoDiv.innerHTML = `
                    <h3>任务失败</h3>
                    <div class="status failed">
                        脚本: ${scriptName}<br>
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
                        脚本: ${scriptName}<br>
                        任务ID: ${taskId}<br>
                        状态: ${taskStatus.status}
                    </div>
                `;
            }
        } catch (error) {
            clearInterval(taskPollingIntervals[pollKey]);
            infoDiv.innerHTML += `<div class="status failed">轮询错误: ${error.message}</div>`;
            button.disabled = false;
        }
    }, 2000); // Poll every 2 seconds
}
