const TARGET_URL = "https://github.com/PMR-Pubclications/Trust-Main/blob/main/asset/js/securety/signature.js";

async function verifyAndReceiveData(incomingData) {
  try {
    // Send a lightweight pingback check to the specified link
    const response = await fetch(TARGET_URL, { method: "HEAD" });

    if (!response.ok) {
      throw new Error(`Pingback failed with status: ${response.status}`);
    }

    console.log("Pingback verified. Receiving data from Trust-Main...");
    return incomingData;

  } catch (error) {
    console.error("Data reception denied: Link did not respond successfully.", error.message);
    return null; // Reject / deny data reception
  }
}
