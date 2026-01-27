import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import rehypeHighlight from "rehype-highlight"

const MarkdownRenderer = ({ content }: { content: string }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeHighlight]}
      components={{
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
