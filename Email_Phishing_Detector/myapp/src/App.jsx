import { useState } from 'react'
import './App.css'
import axios from "axios"

// Server URL
const SERVER_URL = "http://localhost:8000"

/**
 * Main App component
 * @returns App component
 */
function App() {
  // State variables
  const [textFile, setTextFile] = useState("");                      // Text file given by the user
  const [result, setResult] = useState(null);                        // Text file with phishing detection marked
  const [suspiciousWords, setSuspiciousWords] = useState([]);        // Suspicious word list found in the text file
  const [alert, setAlert] = useState(null);                          // Alert message
  const [susPercentage, setSusPercentage] = useState(0);             // Suspicious percentage of the text file

  // Functions
  /**
   * Initialize state variables
   */
  const initializeState = () => {
    setAlert(null)
    setResult(null)
    setSuspiciousWords([])
    setSusPercentage(0)
  }

  /**
   * Check the mail phishing
   * @param {string} textFile - Text file given by the user
   * @returns void
   */
  const checkMailPhishing = async (textFile) => {
    initializeState()

    // Check if text file is inserted
    if (!textFile) {
      setAlert("No text file inserted")
      return
    }

    try {
      // Send the text file to the server for phishing detection
      const response = await axios.post(`${SERVER_URL}/checkMailPhishing`, { textFile });
      const data = response.data

      if (response.status === 200) {
        // Successfully received the response from the server
        setResult(data.response)
        setSuspiciousWords(data.suspiciousWords)
        setSusPercentage(data.susPercentage)
      } else {
        // Error received from the server
        setAlert(data.error)
      }
    } catch (error) {
      setAlert("Checking Error:" + error.message)
    }
  };

  /**
   * Read the text file
   * @param {File} file - Text file given by the user
   * @returns void
   */
  const readTextFile = (file) => {
    initializeState()

    // File reader object to read the text file
    const reader = new FileReader()

    try {
      // When the text file is read, set the text file to the state
      reader.onload = (e) => {
        setTextFile(e.target.result)
      }

      reader.readAsText(file)
    } catch (error) {
      // Error reading the text file
      setAlert("Reading Error:" + error.message)
    }
  }

  return (
    <div className="h-full w-full flex flex-col items-center justify-center">
      <div className="h-2/3 w-2/2 flex flex-col items-center justify-between gap-10 bg-white rounded-md p-10">
        {/* Title */}
        <h1>Email Phishing Detector</h1>

        {/* Text file input */}
        <div className="flex flex-row items-center justify-center gap-2">
          <h2>Insert text file</h2>

          <input
            type="file"
            className="border-2 bg-green-500 text-white rounded-md p-2"
            onChange={(e) => readTextFile(e.target.files[0])}

          />

          {/* Email phishing detection button */}
          <button
            className="border-2 bg-green-500 text-white rounded-md p-2"
            onClick={() => checkMailPhishing(textFile)}
          >
            Check Email
          </button>

          {/* Alert message */}
          {alert && <p className='border-2 rounded-md p-2 text-red-500'>{alert}</p>}
        </div>

        {/* Inserted text file */}
        <div className='w-full flex flex-col items-center justify-start gap-3'>
          <h1>Inserted text file</h1>

          {/* Result text file */}
          <p
            className='border-2 border-gray-300 rounded-md p-2 w-full overflow-y-auto text-lg bg-white'
            dangerouslySetInnerHTML={{ __html: result ? result : textFile || 'No text file inserted' }}
          />
        </div>

        {/* Result analysis */}
        <div className='flex flex-col items-center justify-start gap-3'>
          <h1>Result</h1>

          {/* Suspicious overview */}
          <div className='flex flex-col items-center justify-start gap-3 border-2 border-gray-300 rounded-md p-5'>
            <div className='flex flex-row items-center justify-start gap-15'>
              {/* Suspicious percentage */}
              <div className='flex flex-row gap-3'>
                <h2 className='underline'>Suspicious percentage:</h2>
                <p className='font-bold'>{susPercentage > 0 ? susPercentage : '--'}%</p>
              </div>

              {/* Is suspicious */}
              <div className='flex flex-row gap-3'>
                <h2 className='underline'>Is suspicious:</h2>
                <p className='font-bold'>{susPercentage > 0 ? (susPercentage > 50 ? 'Yes' : 'No') : '--'}</p>
              </div>
            </div>

            {/* Suspicious words */}
            <div className='flex flex-row gap-3'>
                <h2 className='underline'>Suspicious words:</h2>
                <p className='font-bold'>{suspiciousWords.length > 0 ? suspiciousWords.join(', ') : '--'}</p>
              </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
