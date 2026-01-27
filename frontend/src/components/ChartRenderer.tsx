import Plot from "react-plotly.js"
import type { Config, Layout, PlotData, Frame } from "plotly.js"

type PlotlyFigure = {
  data?: PlotData[]
  layout?: Partial<Layout>
  frames?: Frame[]
  config?: Partial<Config>
}

const ChartRenderer = ({ figure }: { figure?: PlotlyFigure | null }) => {
  if (!figure || !figure.data) return null

  return (
    <div className="mt-4 rounded-2xl border border-border bg-panel p-3">
      <Plot
        data={figure.data}
        layout={{
          ...(figure.layout ?? {}),
          autosize: true,
          margin: { l: 40, r: 20, t: 40, b: 40, ...(figure.layout?.margin ?? {}) }
        }}
        frames={figure.frames}
        config={{ responsive: true, displayModeBar: false, ...(figure.config ?? {}) }}
        style={{ width: "100%", height: "100%" }}
        useResizeHandler
      />
    </div>
  )
}

export default ChartRenderer
