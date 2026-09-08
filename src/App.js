import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";

const API = "http://127.0.0.1:8000";

const LAYER_INFO = {
  math:       { label: "Math Engine",      color: "#F59E0B", icon: "🧮", layer: "0A", cost: "FREE (~1ms)" },
  greeting:   { label: "Greetings",        color: "#10B981", icon: "👋", layer: "0A", cost: "FREE (~1ms)" },
  conversion: { label: "Unit Converter",   color: "#10B981", icon: "📏", layer: "0A", cost: "FREE (~1ms)" },
  facts:      { label: "Facts Database",   color: "#10B981", icon: "📚", layer: "0A", cost: "FREE (~1ms)" },
  wikipedia:  { label: "Wikipedia",        color: "#3B82F6", icon: "🌐", layer: "0B", cost: "FREE (~500ms)" },
  duckduckgo: { label: "DuckDuckGo",       color: "#3B82F6", icon: "🦆", layer: "0B", cost: "FREE (~800ms)" },
  tinyml:     { label: "TinyML Classifier",color: "#8B5CF6", icon: "⚡", layer: "1",  cost: "FREE (~2ms)" },
  cache:      { label: "MinHash LSH Cache",color: "#EC4899", icon: "💾", layer: "2",  cost: "FREE (~1ms)" },
  embedder:   { label: "Semantic Embedder",color: "#06B6D4", icon: "🔢", layer: "3",  cost: "FREE (~50ms)" },
  ensemble:   { label: "Ensemble ML (α)",  color: "#F97316", icon: "🤖", layer: "4",  cost: "FREE (~400ms)" },
  groq:       { label: "Groq (Paid)",      color: "#EF4444", icon: "🧠", layer: "5",  cost: "PAID (~900ms)" },
  gemini:     { label: "Gemini (Paid)",    color: "#EF4444", icon: "✨", layer: "5",  cost: "PAID (~1200ms)" },
  gpt4:       { label: "LLM Fallback",     color: "#EF4444", icon: "🧠", layer: "5",  cost: "PAID (~1000ms)" },
  unknown:    { label: "Unknown Router",   color: "#6B7280", icon: "❓", layer: "?",  cost: "N/A" },
};

const LAYERS = [
  { id: "0A", label: "Query Handler", desc: "Math, Greetings, Units, Facts", color: "#F59E0B", icon: "🧮", speed: "~1ms", cost: "FREE" },
  { id: "0B", label: "General Knowledge", desc: "Wikipedia & DuckDuckGo", color: "#3B82F6", icon: "🌐", speed: "~500ms", cost: "FREE" },
  { id: "1",  label: "TinyML", desc: "Keyword Domain Matching", color: "#8B5CF6", icon: "⚡", speed: "~2ms", cost: "FREE" },
  { id: "2",  label: "MinHash Cache", desc: "LSH Near-Duplicate Detection", color: "#EC4899", icon: "💾", speed: "~1ms", cost: "FREE" },
  { id: "3",  label: "Embedder", desc: "MiniLM-L6 Semantic Match", color: "#06B6D4", icon: "🔢", speed: "~50ms", cost: "FREE" },
  { id: "4",  label: "Ensemble ML", desc: "LogReg + LGBM + MLP (α-Aware)", color: "#F97316", icon: "🤖", speed: "~400ms", cost: "FREE" },
  { id: "5",  label: "LLM Inference", desc: "Groq / Gemini Inbuilt", color: "#EF4444", icon: "🧠", speed: "~1000ms", cost: "PAID 💰" },
];

const LLM_PROVIDERS = [
  { id: "auto",   label: "Auto (Smart Selector)", badge: "⚡ Intelligent Model Dispatch", placeholder: "Automatically picks best model (Groq vs Gemini)" },
  { id: "groq",   label: "Groq (Inbuilt)",        badge: "⚡ Inbuilt Key Active",           placeholder: "Using built-in Groq key (Fast)" },
  { id: "gemini", label: "Gemini (Inbuilt)",      badge: "✨ Inbuilt Key Active",           placeholder: "Using built-in Gemini key (Deep Reasoning)" },
  { id: "openai", label: "OpenAI (Custom)",       badge: "Custom Key Required",             placeholder: "sk-..." },
];

