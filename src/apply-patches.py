#!/usr/bin/env python3
"""Apply UI patches to Claude Code VSCode extension webview.

Handles both minified and prettified (beautified) code formats.
v12: Fix $-prefixed var names (v2.1.37+), fix black text (forced dark bg + accent class).
    Row1: model/cost/ctx. Row2: In(total,cache%)/Out/Workdir/GitBranch.
    Row3: 5hr usage%/7d usage%/session time/last activity.
    Row4: 5hr reset countdown + bar / 7d reset countdown + bar.
    Row5: thinking level/msg count/output utilization.
    Row6: cost rate/throughput/compaction counter.
    Avatar: Funko Pop Dustin (48px display, 128px retina) with gradient "DUSTIN" label.
    Layout: flexbox row (metrics left, avatar right).
    Icons: Lucide SVG (inline, unified accent #e04040).
    Palette: Stranger Things red (#e04040) / dark red (#b82030) / white / black.
"""

import sys
import os
import re
import shutil

def _find_ext_dir():
    """Auto-detect Claude Code extension directory."""
    import glob
    base = os.path.expanduser("~/.vscode-server/extensions")
    matches = sorted(glob.glob(os.path.join(base, "anthropic.claude-code-*")))
    if matches:
        return matches[-1]  # latest version
    # Fallback: try non-remote VSCode
    base2 = os.path.expanduser("~/.vscode/extensions")
    matches2 = sorted(glob.glob(os.path.join(base2, "anthropic.claude-code-*")))
    if matches2:
        return matches2[-1]
    print("ERROR: Claude Code extension not found. Set EXT_DIR env var.")
    sys.exit(1)

EXT_DIR = os.environ.get("CC_EXT_DIR") or _find_ext_dir()
WEBVIEW_JS = os.path.join(EXT_DIR, "webview/index.js")
WEBVIEW_CSS = os.path.join(EXT_DIR, "webview/index.css")
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups")

# ─── Dustin Funko Pop avatar (128px retina, base64) ───
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_SCRIPT_DIR)
_B64_PATH = os.path.join(_PROJECT_DIR, "assets", "dustin_128.b64")
if not os.path.exists(_B64_PATH):
    _B64_PATH = os.path.join(_SCRIPT_DIR, "dustin_128.b64")  # fallback: same dir
DUSTIN_IMG_B64 = open(_B64_PATH).read().strip() if os.path.exists(_B64_PATH) else ""

