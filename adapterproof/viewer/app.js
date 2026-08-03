const state = { report: null, adapter: 0, caseName: "rate_limit_then_success" };

const $ = (selector) => document.querySelector(selector);
const pretty = (value) => value.replaceAll("_", " ");
const title = (value) => pretty(value).replace(/\b\w/g, (letter) => letter.toUpperCase());
const node = (tag, className, text) => {
  const result = document.createElement(tag);
  if (className) result.className = className;
  if (text !== undefined) result.textContent = text;
  return result;
};

function reportSummary(report) {
  const cases = report.adapters.flatMap((adapter) => adapter.cases);
  return {
    passed: cases.filter((item) => item.passed).length,
    total: cases.length,
    secretsPersisted: report.adapters.some((adapter) => adapter.secret_value_persisted),
  };
}

function renderSwitcher() {
  $("#adapter-switcher").replaceChildren(...state.report.adapters.map((adapter, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = index === state.adapter ? "adapter-button active" : "adapter-button";
    button.append(
      node("span", "", `0${index + 1}`),
      node("strong", "", pretty(adapter.adapter_id)),
      node("small", "", adapter.gate),
    );
    button.addEventListener("click", () => {
      state.adapter = index;
      render();
    });
    return button;
  }));
}

function renderHeaders(contract) {
  $("#headers").replaceChildren(...contract.headers.map((header) => {
    const row = document.createElement("div");
    row.append(node("code", "", header.name), node("span", "", header.value));
    row.title = header.source;
    return row;
  }));
}

function renderCases(adapter) {
  if (!adapter.cases.some((item) => item.case === state.caseName)) {
    state.caseName = adapter.cases[0].case;
  }
  $("#case-list").replaceChildren(...adapter.cases.map((item, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = item.case === state.caseName ? "case-button active" : "case-button";
    button.dataset.case = item.case;
    button.append(
      node("span", "", String(index + 1).padStart(2, "0")),
      node("strong", "", pretty(item.case)),
      node("i", "", item.passed ? "pass" : "fail"),
    );
    button.addEventListener("click", () => {
      state.caseName = item.case;
      render();
    });
    return button;
  }));
}

function renderReceipts(adapter) {
  const selected = adapter.cases.find((item) => item.case === state.caseName);
  $("#case-title").textContent = title(selected.case);
  $("#case-detail").textContent = selected.detail;
  $("#request-count").textContent = `${selected.actual_requests} / ${selected.expected_requests}`;
  $("#final-state").textContent = pretty(selected.actual_state);
  $("#case-result").textContent = selected.passed ? "PASS" : "FAIL";
  const receipts = selected.receipt_classifications.length ? selected.receipt_classifications : ["no transport"];
  $("#receipts").replaceChildren(...receipts.map((receipt, index) => {
    const item = document.createElement("div");
    item.className = `receipt ${receipt.includes("success") ? "success" : ""}`;
    item.append(
      node("span", "", `receipt ${String(index + 1).padStart(2, "0")}`),
      node("strong", "", pretty(receipt)),
    );
    return item;
  }));
}

function render() {
  const report = state.report;
  const adapter = report.adapters[state.adapter];
  const summary = reportSummary(report);
  $("#run-state").textContent = `${report.gate} · generated report`;
  $("#case-score").textContent = `${summary.passed}/${summary.total}`;
  $("#adapter-count").textContent = report.adapters.length;
  $("#secret-state").textContent = summary.secretsPersisted ? "YES" : "NO";
  $("#manifest-hash").textContent = adapter.manifest_hash;
  $("#adapter-title").textContent = pretty(adapter.adapter_id);
  $("#adapter-gate").textContent = adapter.gate;
  $("#request-method").textContent = adapter.wire_contract.method;
  $("#request-path").textContent = adapter.wire_contract.endpoint_path;
  $("#payload").textContent = JSON.stringify(adapter.mapped_payload, null, 2);
  $("#foundation").textContent = `${report.foundation} · DeliveryGuard ${report.deliveryguard}`;
  renderSwitcher();
  renderHeaders(adapter.wire_contract);
  renderCases(adapter);
  renderReceipts(adapter);
}

try {
  const response = await fetch("/api/report", { cache: "no-store" });
  if (!response.ok) throw new Error(`report request failed: ${response.status}`);
  state.report = await response.json();
  render();
} catch (error) {
  $("#run-state").textContent = "report unavailable";
  $("#case-detail").textContent = error.message;
  document.body.dataset.error = "true";
}
