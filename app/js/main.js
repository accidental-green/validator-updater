const { app, Menu, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { exec, spawn, execSync } = require('child_process');

// Global variables
global.multipleClientsInstalled = null;
global.userSettings = {};
global.installedClients = [];
global.latestClients = [];
global.clientNames = [];

let loadingWindow;
let updateWindow;
let updateProgress;
let miniDash;
let journalsWindow;

const services = [
  'geth', 'besu', 'nethermind', 'reth',
  'lighthousebeacon', 'lighthousevalidator',
  'nimbus', 'prysmbeacon', 'prysmvalidator',
  'teku', 'mevboost'
];

// Define the path to the system Python and set up the environment variables
const pythonPath = 'python3'; // Assuming Python 3 is installed system-wide
const pythonEnv = {
  ...process.env,
  PYTHONPATH: `/usr/lib/python3/dist-packages` // Update PYTHONPATH if needed for requests or other dependencies
};

// Function to execute Python script with the system's Python interpreter
function executePythonScript(scriptPath, args = [], callback) {
  const command = `python3 ${scriptPath} ${args.join(' ')}`; // Use system Python (assuming python3 is installed)
  exec(command, { env: pythonEnv }, (error, stdout, stderr) => {
    if (error) {
      console.error(`Execution error: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Script error output: ${stderr}`);
      return;
    }
    if (stdout) {
      console.log(`Script output: ${stdout}`);
    }
    if (callback) {
      callback(stdout);
    }
  });
}

function firstCheckSudoPrivileges() {
  try {
    console.log("Starting Validator Updater and authenticating sudo access.\n\nPlease enter user password:\n");
    execSync('sudo -v', { stdio: 'inherit' }); // 'inherit' makes the prompt visible
    console.log("Sudo credentials authenticated.");
    return true; // Sudo success
  } catch (error) {
    console.error(`Failed to verify sudo credentials: ${error}`);
    return false; // Sudo failed
  }
}

function checkSudoPrivileges() {
  return new Promise((resolve, reject) => {
    exec('sudo -nv', (error, stdout, stderr) => {
      if (error) {
        console.error(`Sudo check failed: ${error}`);
        resolve(false); // Indicates that sudo privileges are not available without a password prompt
      } else {
        console.log("Sudo privileges are active.");
        resolve(true); // Indicates that sudo privileges are available
      }
    });
  });
}

function fetchInstalledClients(callback) {
  const scriptPath = path.join(process.resourcesPath, 'modules', 'prints.py'); // Assume app is packaged

  // Use system Python (assuming python3 is installed)
  const command = `python3 ${scriptPath}`;

  exec(command, { env: pythonEnv }, (error, stdout, stderr) => {
    if (error) {
      console.error(`Execution error: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Script error output: ${stderr}`);
      return;
    }

    const jsonOutputLine = stdout.split('\n').find(line => line.startsWith('JSON_INSTALLED:'));
    if (jsonOutputLine) {
      try {
        const installedClients = JSON.parse(jsonOutputLine.replace('JSON_INSTALLED: ', ''));
        console.log('Installed Clients:', installedClients);
        global.installedClients = installedClients;
        showClientNames(installedClients);
      } catch (parseError) {
        console.error('Error parsing JSON from Python script:', parseError);
      }
    } else {
      console.error('No JSON output found in the script response.');
    }

    if (callback) {
      callback();
    }
  });
}

function showClientNames(installedClients) {
  const clientNames = installedClients.map(client => Object.keys(client)[0]);
  console.log('Client Names:', clientNames);
  global.clientNames = clientNames;
}

function fetchLatestVersions(callback) {
  const scriptPath = path.join(process.resourcesPath, 'modules', 'latest_versions.py'); // Assume app is packaged

  exec(`python3 ${scriptPath}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`Execution error: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Script error output: ${stderr}`);
      return;
    }

    const jsonLatestOutputLine = stdout.split('\n').find(line => line.startsWith('JSON_LATEST:'));
    if (jsonLatestOutputLine) {
      try {
        const latestClients = JSON.parse(jsonLatestOutputLine.replace('JSON_LATEST: ', ''));
        console.log('Latest Github Clients:', latestClients);
        global.latestClients = latestClients;
      } catch (parseError) {
        console.error('Error parsing JSON from Python script:', parseError);
      }
    } else {
      console.error('No JSON output found in the script response.');
    }

    if (callback) {
      callback();
    }
  });
}

// Client groups with correct names as they appear as keys in the installed clients objects
const executionClients = ['Geth', 'Besu', 'Nethermind', 'Reth'];
const consensusClients = ['Lighthouse', 'Prysm', 'Nimbus', 'Teku'];

async function startServices(data) {
  const hasSudo = await checkSudoPrivileges();
  if (!hasSudo) {
    mainWindow.webContents.send('sudo-required', 'Sudo authentication is required to start services. Please restart the application and enter your password.');
    return;
  }

  console.log("Starting services with the following configuration:", data);

  const pythonScriptPath = path.join(process.resourcesPath, 'modules', 'start.py'); // Assume app is packaged

  const command = `python3 ${pythonScriptPath} '${data.execution}' '${data.consensus}' '${data.validator}' '${data.mevboost}'`;

  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Execution error: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Script error output: ${stderr}`);
      return;
    }
    if (stdout) {
      console.log(`Service start script output: ${stdout}`);
    }
  });
}