# ─── Session Metrics Component v12 (inside inputFooter with flex-wrap) ───
_METRICS_TEMPLATE = r"""
var _ccSessionStart = Date.now();
var _ccAccent = "#e04040";
var _ccDim = "rgba(255,255,255,0.55)";
function _ccV(t) { return n4.default.createElement("span", { className: "cc-accent", style: { color: _ccAccent } }, t); }
var _ccP = {
  brain: [["path",{d:"M12 18V5"}],["path",{d:"M15 13a4.17 4.17 0 0 1-3-4 4.17 4.17 0 0 1-3 4"}],["path",{d:"M17.598 6.5A3 3 0 1 0 12 5a3 3 0 1 0-5.598 1.5"}],["path",{d:"M17.997 5.125a4 4 0 0 1 2.526 5.77"}],["path",{d:"M18 18a4 4 0 0 0 2-7.464"}],["path",{d:"M19.967 17.483A4 4 0 1 1 12 18a4 4 0 1 1-7.967-.517"}],["path",{d:"M6 18a4 4 0 0 1-2-7.464"}],["path",{d:"M6.003 5.125a4 4 0 0 0-2.526 5.77"}]],
  dollar: [["line",{x1:"12",x2:"12",y1:"2",y2:"22"}],["path",{d:"M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"}]],
  layers: [["path",{d:"M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z"}],["path",{d:"M2 12a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 12"}],["path",{d:"M2 17a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 17"}]],
  arrowDown: [["path",{d:"M12 17V3"}],["path",{d:"m6 11 6 6 6-6"}],["path",{d:"M19 21H5"}]],
  arrowUp: [["path",{d:"m18 9-6-6-6 6"}],["path",{d:"M12 3v14"}],["path",{d:"M5 21h14"}]],
  zap: [["path",{d:"M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"}]],
  calDays: [["path",{d:"M8 2v4"}],["path",{d:"M16 2v4"}],["rect",{width:"18",height:"18",x:"3",y:"4",rx:"2"}],["path",{d:"M3 10h18"}],["path",{d:"M8 14h.01"}],["path",{d:"M12 14h.01"}],["path",{d:"M16 14h.01"}],["path",{d:"M8 18h.01"}],["path",{d:"M12 18h.01"}],["path",{d:"M16 18h.01"}]],
  timer: [["line",{x1:"10",x2:"14",y1:"2",y2:"2"}],["line",{x1:"12",x2:"15",y1:"14",y2:"11"}],["circle",{cx:"12",cy:"14",r:"8"}]],
  refresh: [["path",{d:"M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"}],["path",{d:"M21 3v5h-5"}],["path",{d:"M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"}],["path",{d:"M8 16H3v5"}]],
  clock: [["path",{d:"M12 6v6l4 2"}],["circle",{cx:"12",cy:"12",r:"10"}]],
  calClock: [["path",{d:"M16 14v2.2l1.6 1"}],["path",{d:"M16 2v4"}],["path",{d:"M21 7.5V6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h3.5"}],["path",{d:"M3 10h5"}],["path",{d:"M8 2v4"}],["circle",{cx:"16",cy:"16",r:"6"}]],
  dot: [["circle",{cx:"12",cy:"12",r:"10"}],["circle",{cx:"12",cy:"12",r:"1"}]],
  msgSquare: [["path",{d:"M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"}]],
  gauge: [["path",{d:"m12 14 4-4"}],["path",{d:"M3.34 19a10 10 0 1 1 17.32 0"}]],
  folder: [["path",{d:"M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2z"}]],
  gitBr: [["line",{x1:"6",x2:"6",y1:"3",y2:"15"}],["circle",{cx:"18",cy:"6",r:"3"}],["circle",{cx:"6",cy:"18",r:"3"}],["path",{d:"M18 9a9 9 0 0 1-9 9"}]],
};
function _ccIcon(name, sz, clr) {
  var paths = _ccP[name];
  if (!paths) return null;
  var children = paths.map(function(p) {
    var tag = p[0], a = p[1], props = { fill: "none", stroke: clr || _ccAccent, strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round" };
    for (var k in a) props[k] = a[k];
    if (tag === "circle" && name === "dot" && a.r === "1") { props.fill = clr || _ccAccent; }
    return n4.default.createElement(tag, props);
  });
  return n4.default.createElement("svg", { xmlns: "http://www.w3.org/2000/svg", width: sz || 12, height: sz || 12, viewBox: "0 0 24 24", fill: "none", style: { display: "inline-block", verticalAlign: "middle", marginRight: "3px", flexShrink: 0 } }, children);
}
function _ccBar(pct, color, w) {
  var p = Math.min(100, Math.max(0, pct));
  return n4.default.createElement("span", { style: { display: "inline-flex", alignItems: "center", verticalAlign: "middle", width: (w || 50) + "px", height: "6px", background: "rgba(255,255,255,0.08)", borderRadius: "3px", overflow: "hidden", margin: "0 3px" } },
    n4.default.createElement("span", { style: { width: p + "%", height: "100%", background: color, borderRadius: "3px", transition: "width 0.3s ease" } })
  );
}
var _ccDustinImg = "data:image/png;base64,__DUSTIN_B64__";
function _ccAvatar() {
  return n4.default.createElement("div", { style: { display: "flex", flexDirection: "column", alignItems: "center", gap: "2px", flexShrink: 0 } },
    n4.default.createElement("img", { src: _ccDustinImg, style: { width: "48px", height: "48px", borderRadius: "6px", border: "1px solid rgba(255,255,255,0.12)", background: "rgba(255,255,255,0.04)", objectFit: "contain" } }),
    n4.default.createElement("span", { style: { fontSize: "8px", fontWeight: "bold", letterSpacing: "1.5px", background: "linear-gradient(90deg, #e04040, #ff6644, #e04040)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", textShadow: "none" } }, "DUSTIN")
  );
}
function CC_MetricsBar({ session: S }) {
  _Z();
  n4.useEffect(function() {
    S.requestUsageUpdate();
    var _t = setInterval(function() { S.requestUsageUpdate(); }, 60000);
    return function() { clearInterval(_t); };
  }, []);
  var _compactRef = n4.useRef({ count: 0, prevTokens: 0, wasLow: false });
  var ud = S.usageData.value;
  var model = S.currentMainLoopModel.value || "\u2014";
  var cost = ud.totalCost != null ? ud.totalCost.toFixed(4) : "0.0000";
  var busy = S.busy.value;
  var rawIn = ud.inputTokens || 0;
  var outTok = ud.outputTokens || 0;
  var cacheCr = ud.cacheCreation || 0;
  var cacheRd = ud.cacheRead || 0;
  var totalIn = rawIn + cacheCr + cacheRd;
  var cachePct = totalIn > 0 ? Math.round(cacheRd / totalIn * 100) : 0;
  var totalTok = ud.totalTokens || 0;
  var ctxWin = ud.contextWindow || 0;
  var maxOut = ud.maxOutputTokens || 0;
  var effectiveCtx = ctxWin - maxOut - 13000;
  var ctxPct = effectiveCtx > 0 && totalTok > 0 ? Math.round(totalTok / effectiveCtx * 100) : 0;
  var util = S.utilization.value;
  var u5h = util && util.fiveHour ? util.fiveHour.utilization : null;
  var u7d = util && util.sevenDay ? util.sevenDay.utilization : null;
  var now = Date.now();
  var lastMod = S.lastModifiedTime.value || now;
  var ageSec = Math.floor((now - lastMod) / 1000);
  var ageStr = ageSec < 60 ? ageSec + "s" : Math.floor(ageSec / 60) + "m";
  var sesMin = Math.floor((now - _ccSessionStart) / 60000);
  var sesStr = sesMin < 60 ? sesMin + "m" : Math.floor(sesMin / 60) + "h" + (sesMin % 60) + "m";
  var _days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
  var r5h = util && util.fiveHour && util.fiveHour.resetsAt ? new Date(util.fiveHour.resetsAt) : null;
  var r7d = util && util.sevenDay && util.sevenDay.resetsAt ? new Date(util.sevenDay.resetsAt) : null;
  var r5hTime = r5h ? (r5h.getHours() < 10 ? "0" : "") + r5h.getHours() + ":" + (r5h.getMinutes() < 10 ? "0" : "") + r5h.getMinutes() : null;
  var r5hMs = r5h ? Math.max(0, r5h.getTime() - now) : 0;
  var r5hMin = Math.floor(r5hMs / 60000);
  var r5hCd = r5hMs <= 0 ? "soon" : r5hMin < 60 ? r5hMin + "m" : Math.floor(r5hMin / 60) + "h" + (r5hMin % 60 < 10 ? "0" : "") + (r5hMin % 60) + "m";
  var r5hPct = r5hMs > 0 ? Math.min(100, Math.round((1 - r5hMs / 18000000) * 100)) : 100;
  var r7dTime = r7d ? _days[r7d.getDay()] + " " + (r7d.getHours() < 10 ? "0" : "") + r7d.getHours() + ":" + (r7d.getMinutes() < 10 ? "0" : "") + r7d.getMinutes() : null;
  var r7dMs = r7d ? Math.max(0, r7d.getTime() - now) : 0;
  var r7dDays = Math.floor(r7dMs / 86400000);
  var r7dHrs = Math.floor((r7dMs % 86400000) / 3600000);
  var r7dCd = r7dMs <= 0 ? "soon" : r7dDays > 0 ? r7dDays + "d" + r7dHrs + "h" : r7dHrs + "h";
  var r7dPct = r7dMs > 0 ? Math.min(100, Math.round((1 - r7dMs / 604800000) * 100)) : 100;
  var sep = { display: "inline", opacity: "0.3", margin: "0 3px" };
  var row = { display: "flex", gap: "6px", alignItems: "center", flexWrap: "wrap", width: "100%" };
  var itm = { display: "inline-flex", alignItems: "center", gap: "3px" };
  var u5hStr = u5h != null ? Math.floor(u5h) + "%" : "--";
  var u7dStr = u7d != null ? Math.floor(u7d) + "%" : "--";
  var thinkLvl = S.thinkingLevel ? (S.thinkingLevel.value || "off") : "off";
  var thinkColors = { off: _ccDim, low: "#44bb44", medium: "#ddaa00", high: "#ff4444" };
  var thinkClr = thinkColors[thinkLvl] || _ccDim;
  var msgCount = S.messages && S.messages.value ? S.messages.value.length : 0;
  var outPct = maxOut > 0 && outTok > 0 ? Math.round(outTok / maxOut * 100) : 0;
  var outMaxStr = maxOut > 0 ? (maxOut / 1000).toFixed(0) + "k" : "?";
  var costVal = parseFloat(cost);
  var costRate = sesMin > 0 ? (costVal / sesMin * 60) : 0;
  var costRateStr = costRate > 0 ? "$" + costRate.toFixed(2) + "/hr" : "--";
  var throughput = sesMin > 0 ? Math.round((rawIn + outTok) / sesMin) : 0;
  var throughStr = throughput > 0 ? throughput.toLocaleString() + " tok/min" : "--";
  var cwdRaw = S.cwd && S.cwd.value ? S.cwd.value : "";
  var cwdStr = cwdRaw.replace(/^\/home\/[^/]+/, "~");
  var cwdParts = cwdStr.split("/");
  if (cwdParts.length > 3) cwdStr = "~/" + cwdParts.slice(-2).join("/");
  var gitBr = S.gitBranch && S.gitBranch.value ? S.gitBranch.value : "";
  if (_compactRef.current.prevTokens > 500 && totalTok < 100 && !_compactRef.current.wasLow) {
    _compactRef.current.count += 1;
    _compactRef.current.wasLow = true;
  }
  if (totalTok > 500) {
    _compactRef.current.wasLow = false;
  }
  _compactRef.current.prevTokens = totalTok;
  var compactCount = _compactRef.current.count;
  return n4.default.createElement("div", {
    className: "sessionMetrics_cc",
    style: {
      display: "flex",
      flexDirection: "row",
      fontSize: "11px",
      padding: "3px 6px",
      borderBottom: ".5px solid rgba(224,64,64,0.15)",
      gap: "8px",
      alignItems: "center",
      color: _ccDim,
      overflow: "hidden",
    },
  },
    n4.default.createElement("div", { style: { display: "flex", flexDirection: "column", gap: "2px", minWidth: 0 } },
      n4.default.createElement("div", { style: row },
        n4.default.createElement("span", { style: { display: "inline-flex", alignItems: "center", gap: "3px", fontWeight: "600" } }, _ccIcon("brain", 12, _ccAccent), _ccV(model)),
        n4.default.createElement("span", { style: sep }, "|"),
        n4.default.createElement("span", { style: itm }, _ccIcon("dollar", 12, _ccAccent), _ccV("$" + cost)),
        n4.default.createElement("span", { style: sep }, "|"),
        n4.default.createElement("span", { style: itm }, _ccIcon("layers", 12, _ccAccent), _ccBar(ctxPct, _ccAccent, 60), _ccV(ctxPct + "%"), "(" + totalTok.toLocaleString() + "/" + (ctxWin > 0 ? (ctxWin / 1000).toFixed(0) + "k" : "?") + ")"),
        busy && n4.default.createElement("span", { style: sep }, "|"),
        busy && n4.default.createElement("span", { style: { display: "inline-flex", alignItems: "center", gap: "3px", color: _ccAccent, fontWeight: "bold" } }, _ccIcon("dot", 12, "#ff4444"), "BUSY"),
      ),
      n4.default.createElement("div", { style: row },
        n4.default.createElement("span", { style: itm }, _ccIcon("arrowDown", 12, _ccAccent), "In:", _ccV(totalIn.toLocaleString()), cachePct > 0 ? "(" + cachePct + "% cached)" : null),
        n4.default.createElement("span", { style: sep }, "|"),
        n4.default.createElement("span", { style: itm }, _ccIcon("arrowUp", 12, _ccAccent), "Out:", _ccV(outTok.toLocaleString())),
        cwdStr && n4.default.createElement("span", { style: sep }, "|"),
        cwdStr && n4.default.createElement("span", { style: itm }, _ccIcon("folder", 12, _ccAccent), _ccV(cwdStr)),
        gitBr && n4.default.createElement("span", { style: sep }, "|"),
        gitBr && n4.default.createElement("span", { style: itm }, _ccIcon("gitBr", 12, _ccAccent), _ccV(gitBr)),
      ),
      n4.default.createElement("div", { style: row },
        n4.default.createElement("span", { style: itm }, _ccIcon("zap", 12, _ccAccent), "5hr:", _ccBar(u5h || 0, _ccAccent, 40), _ccV(u5hStr)),
        n4.default.createElement("span", { style: sep }, "|"),
        n4.default.createElement("span", { style: itm }, _ccIcon("calDays", 12, _ccAccent), "7d:", _ccBar(u7d || 0, _ccAccent, 40), _ccV(u7dStr)),
        n4.default.createElement("span", { style: sep }, "\u2502"),
        n4.default.createElement("span", { style: itm }, _ccIcon("timer", 12, _ccAccent), _ccV(sesStr)),
        n4.default.createElement("span", { style: sep }, "|"),
        n4.default.createElement("span", { style: itm }, _ccIcon("refresh", 12, _ccAccent), _ccV(ageStr), "ago"),
      ),
      n4.default.createElement("div", { style: row },
        n4.default.createElement("span", { style: itm }, _ccIcon("clock", 12, _ccAccent), "5h reset", r5hTime ? _ccV(r5hTime) : _ccV("--"), r5hCd ? "(" + r5hCd + ")" : null, _ccBar(r5hPct, _ccAccent, 40)),
        n4.default.createElement("span", { style: sep }, "|"),
        n4.default.createElement("span", { style: itm }, _ccIcon("calClock", 12, _ccAccent), "7d reset", r7dTime ? _ccV(r7dTime) : _ccV("--"), r7dCd ? "(" + r7dCd + ")" : null, _ccBar(r7dPct, _ccAccent, 40)),
      ),
      n4.default.createElement("div", { style: row },
        n4.default.createElement("span", { style: itm }, _ccIcon("brain", 12, thinkClr), "Think:", n4.default.createElement("span", { style: { color: thinkClr, fontWeight: "bold" } }, thinkLvl.toUpperCase())),
        n4.default.createElement("span", { style: sep }, "|"),
        n4.default.createElement("span", { style: itm }, _ccIcon("msgSquare", 12, _ccAccent), _ccV(msgCount + ""), "msgs"),
        n4.default.createElement("span", { style: sep }, "|"),
        n4.default.createElement("span", { style: itm }, _ccIcon("arrowUp", 12, _ccAccent), "Out:", _ccBar(outPct, _ccAccent, 40), _ccV(outPct + "%"), "(" + outTok.toLocaleString() + "/" + outMaxStr + ")"),
      ),
      n4.default.createElement("div", { style: row },
        n4.default.createElement("span", { style: itm }, _ccIcon("dollar", 12, _ccAccent), _ccV(costRateStr)),
        n4.default.createElement("span", { style: sep }, "|"),
        n4.default.createElement("span", { style: itm }, _ccIcon("gauge", 12, _ccAccent), _ccV(throughStr)),
        compactCount > 0 && n4.default.createElement("span", { style: sep }, "|"),
        compactCount > 0 && n4.default.createElement("span", { style: itm }, _ccIcon("layers", 12, _ccAccent), "Compact:", _ccV(compactCount + "x")),
      ),
    ),
    _ccAvatar(),
  );
}
"""

