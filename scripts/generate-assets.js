const sharp = require('sharp');
const path = require('path');

async function generateAssets() {
  const assetsDir = path.join(__dirname, '../assets');

  // Icon (1024x1024) - Blue background with white "NS" text
  const iconSvg = `
    <svg width="1024" height="1024" xmlns="http://www.w3.org/2000/svg">
      <rect width="1024" height="1024" fill="#2196F3"/>
      <text x="512" y="600" font-size="400" font-weight="bold" 
            text-anchor="middle" fill="white" font-family="Arial">NS</text>
    </svg>
  `;

  await sharp(Buffer.from(iconSvg))
    .png()
    .toFile(path.join(assetsDir, 'icon.png'));

  // Adaptive Icon (1024x1024) - Same as icon
  await sharp(Buffer.from(iconSvg))
    .png()
    .toFile(path.join(assetsDir, 'adaptive-icon.png'));

  // Splash Screen (1242x2436) - Blue background with white text
  const splashSvg = `
    <svg width="1242" height="2436" xmlns="http://www.w3.org/2000/svg">
      <rect width="1242" height="2436" fill="#2196F3"/>
      <text x="621" y="1100" font-size="120" font-weight="bold" 
            text-anchor="middle" fill="white" font-family="Arial">Network Stream</text>
      <text x="621" y="1250" font-size="80" 
            text-anchor="middle" fill="white" font-family="Arial">Viewer</text>
    </svg>
  `;

  await sharp(Buffer.from(splashSvg))
    .png()
    .toFile(path.join(assetsDir, 'splash.png'));

  // Favicon (32x32) - Small version
  const faviconSvg = `
    <svg width="32" height="32" xmlns="http://www.w3.org/2000/svg">
      <rect width="32" height="32" fill="#2196F3"/>
      <text x="16" y="24" font-size="20" font-weight="bold" 
            text-anchor="middle" fill="white" font-family="Arial">N</text>
    </svg>
  `;

  await sharp(Buffer.from(faviconSvg))
    .png()
    .toFile(path.join(assetsDir, 'favicon.png'));

  console.log('✅ All assets generated successfully!');
}

generateAssets().catch(console.error);
