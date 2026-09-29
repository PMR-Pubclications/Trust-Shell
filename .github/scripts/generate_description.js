const fs = require('fs');
const https = require('https');

async function generateCommitSummary() {
  const diffPath = 'diff.patch';
  
  if (!fs.existsSync(diffPath)) {
    console.log('No patch file found.');
    return;
  }

  const diffContent = fs.readFileSync(diffPath, 'utf8');

  // Truncate diff if it's excessively large to avoid context limit issues
  const maxDiffLength = 6000;
  const truncatedDiff = diffContent.length > maxDiffLength 
    ? diffContent.substring(0, maxDiffLength) + '\n...[Diff Truncated]' 
    : diffContent;

  const prompt = `Analyze the following git diff and write a clear, concise commit message heading and detailed summary of changes:\n\n${truncatedDiff}`;

  const payload = JSON.stringify({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: "You are a professional software engineer summarizing code changes for git commits." },
      { role: "user", content: prompt }
    ],
    max_tokens: 250
  });

  const options = {
    hostname: 'api.openai.com',
    path: '/v1/chat/completions',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
      'Content-Length': Buffer.byteLength(payload)
    }
  };

  const req = https.request(options, (res) => {
    let data = '';
    res.on('data', (chunk) => data += chunk);
    res.on('end', () => {
      try {
        const response = JSON.parse(data);
        const description = response.choices[0].message.content.trim();
        console.log('Generated Summary:\n', description);

        fs.writeFileSync('.github/commit_summary.txt', description);
      } catch (err) {
        console.error('Failed to parse API response:', err.message);
      }
    });
  });

  req.on('error', (e) => console.error('API Request Error:', e));
  req.write(payload);
  req.end();
}

generateCommitSummary();