# Resolve base64 placeholder
METRICS_COMPONENT_DEF = _METRICS_TEMPLATE.replace("__DUSTIN_B64__", DUSTIN_IMG_B64)

# ─── usageData signal patches (prettified) ───
USAGE_DATA_ORIGINAL = """\
  usageData = g1({
    totalTokens: 0,
    totalCost: 0,
    contextWindow: 0,
    maxOutputTokens: 0,
  });"""

USAGE_DATA_PATCHED = """\
  usageData = g1({
    totalTokens: 0,
    totalCost: 0,
    contextWindow: 0,
    maxOutputTokens: 0,
    inputTokens: 0,
    outputTokens: 0,
    cacheCreation: 0,
    cacheRead: 0,
  });"""

# ─── usageData signal patches (minified) - signal function varies (g1, p1, etc.) ───
# Pattern: usageData=XX({totalTokens:0,totalCost:0,contextWindow:0,maxOutputTokens:0})
USAGE_DATA_MIN_PATTERN = r'usageData=([a-zA-Z][a-zA-Z0-9]*)\(\{totalTokens:0,totalCost:0,contextWindow:0,maxOutputTokens:0\}\)'
USAGE_DATA_MIN_REPLACE = r'usageData=\1({totalTokens:0,totalCost:0,contextWindow:0,maxOutputTokens:0,inputTokens:0,outputTokens:0,cacheCreation:0,cacheRead:0})'

