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
