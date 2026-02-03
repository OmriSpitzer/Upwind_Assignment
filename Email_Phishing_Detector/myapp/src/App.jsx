import { useState } from 'react'
import './App.css'
import axios from "axios"
const SERVER_URL = "http://localhost:8000"

function App() {
  const [textFile, setTextFile] = useState("");
  const [result, setResult] = useState(null);
  const [suspiciousWords, setSuspiciousWords] = useState([]);
  const [alert, setAlert] = useState(null);
  const [susPercentage, setSusPercentage] = useState(0);

  const initializeState = () => {
    setAlert(null)
    setResult(null)
    setSuspiciousWords([])
    setSusPercentage(0)
  }
  const checkMailPhishing = async (textFile) => {
    initializeState()
    if (!textFile) {
      setAlert("No text file inserted")
      return
    }
    try {
      const response = await axios.post(`${SERVER_URL}/checkMailPhishing`, { textFile });
      if (response.status === 200) {
        setResult(response.data.response)
        setSuspiciousWords(response.data.suspiciousWords)
        setSusPercentage(response.data.susPercentage)
      } else {
        setAlert("Error checking mail phishing")
      }
    } catch (error) {
      setAlert("Error checking mail phishing")
    }
  };

  const readTextFile = (file) => {
    initializeState()
    const reader = new FileReader()
    try {
      reader.onload = (e) => {
        setTextFile(e.target.result)
      }
      reader.readAsText(file)
    } catch (error) {
      console.error('Error reading text file:', error)
      setTextFile('Error reading text file')
    }
  }

  return (
    <div className="h-screen w-full flex flex-col items-center justify-center">
      <div className="h-3/4 w-full flex flex-col items-center justify-start gap-10 bg-gray-200 rounded-md p-10">
        <h1>Email Phishing Detector</h1>

        <div className="flex flex-row items-center justify-center gap-2">
          <h2>Insert text file</h2>
          <input
            type="file"
            className="border-2 bg-green-500 text-white rounded-md p-2"
            onChange={(e) => readTextFile(e.target.files[0])}

          />
          <button
            className="border-2 bg-green-500 text-white rounded-md p-2"
            onClick={() => checkMailPhishing(textFile)}
          >
            Check Email
          </button>
          {alert && <p className='border-2 rounded-md p-2 text-red-500'>{alert}</p>}
        </div>

        <div className='w-full flex flex-col items-center justify-start gap-3'>
          <h1>Inserted text file</h1>
          <p
            className='border-2 border-gray-300 rounded-md p-2 w-full overflow-y-auto text-lg bg-white'
            dangerouslySetInnerHTML={{ __html: result ? result : textFile || 'No text file inserted' }}
          />
        </div>

        <div className='flex flex-col items-center justify-start gap-3'>
          <h1>Result</h1>
          <p>Suspicious percentage: {susPercentage}%</p>
          <p>Is suspicious: {susPercentage > 50 ? 'Yes' : 'No'}</p>
          <p>Suspicious words: {suspiciousWords.join(', ')}</p>
        </div>
      </div>
    </div>
  )
}

export default App