# ─── updateUsage() patches (prettified) ───
UPDATE_USAGE_ORIGINAL = """\
    this.usageData.value = {
      totalTokens: J,
      totalCost: Z.totalCost,
      contextWindow: Z.contextWindow,
      maxOutputTokens: Z.maxOutputTokens,
    };
  }"""

UPDATE_USAGE_PATCHED = """\
    this.usageData.value = {
      totalTokens: J,
      totalCost: Z.totalCost,
      contextWindow: Z.contextWindow,
      maxOutputTokens: Z.maxOutputTokens,
      inputTokens: $.input_tokens || 0,
      outputTokens: (Z.outputTokens || 0) + ($.output_tokens || 0),
      cacheCreation: $.cache_creation_input_tokens || 0,
      cacheRead: $.cache_read_input_tokens || 0,
    };
  }"""

# ─── updateUsage() patches (minified) ───
UPDATE_USAGE_MIN_ORIGINAL = 'usageData.value={totalTokens:J,totalCost:Z.totalCost,contextWindow:Z.contextWindow,maxOutputTokens:Z.maxOutputTokens}'
UPDATE_USAGE_MIN_PATCHED = 'usageData.value={totalTokens:J,totalCost:Z.totalCost,contextWindow:Z.contextWindow,maxOutputTokens:Z.maxOutputTokens,inputTokens:$.input_tokens||0,outputTokens:(Z.outputTokens||0)+($.output_tokens||0),cacheCreation:$.cache_creation_input_tokens||0,cacheRead:$.cache_read_input_tokens||0}'

# ─── result handler patches (prettified) ───
RESULT_HANDLER_ORIGINAL = """\
        this.usageData.value = {
          totalTokens: J.totalTokens,
          totalCost: $.total_cost_usd,
          contextWindow: X,
          maxOutputTokens: Q,
        };"""

RESULT_HANDLER_PATCHED = """\
        this.usageData.value = {
          totalTokens: J.totalTokens,
          totalCost: $.total_cost_usd,
          contextWindow: X,
          maxOutputTokens: Q,
          inputTokens: J.inputTokens || 0,
          outputTokens: J.outputTokens || 0,
          cacheCreation: J.cacheCreation || 0,
          cacheRead: J.cacheRead || 0,
        };"""

# ─── result handler patches (minified) ───
RESULT_HANDLER_MIN_ORIGINAL = 'usageData.value={totalTokens:J.totalTokens,totalCost:$.total_cost_usd,contextWindow:X,maxOutputTokens:Q}'
RESULT_HANDLER_MIN_PATCHED = 'usageData.value={totalTokens:J.totalTokens,totalCost:$.total_cost_usd,contextWindow:X,maxOutputTokens:Q,inputTokens:J.inputTokens||0,outputTokens:J.outputTokens||0,cacheCreation:J.cacheCreation||0,cacheRead:J.cacheRead||0}'

# ─── compact_boundary patches ───
COMPACT_ORIGINAL = "{ ...this.usageData.value, totalTokens: 0 }"
COMPACT_PATCHED = "{ ...this.usageData.value, totalTokens: 0, inputTokens: 0, outputTokens: 0, cacheCreation: 0, cacheRead: 0 }"
COMPACT_MIN_ORIGINAL = "{...this.usageData.value,totalTokens:0}"
COMPACT_MIN_PATCHED = "{...this.usageData.value,totalTokens:0,inputTokens:0,outputTokens:0,cacheCreation:0,cacheRead:0}"


# JavaScript identifier pattern: can start with $, _, or letter
_JS_ID = r'[\$_a-zA-Z][\$_a-zA-Z0-9]*'


def is_prettified(content):
    """Check if file is prettified (multi-line) vs minified."""
    lines = content.split('\n')
    return len(lines) > 5000


def is_already_patched(content):
    """Check if patches were already applied."""
    return "sessionMetrics_cc" in content


def detect_css_module_var(content):
    """Detect the CSS module variable name (WJ, KJ, etc.) that holds inputFooter."""
    match = re.search(r'(' + _JS_ID + r')\.inputFooter', content)
    if match:
        return match.group(1)
    return "WJ"  # default fallback


def detect_react_var(content, css_var="WJ"):
    """Detect the React variable name (n4, o4, e4, etc.) used in minified code."""
    # Look for pattern: return XX.default.createElement("div",{className:CSS.inputFooter}
    pattern = r'return (' + _JS_ID + r')\.default\.createElement\("div",\{className:' + re.escape(css_var) + r'\.inputFooter\}'
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    # Fallback: look for any XX.default.createElement pattern near inputFooter
    match = re.search(r'(' + _JS_ID + r')\.default\.createElement\("div",\{className:' + _JS_ID + r'\.inputFooter\}', content)
    if match:
        return match.group(1)
    return "n4"  # default fallback


def detect_footer_component(content, css_var="WJ"):
    """Detect the footer component name (dP1, iP1, FO1, etc.) used after inputFooter."""
    # Look for pattern: className:CSS.inputFooter},XX.default.createElement(COMP
    # Exclude CC_MetricsBar which is our own injected component
    pattern = r'className:' + re.escape(css_var) + r'\.inputFooter\},(' + _JS_ID + r')\.default\.createElement\((' + _JS_ID + r')'
    match = re.search(pattern, content)
    if match:
        comp = match.group(2)
        if comp == 'CC_MetricsBar':
            # Already patched, look for the next createElement after CC_MetricsBar
            match2 = re.search(r'createElement\(CC_MetricsBar[^)]*\),(' + _JS_ID + r')\.default\.createElement\((' + _JS_ID + r')', content)
            if match2:
                return match2.group(2)
        return comp
    return "dP1"  # default fallback


