import { useState } from "react"
import StartScreen from "./components/StartScreen"

export default function App() {
  const [username, setUsername] = useState(null)

  if (!username) {
    return <StartScreen onSubmit={setUsername} />
  }

  // placeholder — loading and results screens come next
  return <div>Searching for: {username}</div>
}