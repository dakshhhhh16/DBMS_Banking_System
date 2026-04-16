const fmt = n => "₹" + Number(n).toLocaleString("en-IN");

const endpoints = {
  customers:    "/api/customers",
  accounts:     "/api/accounts",
  branches:     "/api/branches",
  loans:        "/api/loans",
  transactions: "/api/transactions",
  employees:    "/api/employees",
};

const moneyFields = new Set([
  "Balance", "Assets", "Deposits", "Amount", "Paid", "Remaining", "Salary"
]);

async function loadDashboard() {
  const s = await fetch("/api/summary").then(r => r.json());
  document.getElementById("c-branches").textContent  = s.branches;
  document.getElementById("c-customers").textContent = s.customers;
  document.getElementById("c-accounts").textContent  = s.accounts;
  document.getElementById("c-loans").textContent     = s.loans;
  document.getElementById("c-deposit").textContent   = fmt(s.total_deposit);
  document.getElementById("c-loan").textContent      = fmt(s.total_loan);
}

async function loadTable(name) {
  const wrap = document.querySelector(`#${name} .table-wrap`);
  if (wrap.dataset.loaded) return;

  const data = await fetch(endpoints[name]).then(r => r.json());
  if (!data.length) { wrap.innerHTML = "<p style='padding:20px'>No data</p>"; return; }

  const cols = Object.keys(data[0]);
  const head = cols.map(c => `<th>${c.replace(/_/g, " ")}</th>`).join("");
  const rows = data.map(row =>
    "<tr>" + cols.map(c => {
      const v = row[c];
      return `<td>${moneyFields.has(c) && v != null ? fmt(v) : (v ?? "")}</td>`;
    }).join("") + "</tr>"
  ).join("");

  wrap.innerHTML = `<table><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table>`;
  wrap.dataset.loaded = "1";
}

document.querySelectorAll(".tab").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    const name = btn.dataset.tab;
    document.getElementById(name).classList.add("active");
    if (name !== "dashboard") loadTable(name);
  });
});

loadDashboard();
