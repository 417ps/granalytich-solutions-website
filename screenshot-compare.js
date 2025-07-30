const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function takeScreenshot() {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  // Set viewport size
  await page.setViewport({ width: 1400, height: 900 });
  
  // Navigate to the local HTML file
  const filePath = `file://${path.resolve(__dirname, 'index-v3.html')}`;
  await page.goto(filePath);
  
  // Wait for page to load
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Scroll to services section
  await page.evaluate(() => {
    const servicesGrid = document.querySelector('.services-grid');
    if (servicesGrid) {
      servicesGrid.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    // Additional scroll to ensure we see the parallelogram cards
    window.scrollBy(0, 300);
  });
  
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Take screenshot of services section with more height
  const servicesGrid = await page.$('.services-grid');
  if (servicesGrid) {
    const boundingBox = await servicesGrid.boundingBox();
    await page.screenshot({ 
      path: 'current-services-section.png',
      type: 'png',
      clip: {
        x: boundingBox.x,
        y: boundingBox.y - 50,
        width: boundingBox.width,
        height: boundingBox.height + 100  // Add extra height to capture text below
      }
    });
    console.log('✅ Screenshot saved as current-services-section.png');
  }
  
  // Take full page screenshot too
  await page.screenshot({ 
    path: 'current-full-page.png', 
    fullPage: true 
  });
  console.log('✅ Full page screenshot saved as current-full-page.png');
  
  await browser.close();
}

async function analyzeAndSuggestChanges() {
  console.log('\n📊 ANALYSIS:');
  console.log('Compare current-services-section.png with your inspiration image');
  console.log('\n🔍 What to check:');
  console.log('1. Parallelogram angle - should slant left');
  console.log('2. Text positioning - labels below cards');
  console.log('3. Card spacing and proportions');
  console.log('4. Main photo shape on left');
  console.log('5. Hover effects (yellow DETAILS stripe)');
  
  console.log('\n📸 Files created:');
  console.log('- current-services-section.png (services section only)');
  console.log('- current-full-page.png (full page)');
}

// Run the screenshot function
takeScreenshot()
  .then(() => analyzeAndSuggestChanges())
  .catch(console.error);