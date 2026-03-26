import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { SiteHeader } from "../components/SiteHeader";
import "../styles/console.css";

type HealthResponse = {
  status: string;
  initialized: boolean;
  paths: {
    model_dir: string;
    vector_store_dir: string;
  };
};

type SearchResult = {
  rank: number;
  score: number;
  confidence: number;
  content: string;
  source: string;
  metadata: Record<string, string>;
};

type SearchResponse = {
  query: string;
  top_k: number;
  results: SearchResult[];
  paths: {
    model_dir: string;
    vector_store_dir: string;
  };
};

const API_BASE = "/api";
const TOP_K_PRESETS = [3, 5, 8, 10];

function formatPercent(value: number) {
  return `${(value * 100).toFixed(2)}%`;
}

function getMetadataEntries(metadata: Record<string, string>) {
  return Object.entries(metadata).filter(([, value]) => String(value).trim());
}

function getPrimaryMetadataEntry(metadata: Record<string, string>) {
  return getMetadataEntries(metadata)[0];
}

function formatMetadata(metadata: Record<string, string>) {
  const entries = getMetadataEntries(metadata);
  if (!entries.length) {
    return "\u65e0\u9644\u52a0\u5b57\u6bb5";
  }
  return entries.map(([key, value]) => `${key}: ${value}`).join("\n\n");
}

