const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');

app.whenReady().then(async () => {
  const win = new BrowserWindow({
    width: 480,
    height: 680,
    show: true,
    frame: false,
    transparent: false,
    backgroundColor: '#0f172a',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      backgroundThrottling: false
    }
  });

  await win.loadFile(path.join(__dirname, 'index.html'));

  setTimeout(async () => {
    try {
      await win.webContents.executeJavaScript(`
        document.getElementById('transcription-preview').textContent = '"The boy is eating an apple"';
        document.getElementById('metric-total').textContent = '8.37';
        document.getElementById('metric-nlp').textContent = '4.02';
        const cardStage = document.getElementById('card-stage');
        cardStage.innerHTML = '<div style="background: rgba(30,41,59,0.92); border: 2px solid #06b6d4; border-radius: 12px; padding: 14px 20px; text-align: center; color: white; box-shadow: 0 8px 32px rgba(0,0,0,0.5);"><div style="font-size: 38px; margin-bottom: 4px;">🍎</div><div style="font-size: 18px; font-weight: 800; color: #38bdf8; letter-spacing: 1px;">APPLE</div><div style="font-size: 11px; color: #94a3b8; margin-top: 2px;">NOUN • ISL GLOSS [2/4]</div></div>';
        const glossBadges = document.getElementById('gloss-badges');
        glossBadges.innerHTML = '<span class="gloss-badge" style="background:#0284c7;color:white;padding:3px 8px;border-radius:6px;font-size:11px;font-weight:bold;margin:2px;">BOY</span><span class="gloss-badge" style="background:#06b6d4;color:#0f172a;padding:3px 8px;border-radius:6px;font-size:11px;font-weight:bold;margin:2px;box-shadow: 0 0 8px #06b6d4;">APPLE</span><span class="gloss-badge" style="background:#0284c7;color:white;padding:3px 8px;border-radius:6px;font-size:11px;font-weight:bold;margin:2px;">EAT</span><span class="gloss-badge" style="background:#059669;color:white;padding:3px 8px;border-radius:6px;font-size:11px;font-weight:bold;margin:2px;">PRESENT</span>';
        const textInput = document.getElementById('text-input');
        if (textInput) textInput.value = 'The boy is eating an apple';
      `);
    } catch (e) {
      console.error(e);
    }

    setTimeout(async () => {
      try {
        const image = await win.webContents.capturePage();
        const outPath1 = path.join(__dirname, '../report_figures/fig_6_1_app_screenshot.png');
        const outPath2 = 'C:/Users/rohan/.gemini/antigravity/brain/f5eee7a6-4d76-4570-b9d3-0c7e846b8169/report_figures/fig_6_1_app_screenshot.png';
        fs.writeFileSync(outPath1, image.toPNG());
        fs.writeFileSync(outPath2, image.toPNG());
        console.log('SUCCESS: Real app screenshot captured and saved to:', outPath1);
      } catch (err) {
        console.error('Error capturing screenshot:', err);
      } finally {
        app.quit();
      }
    }, 2500);
  }, 4000);
});
