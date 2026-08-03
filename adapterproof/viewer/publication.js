const $ = (selector) => document.querySelector(selector);
const node = (tag, text, className = "") => {
  const result = document.createElement(tag);
  result.textContent = text;
  result.className = className;
  return result;
};
const pretty = (value) => value.replaceAll("_", " ");

function renderProof(card, item) {
  const receipts = card.querySelector(".proof-receipts");
  receipts.replaceChildren(...item.receipt_classifications.map((receipt, index) => {
    const box = node("div", "");
    box.append(node("small", `RECEIPT ${String(index + 1).padStart(2, "0")}`), node("strong", pretty(receipt)));
    return box;
  }));
  const metrics = card.querySelector("dl");
  const values = [
    ["requests", `${item.actual_requests} / ${item.expected_requests}`],
    ["final state", pretty(item.actual_state)],
    ["case gate", item.passed ? "PASS" : "FAIL"],
  ];
  metrics.replaceChildren(...values.map(([label, value]) => {
    const group = document.createElement("div");
    group.append(node("dt", label), node("dd", value));
    return group;
  }));
}

const params = new URLSearchParams(location.search);
const selectedFrame = params.get("frame") || "cover";
document.querySelectorAll("[data-frame]").forEach((frame) => {
  frame.hidden = frame.dataset.frame !== selectedFrame;
});

const response = await fetch("/api/report", { cache: "no-store" });
if (!response.ok) throw new Error(`report request failed: ${response.status}`);
const report = await response.json();
const adapter = report.adapters.find((item) => item.adapter_id === "notification_sink") || report.adapters[0];
const cases = report.adapters.flatMap((item) => item.cases);
const passed = cases.filter((item) => item.passed).length;

$("#cover-score").textContent = `${passed}/${cases.length}`;
$("#cover-request").textContent = `${adapter.wire_contract.method} ${adapter.wire_contract.endpoint_path}`;
$("#cover-headers").textContent = adapter.wire_contract.headers.map((item) => item.name).join(" · ");
$("#cover-payload").textContent = JSON.stringify(adapter.mapped_payload, null, 2);
$("#cover-cases").replaceChildren(...adapter.cases.slice(0, 8).map((item, index) => {
  const row = document.createElement("div");
  row.append(node("span", String(index + 1).padStart(2, "0")), node("strong", pretty(item.case)), node("i", item.passed ? "PASS" : "FAIL"));
  return row;
}));

$("#flow-manifest").textContent = `${adapter.manifest_hash.slice(0, 16)}…`;
$("#flow-request").textContent = `${adapter.wire_contract.method} ${adapter.wire_contract.endpoint_path}`;
$("#flow-score").textContent = `${passed}/${cases.length} cases pass`;
$("#flow-payload").textContent = JSON.stringify(adapter.mapped_payload, null, 2);
$("#flow-headers").replaceChildren(...adapter.wire_contract.headers.map((header) => {
  const row = document.createElement("div");
  row.append(node("code", header.name), node("span", header.value));
  return row;
}));

const indexed = Object.fromEntries(adapter.cases.map((item) => [item.case, item]));
renderProof($("#proof-recovery"), indexed.rate_limit_then_success);
renderProof($("#proof-stopped"), indexed.server_error_exhausted);
document.body.dataset.ready = "true";