def detect_signal_hook(content, css_var="WJ"):
    """Detect the signal reactivity hook name (_Z, MZ, etc.) called at start of footer function."""
    footer_pos = content.find(f'className:{css_var}.inputFooter')
    if footer_pos == -1:
        footer_pos = content.find(f'className: {css_var}.inputFooter')
    if footer_pos == -1:
        return "_Z"  # default fallback

    # Find the footer function definition (last function before inputFooter)
    search_start = max(0, footer_pos - 5000)
    chunk = content[search_start:footer_pos]
    fn_matches = list(re.finditer(r'function ' + _JS_ID + r'\(\{[^}]+\}\)\{', chunk))
    if not fn_matches:
        fn_matches = list(re.finditer(r'function ' + _JS_ID + r'\([^)]+\)\{', chunk))
    if fn_matches:
        body_start = fn_matches[-1].end()
        body = chunk[body_start:body_start+30]
        call = re.match(r'(' + _JS_ID + r')\(\)', body)
        if call:
            return call.group(1)
    return "_Z"  # default fallback


def detect_footer_function(content, css_var="WJ"):
    """Detect the function name containing the inputFooter return (Yi0, Zi0, etc.)."""
    # Find the position of inputFooter usage in the code
    footer_pos = content.find(f'className:{css_var}.inputFooter')
    if footer_pos == -1:
        footer_pos = content.find(f'className: {css_var}.inputFooter')
    if footer_pos == -1:
        return None

    # Search backwards from inputFooter to find the enclosing function definition.
    # Look for the last "function XXXX(" before this position.
    # We search a reasonable chunk before the inputFooter reference.
    search_start = max(0, footer_pos - 5000)
    chunk = content[search_start:footer_pos]
    # Find all function definitions in this chunk; take the last one
    matches = list(re.finditer(r'function (' + _JS_ID + r')\(', chunk))
    if matches:
        return matches[-1].group(1)
    return None


