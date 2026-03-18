#!/usr/bin/env node

const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

const rootDir = path.resolve(__dirname, '..');
const venvPath = path.join(rootDir, '.venv');

const isWin = os.platform() === 'win32';
const pythonCmd = isWin ? 'python' : 'python3';
const venvPythonCmd = isWin ? path.join(venvPath, 'Scripts', 'python') : path.join(venvPath, 'bin', 'python');
const venvPipCmd = isWin ? path.join(venvPath, 'Scripts', 'pip') : path.join(venvPath, 'bin', 'pip');

function runCommand(command, args, cwd) {
    console.log(`\n> ${command} ${args.join(' ')}`);
    const result = spawnSync(command, args, { stdio: 'inherit', cwd: cwd, shell: isWin });
    if (result.error) {
        console.error(`\n[!] Error executing ${command}:`, result.error.message);
        console.error(`[!] Please make sure Node and Python/Pip are installed correctly on your system.\n`);
        process.exit(1);
    }
    if (result.status !== 0 && result.status !== null) {
        console.error(`\n[!] Command failed with exit code ${result.status}\n`);
        process.exit(result.status);
    }
}

console.log('\n--- Image Library App Environment Setup ---');

// 1. Create a virtual environment if it doesn't already exist
if (!fs.existsSync(venvPath)) {
    console.log('\nCreating Python virtual environment in .venv folder...');
    runCommand(pythonCmd, ['-m', 'venv', '.venv'], rootDir);
} else {
    console.log('\nVirtual environment (.venv) already exists. Skipping creation.');
}

// 2. Install requirements using pip
console.log('\nInstalling Python dependencies from requirements.txt...');
runCommand(venvPipCmd, ['install', '-r', 'requirements.txt'], rootDir);

// 3. Initialize the database
console.log('\nChecking and initializing the MySQL database...');
runCommand(venvPythonCmd, ['init_db.py'], rootDir);

// 4. Start the Flask server
console.log('\nStarting the Flask Image Library Application...\n');
// We use spawnSync to block the node process while Flask runs
const appProcess = spawnSync(venvPythonCmd, ['app.py'], { stdio: 'inherit', cwd: rootDir, shell: isWin });

if (appProcess.error) {
    console.error(`\n[!] Failed to start Flask app:`, appProcess.error.message);
    process.exit(1);
}
console.log('\nFlask server stopped.');
