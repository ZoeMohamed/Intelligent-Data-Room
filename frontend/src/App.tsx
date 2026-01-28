import ChatContainer from "./components/ChatContainer"
import { AppStateProvider, useAppState } from "./context/AppState"

const ChatHistorySidebar = () => {
  const { sessions, activeSessionId, createNewChat, switchChat, deleteChat } = useAppState()
  const sortedSessions = [...sessions].sort((a, b) => b.updatedAt.localeCompare(a.updatedAt))

  return (
    <aside className="sticky top-6 hidden h-[calc(100vh-3rem)] w-72 flex-col gap-4 overflow-hidden rounded-[28px] border border-white/40 bg-white/55 p-4 shadow-[0_30px_70px_-45px_rgba(15,23,42,0.35)] backdrop-blur-2xl lg:flex">
      <div className="flex items-center gap-3">
        <img src="/logo.svg" alt="Intelligent Data Room logo" className="h-10 w-10 rounded-2xl" />
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-muted">IDR</p>
          <p className="text-sm font-semibold text-ink">Intelligent Data Room</p>
        </div>
      </div>
      <button
        type="button"
        onClick={createNewChat}
        className="rounded-full bg-accent px-4 py-2 text-xs font-semibold text-white shadow-glow transition hover:brightness-110"
      >
        + New chat
      </button>
      <div className="flex-1 space-y-2 overflow-y-auto pr-1">
        {sortedSessions.map((session) => {
          const isActive = session.id === activeSessionId
          return (
            <div
              key={session.id}
              className={`w-full rounded-2xl border px-3 py-2 text-left text-xs transition ${
                isActive
                  ? "border-accent/50 bg-white/85 text-ink shadow-soft"
                  : "border-white/40 bg-white/60 text-muted hover:border-accent/40 hover:text-ink"
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <button
                  type="button"
                  onClick={() => switchChat(session.id)}
                  className="flex-1 text-left"
                >
                  <div className="truncate text-sm font-semibold text-ink">{session.title}</div>
                  <div className="mt-1 text-[0.7rem] text-muted">
                    {new Date(session.updatedAt).toLocaleDateString()}
                  </div>
                </button>
                <button
                  type="button"
                  onClick={() => deleteChat(session.id)}
                  className="rounded-full border border-white/60 px-2 py-1 text-[0.65rem] font-semibold text-muted transition hover:border-red-200 hover:text-red-500"
                  aria-label="Delete chat"
                >
                  ×
                </button>
              </div>
            </div>
          )
        })}
      </div>
      <div className="text-[0.65rem] text-muted">History is stored locally on this device.</div>
    </aside>
  )
}

const AppShell = () => {
  const { createNewChat } = useAppState()

  return (
    <div className="h-screen text-ink">
      <main className="mx-auto flex h-screen w-full max-w-6xl gap-6 px-4 py-6 sm:px-6">
        <ChatHistorySidebar />
        <section className="flex min-h-0 flex-1 flex-col gap-4">
          <div className="flex items-center justify-between rounded-full border border-white/40 bg-white/60 px-4 py-2 text-xs text-muted shadow-soft backdrop-blur lg:hidden">
            <span className="font-semibold text-ink">Chats</span>
            <button
              type="button"
              onClick={createNewChat}
              className="rounded-full bg-accent px-3 py-1 text-xs font-semibold text-white shadow-glow"
            >
              + New chat
            </button>
          </div>
          <div className="min-h-0 flex-1">
            <ChatContainer />
          </div>
        </section>
      </main>
    </div>
  )
}

const App = () => {
  return (
    <AppStateProvider>
      <AppShell />
    </AppStateProvider>
  )
}

export default App