export function ConsolePage() {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [activeResult, setActiveResult] = useState<SearchResult | null>(null);
  const [loadingHealth, setLoadingHealth] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState("");
  const [lastQuery, setLastQuery] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function fetchHealth() {
      setLoadingHealth(true);
      try {
        const response = await fetch(`${API_BASE}/health`);
        const data: HealthResponse = await response.json();
        if (!response.ok) {
          throw new Error("\u670d\u52a1\u72b6\u6001\u68c0\u67e5\u5931\u8d25");
        }
        if (!cancelled) {
          setHealth(data);
        }
      } catch (fetchError) {
        if (!cancelled) {
          setError(fetchError instanceof Error ? fetchError.message : "\u670d\u52a1\u4e0d\u53ef\u7528");
        }
      } finally {
        if (!cancelled) {
          setLoadingHealth(false);
        }
      }
    }

    void fetchHealth();
    return () => {
      cancelled = true;
    };
  }, []);

  const confidenceAverage = useMemo(() => {
    if (!results.length) {
      return 0;
    }
    return results.reduce((sum, item) => sum + item.confidence, 0) / results.length;
  }, [results]);

  const highestConfidence = useMemo(() => {
    if (!results.length) {
      return 0;
    }
    return Math.max(...results.map((item) => item.confidence));
  }, [results]);

  const primaryMetadataEntry = activeResult ? getPrimaryMetadataEntry(activeResult.metadata) : undefined;
  const primaryMetadataValue = primaryMetadataEntry?.[1] ?? "";
  const secondaryMetadata = activeResult
    ? Object.fromEntries(
        getMetadataEntries(activeResult.metadata).filter(([key]) => key !== primaryMetadataEntry?.[0]),
      )
    : {};

  const serviceState = loadingHealth ? "\u68c0\u6d4b\u4e2d" : health?.status === "ok" ? "ONLINE" : "OFFLINE";
  const serviceTone = loadingHealth ? "is-syncing" : health?.status === "ok" ? "is-online" : "is-offline";
  const serviceHint = health?.initialized
    ? "\u7d22\u5f15\u5df2\u5c31\u7eea"
    : "\u7b49\u5f85\u9996\u6b21\u68c0\u7d22\u52a0\u8f7d";

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) {
      setError("\u8bf7\u8f93\u5165\u68c0\u7d22\u5185\u5bb9");
      return;
    }

    setSearching(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE}/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: trimmed,
          topK,
        }),
      });
      const data: SearchResponse | { error: string } = await response.json();
      if (!response.ok || "error" in data) {
        throw new Error("error" in data ? data.error : "\u68c0\u7d22\u5931\u8d25");
      }

      setResults(data.results);
      setActiveResult(data.results[0] ?? null);
      setHealth((current) =>
        current
          ? { ...current, initialized: true, paths: data.paths }
          : { initialized: true, paths: data.paths, status: "ok" },
      );
      setLastQuery(data.query);
    } catch (searchError) {
      setError(searchError instanceof Error ? searchError.message : "\u68c0\u7d22\u5931\u8d25");
      setResults([]);
      setActiveResult(null);
    } finally {
      setSearching(false);
    }
  }

  return (
    <main className="console-shell">
      <SiteHeader rightSlot={<Link to="/">{ "\u9996\u9875" }</Link>} />

      <section className="dashboard">
        <section className="hero-panel glass">
          <div className="hero-copy">
            <p className="eyebrow">Neural Retrieval Interface</p>
            <h1>{"\u5411\u91cf\u5e93\u68c0\u7d22\u5b9e\u9a8c\u63a7\u5236\u53f0"}</h1>
            <p className="hero-text">
              {
                "FAISS \u4e0e\u672c\u5730\u4e2d\u6587\u5d4c\u5165\u6a21\u578b\u9a71\u52a8\u7684\u68c0\u7d22\u5b9e\u9a8c\u754c\u9762\uff0c\u7528\u4e8e\u5feb\u901f\u9a8c\u8bc1\u67e5\u8be2\u3001\u7ed3\u679c\u547d\u4e2d\u548c\u9644\u52a0\u5143\u6570\u636e\u5c55\u793a\u3002"
              }
            </p>
          </div>

          <div className="hero-metrics">
            <article className={`metric-card service-card ${serviceTone}`}>
              <div className="service-card-top">
                <span>{"\u670d\u52a1\u72b6\u6001"}</span>
                <i className="service-dot" aria-hidden="true" />
              </div>
              <strong>{serviceState}</strong>
              <div className="service-card-footer">
                <small>{serviceHint}</small>
              </div>
            </article>
            <article className="metric-card metric-card-flow">
              <span>{"\u8fd4\u56de\u6761\u6570"}</span>
              <strong>{results.length.toString().padStart(2, "0")}</strong>
              <small>Top K = {topK}</small>
              <div className="metric-orbit" aria-hidden="true" />
            </article>
            <article className="metric-card metric-card-signal">
              <span>{"\u5e73\u5747\u7f6e\u4fe1\u5ea6"}</span>
              <strong>{formatPercent(confidenceAverage || 0)}</strong>
              <small>{"\u6700\u9ad8\u503c"} {formatPercent(highestConfidence || 0)}</small>
              <div className="metric-orbit" aria-hidden="true" />
            </article>
          </div>
        </section>

        <section className="control-panel glass">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Search Input</p>
              <h2>{"\u68c0\u7d22\u5165\u53e3"}</h2>
            </div>
          </div>

          <div className="control-upper">
            <form className="search-form" onSubmit={handleSubmit}>
              <label className="search-field">
                <span>Query</span>
                <input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder={
                    "\u4f8b\u5982\uff1a\u8bbe\u5907\u5f02\u5e38\u544a\u8b66\u3001\u8d28\u91cf\u8ffd\u6eaf\u3001\u5de5\u827a\u53c2\u6570"
                  }
                />
              </label>

              <div className="preset-group">
                <span>Top K Presets</span>
                <div className="preset-row">
                  {TOP_K_PRESETS.map((preset) => (
                    <button
                      key={preset}
                      className={preset === topK ? "preset is-active" : "preset"}
                      type="button"
                      onClick={() => setTopK(preset)}
                    >
                      {preset}
                    </button>
                  ))}
                </div>
              </div>

              <label className="slider-field">
                <span>Precision Window</span>
                <div className="slider-row">
                  <input
                    type="range"
                    min={1}
                    max={12}
                    value={topK}
                    onChange={(event) => setTopK(Number(event.target.value))}
                  />
                  <strong>{topK}</strong>
                </div>
              </label>

              <div className="action-row">
                <button className="primary-btn" type="submit" disabled={searching}>
                  {searching ? "\u68c0\u7d22\u4e2d..." : "\u542f\u52a8\u68c0\u7d22"}
                </button>
                <button
                  className="ghost-btn"
                  type="button"
                  onClick={() => {
                    setQuery("");
                    setResults([]);
                    setActiveResult(null);
                    setError("");
                  }}
                >
                  {"\u6e05\u7a7a\u9762\u677f"}
                </button>
              </div>
            </form>

            <aside className="detail-block detail-block-glow control-preview">
              <span className="control-preview-title">{"\u68c0\u7d22\u7ed3\u679c"}</span>
              <p>{primaryMetadataValue || "\u5f85\u68c0\u7d22"}</p>
            </aside>
          </div>

          <div className="control-stack">

            <div className="control-metrics">
              <article className="micro-card">
                <span>Engine</span>
                <strong>{loadingHealth ? "SYNC" : health?.status === "ok" ? "READY" : "DOWN"}</strong>
              </article>
              <article className="micro-card">
                <span>Index</span>
                <strong>{health?.initialized ? "ARMED" : "STANDBY"}</strong>
              </article>
            </div>

            <div className="path-grid">
              <article className="path-card">
                <span>MODEL_DIR</span>
                <p>{health?.paths.model_dir ?? "\u7b49\u5f85\u8fde\u63a5\u540e\u663e\u793a"}</p>
              </article>
              <article className="path-card">
                <span>VECTOR_STORE</span>
                <p>{health?.paths.vector_store_dir ?? "\u7b49\u5f85\u8fde\u63a5\u540e\u663e\u793a"}</p>
              </article>
            </div>
          </div>

          {error ? <div className="error-banner">{error}</div> : null}
        </section>

        <section className="results-panel glass">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Result Stream</p>
              <h2>{"\u547d\u4e2d\u7ed3\u679c"}</h2>
            </div>
          </div>

          <div className="results-topline results-topline-primary">
            <article className="signal-chip">
              <span>Live Query</span>
              <strong>{lastQuery || "Waiting"}</strong>
            </article>
            <article className="signal-chip">
              <span>Hits</span>
              <strong>{results.length}</strong>
            </article>
            <article className="signal-chip">
              <span>Peak</span>
              <strong>{formatPercent(highestConfidence || 0)}</strong>
            </article>
          </div>

          <div className="results-topline results-topline-secondary">
            <article className="signal-chip signal-chip-detail">
              <span>{"\u6765\u6e90"}</span>
              <strong>{activeResult?.source ?? "--"}</strong>
            </article>
            <article className="signal-chip signal-chip-detail">
              <span>{"\u539f\u59cb\u5206\u6570"}</span>
              <strong>{activeResult ? activeResult.score.toFixed(8) : "--"}</strong>
            </article>
            <article className="signal-chip signal-chip-detail">
              <span>{"\u7f6e\u4fe1\u5ea6"}</span>
              <strong>{activeResult ? formatPercent(activeResult.confidence) : "--"}</strong>
            </article>
          </div>

          <div className="results-layout">
            <div className="result-list">
              <p className="eyebrow results-column-title">Result List</p>
              <p className="detail-term">{"\u8bcd\u6761"}</p>
              {results.length ? (
                results.map((result) => (
                  <button
                    key={`${result.rank}-${result.source}`}
                    className={activeResult?.rank === result.rank ? "result-card is-active" : "result-card"}
                    type="button"
                    onClick={() => setActiveResult(result)}
                  >
                    <div className="result-card-header">
                      <span className="result-rank">#{result.rank}</span>
                      <span className="result-confidence">{formatPercent(result.confidence)}</span>
                    </div>
                    <p>{result.content}</p>
                    <small>{result.source || "unknown source"}</small>
                  </button>
                ))
              ) : (
                <div className="empty-state">
                  <span>{"\u7b49\u5f85\u68c0\u7d22"}</span>
                  <p>
                    {
                      "\u8f93\u5165\u5173\u952e\u8bcd\u5e76\u542f\u52a8\u68c0\u7d22\u540e\uff0c\u7ed3\u679c\u4f1a\u4ee5\u9ad8\u4eae\u5361\u7247\u6d41\u7684\u65b9\u5f0f\u663e\u793a\u5728\u8fd9\u91cc\u3002"
                    }
                  </p>
                </div>
              )}
            </div>

            <aside className="detail-panel">
              <p className="eyebrow">Signal Detail</p>
              <h3>
                {activeResult ? `\u7ed3\u679c #${activeResult.rank}` : "\u5c1a\u672a\u9009\u4e2d\u7ed3\u679c"}
              </h3>
              <div className="detail-block detail-block-glow">
                <span>{"\u5173\u8054\u5185\u5bb9"}</span>
                <p>{primaryMetadataValue || "\u5f85\u68c0\u7d22"}</p>
              </div>
              <div className="detail-block detail-block-wide">
                <span>{"\u9644\u52a0\u5b57\u6bb5"}</span>
                <p>{activeResult ? formatMetadata(secondaryMetadata) : "--"}</p>
              </div>
            </aside>
          </div>
        </section>
      </section>
    </main>
  );
}
