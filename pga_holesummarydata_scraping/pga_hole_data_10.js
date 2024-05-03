const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const ExcelJS = require('exceljs');

puppeteer.use(StealthPlugin());

async function delay(time) {
    return new Promise(function(resolve) {
        setTimeout(resolve, time);
    });
}

async function humanDelay(min = 300, max = 1000) {
    const time = Math.floor(Math.random() * (max - min + 1)) + min;
    await delay(time);
}

async function scrapePGAStats(url, outputFileName) {
    const browser = await puppeteer.launch({ 
        headless: true,
        timeout: 0, // Set to 0 for unlimited timeout
        args: ['--no-sandbox', '--disable-setuid-sandbox'], // Add any necessary args
    });
    const page = await browser.newPage();
    const playerData = [];

    await page.goto(url);
    await page.setDefaultNavigationTimeout(60000);

    const dropdownAIndexes = ['0', '1', '2', '3', '4','5','6','7','8','9','10']; // Specify Dropdown A indexes here
    const dropdownBIndexes = ['0', '1', '2', '3', '4']; // Dropdown B indexes

    for (const dropdownAIndex of dropdownAIndexes) {
        for (const dropdownBIndex of dropdownBIndexes) {
            await scrapeDataForDropdown(page, dropdownAIndex, dropdownBIndex, playerData);
        }
    }

    // Create and save the Excel file after collecting all data
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('PGA Tour Stats');

    worksheet.columns = [
        { header: 'Dropdown A Index', key: 'dropdownAIndex', width: 15 },
        { header: 'Dropdown B Index', key: 'dropdownBIndex', width: 15 },
        { header: 'Course', key: 'name', width: 30 },
        { header: 'Hole', key: 'hole', width: 10 },
        { header: 'Yards', key: 'yards', width: 15 },
        { header: 'AVG', key: 'avg', width: 15 },
        { header: 'plus_minus', key: 'plus_minus', width: 15 },
        { header: 'Eagle', key: 'eagle', width: 15 },
        { header: 'Birdie', key: 'birdie', width: 15 },
        { header: 'Par', key: 'par', width: 15 },
        { header: 'Bogey', key: 'bogey', width: 15 },
        { header: 'DBL Bogey', key: 'dbl_bogey', width: 15 },
        { header: 'DBL Bogey Plus', key: 'dbl_bogey_plus', width: 15 },
    ];

    playerData.forEach(player => {
        worksheet.addRow(player);
    });

    await workbook.xlsx.writeFile(outputFileName);
    console.log(`Excel file has been created at ${outputFileName}.`);

    await browser.close();
}

async function scrapeDataForDropdown(page, dropdownAIndex, dropdownBIndex, playerData) {
    console.log(`Clicking dropdown button for A index ${dropdownAIndex}`);
    await page.click('button.chakra-menu__menu-button.css-1hhxxpx:nth-of-type(1)');
    await delay(8000); // Increasing delay to 4 seconds for better reliability;

    console.log(`Clicking dropdown button for A index ${dropdownAIndex} and B index ${dropdownBIndex}`);
    await page.$$eval(`button[data-index="${dropdownAIndex}"]`, buttons => buttons[0].click());
    await delay(8000); // Increasing delay to 4 seconds for better reliability;

    console.log(`Clicking dropdown button for B index ${dropdownBIndex}`);
    await page.$$eval(`button[data-index="${dropdownBIndex}"]`, buttons => buttons.forEach(button => button.click()));
    await delay(8000); // Increasing delay to 4 seconds for better reliability;

    // Extract data after each dropdown selection
    const data = await page.evaluate((dropdownAIndex, dropdownBIndex) => {
        const rows = document.querySelectorAll('.css-79elbk');
        return Array.from(rows, row => {
            const name = row.querySelector('.css-1tt9zko p')?.innerText;
            const hole = row.querySelectorAll('.css-yiy6zj')[0]?.innerText;
            const yards = row.querySelectorAll('.css-yiy6zj')[1]?.innerText;
            const avg = row.querySelectorAll('.css-yiy6zj')[2]?.innerText;
            const plus_minus = row.querySelectorAll('.css-yiy6zj')[3]?.innerText;
            const eagle = row.querySelectorAll('.css-yiy6zj')[4]?.innerText;
            const birdie = row.querySelectorAll('.css-yiy6zj')[5]?.innerText;
            const par = row.querySelectorAll('.css-yiy6zj')[6]?.innerText;
            const bogey = row.querySelectorAll('.css-yiy6zj')[7]?.innerText;
            const dbl_bogey = row.querySelectorAll('.css-yiy6zj')[8]?.innerText;
            const dbl_bogey_plus = row.querySelectorAll('.css-yiy6zj')[9]?.innerText;
            return { 
                dropdownAIndex, 
                dropdownBIndex,
                name, 
                hole, 
                yards, 
                avg, 
                plus_minus, 
                eagle, 
                birdie, 
                par, 
                bogey, 
                dbl_bogey, 
                dbl_bogey_plus 
            };
        }).filter(player => player.name);
    }, dropdownAIndex, dropdownBIndex);

    playerData.push(...data);
    console.log(`Data collected for dropdown A index ${dropdownAIndex} and dropdown B index ${dropdownBIndex}`);
}

async function main() {
    try {
        const url = 'https://www.pgatour.com/stats/course/toughest-holes';
        const outputFileName = '/Users/danielbrown/Desktop/Golf/data_holesummary/toughest_holes_2.xlsx';
        await scrapePGAStats(url, outputFileName);
    } catch (error) {
        console.error('An error occurred:', error);
    }
}

main();
