'use client';

import { useState, useEffect, useRef, useCallback, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  fetchIncomeSummary,
  fetchTaxCalculation,
  fetchDeadlines,
  fetchUser,
  uploadPDFs,
} from '@/lib/api';
import './dashboard.css';

/* ═══════════════════════════════════════════════════
   Helpers
   ═══════════════════════════════════════════════════ */

function formatINR(amount) {
  if (amount == null || isNaN(amount)) return '₹0';
  const prefix = amount < 0 ? '-₹' : '₹';
  return prefix + Math.abs(amount).toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function daysUntil(dateStr) {
  if (!dateStr) return 999;
  const target = new Date(dateStr);
  const now = new Date();
  return Math.ceil((target - now) / (1000 * 60 * 60 * 24));
}

function getInitials(name) {
  if (!name) return 'U';
  return name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

const MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

const PLATFORM_BADGES = {
  swiggy: 'badge-swiggy',
  uber: 'badge-uber',
  zomato: 'badge-zomato',
  ola: 'badge-ola',
  dunzo: 'badge-dunzo',
  zepto: 'badge-zepto',
  rapido: 'badge-rapido',
};

function getPlatformBadge(name) {
  const key = (name || '').toLowerCase();
  for (const [k, v] of Object.entries(PLATFORM_BADGES)) {
    if (key.includes(k)) return v;
  }
  return 'badge-default';
}

/* ═══════════════════════════════════════════════════
   Loading Skeleton
   ═══════════════════════════════════════════════════ */

function DashboardSkeleton() {
  return (
    <div className="dashboard-page">
      <div className="top-nav">
        <div className="nav-brand">
          <span className="nav-logo">GigSaathi</span>
          <span className="nav-logo-dot" />
        </div>
        <div className="nav-links">
          <span className="skeleton" style={{ width: 80, height: 32, borderRadius: 8 }} />
          <span className="skeleton" style={{ width: 60, height: 32, borderRadius: 8 }} />
          <span className="skeleton" style={{ width: 90, height: 32, borderRadius: 8 }} />
        </div>
        <div className="nav-right">
          <span className="skeleton" style={{ width: 120, height: 32, borderRadius: 8 }} />
        </div>
      </div>

      <div className="dashboard-content">
        <div className="welcome-section">
          <div className="skeleton skeleton-text lg" />
          <div className="skeleton skeleton-text sm" />
        </div>

        <div className="stats-grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton skeleton-card" />
          ))}
        </div>

        <div className="main-grid">
          <div className="skeleton skeleton-block" />
          <div className="skeleton skeleton-block" />
        </div>

        <div className="skeleton skeleton-block" style={{ marginTop: 24 }} />
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   Upload Modal
   ═══════════════════════════════════════════════════ */

function UploadModal({ userId, onClose, onSuccess }) {
  const [files, setFiles] = useState([]);
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const inputRef = useRef(null);

  const handleFiles = useCallback((newFiles) => {
    const pdfFiles = Array.from(newFiles).filter(
      (f) => f.type === 'application/pdf' || f.name.endsWith('.pdf')
    );
    setFiles((prev) => [...prev, ...pdfFiles]);
  }, []);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      setDragOver(false);
      handleFiles(e.dataTransfer.files);
    },
    [handleFiles]
  );

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (!files.length) return;
    setUploading(true);
    setProgress(0);
    setStatus('Uploading...');

    // Simulate progress for UX
    const interval = setInterval(() => {
      setProgress((p) => Math.min(p + 15, 85));
    }, 300);

    try {
      await uploadPDFs(userId, files);
      clearInterval(interval);
      setProgress(100);
      setStatus('Upload successful!');
      setTimeout(() => {
        onSuccess();
        onClose();
      }, 1200);
    } catch (err) {
      clearInterval(interval);
      setStatus('Upload failed. Please try again.');
      setProgress(0);
      setUploading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">📄 Upload Documents</h2>
          <button className="modal-close" onClick={onClose}>
            ✕
          </button>
        </div>

        <div
          className={`drop-zone ${dragOver ? 'drag-over' : ''}`}
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
        >
          <div className="drop-zone-icon">📁</div>
          <p className="drop-zone-text">
            Drag & drop PDF files or <strong>browse</strong>
          </p>
          <p className="drop-zone-hint">Form 16A, bank statements, platform earnings</p>
          <input
            ref={inputRef}
            type="file"
            accept=".pdf"
            multiple
            style={{ display: 'none' }}
            onChange={(e) => handleFiles(e.target.files)}
          />
        </div>

        {files.length > 0 && (
          <div className="file-list">
            {files.map((file, i) => (
              <div key={i} className="file-item">
                <div>
                  <div className="file-name">📄 {file.name}</div>
                  <div className="file-size">{formatFileSize(file.size)}</div>
                </div>
                <button className="file-remove" onClick={() => removeFile(i)}>
                  Remove
                </button>
              </div>
            ))}
          </div>
        )}

        {uploading && (
          <div className="upload-progress">
            <div className="progress-bar-outer">
              <div className="progress-bar-inner" style={{ width: `${progress}%` }} />
            </div>
            <p className={`upload-status ${progress === 100 ? 'upload-success' : ''}`}>
              {status}
            </p>
          </div>
        )}

        <div className="modal-actions">
          <button className="btn-upload" onClick={handleUpload} disabled={!files.length || uploading}>
            {uploading ? (
              <>
                <span className="spinner" /> Uploading...
              </>
            ) : (
              <>⬆ Upload {files.length > 0 ? `${files.length} file${files.length > 1 ? 's' : ''}` : ''}</>
            )}
          </button>
          <button className="btn-cancel" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   Dashboard (inner — reads search params)
   ═══════════════════════════════════════════════════ */

function DashboardInner() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const user = searchParams.get('user') || 'default_user';

  const [loading, setLoading] = useState(true);
  const [income, setIncome] = useState(null);
  const [tax, setTax] = useState(null);
  const [deadlines, setDeadlines] = useState(null);
  const [profile, setProfile] = useState(null);
  const [showUpload, setShowUpload] = useState(false);
  const [error, setError] = useState(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [incomeData, taxData, deadlineData, profileData] = await Promise.allSettled([
        fetchIncomeSummary(user),
        fetchTaxCalculation(user),
        fetchDeadlines(user),
        fetchUser(user),
      ]);

      setIncome(incomeData.status === 'fulfilled' ? incomeData.value : null);
      setTax(taxData.status === 'fulfilled' ? taxData.value : null);
      setDeadlines(deadlineData.status === 'fulfilled' ? deadlineData.value : null);
      setProfile(profileData.status === 'fulfilled' ? profileData.value : null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading) return <DashboardSkeleton />;

  /* ── Derive display data with safe fallbacks ── */

  const userName = profile?.name || user.replace(/_/g, ' ');
  const totalIncome = income?.total_income ?? income?.gross_income ?? 0;
  const totalTDS = income?.total_tds ?? tax?.tds_credit ?? 0;
  const netPayable = tax?.net_payable ?? tax?.tax_payable ?? 0;
  const platforms = income?.platforms ?? income?.platform_breakdown ?? [];
  const platformCount = platforms.length || income?.platform_count || 0;

  // Tax summary fields
  const grossIncome = tax?.gross_income ?? totalIncome;
  const deduction44ADA = tax?.deduction_44ada ?? Math.round(grossIncome * 0.5);
  const taxableIncome = tax?.taxable_income ?? grossIncome - deduction44ADA;
  const taxLiability = tax?.tax_liability ?? tax?.total_tax ?? 0;
  const tdsCredit = tax?.tds_credit ?? totalTDS;
  const section87A = tax?.section_87a_rebate ?? tax?.rebate_87a ?? 0;

  // Deadlines
  const nextDeadline = Array.isArray(deadlines) && deadlines.length > 0 ? deadlines[0] : deadlines;
  const deadlineDays = nextDeadline ? daysUntil(nextDeadline.date || nextDeadline.due_date) : 999;
  const isUrgent = deadlineDays <= 15 && deadlineDays > 0;

  // Monthly data
  const monthlyData = income?.monthly_income ?? income?.monthly ?? [];

  return (
    <div className="dashboard-page">
      {/* ── Top Navigation ─────────────────────── */}
      <nav className="top-nav">
        <div className="nav-brand">
          <span className="nav-logo">GigSaathi</span>
          <span className="nav-logo-dot" />
        </div>

        <div className="nav-links">
          <Link href={`/dashboard?user=${user}`} className="nav-link active">
            📊 Dashboard
          </Link>
          <Link href={`/chat?user=${user}`} className="nav-link">
            💬 Chat
          </Link>
          <Link href={`/itr?user=${user}`} className="nav-link">
            📋 ITR Summary
          </Link>
        </div>

        <div className="nav-right">
          <div className="nav-user">
            <div className="nav-user-avatar">{getInitials(userName)}</div>
            <span>{userName}</span>
          </div>
          <button className="btn-switch" onClick={() => router.push('/')}>
            Switch User
          </button>
        </div>
      </nav>

      <div className="dashboard-content">
        {/* ── Welcome Header ───────────────────── */}
        <div className="welcome-section">
          <h1 className="welcome-greeting">
            Welcome back, <span>{userName.split(' ')[0]}</span> 👋
          </h1>
          <p className="welcome-sub">
            Here&apos;s your financial overview for FY 2025–26
          </p>
        </div>

        {/* ── Deadline Alert Banner ────────────── */}
        {nextDeadline && deadlineDays > 0 && deadlineDays < 90 && (
          <div className={`deadline-banner ${isUrgent ? 'urgent' : ''}`}>
            <div className="deadline-info">
              <span className="deadline-icon">⚠️</span>
              <span className="deadline-text">
                <strong>{nextDeadline.title || nextDeadline.name || 'Advance Tax Due'}</strong>
                {' — '}
                {nextDeadline.date || nextDeadline.due_date}
                {netPayable > 0 && ` — ${formatINR(netPayable)} remaining`}
              </span>
            </div>
            <span className={`deadline-badge ${isUrgent ? 'danger' : 'warning'}`}>
              {deadlineDays} day{deadlineDays !== 1 ? 's' : ''} left
            </span>
          </div>
        )}

        {/* ── Stats Row (4 cards) ──────────────── */}
        <div className="stats-grid">
          <div className="stat-card accent-emerald animate-fade-in anim-delay-1">
            <div className="stat-header">
              <span className="stat-label">Total Income</span>
              <span className="stat-icon">📊</span>
            </div>
            <div className="stat-value">{formatINR(totalIncome)}</div>
            <div className="stat-sub">{platformCount} platform{platformCount !== 1 ? 's' : ''} combined</div>
          </div>

          <div className="stat-card accent-violet animate-fade-in anim-delay-2">
            <div className="stat-header">
              <span className="stat-label">TDS Deducted</span>
              <span className="stat-icon">🏦</span>
            </div>
            <div className="stat-value">{formatINR(totalTDS)}</div>
            <div className="stat-sub">Tax deducted at source</div>
          </div>

          <div className="stat-card accent-amber animate-fade-in anim-delay-3">
            <div className="stat-header">
              <span className="stat-label">Net Tax Payable</span>
              <span className="stat-icon">💰</span>
            </div>
            <div className={`stat-value ${netPayable <= 0 ? 'text-green' : 'text-red'}`}>
              {netPayable <= 0 ? `${formatINR(Math.abs(netPayable))} refund` : formatINR(netPayable)}
            </div>
            <div className="stat-sub">{netPayable <= 0 ? 'You get money back!' : 'Remaining liability'}</div>
          </div>

          <div className="stat-card accent-cyan animate-fade-in anim-delay-4">
            <div className="stat-header">
              <span className="stat-label">Platforms</span>
              <span className="stat-icon">🔗</span>
            </div>
            <div className="stat-value">{platformCount}</div>
            <div className="stat-sub">Active gig platforms</div>
          </div>
        </div>

        {/* ── Two-Column Layout ────────────────── */}
        <div className="main-grid">
          {/* Left: Platform Breakdown */}
          <div className="card animate-fade-in anim-delay-4">
            <h2 className="card-title">
              <span className="card-title-icon">🏢</span> Platform Breakdown
            </h2>
            <div className="platform-list">
              {platforms.length > 0 ? (
                platforms.map((p, i) => {
                  const name = p.platform || p.name || `Platform ${i + 1}`;
                  const gross = p.gross_income ?? p.income ?? p.amount ?? 0;
                  const tds = p.tds ?? p.tds_deducted ?? 0;
                  const pct = totalIncome > 0 ? Math.round((gross / totalIncome) * 100) : 0;

                  return (
                    <div key={i} className="platform-item">
                      <div className="platform-row">
                        <div className="platform-name-group">
                          <span className={`platform-badge ${getPlatformBadge(name)}`}>{name}</span>
                        </div>
                        <div className="platform-amounts">
                          <div className="platform-gross">{formatINR(gross)}</div>
                          {tds > 0 && <div className="platform-tds">TDS: {formatINR(tds)}</div>}
                        </div>
                      </div>
                      <div className="progress-track">
                        <div className="progress-fill" style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  );
                })
              ) : (
                <p style={{ color: '#6b7280', fontSize: '0.9rem', padding: 16 }}>
                  No platform data available. Upload your earnings documents to see breakdown.
                </p>
              )}
            </div>
          </div>

          {/* Right: Tax Summary + Quick Actions */}
          <div>
            <div className="card animate-fade-in anim-delay-5" style={{ marginBottom: 20 }}>
              <h2 className="card-title">
                <span className="card-title-icon">🧮</span> Tax Summary
              </h2>
              <div className="tax-summary-list">
                <div className="tax-row">
                  <span className="tax-label">Gross Income</span>
                  <span className="tax-value">{formatINR(grossIncome)}</span>
                </div>
                <div className="tax-row">
                  <span className="tax-label">44ADA Deduction (50%)</span>
                  <span className="tax-value savings">-{formatINR(deduction44ADA)}</span>
                </div>
                <div className="tax-row">
                  <span className="tax-label">Taxable Income</span>
                  <span className="tax-value">{formatINR(taxableIncome)}</span>
                </div>
                <div className="tax-row">
                  <span className="tax-label">Tax Liability</span>
                  <span className="tax-value">{formatINR(taxLiability)}</span>
                </div>
                {section87A > 0 && (
                  <div className="tax-row">
                    <span className="tax-label">Section 87A Rebate</span>
                    <span className="tax-value savings">-{formatINR(section87A)}</span>
                  </div>
                )}
                <div className="tax-row">
                  <span className="tax-label">TDS Credit</span>
                  <span className="tax-value savings">-{formatINR(tdsCredit)}</span>
                </div>
                <div className="tax-row highlight">
                  <span className="tax-label">
                    {netPayable <= 0 ? '🎉 Refund Due' : 'Net Payable'}
                  </span>
                  <span className={`tax-value ${netPayable <= 0 ? 'text-green' : 'text-red'}`}>
                    {formatINR(Math.abs(netPayable))}
                  </span>
                </div>
              </div>

              {section87A > 0 && (
                <div className="rebate-info">
                  ✅ Section 87A rebate of {formatINR(section87A)} applied — taxable income is under ₹7,00,000
                </div>
              )}
            </div>

            {/* Quick Actions */}
            <div className="card quick-actions animate-fade-in anim-delay-6">
              <h2 className="card-title">
                <span className="card-title-icon">⚡</span> Quick Actions
              </h2>
              <div className="actions-grid">
                <button className="btn-action btn-primary" onClick={() => setShowUpload(true)}>
                  <span className="btn-action-icon">📤</span>
                  Upload PDFs
                </button>
                <Link href={`/chat?user=${user}`} className="btn-action btn-secondary">
                  <span className="btn-action-icon">💬</span>
                  Chat with Agent
                </Link>
                <Link href={`/itr?user=${user}`} className="btn-action btn-secondary">
                  <span className="btn-action-icon">📋</span>
                  View ITR Summary
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* ── Monthly Income Chart ─────────────── */}
        {monthlyData.length > 0 && (
          <div className="card chart-section animate-fade-in anim-delay-6">
            <h2 className="card-title">
              <span className="card-title-icon">📈</span> Monthly Earnings
            </h2>
            <div className="chart-container">
              {(() => {
                const maxAmount = Math.max(...monthlyData.map((m) => m.amount ?? m.income ?? 0), 1);
                return monthlyData.map((m, i) => {
                  const amount = m.amount ?? m.income ?? 0;
                  const pct = Math.max((amount / maxAmount) * 100, 2);
                  const monthLabel = m.month
                    ? typeof m.month === 'number'
                      ? MONTH_LABELS[m.month - 1] || m.month
                      : String(m.month).slice(0, 3)
                    : MONTH_LABELS[i] || `M${i + 1}`;

                  return (
                    <div key={i} className="chart-bar-row">
                      <span className="chart-month">{monthLabel}</span>
                      <div className="chart-bar-track">
                        <div
                          className={`chart-bar-fill ${i % 2 === 0 ? '' : 'alt'}`}
                          style={{ width: `${pct}%`, animationDelay: `${i * 0.08}s` }}
                        />
                      </div>
                      <span className="chart-amount">{formatINR(amount)}</span>
                    </div>
                  );
                });
              })()}
            </div>
          </div>
        )}

        {/* ── Error State ──────────────────────── */}
        {error && (
          <div
            style={{
              marginTop: 24,
              padding: '16px 20px',
              borderRadius: 12,
              background: 'rgba(239,68,68,0.1)',
              border: '1px solid rgba(239,68,68,0.25)',
              color: '#f87171',
              fontSize: '0.88rem',
            }}
          >
            ⚠️ Some data could not be loaded: {error}
          </div>
        )}
      </div>

      {/* ── Upload Modal ───────────────────────── */}
      {showUpload && (
        <UploadModal
          userId={user}
          onClose={() => setShowUpload(false)}
          onSuccess={loadData}
        />
      )}
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   Page Export (Suspense boundary for useSearchParams)
   ═══════════════════════════════════════════════════ */

export default function DashboardPage() {
  return (
    <Suspense fallback={<DashboardSkeleton />}>
      <DashboardInner />
    </Suspense>
  );
}