def patch_js():
    """Patch webview/index.js with session metrics bar + token tracking."""
    print("[1/3] Patching webview/index.js...")

    with open(WEBVIEW_JS, 'r') as f:
        content = f.read()

    prettified = is_prettified(content)
    print(f"  Format: {'prettified' if prettified else 'minified'}")

    # ─── Detect minified variable names ───
    css_var = detect_css_module_var(content)
    react_var = detect_react_var(content, css_var)
    footer_comp = detect_footer_component(content, css_var)
    signal_hook = detect_signal_hook(content, css_var)
    print(f"  Detected: CSS={css_var}, React={react_var}, FooterComp={footer_comp}, SignalHook={signal_hook}")

    # ─── PATCH 0a: usageData signal - add individual token fields ───
    if 'inputTokens:0' not in content and 'inputTokens: 0,' not in content:
        if USAGE_DATA_ORIGINAL in content:
            content = content.replace(USAGE_DATA_ORIGINAL, USAGE_DATA_PATCHED, 1)
            print("  OK: usageData signal patched (prettified)")
        elif re.search(USAGE_DATA_MIN_PATTERN, content):
            content = re.sub(USAGE_DATA_MIN_PATTERN, USAGE_DATA_MIN_REPLACE, content, count=1)
            print("  OK: usageData signal patched (minified)")
        else:
            print("  WARNING: Could not find usageData original pattern")
    else:
        print("  SKIP: usageData already patched")

    # ─── PATCH 0b: updateUsage() - store individual tokens ───
    if 'inputTokens:$.input_tokens' not in content and 'inputTokens: $.input_tokens' not in content:
        if UPDATE_USAGE_ORIGINAL in content:
            content = content.replace(UPDATE_USAGE_ORIGINAL, UPDATE_USAGE_PATCHED, 1)
            print("  OK: updateUsage() patched (prettified)")
        elif UPDATE_USAGE_MIN_ORIGINAL in content:
            content = content.replace(UPDATE_USAGE_MIN_ORIGINAL, UPDATE_USAGE_MIN_PATCHED, 1)
            print("  OK: updateUsage() patched (minified)")
        else:
            print("  WARNING: Could not find updateUsage() original pattern")
    else:
        print("  SKIP: updateUsage() already patched")

    # ─── PATCH 0c: result handler - preserve individual tokens ───
    if 'inputTokens:J.inputTokens' not in content and 'inputTokens: J.inputTokens' not in content:
        if RESULT_HANDLER_ORIGINAL in content:
            content = content.replace(RESULT_HANDLER_ORIGINAL, RESULT_HANDLER_PATCHED, 1)
            print("  OK: result handler patched (prettified)")
        elif RESULT_HANDLER_MIN_ORIGINAL in content:
            content = content.replace(RESULT_HANDLER_MIN_ORIGINAL, RESULT_HANDLER_MIN_PATCHED, 1)
            print("  OK: result handler patched (minified)")
        else:
            print("  WARNING: Could not find result handler original pattern")
    else:
        print("  SKIP: result handler already patched")

    # ─── PATCH 0d: compact_boundary - reset individual tokens ───
    if COMPACT_ORIGINAL in content:
        content = content.replace(COMPACT_ORIGINAL, COMPACT_PATCHED, 1)
        print("  OK: compact_boundary patched (prettified)")
    elif COMPACT_MIN_ORIGINAL in content:
        content = content.replace(COMPACT_MIN_ORIGINAL, COMPACT_MIN_PATCHED, 1)
        print("  OK: compact_boundary patched (minified)")
    elif COMPACT_PATCHED in content or COMPACT_MIN_PATCHED in content:
        print("  SKIP: compact_boundary already patched")
    else:
        print("  WARNING: Could not find compact_boundary pattern")

    # ─── PATCH 1a: Define CC_MetricsBar component ───
    if 'function CC_MetricsBar' not in content:
        # Replace n4 with detected React variable in template
        metrics_def = METRICS_COMPONENT_DEF.replace('n4.', f'{react_var}.')
        metrics_def = metrics_def.replace('_Z();', f'{signal_hook}();')

        if prettified:
            # Prettified: insert as new lines before the footer function
            lines = content.split('\n')
            footer_fn = detect_footer_function(content, css_var)
            insert_line = None

            if footer_fn:
                for i, line in enumerate(lines):
                    if f'function {footer_fn}(' in line:
                        insert_line = i
                        break

            if insert_line is None:
                # Fallback: search for any function line near inputFooter
                for i, line in enumerate(lines):
                    if 'function Zi0({' in line or 'function Zi0(' in line:
                        insert_line = i
                        break

            if insert_line is None:
                print("  ERROR: Could not find footer function definition!")
                return False

            lines.insert(insert_line, metrics_def)
            print(f"  OK: CC_MetricsBar defined at line {insert_line} (prettified)")
            content = '\n'.join(lines)
        else:
            # Minified: use string replacement to inject before the footer function.
            # CANNOT use line-based insertion because minified code has multi-line
            # template literals that would swallow the injected code as string content.
            footer_fn = detect_footer_function(content, css_var)
            if footer_fn:
                anchor = f'function {footer_fn}('
            else:
                print("  ERROR: Could not detect footer function name!")
                return False

            if anchor not in content:
                print(f"  ERROR: Could not find anchor '{anchor}' in content!")
                return False

            # Inject the component definition right before the footer function.
            # The definition ends with a closing brace+newline; add a newline separator.
            content = content.replace(anchor, metrics_def + '\n' + anchor, 1)
            print(f"  OK: CC_MetricsBar defined before {footer_fn} (minified, string replacement)")
    else:
        print("  SKIP: CC_MetricsBar already defined")

    # ─── PATCH 1b: Insert CC_MetricsBar as sibling ABOVE inputFooter via wrapper div ───
    # Build dynamic METRICS_BAR_CALL with correct React var
    metrics_bar_call = f'{react_var}.default.createElement(CC_MetricsBar, {{ session: $ }}),'

    if 'CC_MetricsBar' in content and 'createElement(CC_MetricsBar' not in content:
        if prettified:
            lines = content.split('\n')
            injected = False

            for i in range(len(lines)):
                line = lines[i].strip()
                if f'{{ className: {css_var}.inputFooter }},' in line or f'{{className:{css_var}.inputFooter}},' in line:
                    # Check if footer_comp is on the same line (post-clean scenario)
                    comp_marker = f'{react_var}.default.createElement({footer_comp}'
                    if footer_comp in lines[i]:
                        indent = "    "
                        old_line = lines[i]
                        try:
                            comp_idx = old_line.index(comp_marker)
                        except ValueError:
                            comp_idx = old_line.index(f'.default.createElement({footer_comp}')
                        part1 = old_line[:comp_idx].rstrip()
                        part2 = indent + old_line[comp_idx:]
                        lines[i] = part1
                        lines.insert(i + 1, indent + metrics_bar_call)
                        lines.insert(i + 2, part2)
                        injected = True
                        print(f"  OK: CC_MetricsBar call injected at line {i+1} (same-line split)")
                        break
                    # Normal case: footer_comp on next line
                    for j in range(i + 1, min(i + 5, len(lines))):
                        if footer_comp in lines[j]:
                            indent = "    "
                            lines.insert(j, indent + metrics_bar_call)
                            injected = True
                            print(f"  OK: CC_MetricsBar call injected at line {j}")
                            break
                    if injected:
                        break

            if not injected:
                print("  ERROR: Could not find inputFooter injection point (prettified mode)")
                return False

            content = '\n'.join(lines)
        else:
            # Minified: add CC_MetricsBar as FIRST CHILD of inputFooter.
            # Layout may be squeezed but we can fix with CSS (flex-wrap).
            #
            # Original: return R.createElement("div",{className:CSS.inputFooter}, ...children...)
            # Patched:  return R.createElement("div",{className:CSS.inputFooter}, CC_MetricsBar, ...children...)
            old_return = f'return {react_var}.default.createElement("div",{{className:{css_var}.inputFooter}},'
            new_return = old_return + metrics_bar_call

            if old_return not in content:
                print("  ERROR: Could not find inputFooter return (minified mode)")
                print(f"         Looking for: {old_return[:80]}...")
                return False

            content = content.replace(old_return, new_return, 1)
            print("  OK: CC_MetricsBar injected as first child of inputFooter (minified)")
    elif 'createElement(CC_MetricsBar' in content:
        print("  SKIP: CC_MetricsBar call already injected")

    # ─── PATCH 2: Make er0 always visible ───
    er0_patterns = [
        ('if (U >= 50) return null;', '/* patched: always show */'),
        ('if(U>=50)return null}', '/*er0*/}'),
        ('if(U>=50)return null;', '/* patched: always show */'),
    ]

    er0_patched = False
    for old_pat, new_pat in er0_patterns:
        if old_pat in content:
            content = content.replace(old_pat, new_pat, 1)
            print(f"  OK: er0 visibility check removed (pattern: {old_pat[:30]}...)")
            er0_patched = True
            break

    if not er0_patched:
        if '/* patched: always show */' in content:
            print("  SKIP: er0 already patched")
        else:
            print("  WARNING: Could not find er0 visibility check (may need manual fix)")

    with open(WEBVIEW_JS, 'w') as f:
        f.write(content)

    print("  DONE: webview/index.js patched")
    return True


def patch_css():
    """Patch webview/index.css with flex-wrap and metrics styles."""
    print("[2/3] Patching webview/index.css...")

    with open(WEBVIEW_CSS, 'r') as f:
        content = f.read()

    changed = False

    # CC_MetricsBar is INSIDE inputFooter. Add flex-wrap so it gets its own row.

    # ─── Append custom styles (if not already there) ───
    if '.sessionMetrics_cc' not in content:
        custom_css = (
            '\n/* Custom Session Metrics Bar - cc-improve v12-debug */'
            '\n.inputFooter_gGYT1w{flex-wrap:wrap !important}'
            '\n.sessionMetrics_cc{flex:0 0 100% !important;order:-1 !important}'
        )
        content += custom_css
        print("  OK: Custom CSS appended")
        changed = True
    else:
        print("  SKIP: Custom CSS already present")

    # ─── Stranger Things color palette overrides ───
    if '/* ST palette */' not in content:
        st_css = (
            '\n/* ST palette */'
            '\n:root{--app-claude-orange:#e04040 !important;--app-claude-clay-button-orange:#b82030 !important}'
            '\n.inputContainer_cKsPxg{border-color:rgba(224,64,64,0.25) !important}'
            '\n.inputContainer_cKsPxg:focus-within{border-color:#e04040 !important;box-shadow:0 0 6px rgba(224,64,64,0.3) !important}'
            '\n.inputFooter_gGYT1w{border-top-color:rgba(224,64,64,0.15) !important}'
        )
        content += st_css
        print("  OK: Stranger Things palette CSS appended")
        changed = True
    else:
        print("  SKIP: ST palette CSS already present")

    if changed:
        with open(WEBVIEW_CSS, 'w') as f:
            f.write(content)

    print("  DONE: webview/index.css patched")
    return True