const SAMPLE_QUERIES = [
  { text: "what is sinx/cosx", layer: "0A", label: "Math (Layer 0A)" },
  { text: "who was Marie Curie", layer: "0B", label: "Wikipedia (Layer 0B)" },
  { text: "where is my package", layer: "2", label: "MinHash Cache (Layer 2)" },
  { text: "i want a refund for my item", layer: "1", label: "TinyML (Layer 1)" },
  { text: "cancel my subscription plan immediately", layer: "4", label: "Ensemble (Layer 4)" },
  { text: "write a python binary search function", layer: "5", label: "Code Auto (Layer 5)" },
  { text: "Explain quantum superposition in detail with examples", layer: "5", label: "Deep Dive Auto (Layer 5)" },
];

// ── ORBITAL LOGO ───────────────────────────────────────────────
function OrbitalLogo({ size = 40, animating = false }) {
  return (
    <svg width={size} height={size} viewBox="0 0 100 100">
      <defs>
        <radialGradient id="sunG2" cx="40%" cy="35%" r="60%">
          <stop offset="0%" stopColor="#ffffff"/>
          <stop offset="40%" stopColor="#FEF08A"/>
          <stop offset="100%" stopColor="#F59E0B"/>
        </radialGradient>
      </defs>
      <ellipse cx="50" cy="50" rx="45" ry="14" fill="none"
        stroke="#ffffff" strokeWidth="1" opacity="0.2"
        transform="rotate(-15 50 50)"/>
      <ellipse cx="50" cy="50" rx="34" ry="10" fill="none"
        stroke="#ffffff" strokeWidth="1.5" opacity="0.45"
        transform="rotate(-15 50 50)"/>
      <motion.ellipse cx="50" cy="50" rx="22" ry="7" fill="none"
        stroke="#F59E0B" strokeWidth="2.5" opacity="0.9"
        transform="rotate(-15 50 50)"
        animate={animating ? { opacity:[0.9,1,0.9] } : {}}
        transition={{ duration: 0.8, repeat: Infinity }}/>
      <circle cx="50" cy="50" r="14" fill="#0f1e38"/>
      <circle cx="50" cy="50" r="10" fill="#1e3050"/>
      <circle cx="50" cy="50" r="7"  fill="#B45309"/>
      <circle cx="50" cy="50" r="6"  fill="#F59E0B"/>
      <circle cx="50" cy="50" r="4"  fill="url(#sunG2)"/>
      <circle cx="47" cy="47" r="1.5" fill="#ffffff" opacity="0.9"/>
      <motion.circle cx="72" cy="42" r="3.5" fill="#ffffff" opacity="0.9"
        animate={animating ? { cx:[72,50,28,50,72], cy:[42,35,42,55,42] } : {}}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}/>
    </svg>
  );
}

// ── CANVAS STARS ───────────────────────────────────────────────
const CanvasStars = React.memo(() => {
  const canvasRef = useRef(null);
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let animId;

    const resize = () => {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    const stars = Array.from({ length: 160 }, () => ({
      baseX: Math.random() * window.innerWidth,
      baseY: Math.random() * window.innerHeight,
      orbitRX: Math.random() * 25 + 6,
      orbitRY: Math.random() * 12 + 3,
      speed:   Math.random() * 0.003 + 0.0008,
      angle:   Math.random() * Math.PI * 2,
      size:    Math.random() * 1.8 + 0.4,
      opacity: Math.random() * 0.6 + 0.4,
      color:   ["#ffffff","#FEF08A","#BAE6FD","#C4B5FD"][Math.floor(Math.random() * 4)],
    }));

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      stars.forEach(s => {
        s.angle += s.speed;
        const x = s.baseX + Math.cos(s.angle) * s.orbitRX;
        const y = s.baseY + Math.sin(s.angle) * s.orbitRY;
        const twinkle = 0.5 + 0.5 * Math.sin(s.angle * 2.5);
        const alpha   = s.opacity * twinkle;

        const grd = ctx.createRadialGradient(x, y, 0, x, y, s.size * 4);
        grd.addColorStop(0, s.color + "cc");
        grd.addColorStop(1, s.color + "00");
        ctx.globalAlpha = alpha * 0.35;
        ctx.fillStyle   = grd;
        ctx.beginPath();
        ctx.arc(x, y, s.size * 4, 0, Math.PI * 2);
        ctx.fill();

        ctx.globalAlpha = alpha;
        ctx.fillStyle   = s.color;
        ctx.beginPath();
        ctx.arc(x, y, s.size, 0, Math.PI * 2);
        ctx.fill();
      });
      ctx.globalAlpha = 1;
      animId = requestAnimationFrame(draw);
    };

    draw();
    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return <canvas ref={canvasRef} style={{ position: "absolute", inset: 0, pointerEvents: "none" }}/>;
});

