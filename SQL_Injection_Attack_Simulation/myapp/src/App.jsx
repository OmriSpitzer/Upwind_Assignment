import { useState } from 'react'
import './App.css'
import axios from "axios"
const SERVER_URL = "http://localhost:8001"

function App() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [userData, setUserData] = useState(null)
  const [alert, setAlert] = useState(null)
  const [isSecure, setIsSecure] = useState(false)

  const initializeState = () => {
    setAlert(null)
    setUserData(null)
  }

  const isValid = () => {
    if (!username) {
      setAlert("Please fill in the username field")
      return false
    }
    if (!password) {
      setAlert("Please fill in the password field")
      return false
    }
    return true
  }

  const login = async () => {
    if (!isValid()) {
      setAlert("Please fill in the username and password fields")
      return
    }
    initializeState()

    try {
      const response = await axios.post(`${SERVER_URL}/login`, { username, password, isSecure })

      if (response.status === 200) {
        setUserData(response.data.userData)
      } else {
        setAlert("Error logging in")
      }
    } catch (error) {
      setAlert("Error logging in: " + error.message)
    }
  }
  return (
    <div className="h-screen w-full flex flex-col items-center justify-center">
      <div className="h-3/4 w-full flex flex-col items-center justify-start gap-10 rounded-md p-10 bg-gray-200 border-5 border-gray-400">
        <h1>SQL Injection Attack Simulation</h1>

        <div className="flex flex-col items-center justify-start gap-5">
          <div className="flex flex-row items-center justify-start gap-5">
            <h2>Username :</h2>
            <input type="text" placeholder="ex. user123" value={username} onChange={(e) => setUsername(e.target.value)} />

            <h2>Password :</h2>
            <input type="text" placeholder="ex. password123" value={password} onChange={(e) => setPassword(e.target.value)} />

            <button onClick={() => { initializeState(); setUsername(""); setPassword(""); }}>Reset</button>
          </div>



          <div className="flex flex-row items-center justify-start gap-4">
            <h2> Regular Login:</h2>
            <button onClick={login}>Login</button>
            <button onClick={() => setPassword("' OR '1'='1")}>SQL Injection</button>

            <h2>Secure:</h2>
            <button
              className={isSecure ? 'btn-secure' : 'btn-not-secure'}
              onClick={() => setIsSecure(!isSecure)}
            >
              {isSecure ? 'DB Secure' : 'DB Not Secure'}
            </button>
          </div>

          <p className='p-2 text-red-500'>{alert || ''}</p>

          <div className='flex flex-col w-full items-center justify-start gap-3'>
            <h1>Result</h1>

            <div className='w-full border-2 rounded-md p-2 flex flex-col items-start justify-start gap-2 overflow-y-auto'>
              {userData && userData.length > 0 ? (
                <div className='flex flex-row w-full justify-between'>
                  {userData.map((user, index) => (
                    <div className='flex flex-col gap-1' key={index}>
                      {Object.entries(user).map(([key, value]) => (
                        <div className='flex flex-row items-center justify-start gap-3' key={key}>
                          <span className='font-semibold'>{key}:</span>
                          <span>{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              ) : (
                <h2>No user data</h2>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