def verify():
    """Verify patches were applied correctly."""
    print("[3/3] Verifying patches...")

    with open(WEBVIEW_JS, 'r') as f:
        js = f.read()

    with open(WEBVIEW_CSS, 'r') as f:
        css = f.read()

    checks = [
        ("JS: _ccSessionStart defined", "_ccSessionStart = Date.now()" in js),
        ("JS: _ccAccent defined", '_ccAccent = "#e04040"' in js),
        ("JS: _ccDim defined", '_ccDim = "rgba(255,255,255,0.55)"' in js),
        ("JS: _ccV value helper", "function _ccV(" in js),
        ("JS: _ccP icon paths defined", "var _ccP = {" in js and '"brain"' in js),
        ("JS: _ccIcon function present", "function _ccIcon(" in js),
        ("JS: _ccBar helper present", "function _ccBar(" in js),
        ("JS: _ccDustinImg defined", "_ccDustinImg" in js and "data:image/png;base64," in js),
        ("JS: _ccAvatar function present", "function _ccAvatar()" in js),
        ("JS: metrics component present", "function CC_MetricsBar" in js),
        ("JS: metrics bar in DOM", "sessionMetrics_cc" in js),
        ("JS: CC_MetricsBar call injected", 'createElement(CC_MetricsBar' in js),
        ("JS: row layout (flexDirection row)", 'flexDirection: "row"' in js),
        ("JS: avatar called", "_ccAvatar()" in js),
        ("JS: icons used in Row1", '_ccIcon("brain"' in js and '_ccIcon("dollar"' in js and '_ccIcon("layers"' in js),
        ("JS: icons used in Row2", '_ccIcon("arrowDown"' in js and '_ccIcon("arrowUp"' in js),
        ("JS: icons used in Row3", '_ccIcon("zap"' in js and '_ccIcon("calDays"' in js and '_ccIcon("timer"' in js),
        ("JS: icons used in Row4", '_ccIcon("clock"' in js and '_ccIcon("calClock"' in js),
        ("JS: usageData has inputTokens", "inputTokens:0" in js or "inputTokens: 0," in js),
        ("JS: updateUsage stores individual tokens", "inputTokens:$.input_tokens" in js or "inputTokens: $.input_tokens" in js),
        ("JS: result handler preserves tokens", "inputTokens:J.inputTokens" in js or "inputTokens: J.inputTokens" in js),
        ("JS: compact_boundary resets tokens", "inputTokens:0,outputTokens:0" in js or "inputTokens: 0, outputTokens: 0" in js),
        ("JS: Row2 shows totalIn with cache%", "cachePct" in js),
        ("JS: Row3 utilization signals", "S.utilization.value" in js),
        ("JS: Row3 session time", "_ccSessionStart" in js and "sesMin" in js),
        ("JS: Row3 last activity", "S.lastModifiedTime.value" in js),
        ("JS: Row4 reset countdowns", "r5hTime" in js and "r7dCd" in js and "r7dPct" in js),
        ("JS: er0 patched",
            'if (U >= 50) return null;' not in js and
            'if(U>=50)return null}' not in js and
            'if(U>=50)return null;' not in js),
        ("CSS: custom styles", ".sessionMetrics_cc" in css),
        ("CSS: flex-wrap on inputFooter", "flex-wrap:wrap" in css),
        ("CSS: ST palette accent", "--app-claude-orange:#e04040" in css),
        ("CSS: ST palette button", "--app-claude-clay-button-orange:#b82030" in css),
        ("CSS: ST input border", "inputContainer_cKsPxg" in css and "rgba(224,64,64" in css),
        ("JS: dim/accent color scheme", "_ccV(" in js and "color: _ccDim" in js),
        ("JS: Row5 thinking level", "thinkLvl" in js and "thinkClr" in js),
        ("JS: Row5 message count", "msgCount" in js),
        ("JS: Row5 output utilization", "outPct" in js and "outMaxStr" in js),
        ("JS: Row6 cost rate", "costRateStr" in js),
        ("JS: Row6 throughput", "throughStr" in js),
        ("JS: Row6 compaction counter", "_compactRef" in js and "compactCount" in js),
        ("JS: icons used in Row5", '_ccIcon("msgSquare"' in js),
        ("JS: icons used in Row6", '_ccIcon("gauge"' in js),
        ("JS: Row2 workdir display", "cwdStr" in js and "cwdRaw" in js and "S.cwd" in js),
        ("JS: Row2 git branch display", "gitBr" in js and "S.gitBranch" in js),
        ("JS: icons used in Row2 (folder+gitBr)", '_ccIcon("folder"' in js and '_ccIcon("gitBr"' in js),
    ]

    all_ok = True
    for name, ok in checks:
        status = "PASS" if ok else "FAIL"
        print(f"  {status}: {name}")
        if not ok:
            all_ok = False

    return all_ok


def restore():
    """Restore from backup or re-download extension."""
    print("Restoring original files from backup...")
    backup_js = os.path.join(BACKUP_DIR, "webview-index.js.bak")
    backup_css = os.path.join(BACKUP_DIR, "webview-index.css.bak")

    if os.path.exists(backup_js):
        shutil.copy2(backup_js, WEBVIEW_JS)
        print(f"  Restored JS ({os.path.getsize(WEBVIEW_JS)} bytes)")
    else:
        print(f"  WARNING: JS backup not found at {backup_js}")

    if os.path.exists(backup_css):
        shutil.copy2(backup_css, WEBVIEW_CSS)
        print(f"  Restored CSS ({os.path.getsize(WEBVIEW_CSS)} bytes)")
    else:
        print(f"  WARNING: CSS backup not found at {backup_css}")

    print("DONE: Restore complete.")