// ── BACKGROUND ─────────────────────────────────────────────────
function KuiperBackground() {
  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 0, overflow: "hidden", pointerEvents: "none" }}>
      <div style={{ position: "absolute", inset: 0,
        background: "radial-gradient(ellipse at 50% 55%, #150600 0%, #0a0400 35%, #030008 65%, #000000 100%)" }}/>
      <CanvasStars />
      <div style={{ position: "absolute", inset: 0,
        background: "radial-gradient(ellipse at 50% 50%, transparent 0%, #00000088 70%, #000000cc 100%)" }}/>
    </div>
  );
}

// ── STATS / COST DASHBOARD ─────────────────────────────────────
function CostDashboard({ stats }) {
  if (!stats) return null;
  const total = stats.total_queries || 1;
  const local = stats.local_handled || 0;
  const llm = stats.llm_calls || 0;
  const pct = Math.round((local / total) * 100);

  return (
    <div style={{ padding: "16px 20px" }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: 10, marginBottom: 16 }}>
        <div style={{ background: "#ffffff08", border: "1px solid #ffffff12", borderRadius: 10, padding: "10px 14px", textAlign: "center" }}>
          <div style={{ fontSize: 20, fontWeight: 800, color: "#10B981" }}>{stats.estimated_saved}</div>
          <div style={{ fontSize: 9, color: "#ffffff50", letterSpacing: "1px", textTransform: "uppercase" }}>Estimated Saved</div>
        </div>
        <div style={{ background: "#ffffff08", border: "1px solid #ffffff12", borderRadius: 10, padding: "10px 14px", textAlign: "center" }}>
          <div style={{ fontSize: 20, fontWeight: 800, color: "#F59E0B" }}>{stats.local_rate}</div>
          <div style={{ fontSize: 9, color: "#ffffff50", letterSpacing: "1px", textTransform: "uppercase" }}>Local Handled</div>
        </div>
        <div style={{ background: "#ffffff08", border: "1px solid #ffffff12", borderRadius: 10, padding: "10px 14px", textAlign: "center" }}>
          <div style={{ fontSize: 20, fontWeight: 800, color: stats.tier_color || "#3B82F6" }}>α = {stats.alpha}</div>
          <div style={{ fontSize: 9, color: "#ffffff50", letterSpacing: "1px", textTransform: "uppercase" }}>Tier: {stats.price_tier_name}</div>
        </div>
        <div style={{ background: "#ffffff08", border: "1px solid #ffffff12", borderRadius: 10, padding: "10px 14px", textAlign: "center" }}>
          <div style={{ fontSize: 20, fontWeight: 800, color: "#EF4444" }}>{llm} Calls</div>
          <div style={{ fontSize: 9, color: "#ffffff50", letterSpacing: "1px", textTransform: "uppercase" }}>LLM Invocations</div>
        </div>
      </div>

      <div style={{ fontSize: 11, color: "#ffffff70", marginBottom: 6 }}>
        💡 <strong>Dynamic Alpha Routing:</strong> {stats.price_reasoning}
      </div>

      <div style={{ height: 8, borderRadius: 4, background: "#EF444430", overflow: "hidden", marginBottom: 14 }}>
        <motion.div initial={{ width: 0 }} animate={{ width: `${pct}%` }} transition={{ duration: 0.8 }}
          style={{ height: "100%", background: "linear-gradient(90deg, #10B981, #F59E0B)", borderRadius: 4 }}/>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 8 }}>
        {LAYERS.map(layer => {
          const count = stats.layer_counts?.[layer.id] || 0;
          return (
            <div key={layer.id} style={{ background: "#ffffff05", border: "1px solid #ffffff0a", borderRadius: 8, padding: "6px 10px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span style={{ fontSize: 11, color: layer.color }}>{layer.icon} Layer {layer.id}</span>
              <span style={{ fontSize: 11, fontWeight: 700, color: "#ffffff80" }}>{count}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── MAIN APP ───────────────────────────────────────────────────
export default function App() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem("kuiper_history") || "[]"); } catch { return []; }
  });
  const [error, setError] = useState(null);
  const [activeLayer, setActiveLayer] = useState(null);
  const [apiKey, setApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [provider, setProvider] = useState("auto");
  const [showDash, setShowDash] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    try { sessionStorage.setItem("kuiper_history", JSON.stringify(history)); } catch {}
  }, [history]);

  const fetchStats = async () => {
    try {
      const res = await axios.get(`${API}/stats`);
      setStats(res.data);
    } catch {}
  };

  useEffect(() => {
    fetchStats();
    const iv = setInterval(fetchStats, 3000);
    return () => clearInterval(iv);
  }, []);

  const handleQuery = async (overrideQuery) => {
    const q = overrideQuery || query;
    if (!q.trim()) return;
    setLoading(true);
    setResult(null);
    setError(null);
    setActiveLayer(null);

    // Dynamic pipeline step visualizer animation
    const sequence = ["0A", "0B", "1", "2", "3", "4", "5"];
    for (let i = 0; i < sequence.length; i++) {
      setActiveLayer(sequence[i]);
      await new Promise(r => setTimeout(r, 90));
    }

    try {
      const res = await axios.post(`${API}/query`, {
        query: q,
        provider,
        api_key: apiKey || null,
      });
      setResult(res.data);
      setActiveLayer(res.data.layer);
      setHistory(prev => [{ ...res.data, query: q }, ...prev.slice(0, 49)]);
      fetchStats();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to communicate with Kuiper API.");
      setActiveLayer(null);
    }
    setLoading(false);
  };

  const handleKey = e => { if (e.key === "Enter") handleQuery(); };
  const currentProvider = LLM_PROVIDERS.find(p => p.id === provider);
  const layerInfo = result ? LAYER_INFO[result.handled_by] || LAYER_INFO.unknown : null;

  return (
    <div style={{ minHeight: "100vh", color: "#ffffff", fontFamily: "'Inter', system-ui, -apple-system, sans-serif", display: "flex", position: "relative" }}>
      <KuiperBackground />

      {/* ── LEFT SIDEBAR ── */}
      <motion.div
        initial={false}
        animate={{ width: sidebarOpen ? 260 : 0, minWidth: sidebarOpen ? 260 : 0 }}
        transition={{ duration: 0.35, ease: [0.4, 0, 0.2, 1] }}
        style={{
          height: "100vh", position: "sticky", top: 0,
          background: "#00000085", backdropFilter: "blur(24px)",
          borderRight: "1px solid #ffffff12",
          display: "flex", flexDirection: "column",
          overflow: "hidden", zIndex: 20, flexShrink: 0,
        }}>
        <div style={{ width: 260, display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" }}>
          
          {/* Logo header */}
          <div style={{ padding: "18px 16px 14px", borderBottom: "1px solid #ffffff10", display: "flex", alignItems: "center", gap: 10 }}>
            <OrbitalLogo size={32} animating={loading} />
            <div>
              <div style={{ fontSize: 16, fontWeight: 800, background: "linear-gradient(90deg, #FFFFFF, #F59E0B)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
                Kuiper Router
              </div>
              <div style={{ fontSize: 9, color: "#ffffff40", letterSpacing: "1.5px" }}>
                7-LAYER INTELLIGENT AI
              </div>
            </div>
          </div>

          {/* Architecture Legend */}
          <div style={{ padding: "12px 16px 6px", fontSize: 9, color: "#ffffff40", letterSpacing: "1.5px", textTransform: "uppercase" }}>
            ARCHITECTURE LAYERS
          </div>
          <div style={{ padding: "0 10px 10px", display: "flex", flexDirection: "column", gap: 4 }}>
            {LAYERS.map(l => (
              <div key={l.id} style={{ display: "flex", alignItems: "center", gap: 8, padding: "5px 8px", borderRadius: 6, background: "#ffffff05", border: "1px solid #ffffff08" }}>
                <span style={{ fontSize: 12 }}>{l.icon}</span>
                <div style={{ flex: 1, overflow: "hidden" }}>
                  <div style={{ fontSize: 11, fontWeight: 600, color: l.color }}>Layer {l.id}: {l.label}</div>
                  <div style={{ fontSize: 9, color: "#ffffff50", whiteSpace: "nowrap", textOverflow: "ellipsis", overflow: "hidden" }}>{l.desc}</div>
                </div>
                <span style={{ fontSize: 9, padding: "2px 6px", borderRadius: 4, background: l.cost.includes("FREE") ? "#10B98120" : "#EF444420", color: l.cost.includes("FREE") ? "#10B981" : "#EF4444", fontWeight: 700 }}>
                  {l.speed}
                </span>
              </div>
            ))}
          </div>

          {/* History label */}
          <div style={{ padding: "10px 16px 6px", borderTop: "1px solid #ffffff10", fontSize: 9, color: "#ffffff40", letterSpacing: "1.5px" }}>
            RECENT TRACES ({history.length})
          </div>

          {/* History list */}
          <div style={{ flex: 1, overflowY: "auto", padding: "0 8px 16px" }}>
            {history.length === 0 && (
              <div style={{ padding: "20px 8px", fontSize: 12, color: "#ffffff25", textAlign: "center" }}>
                No queries processed yet
              </div>
            )}
            <AnimatePresence>
              {history.map((h, i) => {
                const info = LAYER_INFO[h.handled_by] || LAYER_INFO.unknown;
                const isActive = result?.query === h.query;
                return (
                  <motion.div key={`${h.query}-${i}`}
                    initial={{ opacity: 0, x: -15 }}
                    animate={{ opacity: 1, x: 0 }}
                    onClick={() => { setQuery(h.query); setResult(h); setActiveLayer(h.layer); }}
                    style={{
                      padding: "8px 10px", borderRadius: 8, marginBottom: 3,
                      cursor: "pointer", display: "flex", alignItems: "center", gap: 8,
                      background: isActive ? "#ffffff18" : "#ffffff04",
                      border: `1px solid ${isActive ? info.color : "transparent"}`
                    }}>
                    <span style={{ fontSize: 10, padding: "2px 5px", borderRadius: 4, background: `${info.color}25`, color: info.color, fontWeight: 700 }}>
                      {h.layer}
                    </span>
                    <div style={{ flex: 1, fontSize: 12, color: "#ffffff90", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {h.query}
                    </div>
                    <span style={{ fontSize: 10, color: "#ffffff40" }}>{h.latency_ms}ms</span>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        </div>
      </motion.div>

      {/* ── MAIN WORKSPACE ── */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden", position: "relative", zIndex: 1 }}>
        
        {/* Top Header */}
        <div style={{ padding: "10px 24px", borderBottom: "1px solid #ffffff12", display: "flex", alignItems: "center", justifyContent: "space-between", background: "#00000060", backdropFilter: "blur(20px)", flexShrink: 0 }}>
          <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}
            onClick={() => setSidebarOpen(p => !p)}
            style={{ background: "none", border: "none", color: "#ffffff80", fontSize: 20, cursor: "pointer", padding: "4px 8px" }}>
            ☰
          </motion.button>

          {/* Stats Bar */}
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            {stats && (
              <>
                <div style={{ padding: "5px 12px", background: "#ffffff08", borderRadius: 8, border: "1px solid #ffffff12", textAlign: "center" }}>
                  <div style={{ fontSize: 13, fontWeight: 800, color: "#10B981" }}>{stats.estimated_saved}</div>
                  <div style={{ fontSize: 8, color: "#ffffff50" }}>Saved</div>
                </div>
                <div style={{ padding: "5px 12px", background: "#ffffff08", borderRadius: 8, border: "1px solid #ffffff12", textAlign: "center" }}>
                  <div style={{ fontSize: 13, fontWeight: 800, color: "#F59E0B" }}>{stats.local_rate}</div>
                  <div style={{ fontSize: 8, color: "#ffffff50" }}>Local Rate</div>
                </div>
                <div style={{ padding: "5px 12px", background: "#ffffff08", borderRadius: 8, border: "1px solid #ffffff12", textAlign: "center" }}>
                  <div style={{ fontSize: 13, fontWeight: 800, color: stats.tier_color || "#3B82F6" }}>α = {stats.alpha}</div>
                  <div style={{ fontSize: 8, color: "#ffffff50" }}>{stats.price_tier_name} Tier</div>
                </div>
              </>
            )}

            <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
              onClick={() => setShowDash(p => !p)}
              style={{
                padding: "8px 16px", borderRadius: 8, cursor: "pointer",
                border: `1px solid ${showDash ? "#F59E0B" : "#ffffff25"}`,
                background: showDash ? "#F59E0B25" : "#ffffff08",
                color: showDash ? "#F59E0B" : "#ffffff90", fontSize: 12, fontWeight: 600
              }}>
              📊 Cost & Alpha Matrix
            </motion.button>
          </div>
        </div>

        {/* Dashboard Dropdown */}
        <AnimatePresence>
          {showDash && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}
              style={{ overflow: "hidden", background: "#00000085", backdropFilter: "blur(20px)", borderBottom: "1px solid #ffffff15" }}>
              <div style={{ maxWidth: 840, margin: "0 auto" }}>
                <CostDashboard stats={stats} />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Center Content */}
        <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", alignItems: "center", padding: "36px 24px 32px" }}>
          
          {/* Hero */}
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} style={{ textAlign: "center", marginBottom: 24 }}>
            <OrbitalLogo size={52} animating={loading} />
            <div style={{ fontSize: 32, fontWeight: 800, letterSpacing: "-0.5px", marginTop: 12, marginBottom: 6, background: "linear-gradient(135deg, #FFFFFF, #F59E0B)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
              Kuiper Multi-Layer Intelligent Router
            </div>
            <div style={{ fontSize: 14, color: "#ffffff70", maxWidth: 540, margin: "0 auto" }}>
              Queries cascade through 7 smart layers — math, facts, Wikipedia, TinyML, cache, and embeddings — auto-selecting the best model when LLM is needed.
            </div>
          </motion.div>

          {/* Main Input Stack */}
          <div style={{ width: "100%", maxWidth: 780, display: "flex", flexDirection: "column", gap: 12 }}>
            
            {/* Provider and Inbuilt Key Selector */}
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <select value={provider} onChange={e => setProvider(e.target.value)}
                style={{ padding: "12px 14px", borderRadius: 12, background: "#ffffff12", border: "1px solid #ffffff25", color: "#ffffff", fontSize: 13, cursor: "pointer", outline: "none", backdropFilter: "blur(10px)" }}>
                {LLM_PROVIDERS.map(p => (
                  <option key={p.id} value={p.id} style={{ background: "#111827" }}>
                    {p.label}
                  </option>
                ))}
              </select>

              <div style={{ flex: 1, background: "#ffffff12", borderRadius: 12, border: "1px solid #ffffff20", padding: "10px 14px", display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ fontSize: 14 }}>🔑</span>
                <input type={showKey ? "text" : "password"} value={apiKey} onChange={e => setApiKey(e.target.value)}
                  placeholder={currentProvider?.placeholder || "Automatic optimal model selection"}
                  style={{ flex: 1, background: "transparent", border: "none", outline: "none", color: "#ffffff", fontSize: 12, fontFamily: "monospace" }}/>
                
                {currentProvider?.badge && !apiKey && (
                  <span style={{ padding: "3px 8px", borderRadius: 12, background: "#10B98120", border: "1px solid #10B98160", color: "#10B981", fontSize: 10, fontWeight: 700 }}>
                    {currentProvider.badge}
                  </span>
                )}
                {apiKey && (
                  <button onClick={() => setShowKey(p => !p)} style={{ background: "none", border: "none", color: "#ffffff60", cursor: "pointer", fontSize: 11 }}>
                    {showKey ? "Hide" : "Show"}
                  </button>
                )}
              </div>
            </div>

            {/* Query Input Field */}
            <div style={{ display: "flex", gap: 10 }}>
              <input value={query} onChange={e => setQuery(e.target.value)} onKeyDown={handleKey}
                placeholder="Ask anything (math, science, coding, essay, facts, order status)..."
                style={{ flex: 1, padding: "16px 20px", borderRadius: 14, border: "1px solid #ffffff30", background: "#ffffff18", color: "#ffffff", fontSize: 15, outline: "none", backdropFilter: "blur(12px)" }}/>
              <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                onClick={() => handleQuery()} disabled={loading}
                style={{
                  padding: "16px 28px", borderRadius: 14, border: "none",
                  background: loading ? "#ffffff20" : "linear-gradient(135deg, #F59E0B, #D97706)",
                  color: "#ffffff", fontSize: 15, fontWeight: 700, cursor: loading ? "not-allowed" : "pointer",
                  boxShadow: "0 0 20px #F59E0B33", whiteSpace: "nowrap"
                }}>
                {loading ? "Cascading..." : "Run Query →"}
              </motion.button>
            </div>

            {/* Pipeline Visualizer (All 7 Layers) */}
            <div style={{ background: "#ffffff0a", borderRadius: 14, border: "1px solid #ffffff15", padding: "14px 18px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                <span style={{ fontSize: 10, color: "#ffffff60", letterSpacing: "1.5px", textTransform: "uppercase" }}>
                  7-LAYER EXECUTION PIPELINE
                </span>
                <span style={{ fontSize: 10, color: "#F59E0B" }}>
                  ⚡ Free Local Layers (0A ➔ 4) | 🧠 Auto-LLM (5)
                </span>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(95px, 1fr))", gap: 6 }}>
                {LAYERS.map(layer => {
                  const isActive = activeLayer === layer.id;
                  const isMatch = result && result.layer === layer.id;
                  return (
                    <motion.div key={layer.id}
                      animate={{
                        scale: isMatch ? 1.05 : isActive ? 1.02 : 1,
                        boxShadow: isMatch ? `0 0 16px ${layer.color}90` : "none"
                      }}
                      style={{
                        padding: "8px 10px", borderRadius: 8,
                        background: isMatch ? `${layer.color}35` : isActive ? `${layer.color}18` : "#ffffff05",
                        border: `1px solid ${isMatch ? layer.color : isActive ? `${layer.color}60` : "#ffffff0d"}`,
                        textAlign: "center", transition: "all 0.2s"
                      }}>
                      <div style={{ fontSize: 11, fontWeight: 800, color: isMatch ? "#FFFFFF" : layer.color }}>
                        {layer.icon} {layer.id}
                      </div>
                      <div style={{ fontSize: 9, color: "#ffffff80", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                        {layer.label}
                      </div>
                      <div style={{ fontSize: 8, color: layer.cost.includes("FREE") ? "#10B981" : "#EF4444", fontWeight: 700, marginTop: 2 }}>
                        {layer.cost}
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>

            {/* Quick Sample Prompts */}
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap", alignItems: "center" }}>
              <span style={{ fontSize: 11, color: "#ffffff50", marginRight: 4 }}>Try:</span>
              {SAMPLE_QUERIES.map((s, idx) => (
                <button key={idx} onClick={() => { setQuery(s.text); handleQuery(s.text); }}
                  style={{ padding: "4px 10px", borderRadius: 16, background: "#ffffff08", border: "1px solid #ffffff15", color: "#ffffff90", fontSize: 11, cursor: "pointer", transition: "background 0.15s" }}
                  onMouseEnter={e => e.currentTarget.style.background = "#ffffff18"}
                  onMouseLeave={e => e.currentTarget.style.background = "#ffffff08"}>
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          {/* ── RESULT CARD ── */}
          <div style={{ width: "100%", maxWidth: 780, marginTop: 20 }}>
            {error && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                style={{ background: "#EF444415", border: "1px solid #EF444460", borderRadius: 12, padding: "14px 18px", color: "#EF4444", marginBottom: 16, fontSize: 14 }}>
                ⚠️ {error}
              </motion.div>
            )}

            <AnimatePresence>
              {result && layerInfo && (
                <motion.div key={result.query + result.latency_ms}
                  initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
                  style={{
                    background: "#00000085", borderRadius: 18,
                    border: `1px solid ${layerInfo.color}60`,
                    padding: "24px", backdropFilter: "blur(24px)",
                    boxShadow: `0 0 35px ${layerInfo.color}20`
                  }}>
                  
                  {/* Top Bar of Result */}
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14, flexWrap: "wrap" }}>
                    <div style={{ padding: "6px 14px", borderRadius: 20, background: layerInfo.color, color: "#000000", fontSize: 12, fontWeight: 800 }}>
                      {layerInfo.icon} {result.layer_name || layerInfo.label}
                    </div>

                    <div style={{ color: "#ffffff90", fontSize: 12 }}>
                      ⚡ Latency: <strong>{result.latency_ms}ms</strong>
                    </div>

                    {result.cost_saved ? (
                      <div style={{ padding: "4px 12px", borderRadius: 20, background: "#10B98120", border: "1px solid #10B98180", color: "#10B981", fontSize: 11, fontWeight: 700 }}>
                        💰 100% LLM Cost Saved (Free Layer)
                      </div>
                    ) : (
                      <div style={{ padding: "4px 12px", borderRadius: 20, background: "#EF444420", border: "1px solid #EF444480", color: "#EF4444", fontSize: 11, fontWeight: 700 }}>
                        🧠 Auto-LLM ({result.model || provider})
                      </div>
                    )}

                    {result.tokens && (
                      <span style={{ fontSize: 11, color: "#ffffff60" }}>
                        Tokens: {result.tokens}
                      </span>
                    )}
                  </div>

                  {/* Auto Model Selection Reason */}
                  {result.selection_reason && (
                    <div style={{ marginBottom: 12, padding: "6px 12px", borderRadius: 8, background: "#3B82F615", border: "1px solid #3B82F640", fontSize: 11, color: "#93C5FD" }}>
                      🎯 <strong>Optimal Model Selected:</strong> {result.selection_reason}
                    </div>
                  )}

                  {/* Query Question */}
                  <div style={{ fontSize: 13, color: "#ffffff70", marginBottom: 8, fontStyle: "italic" }}>
                    "{result.query}"
                  </div>

                  {/* Answer Text with full whitespace formatting */}
                  <div style={{ fontSize: 15, fontWeight: 400, lineHeight: 1.7, color: "#FFFFFF", marginBottom: 16, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                    {result.answer}
                  </div>

                  {/* Step Breakdown */}
                  {result.steps && result.steps.length > 0 && (
                    <div style={{ background: "#ffffff05", border: "1px solid #ffffff0a", borderRadius: 10, padding: "10px 14px", marginBottom: 12 }}>
                      <div style={{ fontSize: 10, color: "#ffffff50", textTransform: "uppercase", letterSpacing: "1px", marginBottom: 6 }}>
                        Cascade Execution Trace
                      </div>
                      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                        {result.steps.map((st, idx) => (
                          <div key={idx} style={{ fontSize: 11, padding: "3px 8px", borderRadius: 6, background: st.status === "HIT" ? "#10B98125" : st.status === "INVOKED" ? "#EF444425" : "#ffffff08", border: `1px solid ${st.status === "HIT" ? "#10B98160" : st.status === "INVOKED" ? "#EF444460" : "#ffffff10"}`, color: st.status === "HIT" ? "#10B981" : st.status === "INVOKED" ? "#EF4444" : "#ffffff60" }}>
                            Layer {st.layer}: {st.name} ➔ <strong>{st.status}</strong> ({st.latency_ms}ms)
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Bottom Meta */}
                  <div style={{ display: "flex", gap: 16, fontSize: 11, color: "#ffffff60", borderTop: "1px solid #ffffff10", paddingTop: 12 }}>
                    <span>Active α: <strong>{result.alpha}</strong></span>
                    <span>Price Tier: <strong>{result.price_tier}</strong></span>
                    <span>Confidence: <strong>{result.confidence ? `${Math.round(result.confidence * 100)}%` : "100%"}</strong></span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}