const txnType = document.getElementById("txn_type");
const targetWrap = document.getElementById("target-account-wrap");
const targetInput = targetWrap ? targetWrap.querySelector("input") : null;

function refreshTransactionForm() {
  if (!txnType || !targetWrap || !targetInput) {
    return;
  }
  const showTarget = txnType.value === "Transfer";
  targetWrap.hidden = !showTarget;
  targetInput.required = showTarget;
}

if (txnType) {
  txnType.addEventListener("change", refreshTransactionForm);
  refreshTransactionForm();
}

async function parseApiError(response) {
  try {
    const payload = await response.json();
    if (payload && typeof payload.error === "string") {
      return payload.error;
    }
  } catch (err) {
    return `Request failed with status ${response.status}.`;
  }
  return `Request failed with status ${response.status}.`;
}

const accountUpdateForms = document.querySelectorAll(".js-account-update-form");
const accountCloseForms = document.querySelectorAll(".js-account-close-form");

accountUpdateForms.forEach((form) => {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const accountNo = form.dataset.accountNo;
    const csrfToken = form.querySelector("[name='csrf_token']")?.value;
    const accType = form.querySelector("[name='acc_type']")?.value;
    const branchId = form.querySelector("[name='branch_id']")?.value;

    if (!accountNo || !csrfToken) {
      window.alert("Missing account details for update.");
      return;
    }

    const response = await fetch(`/api/accounts/${accountNo}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrfToken,
      },
      body: JSON.stringify({
        acc_type: accType,
        branch_id: branchId,
      }),
    });

    if (!response.ok) {
      const message = await parseApiError(response);
      window.alert(message);
      return;
    }

    window.location.reload();
  });
});

accountCloseForms.forEach((form) => {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const accountNo = form.dataset.accountNo;
    const csrfToken = form.querySelector("[name='csrf_token']")?.value;

    if (!accountNo || !csrfToken) {
      window.alert("Missing account details for close request.");
      return;
    }

    const shouldClose = window.confirm(`Close account ${accountNo}? This action cannot be undone.`);
    if (!shouldClose) {
      return;
    }

    const response = await fetch(`/api/accounts/${accountNo}`, {
      method: "DELETE",
      headers: {
        "X-CSRF-Token": csrfToken,
      },
    });

    if (!response.ok) {
      const message = await parseApiError(response);
      window.alert(message);
      return;
    }

    window.location.reload();
  });
});
