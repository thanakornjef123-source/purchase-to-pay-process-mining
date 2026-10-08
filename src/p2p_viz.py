"""Consistent Graphviz styling for every process diagram in the project.

PM4Py's own visualisers draw oversized start/end symbols and place edge labels
on top of lines, so the DFG and the discovered BPMN are re-drawn here from
PM4Py's objects (the discovery itself is unchanged).
"""
import graphviz

FONT = "Helvetica"
BLUE_FILL, BLUE_LINE = "#e8f1f8", "#2a6f97"
RED_FILL, RED_LINE = "#fdecea", "#c44e52"
GREEN_FILL, GREEN_LINE = "#e3f4e1", "#3a7d44"
GATE_FILL, GATE_LINE = "#fff7d6", "#b08900"
EVENT_SIZE = "0.28"          # same start/end size in every diagram


def new_graph(name, title=None, rankdir="LR", **graph):
    attrs = {"rankdir": rankdir, "splines": "spline", "nodesep": "0.45", "ranksep": "0.55",
             "fontname": FONT, "fontsize": "13", "pad": "0.25", "forcelabels": "true"}
    if title:
        attrs.update(label=title + "\n ", labelloc="t")   # blank line keeps the title off the first node
    attrs.update(graph)
    return graphviz.Digraph(name,
                            graph_attr=attrs,
                            node_attr={"fontname": FONT, "fontsize": "10"},
                            edge_attr={"fontname": FONT, "fontsize": "9", "color": "#555555",
                                       "arrowsize": "0.7", "labeldistance": "1.6"})


def start(g, name="start"):
    g.node(name, "", shape="circle", width=EVENT_SIZE, height=EVENT_SIZE, fixedsize="true",
           style="filled", fillcolor="#7fbf7f", color="#3a7d44", penwidth="1.2")


def end(g, name="end"):
    g.node(name, "", shape="doublecircle", width=EVENT_SIZE, height=EVENT_SIZE, fixedsize="true",
           style="filled", fillcolor="#f4a261", color="#9c5b1f", penwidth="1.2")


def task(g, name, label, kind="normal", **kw):
    fill, line = {"normal": (BLUE_FILL, BLUE_LINE), "issue": (RED_FILL, RED_LINE),
                  "new": (GREEN_FILL, GREEN_LINE)}[kind]
    g.node(name, label, shape="box", style="rounded,filled", fillcolor=fill, color=line,
           margin="0.14,0.07", **kw)


def gateway(g, name, label="", **kw):
    attrs = {"fontsize": "9", **kw}
    g.node(name, label, shape="diamond", style="filled", fillcolor=GATE_FILL, color=GATE_LINE, **attrs)


def note(g, name, label):
    g.node(name, label, shape="note", style="filled", fillcolor=RED_FILL, color=RED_LINE, fontsize="9")


def wrap(text, width=18):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    return "\\n".join(lines)


def dfg_graph(dfg, start_acts, end_acts, act_counts, title=None, rankdir="LR"):
    """Frequency DFG. Edge width scales with frequency; labels sit on the edge, not over it."""
    g = new_graph("dfg", title, rankdir, nodesep="0.55", ranksep="0.6")
    top = max(list(dfg.values()) + list(start_acts.values()) + list(end_acts.values()))
    pen = lambda n: f"{0.8 + 3.2 * n / top:.2f}"
    ids = {a: f"a{i}" for i, a in enumerate(sorted(act_counts))}
    for a, n in act_counts.items():
        task(g, ids[a], f"{wrap(a)}\\n({n:,})")
    start(g); end(g)
    for a, n in start_acts.items():
        g.edge("start", ids[a], label=f" {n:,} ", penwidth=pen(n))
    for a, n in end_acts.items():
        g.edge(ids[a], "end", label=f" {n:,} ", penwidth=pen(n))
    for (a, b), n in dfg.items():
        if a == b:   # self-loop: dot places a plain label beside the loop
            g.edge(ids[a], ids[b], label=f" {n:,} ", penwidth=pen(n))
        else:
            g.edge(ids[a], ids[b], label=f" {n:,} ", penwidth=pen(n))
    return g


