const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Generic fetch wrapper with error handling.
 */
async function apiFetch(endpoint, options = {}) {
  const defaultHeaders = {};
  // Only set Content-Type for non-FormData bodies
  if (!(options.body instanceof FormData)) {
    defaultHeaders['Content-Type'] = 'application/json';
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      ...defaultHeaders,
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!res.ok) {
    const errorBody = await res.text();
    throw new Error(
      `API Error ${res.status}: ${res.statusText} — ${errorBody}`
    );
  }

  return await res.json();
}

/* ──────────────────────────────────────────────
   User endpoints
   ────────────────────────────────────────────── */

export async function fetchUser(userId) {
  return apiFetch(`/users/${userId}`);
}

export async function fetchUsers() {
  return apiFetch('/users');
}

/* ──────────────────────────────────────────────
   Income endpoint — normalized for dashboard
   ────────────────────────────────────────────── */

export async function fetchIncomeSummary(userId) {
  const data = await apiFetch(`/income/${userId}`);

  // Normalize backend field names → what the dashboard consumes
  // Backend returns: total_gross_income, total_tds_deducted, by_platform, by_month
  // Dashboard expects: total_income, total_tds, platforms, monthly_income
  return {
    ...data,
    // top-level totals
    total_income: data.total_gross_income ?? data.total_income ?? 0,
    total_tds: data.total_tds_deducted ?? data.total_tds ?? 0,
    gross_income: data.total_gross_income ?? data.gross_income ?? 0,

    // platform breakdown: backend uses by_platform[]
    platforms: (data.by_platform ?? data.platforms ?? []).map((p) => ({
      ...p,
      name: p.platform ?? p.name,
      income: p.gross_income ?? p.income ?? p.amount ?? 0,
      tds: p.tds_deducted ?? p.tds ?? 0,
    })),
    platform_count: (data.by_platform ?? data.platforms ?? []).length,

    // monthly breakdown: backend uses by_month[]
    // Dashboard monthly chart expects: { month, amount }
    monthly_income: (data.by_month ?? data.monthly_income ?? data.monthly ?? []).map(
      (m) => ({
        ...m,
        month: m.month ?? m.month_name,
        amount: m.gross_income ?? m.amount ?? m.income ?? 0,
      })
    ),
  };
}

/* ──────────────────────────────────────────────
   Tax endpoints — normalized for dashboard
   ────────────────────────────────────────────── */

export async function fetchTaxCalculation(userId) {
  const data = await apiFetch(`/tax/${userId}`);

  // Backend returns: gross_income, taxable_income, total_tax, tds_credit,
  //                  net_payable, tax_before_cess, cess, slab_breakdown,
  //                  section_44ADA_applied, presumptive_income
  // Dashboard also looks for: tax_liability, deduction_44ada, section_87a_rebate
  const gross = data.gross_income ?? 0;
  const presumptive = data.presumptive_income ?? null;
  const deduction44ADA = presumptive != null ? gross - presumptive : Math.round(gross * 0.5);

  // Rebate 87A: backend bakes it in but doesn't surface it separately.
  // Re-derive: if taxable_income ≤ 12,00,000 rebate = min(tax_before_cess, 60,000)
  const taxable = data.taxable_income ?? 0;
  const taxBeforeCess = data.tax_before_cess ?? 0;
  const rebate87A =
    data.rebate_87a ??
    data.section_87a_rebate ??
    (taxable <= 1200000 ? Math.min(taxBeforeCess, 60000) : 0);

  return {
    ...data,
    tax_liability: data.total_tax ?? data.tax_liability ?? 0,
    deduction_44ada: deduction44ADA,
    section_87a_rebate: rebate87A,
    tds_credit: data.tds_credit ?? 0,
    net_payable: data.net_payable ?? 0,
  };
}

export async function fetchDeductions(userId) {
  return apiFetch(`/tax/${userId}/deductions`);
}

export async function fetchITRSummary(userId) {
  return apiFetch(`/tax/${userId}/itr`);
}

/* ──────────────────────────────────────────────
   Deadlines — normalized for dashboard
   ────────────────────────────────────────────── */

export async function fetchDeadlines(userId) {
  const data = await apiFetch(`/deadlines/${userId}`);

  // Backend returns: { deadlines: [...], next_deadline: {...}, alert_level, ... }
  // Dashboard does: Array.isArray(deadlines) ? deadlines[0] : deadlines
  // So we surface next_deadline as the primary value (object form).
  const next = data.next_deadline ?? (Array.isArray(data.deadlines) ? data.deadlines.find((d) => !d.is_past) : null);

  if (!next) return null;

  // Normalize field names the deadline banner expects
  return {
    ...next,
    title: next.title ?? next.name ?? 'Advance Tax Due',
    date: next.due_date ?? next.date,
    amount: next.amount_due ?? next.amount ?? 0,
  };
}

/* ──────────────────────────────────────────────
   PDF Upload
   ────────────────────────────────────────────── */

export async function uploadPDFs(userId, files) {
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }

  return apiFetch(`/upload/${userId}`, {
    method: 'POST',
    body: formData,
    // Content-Type is NOT set — browser adds multipart boundary automatically
  });
}

/* ──────────────────────────────────────────────
   Chat — regular request/response
   ────────────────────────────────────────────── */

export async function sendChatMessage(userId, message) {
  return apiFetch('/chat', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, message }),
  });
}

/* ──────────────────────────────────────────────
   Chat — SSE streaming
   ────────────────────────────────────────────── */

export async function streamChat(userId, message, onChunk) {
  const res = await fetch(`${API_BASE}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, message }),
  });

  if (!res.ok) {
    const errorBody = await res.text();
    throw new Error(
      `Stream Error ${res.status}: ${res.statusText} — ${errorBody}`
    );
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Process SSE lines from the buffer
    const lines = buffer.split('\n');
    // Keep the last (possibly incomplete) line in the buffer
    buffer = lines.pop() || '';

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith(':')) continue;

      if (trimmed.startsWith('data: ')) {
        const data = trimmed.slice(6);
        if (data === '[DONE]') return;

        try {
          const parsed = JSON.parse(data);
          onChunk(parsed);
        } catch {
          onChunk({ content: data });
        }
      }
    }
  }
}

export async function clearChatHistory(userId) {
  return apiFetch(`/chat/${userId}/history`, {
    method: 'DELETE',
  });
}