async function stopServices(data) {
  const hasSudo = await checkSudoPrivileges();
  if (!hasSudo) {
    mainWindow.webContents.send('sudo-required', 'Sudo authentication is required to stop services. Please restart the application and enter your password.');
    return;
  }

  console.log("Stopping services with the following configuration:", data);

  const pythonScriptPath = path.join(process.resourcesPath, 'modules', 'stop.py'); // Assume app is packaged

  const command = `python3 ${pythonScriptPath} '${data.execution}' '${data.consensus}' '${data.validator}' '${data.mevboost}'`;

  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Execution error: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Script error output: ${stderr}`);
      return;
    }
    if (stdout) {
      console.log(`Service stop script output: ${stdout}`);
    }
  });
}

function createWindow(filename) {
  let window = new BrowserWindow({
      width: 800,
      height: 600,
      webPreferences: {
          preload: path.join(__dirname, 'preload.js'),
          contextIsolation: true,
          nodeIntegration: false,
          enableRemoteModule: false,
      }
  });
  window.setMenu(null);
  window.loadFile(filename);
  return window;
}

function createBigWindow(filename) {
  let window = new BrowserWindow({
      width: 800,
      height: 700,
      webPreferences: {
          preload: path.join(__dirname, 'preload.js'),
          contextIsolation: true,
          nodeIntegration: false,
          enableRemoteModule: false,
      }
  });
  window.setMenu(null);
  window.loadFile(filename);
  return window;
}

function createMiniDashWindow(filename) {
  let window = new BrowserWindow({
      width: 620,
      height: 400,
      webPreferences: {
          preload: path.join(__dirname, 'preload.js'),
          contextIsolation: true,
          nodeIntegration: false,
          enableRemoteModule: false,
      }
  });
  window.setMenu(null);
  window.loadFile(filename);
  return window;
}

function createJournalsWindow() {
  journalsWindow = createWindow('app/html/journals.html');
  journalsWindow.maximize();
  journalsWindow.webContents.on('did-finish-load', () => {
    journalsWindow.webContents.send('get-installed-versions', global.installedClients);
  });
}

function createWideWindow(filename) {
  let window = new BrowserWindow({
      width: 860,
      height: 680,
      webPreferences: {
          preload: path.join(__dirname, 'preload.js'),
          contextIsolation: true,
          nodeIntegration: false,
          enableRemoteModule: false,
      }
  });
  window.setMenu(null);
  window.loadFile(filename);
  return window;
}

function createWiderWindow(filename) {
  let window = new BrowserWindow({
      width: 1000,
      height: 540,
      webPreferences: {
          preload: path.join(__dirname, 'preload.js'),
          contextIsolation: true,
          nodeIntegration: false,
          enableRemoteModule: false,
      }
  });
  window.setMenu(null);
  window.loadFile(filename);
  return window;
}

function createUpWindow(filename) {
  let window = new BrowserWindow({
      width: 500,
      height: 570,
      webPreferences: {
          preload: path.join(__dirname, 'preload.js'),
          contextIsolation: true,
          nodeIntegration: false,
          enableRemoteModule: false,
      }
  });
  window.setMenu(null);
  window.loadFile(filename);
  return window;
}


function createNoClientsPopup() {
  installWindow = createWiderWindow('app/html/noClients.html');
}

function createLoadingWindow() {
  loadingWindow = createWindow('app/html/loading.html')
}

function createUpdateWindow() {
  updateWindow = createUpWindow('app/html/updateWindow.html')

  updateWindow.webContents.on('did-finish-load', () => {
    // Assuming `global.installedClients` and `global.latestClients` are properly set
    updateWindow.webContents.send('get-installed-versions', global.installedClients, global.latestClients);
  });
}

function createUpdateProgressWindow() {
  updateProgress = createWideWindow('app/html/updateProgress.html');
}

function createMiniDash() {
  miniDash = createMiniDashWindow('app/html/miniDash.html');
  miniDash.webContents.on('did-finish-load', () => {
    miniDash.webContents.send('get-installed-versions', global.installedClients);
  });
}

app.disableHardwareAcceleration();

app.whenReady().then(() => {
  firstCheckSudoPrivileges();
  createLoadingWindow();

  fetchInstalledClients(() => {
    fetchLatestVersions(() => {
      const clientsInstalled = global.installedClients.length > 0;

      if (clientsInstalled) {
        console.log("Clients installed:", clientsInstalled);
        createUpdateWindow();
      } else {
        createNoClientsPopup();
      }

      if (loadingWindow) {
        loadingWindow.close();
        loadingWindow = null;
      }
    });
  });
});



app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

ipcMain.on('quit-app', () => {
  app.quit();
});

ipcMain.handle('check-sudo-privileges', async (event) => {
  const hasSudo = await checkSudoPrivileges();  // Assumes checkSudoPrivileges returns a promise that resolves to a boolean
  if (!hasSudo) {
      event.sender.send('sudo-required', 'Sudo privileges are required.');
  }
  return hasSudo;
});

ipcMain.on('startServices', (event, settings) => {
  const { execution, consensus, mevboost } = settings;
  startServices(settings);
});

ipcMain.on('stopServices', (event, settings) => {
  const { execution, consensus, mevboost } = settings;
  stopServices(settings);
});

ipcMain.on('open-update-popup', (event, args) => {
  createUpdateWindow();
  if (startupWindow) {
    startupWindow.close();
    startupWindow = null;
  }
  if (freshStartupWindow) {
    freshStartupWindow.close();
    freshStartupWindow = null;
  }
  if (installWindow) {
    installWindow.close();
    installWindow = null;
  }
});

ipcMain.on('send-input', (event, input) => {
    if (pythonProcess) {
        pythonProcess.stdin.write(input + "\n"); // Send input to Python process
    }
});

ipcMain.handle('get-logs', async (event, serviceName, lines) => {
  if (!serviceName) return 'Service name is required.';

  try {
    const command = `journalctl -u ${serviceName} --no-pager -n ${lines} --reverse`;
    const logs = await runCommand(command);
    return logs;
  } catch (error) {
    return `Error fetching logs for ${serviceName}`;
  }
});

function runCommand(command, args = []) {
  return new Promise((resolve, reject) => {
      exec(command, (error, stdout, stderr) => {
          if (error) {
              console.error(`exec error: ${error}`);
              return reject(stderr);
          }
          resolve(stdout);
      });
  });
}

ipcMain.handle('get-installed-versions', async (event) => {
    fetchInstalledClients();
  });

ipcMain.handle('get-running-services', async () => {
  const runningServices = await Promise.all(services.map(async (service) => {
      return new Promise((resolve) => {
          exec(`systemctl is-active ${service}`, (error, stdout, stderr) => {
              if (!error && stdout.trim() === 'active') {
                  resolve(service);
              } else {
                  resolve(null);
              }
          });
      });
  }));
  return runningServices.filter(Boolean); // Filter out null values
});

ipcMain.on('start-update', (event, settings) => {
  if (!updateProgress) createUpdateProgressWindow();
  if (updateWindow) {
    updateWindow.close();
    updateWindow = null;
  }

  console.log("\nStarting Update with settings:");
  console.table(settings);

  global.appSettings = settings;

  const scriptPath = path.join(process.resourcesPath, 'modules', 'updater.py'); // Assume app is packaged

  const args = ['-u', scriptPath, settings.execution, settings.consensus, settings.mevboost];
  const childProcess = spawn('python3', args);

  childProcess.stdout.on('data', (data) => {
    const lines = data.toString().split('\n');
  
    for (let line of lines) {
      if (!line) continue;
  
      const lower = line.toLowerCase();
  
      if (
        line.includes("UPDATE") ||
        line.includes("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Note:") ||
        line.includes("Version:") ||
        line.includes("Execution Client:") ||
        line.includes("Consensus Client:") ||
        line.includes("MEVboost:")
      ) {
        if (!lower.includes("successfully")) {
          updateProgress.webContents.send('process-output', line);
        }
      }
    }
  });
  

  childProcess.on('close', (code) => {
    fetchInstalledClients(() => {
      if (updateProgress) {
        let message = `Process exited with code ${code}`;
        if (code === 0) {
          message = "##### UPDATES COMPLETE ######";
        } else if (code === 1) {
          message = "EXIT - UPDATE FAILED AT THIS POINT\n\n Please exit or go back to the main menu.";
        }
        updateProgress.webContents.send('process-complete', message);
      }
    });
  });

  handleChildProcessOutput(childProcess);
});

ipcMain.on('minidash-start', (event) => {
  createMiniDash();
  if (updateProgress) {
    updateProgress.close();
    updateProgress = null;
  }
  if (journalsWindow) {
    journalsWindow.close();
    journalsWindow = null;
  }
});

ipcMain.on('journals-start', (event) => {
  journalsWindow = null;
  createJournalsWindow();
  if (miniDash) {
    miniDash.close();
    miniDash = null;
  }
});

function logEntry(type, data) {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] [${type.toUpperCase()}]: ${data.trim()}`);
}

// Function to handle output from child processes
function handleChildProcessOutput(child) {
  child.stdout.on('data', (data) => {
    logEntry('stdout', data.toString());
  });

  child.stderr.on('data', (data) => {
    logEntry('stderr', data.toString());
  });

  child.on('close', (code) => {
    logEntry('info', `Child process exited with code ${code}`);
  });
}

process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  require('electron').dialog.showErrorBox('Uncaught Exception', error.message || "An error occurred");
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  require('electron').dialog.showErrorBox('Unhandled Rejection', reason.message || "An error occurred");
});
