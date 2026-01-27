import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import rehypeHighlight from "rehype-highlight"

const MarkdownRenderer = ({ content }: { content: string }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeHighlight]}
      components={{
        table: ({ ...props }) => (
          <div className="mt-3 overflow-x-auto rounded-2xl border border-border bg-panel p-3">
            <table className="w-full border-collapse text-xs text-ink" {...props} />
          </div>
        ),
        thead: ({ ...props }) => (
          <thead className="bg-surface text-[0.7rem] uppercase tracking-[0.12em] text-muted" {...props} />
        ),
        th: ({ ...props }) => (
          <th className="border-b border-border px-3 py-2 text-left font-semibold" {...props} />
        ),
        td: ({ ...props }) => (
          <td className="border-b border-border px-3 py-2 align-top" {...props} />
        ),
        tbody: ({ ...props }) => <tbody className="divide-y divide-border/60" {...props} />,
        pre: ({ ...props }) => (
          <pre className="mt-3 overflow-x-auto rounded-xl border border-border bg-surface p-4 text-xs text-ink" {...props} />
        ),
        code: ({ inline, className, children, ...props }) =>
          inline ? (
            <code className="rounded bg-accentSoft px-1 py-0.5 text-xs text-ink" {...props}>
              {children}
            </code>
          ) : (
            <code className={className} {...props}>
              {children}
            </code>
          )
      }}
    >
      {content}
    </ReactMarkdown>
  )
}

export default MarkdownRenderer
