import { useState } from 'react'
import './App.css'
import axios from "axios"
const SERVER_URL = "http://localhost:8000"

function App() {
  const [textFile, setTextFile] = useState("");
  const [result, setResult] = useState(null);
  const [alert, setAlert] = useState(null);

  const checkMailPhishing = async (textFile) => {
    setAlert(null)
    setResult(null)
    if (!textFile) {
      setAlert("No text file inserted")
      return
    }
    try {
      const response = await axios.post(`${SERVER_URL}/checkMailPhishing`, { textFile });
      if (response.status === 200) {
        setResult(response.data.response)
      } else {
        setAlert("Error checking mail phishing")
      }
    } catch (error) {
      setAlert("Error checking mail phishing")
    }
  };

  const readTextFile = (file) => {
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
    <div className="flex flex-col items-center justify-center h-screen w-full">
      <div className="flex flex-col items-center justify-center gap-4 bg-gray-200 rounded-md p-20 w-full">
        <h1>Email Phishing Detector</h1>

        <div className="flex flex-row items-center justify-center gap-2">
          <h2>Insert text file</h2>
          <input
            type="file"
            className="border-2 bg-green-500 text-white rounded-md p-2"
            onChange={(e) => readTextFile(e.target.files[0])}

          />

        </div>

        <div className='flex flex-row items-center justify-center gap-2'>
          <button
            className="border-2 bg-green-500 text-white rounded-md p-2"
            onClick={() => checkMailPhishing(textFile)}
          >
            Check Email
          </button>
          {alert && <p className='border-2 rounded-md p-2 text-red-500'>{alert}</p>}
        </div>

        <div className='w-full h-full flex flex-col items-center justify-center gap-3'>
          <h1>Inserted text file</h1>
          <p 
            className='border-2 rounded-md p-2 w-full h-full'
            dangerouslySetInnerHTML={{ __html: result? result : textFile || 'No text file inserted' }}
          />
        </div>
      </div>
    </div>
  )
}

export default App
