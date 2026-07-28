const { chromium } = require("playwright");
const sharp = require("sharp");
const fs = require("fs");

(async () => {
  const browser = await chromium.launch({
    headless: true
  });

  const page = await browser.newPage({
    viewport: {
      width: 1200,
      height: 900
    }
  });

  await page.goto(
    "https://dcdn.dstn.to/profile/1138159340923125863",
    {
      waitUntil: "networkidle"
    }
  );

  await page.screenshot({
    path: "profile.png"
  });

  const png = fs.readFileSync("profile.png").toString("base64");

  fs.writeFileSync(
    "discord-profile.svg",
    `
<svg xmlns="http://www.w3.org/2000/svg"
     width="1200"
     height="900">
  <image
    href="data:image/png;base64,${png}"
    width="1200"
    height="900"/>
</svg>`
  );

  await browser.close();
})();
