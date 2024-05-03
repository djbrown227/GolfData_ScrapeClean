const puppeteer = require('puppeteer');
const ExcelJS = require('exceljs');

function delay(time) {
    return new Promise(function(resolve) {
        setTimeout(resolve, time);
    });
}

async function scrapeGolfSite(url, outputFileName) {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    await page.goto(url);

    // Scrape event title and date
    const eventTitle = await page.$eval('.Leaderboard__Event__Title', el => el.innerText.trim());
    const eventDate = await page.$eval('.Leaderboard__Event__Date', el => el.innerText.trim());

    let playerData = [];
    const expandableRows = await page.$$('.PlayerRow__Overview--expandable');

    for (let i = 0; i < expandableRows.length; i++) {
        await expandableRows[i].click();
        await delay(1000);

        const playerName = await expandableRows[i].$eval('.AnchorLink.leaderboard_player_name', node => node.innerText.trim());
        const score = await expandableRows[i].$eval('.Table__TD:nth-child(4)', node => node.innerText.trim());

        let record = { playerName, score, pars: [], scores: [], dropdownValues: [] };

        const dropdownExists = await page.evaluate(() => {
            const dropdown = document.querySelector('.Scorecards__Dropdown .dropdown__select');
            return dropdown !== null;
        });

        if (dropdownExists) {
            const dropdownSelector = '.Scorecards__Dropdown .dropdown__select';
            await page.waitForSelector(dropdownSelector);
            const dropdownOptions = await page.$$eval(`${dropdownSelector} option`, options => options.map(option => option.value));

            for (const value of dropdownOptions) {
                await page.select(dropdownSelector, value);
                await delay(1000);

                const newPars = await page.evaluate(() => {
                    return Array.from(document.querySelectorAll('.Table__TR--sm.Table__even[data-idx="0"] .Table__TD .Scorecard__Score')).map(span => span.innerText.trim());
                });

                const newScores = await page.evaluate(() => {
                    return Array.from(document.querySelectorAll('.Table__TR--sm.Table__even[data-idx="1"] .Table__TD .Scorecard__Score')).map(span => span.innerText.trim());
                });

                record.dropdownValues.push(value);
                record.pars.push(newPars);
                record.scores.push(newScores);
            }
        }

        playerData.push(record);

        await expandableRows[i].click();
        await delay(1000);
    }

    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Golf Scores');

    // Add event information to the top of the sheet
    worksheet.addRow(['Event Title', eventTitle]);
    worksheet.addRow(['Event Date', eventDate]);
    worksheet.addRow([]); // Add an empty row for spacing

    // Add headers for player data
    worksheet.addRow(['Player Name', 'Score', 'Dropdown Value', 'Pars', 'Scores']);

    // Populate the worksheet with the scraped data
    playerData.forEach(player => {
        if (player.dropdownValues.length > 0) {
            player.dropdownValues.forEach((dropdownValue, index) => {
                worksheet.addRow([
                    player.playerName,
                    player.score,
                    dropdownValue,
                    player.pars[index].join(", "),
                    player.scores[index].join(", ")
                ]);
            });
        } else {
            worksheet.addRow([player.playerName, player.score, 'No additional data', 'No additional data', 'No additional data']);
        }
    });

    // Write to file
    await workbook.xlsx.writeFile(outputFileName);

    console.log(`Excel file has been created at ${outputFileName}.`);

    await browser.close();
}

async function main() {
    try {
        const site1 = 'https://www.espn.com/golf/leaderboard/_/tournamentId/401580344';
        const outputFile1 = '/Users/danielbrown/Desktop/Golf/data_holebyhole/tournament_golf_scores80.xlsx';
        await scrapeGolfSite(site1, outputFile1);

        await delay(10000); // Wait 10 seconds before starting the next scrape

        const site2 = 'https://www.espn.com/golf/leaderboard/_/tournamentId/401580346'; // Replace with the actual URL of the second site
        const outputFile2 = '/Users/danielbrown/Desktop/Golf/data_holebyhole/tournament_golf_scores81.xlsx';
        await scrapeGolfSite(site2, outputFile2);
    } catch (error) {
        console.error('An error occurred:', error);
    }
}

main();



