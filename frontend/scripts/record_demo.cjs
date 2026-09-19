const { chromium } = require('playwright-core');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const FFMPEG_PATH = 'C:\\Users\\rushi\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-9.0.1-full_build\\bin\\ffmpeg.exe';
const RECORDING_DIR = path.join(__dirname, '..', 'recordings');
const OUTPUT_MP4 = path.join(__dirname, '..', 'paladin_demo.mp4');

if (!fs.existsSync(RECORDING_DIR)) {
  fs.mkdirSync(RECORDING_DIR, { recursive: true });
}

// Clean previous recordings
for (const file of fs.readdirSync(RECORDING_DIR)) {
  if (file.endsWith('.webm')) {
    try { fs.unlinkSync(path.join(RECORDING_DIR, file)); } catch {}
  }
}

async function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function recordDemo() {
  console.log('[*] Launching Chrome at:', CHROME_PATH);
  const browser = await chromium.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--hide-scrollbars',
      '--window-size=1440,900',
    ],
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    recordVideo: {
      dir: RECORDING_DIR,
      size: { width: 1440, height: 900 },
    },
  });

  const page = await context.newPage();
  console.log('[*] Loading Paladin at http://localhost:5173...');
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
  await sleep(1500);

  // Helper smooth scroll
  async function smoothScroll(targetY, durationMs = 800) {
    const steps = 25;
    const startY = await page.evaluate(() => window.scrollY);
    const diff = targetY - startY;
    for (let i = 1; i <= steps; i++) {
      const current = startY + (diff * (i / steps));
      await page.evaluate((pos) => window.scrollTo(0, pos), current);
      await sleep(durationMs / steps);
    }
  }

  // ==========================================
  // PART 1: OVERVIEW & HARDWARE ENCLAVE POSTURE (0s - 7s)
  // ==========================================
  console.log('[*] Step 1: Overview Dashboard & Hardware Diode Posture (0s - 7s)');
  await sleep(2000);
  await smoothScroll(380, 1000);
  await sleep(1800);
  await smoothScroll(0, 800);
  await sleep(1000);

  // ==========================================
  // PART 2: INCIDENTS & FORENSIC INVESTIGATION (7s - 16s)
  // ==========================================
  console.log('[*] Step 2: Incidents Triage & Forensic Slide-over Drawer (7s - 16s)');
  await page.click('.nav-tab:has-text("Incidents")');
  await sleep(1200);

  // Filter by Severity: CRITICAL
  const critBtn = page.locator('button.filter-pill:has-text("CRITICAL")').first();
  if (await critBtn.isVisible()) {
    await critBtn.click();
    await sleep(1000);
    // Switch back to ALL
    const allBtn = page.locator('button.filter-pill:has-text("ALL")').first();
    if (await allBtn.isVisible()) {
      await allBtn.click();
      await sleep(800);
    }
  }

  // Click on the first incident row in the table
  const incidentRow = page.locator('tbody tr').first();
  if (await incidentRow.isVisible()) {
    await incidentRow.click();
    console.log('[+] Opened Forensic Investigation Drawer');
    await sleep(2200);

    // Click ACKNOWLEDGE inside drawer
    const ackBtn = page.locator('.incident-drawer .btn-ack').first();
    if (await ackBtn.isVisible()) {
      await ackBtn.click();
      console.log('[+] Clicked Acknowledge Incident');
      await sleep(1400);
    }

    // Close drawer
    const closeBtn = page.locator('.drawer-header .close-btn').first();
    if (await closeBtn.isVisible()) {
      await closeBtn.click();
      await sleep(800);
    }
  }

  // ==========================================
  // PART 3: REPLAY WORKBENCH & ATTACK SIMULATION (16s - 26s)
  // ==========================================
  console.log('[*] Step 3: Replay Workbench & Attack Simulation (16s - 26s)');
  await page.click('.nav-tab:has-text("Replay Lab")');
  await sleep(1400);

  // Select DDoS scenario card
  const scenarioCard = page.locator('.scenario-card:has-text("Volumetric SYN Flood"), .scenario-card:has-text("02_ddos")').first();
  if (await scenarioCard.isVisible()) {
    await scenarioCard.click();
    await sleep(800);
  }

  // Click START REPLAY button
  const startBtn = page.locator('.replay-header button:has-text("START"), button:has-text("START REPLAY"), .btn-start').first();
  if (await startBtn.isVisible()) {
    await startBtn.click();
    console.log('[+] Clicked START simulation');
    await sleep(3500);
  } else {
    // fallback start button
    const anyStart = page.locator('button:has-text("START")').first();
    if (await anyStart.isVisible()) {
      await anyStart.click();
      await sleep(3500);
    }
  }

  // Scroll to view replay telemetry logs
  await smoothScroll(250, 800);
  await sleep(1500);
  await smoothScroll(0, 600);

  // ==========================================
  // PART 4: THREAT ENGINES & CALIBRATION (26s - 34s)
  // ==========================================
  console.log('[*] Step 4: Threat Engines & AI Sensitivity (26s - 34s)');
  await page.click('.nav-tab:has-text("Detectors")');
  await sleep(1500);
  await smoothScroll(320, 1000);
  await sleep(2200);
  await smoothScroll(0, 800);
  await sleep(1000);

  // ==========================================
  // PART 5: TELEMETRY & NETWORK FLOWS (34s - 40s)
  // ==========================================
  console.log('[*] Step 5: Network Telemetry & Ingest Pipeline (34s - 40s)');
  await page.click('.nav-tab:has-text("Telemetry")');
  await sleep(1500);
  await smoothScroll(300, 900);
  await sleep(2000);
  await smoothScroll(0, 700);

  // ==========================================
  // PART 6: ENCLAVE ARCHITECTURE & CONCLUSION (40s - 45s)
  // ==========================================
  console.log('[*] Step 6: Hardware Data Diode Invariants & Enclave (40s - 43s)');
  await page.click('.nav-tab:has-text("Enclave")');
  await sleep(2200);

  console.log('[*] Step 7: Return to Operations Overview for Final Posture (43s - 46s)');
  await page.click('.nav-tab:has-text("Overview")');
  await sleep(2500);

  console.log('[*] Wrapping up browser session...');
  await page.close();
  await context.close();
  await browser.close();

  // Find generated webm
  const files = fs.readdirSync(RECORDING_DIR).filter((f) => f.endsWith('.webm'));
  if (files.length === 0) throw new Error('No webm recording produced');
  
  files.sort((a, b) => fs.statSync(path.join(RECORDING_DIR, b)).mtimeMs - fs.statSync(path.join(RECORDING_DIR, a)).mtimeMs);
  const recordedWebm = path.join(RECORDING_DIR, files[0]);
  console.log('[+] Raw video captured at:', recordedWebm);

  // Transcode to MP4 with FFmpeg
  console.log('[*] Transcoding to high quality MP4 using FFmpeg...');
  const ffmpegCmd = `"${FFMPEG_PATH}" -y -i "${recordedWebm}" -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -r 30 "${OUTPUT_MP4}"`;
  execSync(ffmpegCmd, { stdio: 'inherit' });

  if (fs.existsSync(OUTPUT_MP4)) {
    const stats = fs.statSync(OUTPUT_MP4);
    console.log(`[SUCCESS] Demo video successfully produced: ${OUTPUT_MP4} (${(stats.size / 1024 / 1024).toFixed(2)} MB)`);
  } else {
    throw new Error('FFmpeg failed to produce output MP4');
  }
}

recordDemo().catch((err) => {
  console.error('[-] Automation failed:', err);
  process.exit(1);
});
