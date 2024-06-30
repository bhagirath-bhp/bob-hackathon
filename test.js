const fs = require("node:fs");
const path = require("node:path");
const axios = require("axios");

async function test(filePath) {
  try {
    const fullPath = path.resolve(filePath); // Resolve the full path of the file
    const fileBuffer = fs.readFileSync(fullPath); // Read the file into a buffer
    const base64 = fileBuffer.toString("base64"); // Convert the buffer to a base64 string
    // Send the base64 string instead of the buffer object
    await axios
      .post("https://bob-hackathon.onrender.com/openai/process-docs", {
        buffer: base64,
      })
      .then(response => {
        console.log(
          "Successfully sent the file. Server response:",
          response.data
        );
      })
      .catch(error => {
        console.error("Failed to send the file:", error);
      });
  } catch (error) {
    console.error("Failed to process the file:", error);
  }
}

// Example usage with a file named 'test.pdf' in your main directory
const filePath = "./test.pdf"; // Adjust the path to where your file is located
test(filePath);
