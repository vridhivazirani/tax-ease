'use client';

import { useSearchParams } from 'next/navigation';
import { Suspense, useEffect, useState } from 'react';
import Link from 'next/link';
import { fetchITRSummary } from '@/lib/api';
import styles from './itr.module.css';

/* ────────────────────────────────────────────────
   Helpers
   ──────────────────────────────────────────────── */

function formatINR(amount) {
  if (amount == null) return '₹0';
  const num = Number(amount);
  return '₹' + num.toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

function formatPercent(rate) {
  if (rate == null) return '0%';
  const num = Number(rate);
  // If the rate is already in percent form (e.g. 5, 10, 20), show as-is
  // If decimal (e.g. 0.05), convert
  const pct = num > 1 ? num : num * 100;
  return pct % 1 === 0 ? `${pct}%` : `${pct.toFixed(1)}%`;
}

/* ────────────────────────────────────────────────
   Fallback / Mock Data
   ──────────────────────────────────────────────── */

const FALLBACK_DATA = {
  personal_info: {
    name: 'Ravi Kumar',
    pan: 'ABCPK1234F',
    state: 'Karnataka',
    filing_status: 'Individual',
    tax_regime: 'New Regime (u/s 115BAC)',
  },
  schedule_bp: {
    nature_of_business: 'Transportation / Delivery Services',
    gross_receipts: 336000,
    presumptive_income: 168000,
    presumptive_rate: 50,
    section_44ada: true,
    platform_receipts: [
      { platform: 'Swiggy', amount: 156000, tds: 15600 },
      { platform: 'Zomato', amount: 120000, tds: 12000 },
      { platform: 'Dunzo', amount: 60000, tds: 6000 },
    ],
  },
  income_computation: {
    income_from_business: 168000,
    gross_total_income: 168000,
    deductions: 0,
    deduction_label: 'None (New Regime)',
    total_taxable_income: 168000,
  },
  tax_computation: {
    slab_breakdown: [
      { slab: '₹0 – ₹4,00,000', rate: 0, taxable_amount: 168000, tax: 0 },
      { slab: '₹4,00,001 – ₹8,00,000', rate: 5, taxable_amount: 0, tax: 0 },
      { slab: '₹8,00,001 – ₹12,00,000', rate: 10, taxable_amount: 0, tax: 0 },
      { slab: '₹12,00,001 – ₹16,00,000', rate: 15, taxable_amount: 0, tax: 0 },
      { slab: '₹16,00,001 – ₹20,00,000', rate: 20, taxable_amount: 0, tax: 0 },
      { slab: '₹20,00,001 – ₹24,00,000', rate: 25, taxable_amount: 0, tax: 0 },
      { slab: 'Above ₹24,00,000', rate: 30, taxable_amount: 0, tax: 0 },
    ],
    tax_before_cess: 0,
    rebate_87a: 0,
    rebate_applicable: true,
    tax_after_rebate: 0,
    cess: 0,
    cess_rate: 4,
    total_tax_liability: 0,
  },
  tax_paid: {
    tds_claimed: 33600,
    platform_tds: [
      { platform: 'Swiggy', tds: 15600 },
      { platform: 'Zomato', tds: 12000 },
      { platform: 'Dunzo', tds: 6000 },
    ],
    advance_tax: 0,
    total_taxes_paid: 33600,
    tax_payable: -33600,
  },
  recommendation:
    'Your total income of ₹1,68,000 is below the basic exemption limit of ₹4,00,000 under the New Tax Regime. You have ZERO tax liability. However, TDS of ₹33,600 was deducted by platforms. Filing your ITR-4 will help you claim a full refund of ₹33,600. We strongly recommend filing before 31st July 2026.',
};

/* ────────────────────────────────────────────────
   Main Page Content Component
   ──────────────────────────────────────────────── */

function ITRPageContent() {
  const searchParams = useSearchParams();
  const userId = searchParams.get('user') || 'ravi_kumar';

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchITRSummary(userId);
        if (!cancelled) setData(result);
      } catch (err) {
        console.warn('[ITR] API failed, using fallback data:', err.message);
        if (!cancelled) setData(FALLBACK_DATA);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => { cancelled = true; };
  }, [userId]);

  /* ── Loading ── */
  if (loading) {
    return (
      <div className={styles.itrPage}>
        <div className={styles.loadingContainer}>
          <div className={styles.loadingSpinner} />
          <p className={styles.loadingText}>Preparing your ITR summary…</p>
        </div>
      </div>
    );
  }

  /* ── Error ── */
  if (error && !data) {
    return (
      <div className={styles.itrPage}>
        <div className={styles.errorContainer}>
          <span className={styles.errorIcon}>⚠️</span>
          <h2 className={styles.errorTitle}>Failed to load ITR data</h2>
          <p className={styles.errorMessage}>{error}</p>
          <button className={styles.retryBtn} onClick={() => window.location.reload()}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const {
    personal_info: personal = {},
    schedule_bp: bp = {},
    income_computation: income = {},
    tax_computation: tax = {},
    tax_paid: paid = {},
    recommendation = '',
  } = data;

  const isRefund = (paid.tax_payable ?? 0) < 0;
  const refundAmount = Math.abs(paid.tax_payable ?? 0);

  return (
    <div className={styles.itrPage}>
      {/* Background orbs */}
      <div className={styles.itrBg}>
        <div className={styles.itrOrb1} />
        <div className={styles.itrOrb2} />
      </div>

      <div className={styles.itrContainer}>
        {/* ──────────────────────────────────────
            HEADER
        ────────────────────────────────────── */}
        <header className={`${styles.header} ${styles.animateIn}`} style={{ animationDelay: '0s' }}>
          <Link href={`/dashboard?user=${userId}`} className={styles.backLink}>
            <span className={styles.backArrow}>←</span>
            Back to Dashboard
          </Link>

          <div className={styles.headerTop}>
            <div className={styles.headerTitles}>
              <h1>ITR-4 (Sugam) Summary</h1>
              <p className={styles.headerSubtitle}>
                Assessment Year 2026-27 &nbsp;|&nbsp; Financial Year 2025-26
              </p>
            </div>

            <div className={styles.headerActions}>
              <span className={styles.statusBadge}>
                <span className={styles.statusDot} />
                Ready to File
              </span>
              <button className={styles.exportBtn} onClick={() => window.print()}>
                🖨️ Export as PDF
              </button>
            </div>
          </div>
        </header>

        {/* ──────────────────────────────────────
            1 — PERSONAL INFORMATION
        ────────────────────────────────────── */}
        <section className={`${styles.sectionCard} ${styles.animateIn}`} style={{ animationDelay: '0.1s' }}>
          <div className={styles.sectionHeader}>
            <div className={styles.sectionIcon}>👤</div>
            <h2 className={styles.sectionTitle}>Personal Information</h2>
          </div>

          <div className={styles.infoGrid}>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Name</span>
              <span className={styles.infoValue}>{personal.name || '—'}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>PAN</span>
              <span className={styles.infoValue}>{personal.pan || '—'}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>State</span>
              <span className={styles.infoValue}>{personal.state || '—'}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Filing Status</span>
              <span className={styles.infoValue}>{personal.filing_status || '—'}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Tax Regime</span>
              <span className={styles.infoValue}>{personal.tax_regime || '—'}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>ITR Form</span>
              <span className={styles.infoValue}>ITR-4 (Sugam)</span>
            </div>
          </div>
        </section>

        {/* ──────────────────────────────────────
            2 — SCHEDULE BP (Business / Profession)
        ────────────────────────────────────── */}
        <section className={`${styles.sectionCard} ${styles.animateIn}`} style={{ animationDelay: '0.2s' }}>
          <div className={styles.sectionHeader}>
            <div className={styles.sectionIcon}>💼</div>
            <h2 className={styles.sectionTitle}>Income from Business / Profession (Schedule BP)</h2>
          </div>

          <div className={styles.infoGrid}>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Nature of Business</span>
              <span className={styles.infoValue}>{bp.nature_of_business || '—'}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Gross Receipts</span>
              <span className={`${styles.infoValue} ${styles.highlightAmount}`}>
                {formatINR(bp.gross_receipts)}
              </span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>
                Presumptive Income u/s 44ADA ({bp.presumptive_rate || 50}%)
              </span>
              <span className={`${styles.infoValue} ${styles.highlightViolet}`}>
                {formatINR(bp.presumptive_income)}
              </span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.infoLabel}>Section 44ADA</span>
              <span className={styles.infoValue}>
                {bp.section_44ada ? (
                  <span className={`${styles.badge} ${styles.badgeGreen}`}>✓ Applied</span>
                ) : (
                  <span className={`${styles.badge} ${styles.badgeAmber}`}>Not Applied</span>
                )}
              </span>
            </div>
          </div>

          {/* Platform-wise receipts table */}
          {bp.platform_receipts && bp.platform_receipts.length > 0 && (
            <>
              <div className={styles.divider} />
              <h3 style={{ fontSize: '0.82rem', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 4, paddingLeft: 14 }}>
                Platform-wise Receipts
              </h3>
              <table className={styles.dataTable}>
                <thead>
                  <tr>
                    <th>Platform</th>
                    <th className={styles.alignRight}>Gross Receipts</th>
                    <th className={styles.alignRight}>TDS Deducted</th>
                  </tr>
                </thead>
                <tbody>
                  {bp.platform_receipts.map((row, i) => (
                    <tr key={i}>
                      <td>{row.platform}</td>
                      <td className={styles.alignRight}>{formatINR(row.amount)}</td>
                      <td className={styles.alignRight}>{formatINR(row.tds)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </section>

        {/* ──────────────────────────────────────
            3 — TOTAL INCOME COMPUTATION (Part B)
        ────────────────────────────────────── */}
        <section className={`${styles.sectionCard} ${styles.animateIn}`} style={{ animationDelay: '0.3s' }}>
          <div className={styles.sectionHeader}>
            <div className={styles.sectionIcon}>📊</div>
            <h2 className={styles.sectionTitle}>Total Income Computation (Part B)</h2>
          </div>

          <div className={styles.summaryRow}>
            <span className={styles.summaryLabel}>Income from Business / Profession</span>
            <span className={styles.summaryValue}>{formatINR(income.income_from_business)}</span>
          </div>
          <div className={styles.summaryRow}>
            <span className={styles.summaryLabel}>Gross Total Income</span>
            <span className={styles.summaryValue}>{formatINR(income.gross_total_income)}</span>
          </div>
          <div className={styles.summaryRow}>
            <span className={styles.summaryLabel}>Deductions</span>
            <span className={styles.summaryValue}>
              {income.deductions > 0 ? (
                formatINR(income.deductions)
              ) : (
                <span style={{ color: '#9ca3af', fontWeight: 400, fontStyle: 'italic' }}>
                  {income.deduction_label || 'None (New Regime)'}
                </span>
              )}
            </span>
          </div>

          <div className={styles.summaryRowHighlight}>
            <span className={styles.summaryLabel}>Total Taxable Income</span>
            <span className={styles.highlightViolet} style={{ fontSize: '1.3rem' }}>
              {formatINR(income.total_taxable_income)}
            </span>
          </div>
        </section>

        {/* ──────────────────────────────────────
            4 — TAX COMPUTATION (Part B-TTI)
        ────────────────────────────────────── */}
        <section className={`${styles.sectionCard} ${styles.animateIn}`} style={{ animationDelay: '0.4s' }}>
          <div className={styles.sectionHeader}>
            <div className={styles.sectionIcon}>🧮</div>
            <h2 className={styles.sectionTitle}>Tax Computation (Part B-TTI)</h2>
          </div>

          {/* Slab breakdown table */}
          <table className={styles.dataTable}>
            <thead>
              <tr>
                <th>Income Slab</th>
                <th className={styles.alignRight}>Rate</th>
                <th className={styles.alignRight}>Taxable Amount</th>
                <th>Tax</th>
              </tr>
            </thead>
            <tbody>
              {(tax.slab_breakdown || []).map((slab, i) => (
                <tr key={i}>
                  <td>{slab.slab}</td>
                  <td className={styles.alignRight}>{formatPercent(slab.rate)}</td>
                  <td className={styles.alignRight}>{formatINR(slab.taxable_amount)}</td>
                  <td>{formatINR(slab.tax)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className={styles.divider} />

          {/* Tax summary rows */}
          <div className={styles.summaryRow}>
            <span className={styles.summaryLabel}>Tax before Cess</span>
            <span className={styles.summaryValue}>{formatINR(tax.tax_before_cess)}</span>
          </div>

          {tax.rebate_applicable && (
            <div className={styles.summaryRowGreen}>
              <span className={styles.summaryLabel}>
                ✓ Section 87A Rebate
              </span>
              <span className={styles.summaryValue}>
                – {formatINR(tax.rebate_87a)}
              </span>
            </div>
          )}

          <div className={styles.summaryRow}>
            <span className={styles.summaryLabel}>Tax after Rebate</span>
            <span className={styles.summaryValue}>{formatINR(tax.tax_after_rebate)}</span>
          </div>
          <div className={styles.summaryRow}>
            <span className={styles.summaryLabel}>
              Health &amp; Education Cess ({tax.cess_rate || 4}%)
            </span>
            <span className={styles.summaryValue}>{formatINR(tax.cess)}</span>
          </div>

          <div className={styles.summaryRowHighlight}>
            <span className={styles.summaryLabel}>Total Tax Liability</span>
            <span className={styles.highlightViolet} style={{ fontSize: '1.3rem' }}>
              {formatINR(tax.total_tax_liability)}
            </span>
          </div>
        </section>

        {/* ──────────────────────────────────────
            5 — TAX PAID & VERIFICATION
        ────────────────────────────────────── */}
        <section className={`${styles.sectionCard} ${styles.animateIn}`} style={{ animationDelay: '0.5s' }}>
          <div className={styles.sectionHeader}>
            <div className={styles.sectionIcon}>🏦</div>
            <h2 className={styles.sectionTitle}>Tax Paid &amp; Verification</h2>
          </div>

          {/* Platform TDS table */}
          {paid.platform_tds && paid.platform_tds.length > 0 && (
            <>
              <h3 style={{ fontSize: '0.82rem', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 4, paddingLeft: 14 }}>
                TDS Claimed (Platform-wise)
              </h3>
              <table className={styles.dataTable}>
                <thead>
                  <tr>
                    <th>Platform</th>
                    <th>TDS Deducted</th>
                  </tr>
                </thead>
                <tbody>
                  {paid.platform_tds.map((row, i) => (
                    <tr key={i}>
                      <td>{row.platform}</td>
                      <td>{formatINR(row.tds)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className={styles.divider} />
            </>
          )}

          <div className={styles.summaryRow}>
            <span className={styles.summaryLabel}>Total TDS Claimed</span>
            <span className={styles.summaryValue}>{formatINR(paid.tds_claimed)}</span>
          </div>
          <div className={styles.summaryRow}>
            <span className={styles.summaryLabel}>Advance Tax Paid</span>
            <span className={styles.summaryValue}>{formatINR(paid.advance_tax)}</span>
          </div>
          <div className={styles.summaryRow}>
            <span className={styles.summaryLabel}>Total Taxes Paid</span>
            <span className={styles.summaryValue} style={{ fontWeight: 700 }}>
              {formatINR(paid.total_taxes_paid)}
            </span>
          </div>

          <div className={styles.divider} />

          {/* Final verdict: Payable or Refund */}
          {isRefund ? (
            <div className={styles.summaryRowGreen}>
              <div className={styles.refundParty}>
                <span className={styles.partyEmoji}>🎉</span>
                <span className={styles.refundLabel}>Refund Due</span>
                <span className={styles.highlightGreen}>{formatINR(refundAmount)}</span>
              </div>
            </div>
          ) : (
            <div className={(paid.tax_payable ?? 0) > 0 ? styles.summaryRowRed : styles.summaryRowHighlight}>
              <span className={styles.summaryLabel}>
                {(paid.tax_payable ?? 0) > 0 ? 'Tax Payable' : 'Balance'}
              </span>
              <span className={(paid.tax_payable ?? 0) > 0 ? styles.highlightRed : styles.summaryValue}>
                {formatINR(paid.tax_payable)}
              </span>
            </div>
          )}
        </section>

        {/* ──────────────────────────────────────
            6 — FILING RECOMMENDATION
        ────────────────────────────────────── */}
        <section className={`${styles.recommendationCard} ${styles.animateIn}`} style={{ animationDelay: '0.6s' }}>
          <div className={styles.sectionHeader}>
            <div className={styles.sectionIcon}>💡</div>
            <h2 className={styles.sectionTitle}>Filing Recommendation</h2>
          </div>

          <p className={styles.recommendationText}>
            {recommendation}
          </p>

          <a
            href="https://www.incometax.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            className={styles.ctaBtn}
          >
            File on Income Tax Portal
            <span className={styles.ctaArrow}>→</span>
          </a>
        </section>
      </div>
    </div>
  );
}

/* ────────────────────────────────────────────────
   Suspense Wrapper (required for useSearchParams)
   ──────────────────────────────────────────────── */

export default function ITRPage() {
  return (
    <Suspense
      fallback={
        <div className={styles.itrPage}>
          <div className={styles.loadingContainer}>
            <div className={styles.loadingSpinner} />
            <p className={styles.loadingText}>Loading…</p>
          </div>
        </div>
      }
    >
      <ITRPageContent />
    </Suspense>
  );
}