def clean():
    """Remove all patches, leaving clean prettified code."""
    print("Cleaning patches from files...")

    with open(WEBVIEW_JS, 'r') as f:
        js = f.read()

    # For minified code: remove entire metrics block as a single unit.
    # In minified code, 'function ai0(' was in the MIDDLE of a huge line.
    # The injection split it with newlines. Clean must rejoin by removing
    # ALL newlines around the block (replace with empty string, not '\n').
    if not is_prettified(js) and 'var _ccSessionStart' in js:
        js = re.sub(
            r'\n+var _ccSessionStart = Date\.now\(\);.*?function CC_MetricsBar\(\{[^}]*\}\)[^\n]*\n.*?\n\}\n*',
            '', js, count=1, flags=re.DOTALL
        )

    # Remove _ccSessionStart variable
    js_clean = re.sub(r'\nvar _ccSessionStart = Date\.now\(\);\n', '\n', js, count=1)

    # Remove _ccAccent variable
    js_clean = re.sub(r'\nvar _ccAccent = "[^"]*";\n', '\n', js_clean, count=1)

    # Remove _ccDim variable
    js_clean = re.sub(r'\nvar _ccDim = "[^"]*";\n', '\n', js_clean, count=1)

    # Remove _ccV function (single line - use [^\n]* to handle nested braces)
    js_clean = re.sub(r'\nfunction _ccV\([^)]*\)[^\n]*\n', '\n', js_clean)

    # Remove _ccP icon paths object (multi-line)
    pattern_icons = r'\nvar _ccP = \{.*?\n\};\n'
    js_clean = re.sub(pattern_icons, '\n', js_clean, count=1, flags=re.DOTALL)

    # Remove _ccIcon function definition (multi-line)
    pattern_icon_fn = r'\nfunction _ccIcon\([^)]*\).*?\n\}\n'
    js_clean = re.sub(pattern_icon_fn, '\n', js_clean, count=1, flags=re.DOTALL)

    # Remove _ccBar helper function
    pattern_bar = r'\nfunction _ccBar\([^)]*\).*?\n\}\n'
    js_clean = re.sub(pattern_bar, '\n', js_clean, count=1, flags=re.DOTALL)

    # Remove _ccDustinImg variable (single long line with base64)
    js_clean = re.sub(r'\nvar _ccDustinImg = "[^"]*";\n', '\n', js_clean, count=1)

    # Remove _ccAvatar function definition (multi-line)
    pattern_avatar = r'\nfunction _ccAvatar\(\).*?\n\}\n'
    js_clean = re.sub(pattern_avatar, '\n', js_clean, count=1, flags=re.DOTALL)

    # Remove CC_MetricsBar component definition (multi-line)
    pattern_def = r'\nfunction CC_MetricsBar\(\{[^}]*\}.*?\n\}\n'
    js_clean = re.sub(pattern_def, '\n', js_clean, count=1, flags=re.DOTALL)

    # Remove CC_MetricsBar call - handle both prettified (with newlines) and minified (inline)
    # Pattern covers both: {session:$} (no spaces) and { session: $ } (with spaces)
    js_clean = re.sub(r'' + _JS_ID + r'\.default\.createElement\(CC_MetricsBar,\s*\{[^}]*\}\),?', '', js_clean, count=1)

    # No wrapper div to remove — CC_MetricsBar is inside inputFooter.
    # The CC_MetricsBar createElement call removal (above) handles it.

    # Reverse usageData signal patch (prettified and minified)
    js_clean = js_clean.replace(USAGE_DATA_PATCHED, USAGE_DATA_ORIGINAL)
    # For minified: remove added fields from usageData signal
    js_clean = re.sub(r',inputTokens:0,outputTokens:0,cacheCreation:0,cacheRead:0\}', '}', js_clean)

    # Reverse updateUsage() patch (prettified and minified)
    js_clean = js_clean.replace(UPDATE_USAGE_PATCHED, UPDATE_USAGE_ORIGINAL)
    js_clean = js_clean.replace(UPDATE_USAGE_MIN_PATCHED, UPDATE_USAGE_MIN_ORIGINAL)

    # Reverse result handler patch (prettified and minified)
    js_clean = js_clean.replace(RESULT_HANDLER_PATCHED, RESULT_HANDLER_ORIGINAL)
    js_clean = js_clean.replace(RESULT_HANDLER_MIN_PATCHED, RESULT_HANDLER_MIN_ORIGINAL)

    # Reverse compact_boundary patch (prettified and minified)
    js_clean = js_clean.replace(COMPACT_PATCHED, COMPACT_ORIGINAL)
    js_clean = js_clean.replace(COMPACT_MIN_PATCHED, COMPACT_MIN_ORIGINAL)

    # Restore er0 visibility check
    js_clean = js_clean.replace('/*er0*/}', 'if(U>=50)return null}')
    js_clean = js_clean.replace('/* patched: always show */', 'if (U >= 50) return null;')

    with open(WEBVIEW_JS, 'w') as f:
        f.write(js_clean)
    print("  OK: JS cleaned")

    with open(WEBVIEW_CSS, 'r') as f:
        css = f.read()

    # Remove custom CSS (sessionMetrics + ST palette - everything after the marker)
    css = re.sub(r'\n/\* Custom Session Metrics Bar.*$', '', css, flags=re.DOTALL)
    # Remove ST palette CSS (in case it was added separately)
    css = re.sub(r'\n/\* ST palette \*/.*$', '', css, flags=re.DOTALL)
    # Note: inputFooter CSS is no longer modified (wrapper approach), no revert needed

    with open(WEBVIEW_CSS, 'w') as f:
        f.write(css)
    print("  OK: CSS cleaned")

    print("DONE: All patches removed.")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "apply"

    if mode == "apply":
        print("=" * 60)
        print("cc-metrics v12: Applying UI patches to Claude Code Extension")
        print("=" * 60)
        print(f"Extension: {EXT_DIR}")
        print(f"JS size: {os.path.getsize(WEBVIEW_JS):,} bytes")
        print(f"Avatar b64: {len(DUSTIN_IMG_B64)} chars")
        print()

        ok1 = patch_js()
        ok2 = patch_css()
        ok3 = verify()

        if ok1 and ok2 and ok3:
            print("\n" + "=" * 60)
            print("ALL PATCHES APPLIED SUCCESSFULLY!")
            print("Reload VSCode: Ctrl+Shift+P > Developer: Reload Window")
            print("=" * 60)
        else:
            print("\nSome patches failed. Check errors above.")
            sys.exit(1)

    elif mode == "backup":
        os.makedirs(BACKUP_DIR, exist_ok=True)
        shutil.copy2(WEBVIEW_JS, os.path.join(BACKUP_DIR, "webview-index.js.bak"))
        shutil.copy2(WEBVIEW_CSS, os.path.join(BACKUP_DIR, "webview-index.css.bak"))
        print(f"Backed up to {BACKUP_DIR}")
        print(f"  JS:  {os.path.getsize(WEBVIEW_JS):,} bytes")
        print(f"  CSS: {os.path.getsize(WEBVIEW_CSS):,} bytes")

    elif mode == "restore":
        restore()

    elif mode == "clean":
        clean()

    elif mode == "verify":
        verify()

    else:
        print(f"Usage: {sys.argv[0]} [apply|backup|restore|clean|verify]")
        print("  apply   - Apply UI patches (idempotent)")
        print("  backup  - Backup original extension files")
        print("  restore - Restore from backup files")
        print("  clean   - Remove patches from current files")
        print("  verify  - Check if patches are applied")
        sys.exit(1)


if __name__ == "__main__":
    main()
