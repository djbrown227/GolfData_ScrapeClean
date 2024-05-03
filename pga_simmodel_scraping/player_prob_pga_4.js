// Import puppeteer-extra and the stealth plugin
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

const ExcelJS = require('exceljs');

function delay(time) {
    return new Promise(function(resolve) {
        setTimeout(resolve, time);
    });
}

// A helper function to add a random delay to mimic human behavior
async function humanDelay(min = 300, max = 1000) {
    const time = Math.floor(Math.random() * (max - min + 1)) + min;
    await delay(time);
}
async function scrapeGolfSite(url, outputFileName) {
    const browser = await puppeteer.launch({ headless: false }); // Consider running in headful mode for debugging
    const page = await browser.newPage();

    // Navigate to the new URL directly
    await page.goto(url);

    // Set navigation timeout to 60 seconds
    await page.setDefaultNavigationTimeout(2000);

    // Wait for the page and JavaScript to fully load
    //await page.waitForNavigation({ waitUntil: 'networkidle0' });

    // Scrape the data
    const playerData = await page.evaluate(() => {
        const data = [];
        const rows = document.querySelectorAll('.css-1qtrmek'); // Adjust this selector to match the actual rows in the table
        rows.forEach(row => {
            const nameElement = row.querySelector('.css-n0vuzw .chakra-text');
            const winPercentageElement = row.querySelectorAll('.css-l4z11p .chakra-text')[9];
            const probTop10Element = row.querySelectorAll('.css-l4z11p .chakra-text')[10];
            const probMakeCutElement = row.querySelector('.css-4lb9jb .css-1q3u2k7');

            const name = nameElement ? nameElement.innerText : null;
            const winPercentage = winPercentageElement ? winPercentageElement.innerText : null;
            const probTop10 = probTop10Element ? probTop10Element.innerText : null;
            const probMakeCut = probMakeCutElement ? probMakeCutElement.innerText : null;

            if (name) {
                data.push({ name, winPercentage, probTop10, probMakeCut });
            }
        });
        return data;
    });

    // Create an Excel file
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('PGA Tour Stats');

    worksheet.columns = [
        { header: 'Name', key: 'name', width: 30 },
        { header: 'Win%', key: 'winPercentage', width: 10 },
        { header: 'Prob Top 10', key: 'probTop10', width: 15 },
        { header: 'Prob Make Cut', key: 'probMakeCut', width: 15 },
    ];

     // Add data to worksheet
     playerData.forEach(player => {
        worksheet.addRow(player);
    });

    // Save the Excel file
    await workbook.xlsx.writeFile(outputFileName);
    console.log(`Excel file has been created at ${outputFileName}.`);

    // Close the browser
    await browser.close();
}

async function main() {
    try {
        const url = 'https://www.pgatour.com/leaderboard/probability';
        const outputFileName = '/Users/danielbrown/Desktop/Golf/data_playerprob/rbcheritage.xlsx';
        await scrapeGolfSite(url, outputFileName);
    } catch (error) {
        console.error('An error occurred:', error);
    }
}

main();