def bpmn_graph(bpmn, title=None, rankdir="LR", compact=False):
    """Draw a PM4Py BPMN object top-to-bottom (or left-to-right) in process order.

    - pass-through gateways (1 in, 1 out, left over from tau loops) are dropped;
    - loop-back edges are found with a depth-first walk from the start event and drawn
      with constraint=false, so Graphviz ranks nodes by the forward flow and the layout
      does not depend on PM4Py's random node ids.
    """
    nodes = {n.get_id(): n for n in bpmn.get_nodes()}
    edges = {(f.get_source().get_id(), f.get_target().get_id()) for f in bpmn.get_flows()}
    kind = lambda n: type(nodes[n]).__name__
    changed = True
    while changed:
        changed = False
        for n in list(nodes):
            if "Gateway" not in kind(n):
                continue
            ins = [s for s, t in edges if t == n]
            outs = [t for s, t in edges if s == n]
            if len(ins) == 1 and len(outs) == 1 and ins[0] != outs[0]:
                edges -= {(ins[0], n), (n, outs[0])}
                edges.add((ins[0], outs[0]))
                del nodes[n]
                changed = True

    # deterministic labels for ordering: tasks by name, gateways by the first task they lead to
    succ = {n: sorted(t for s, t in edges if s == n) for n in nodes}
    def first_task(n, seen=()):
        if "Gateway" not in kind(n) and "Event" not in kind(n):
            return nodes[n].get_name()
        if n in seen:
            return "~"
        return min((first_task(t, seen + (n,)) for t in succ[n]), default="~")
    pred = {n: sorted(s for s, t in edges if t == n) for n in nodes}
    def last_task(n, seen=()):
        if "Gateway" not in kind(n) and "Event" not in kind(n):
            return nodes[n].get_name()
        if n in seen:
            return "~"
        return min((last_task(p_, seen + (n,)) for p_ in pred[n]), default="")
    key = {n: (first_task(n), kind(n), last_task(n), len(succ[n]), len(pred[n])) for n in nodes}
    for n in succ:
        succ[n].sort(key=lambda t: key[t])
    start_id = next(n for n in nodes if kind(n) == "StartEvent")
    back, state = set(), {}
    def dfs(n):
        state[n] = "open"
        for t in succ[n]:
            if state.get(t) == "open":
                back.add((n, t))
            elif t not in state:
                dfs(t)
        state[n] = "done"
    dfs(start_id)
    order = {n: i for i, n in enumerate(state)}            # DFS visit order (deterministic)
    name = {n: f"n{order.get(n, len(order) + i)}" for i, n in enumerate(sorted(nodes, key=lambda n: key[n]))}

    g = new_graph("bpmn", title, rankdir, nodesep="0.3" if compact else "0.4",
                  ranksep="0.2" if compact else "0.38")
    if compact:   # larger text for a tall diagram printed on one page
        g.node_attr["fontsize"] = "15"
    for nid in sorted(nodes, key=lambda n: name[n]):
        n, k = nodes[nid], kind(nid)
        if k == "StartEvent":
            start(g, name[nid])
        elif "EndEvent" in k:
            end(g, name[nid])
        elif k == "ParallelGateway":
            gateway(g, name[nid], "+", width="0.36" if compact else "0.42", height="0.36" if compact else "0.42", fixedsize="true", fontsize="14")
        elif "Gateway" in k:
            gateway(g, name[nid], "×", width="0.36" if compact else "0.42", height="0.36" if compact else "0.42", fixedsize="true", fontsize="12")
        else:
            task(g, name[nid], wrap(n.get_name(), 26 if compact else 22))
    for s_, t in sorted(edges, key=lambda e: (name[e[0]], name[e[1]])):
        if (s_, t) in back:
            g.edge(name[s_], name[t], constraint="false", color="#8a8a8a", style="dashed")
        else:
            g.edge(name[s_], name[t])
    return g
