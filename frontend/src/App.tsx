import ChatContainer from "./components/ChatContainer"
import { AppStateProvider } from "./context/AppState"

const App = () => {
  return (
    <AppStateProvider>
      <div className="min-h-screen text-ink">
        <main className="mx-auto flex min-h-screen w-full max-w-4xl flex-col px-4 py-6 sm:px-6">
          <ChatContainer />
        </main>
      </div>
    </AppStateProvider>
  )
}

export default App
