import { useState } from 'react'
import './App.css'
import axios from "axios"

// Server URL
const SERVER_URL = "http://localhost:8001"

/**
 * App component
 * @returns {JSX.Element}
 */
function App() {
  // State variables
  const [username, setUsername] = useState("")        // Username input
  const [password, setPassword] = useState("")        // Password input
  const [userData, setUserData] = useState(null)      // Users retrieved from the database
  const [alert, setAlert] = useState(null)            // Alert message
  const [isSecure, setIsSecure] = useState(false)     // Flag if using secure mode

  // Functions
  /**
   * Initialize state variables
   */
  const initializeState = () => {
    setAlert(null)
    setUserData(null)
  }

  /**
   * Initialize input fields
   */
  const initializeInputs = () => {
    setUsername("")
    setPassword("")
  }

  /**
   * Empty validation check for username and password
   * @returns {boolean}
   */
  const isValid = () => {
    let isValid = true

    // Username check
    if (!username) {
      setAlert("Please fill in the username field")
      isValid = false
    }
    // Password check
    else if (!password) {
      setAlert("Please fill in the password field")
      isValid = false
    }

    return isValid
  }

  /**
   * Login function
   * @returns {void}
   */
  const login = async () => {
    // Validation check
    if (!isValid()) {
      setAlert("Please fill in the username and password fields")
      return
    }

    // Initialize state variables
    initializeState()

    try {
      // Send the login request to the server
      const response = await axios.post(`${SERVER_URL}/login`, { username, password, isSecure })

      if (response.status === 200) {
        // Successfully received the response from the server
        const userData = response.data.userData
        setUserData(userData)
        if (!userData?.length) {
          setAlert("User not found")
        }
      } else {
        // Error received from the server
        const error = response.data.response
        setAlert(error)
      }
    } catch (error) {
      // Error sending to the server
      setAlert("Error logging in: " + error.message)
    }
  }

  return (
    <div className="h-full w-full flex flex-col items-center justify-center">
      <div className="h-3/4 w-full flex flex-col items-center justify-start gap-10 rounded-md p-10 bg-gray-200 border-5 border-gray-400">
        {/* Title */}
        <h1>SQL Injection Attack Simulation</h1>

        <div className="flex flex-col items-center justify-start gap-5">
          {/* Username and password input */}
          <div className="flex flex-row items-center justify-start gap-5">
            {/* Username input */}
            <h2>Username :</h2>
            <input type="text" placeholder="ex. user123" value={username} onChange={(e) => setUsername(e.target.value)} />

            {/* Password input */}
            <h2>Password :</h2>
            <input type="text" placeholder="ex. password123" value={password} onChange={(e) => setPassword(e.target.value)} />

            {/* Reset button */}
            <button onClick={() => { initializeState(); initializeInputs(); }}>Reset</button>
          </div>

          {/* Login options */}
          <div className="flex flex-row items-center justify-start gap-4">
            {/* Regular login button */}
            <h2> Regular Login:</h2>
            <button onClick={login}>Login</button>

            {/* SQL Injection button */}
            <button onClick={() => setPassword("' OR '1'='1")}>SQL Injection</button>

            {/* Secure mode toggle button */}
            <h2>Secure:</h2>
            <button
              className={isSecure ? 'btn-secure' : 'btn-not-secure'}
              onClick={() => setIsSecure(!isSecure)}
            >
              {isSecure ? 'DB Secure' : 'DB Not Secure'}
            </button>
          </div>

          {/* Alert message */}
          <p className='p-2 text-red-500'>{alert || ''}</p>

          {/* Result output box */}
          <div className='flex flex-col w-full items-center justify-start gap-3'>
            <h1>Result</h1>

            {/* Result output */}
            <div className='w-full border-2 rounded-md p-2 flex flex-col items-start justify-start gap-2 overflow-y-auto'>
              {userData && userData.length > 0 ? (
                <div className='grid grid-cols-2 w-full gap-3'>
                  {/* User data */}
                  {userData.map((user, index) => (
                    <div className='flex flex-col w-full gap-1 border-b-10 border-gray-300 rounded-md pb-2' key={index}>
                      {Object.entries(user).map(([key, value]) => (
                        // User details
                        <div className='flex flex-row items-center justify-start gap-3' key={key}>
                          <span className='font-semibold'>{key}:</span>
                          <span>{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              ) : (
                // No user data received
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
