import axios from 'axios';

// ================= USER CONFIGURATION =================
const F2POOL_API_KEY = 'stratum+tcp://btc-na.f2pool.com:1314'; // Replace with your F2Pool API key
const PAYOUT_ADDRESS = '3QnhndxFC1jYsuhHN5mG1nfq9h123daS4h'; // Replace with your cold storage or target BTC address
const PAYOUT_THRESHOLD = '0.05'; // Target threshold in BTC (minimum standard pool threshold is 0.001)
const CURRENCY = 'btc';
// ======================================================

const f2poolClient = axios.create({
  baseURL: 'https://api.f2pool.com/v2',
  headers: {
    'F2POOL-API-KEY': F2POOL_API_KEY,
    'Content-Type': 'application/json',
  },
});

/**
 * Updates the payout address for the specified asset.
 */
async function setPayoutAddress(currency, address) {
  try {
    const response = await f2poolClient.post('/assets/address', {
      currency: currency,
      address: address,
    });
    console.log(`[+] Payout address updated successfully:`, response.data);
    return true;
  } catch (error) {
    console.error(`[-] Failed to set payout address:`, error.response ? error.response.data : error.message);
    return false;
  }
}

/**
 * Sets the automatic payout threshold for the specified asset.
 */
async function setPayoutThreshold(currency, threshold) {
  try {
    const response = await f2poolClient.post('/assets/threshold', {
      currency: currency,
      threshold: threshold,
    });
    console.log(`[+] Payout threshold set to ${threshold} ${currency.toUpperCase()}:`, response.data);
    return true;
  } catch (error) {
    console.error(`[-] Failed to set payout threshold:`, error.response ? error.response.data : error.message);
    return false;
  }
}

async function configurePayoutSettings() {
  console.log(`Starting payout configuration for ${CURRENCY.toUpperCase()}...`);
  
  // 1. Update target wallet address
  const addressSuccess = await setPayoutAddress(CURRENCY, PAYOUT_ADDRESS);
  
  // 2. Set threshold to 0.05 BTC
  if (addressSuccess) {
    await setPayoutThreshold(CURRENCY, PAYOUT_THRESHOLD);
  }
}

configurePayoutSettings();
