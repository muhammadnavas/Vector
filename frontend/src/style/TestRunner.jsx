    import { useEffect, useRef, useState } from 'react';
import { discoverEndpoints, getExecution, triggerTestRun } from '../services/api';
import './TestRunner.css';

const token = {
  purple: '#7c3aed',
  indigo: '#6366f1',
  violet: '#8b5cf6',
  textMuted: 'rgba(255,255,255,0.55)',
  textDim: 'rgba(255,255,255,0.35)',
  border: 'rgba(124,58,237,0.18)',
  cardBg: 'rgba(255,255,255,0.03)',
  cardBgHover: 'rgba(124,58,237,0.08)',
  success: '#10b981',
  danger: '#ef4444',
};

export default function TestRunner() {
  const [repoName, setRepoName] = useState('api-service');
  const [repoUrl, setRepoUrl] = useState('https://github.com/company/api-service');
  const [baseApiUrl, setBaseApiUrl] = useState('');
  const [commitSha, setCommitSha] = useState('');
  const [commitMessage, setCommitMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentExecution, setCurrentExecution] = useState(null);
  const [error, setError] = useState(null);
  const [methodFilter, setMethodFilter] = useState('ALL');
  const [frameworkFilter, setFrameworkFilter] = useState('ALL');
  const [authFilter, setAuthFilter] = useState('ALL');
  const pollIntervalRef = useRef(null);

  const clearPolling = () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  };

  const pollExecution = (webhookId) => {
    clearPolling();
    let retries = 0;
    pollIntervalRef.current = setInterval(async () => {
      try {
        const execution = await getExecution(webhookId);
        if (
          execution.status === 'completed' ||
          execution.status === 'failed' ||
          execution.success === false
        ) {
          clearPolling();
          setCurrentExecution(execution);
          setLoading(false);
        }
      } catch (err) {
        const status = err?.status;
        const message = String(err?.message || '').toLowerCase();

        if (status === 404 || message.includes('execution not found')) {
          clearPolling();
          setError('Execution not found. It may have expired or backend was restarted. Please run discovery again.');
          setLoading(false);
          return;
        }

        retries += 1;
        if (retries > 30) {
          clearPolling();
          setError('Execution timeout - check backend logs');
          setLoading(false);
        }
      }
    }, 1000);
  };

  useEffect(() => {
    return () => {
      clearPolling();
    };
  }, []);

  // Generate random commit SHA and message
  useEffect(() => {
    setCommitSha(Math.random().toString(16).substring(7) + Math.random().toString(16).substring(7));
    setCommitMessage('Add new API endpoints with validation');
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    clearPolling();
    setLoading(true);
    setError(null);

    try {
      const webhookId = `test-${Date.now()}`;

      const response = await triggerTestRun({
        webhook_id: webhookId,
        repo_name: repoName,
        repo_url: repoUrl,
        base_api_url: baseApiUrl || null,
        commit_sha: commitSha,
        commit_message: commitMessage,
      });
      pollExecution(webhookId);

      // Set execution with pending status immediately
      setCurrentExecution({
        webhook_id: webhookId,
        status: 'pending',
        repo: response.repo || repoName,
        commit: commitSha.slice(0, 7),
      });
    } catch (err) {
      setError(err.message || 'Failed to trigger test run');
      setLoading(false);
    }
  };

  const handleDiscover = async () => {
    clearPolling();
    setLoading(true);
    setError(null);

    try {
      const response = await discoverEndpoints({
        repo_url: repoUrl,
        repo_name: repoName,
        base_api_url: baseApiUrl || null,
      });

      setCurrentExecution({
        webhook_id: response.webhook_id,
        status: 'pending',
        repo: response.repo || repoName,
        repo_url: repoUrl,
        commit: '-',
      });

      pollExecution(response.webhook_id);
    } catch (err) {
      setError(err.message || 'Failed to discover endpoints');
      setLoading(false);
    }
  };

  const endpointList = currentExecution?.endpoints || [];
  const frameworkOptions = [...new Set(endpointList.map((endpoint) => endpoint.framework || 'Unknown'))].sort();
  const filteredEndpoints = endpointList.filter((endpoint) => {
    const endpointMethod = endpoint.method || 'ANY';
    const endpointFramework = endpoint.framework || 'Unknown';
    const endpointAuth = endpoint.auth_required ? 'AUTH' : 'PUBLIC';

    return (
      (methodFilter === 'ALL' || endpointMethod === methodFilter) &&
      (frameworkFilter === 'ALL' || endpointFramework === frameworkFilter) &&
      (authFilter === 'ALL' || endpointAuth === authFilter)
    );
  });

  return (
    <div style={{ padding: '24px' }}>
      {/* Form Section */}
      <div
        style={{
          maxWidth: '600px',
          margin: '0 auto 40px',
          background: token.cardBg,
          border: `1px solid ${token.border}`,
          borderRadius: '16px',
          padding: '32px',
          backdropFilter: 'blur(12px)',
        }}
      >
        <h2
          style={{
            color: 'white',
            marginBottom: '24px',
            fontSize: '1.5rem',
            fontWeight: 700,
          }}
        >
          🚀 Trigger Test Run
        </h2>

        <form onSubmit={handleSubmit}>
          {/* Repository Name */}
          <div style={{ marginBottom: '20px' }}>
            <label
              style={{
                display: 'block',
                color: token.textMuted,
                fontSize: '0.875rem',
                marginBottom: '8px',
                fontWeight: 600,
              }}
            >
              Repository Name
            </label>
            <input
              type="text"
              value={repoName}
              onChange={(e) => setRepoName(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: `1px solid ${token.border}`,
                background: 'rgba(0,0,0,0.3)',
                color: 'white',
                fontSize: '0.9rem',
                fontFamily: 'inherit',
              }}
              placeholder="my-api-repo"
            />
          </div>

          {/* Repository URL */}
          <div style={{ marginBottom: '20px' }}>
            <label
              style={{
                display: 'block',
                color: token.textMuted,
                fontSize: '0.875rem',
                marginBottom: '8px',
                fontWeight: 600,
              }}
            >
              Repository URL
            </label>
            <input
              type="text"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: `1px solid ${token.border}`,
                background: 'rgba(0,0,0,0.3)',
                color: 'white',
                fontSize: '0.9rem',
                fontFamily: 'inherit',
              }}
              placeholder="https://github.com/user/repo"
            />
          </div>

          {/* Base API URL for Live Checks */}
          <div style={{ marginBottom: '20px' }}>
            <label
              style={{
                display: 'block',
                color: token.textMuted,
                fontSize: '0.875rem',
                marginBottom: '8px',
                fontWeight: 600,
              }}
            >
              Base API URL (optional)
            </label>
            <input
              type="text"
              value={baseApiUrl}
              onChange={(e) => setBaseApiUrl(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: `1px solid ${token.border}`,
                background: 'rgba(0,0,0,0.3)',
                color: 'white',
                fontSize: '0.9rem',
                fontFamily: 'inherit',
              }}
              placeholder="https://api.example.com"
            />
          </div>

          {/* Commit SHA */}
          <div style={{ marginBottom: '20px' }}>
            <label
              style={{
                display: 'block',
                color: token.textMuted,
                fontSize: '0.875rem',
                marginBottom: '8px',
                fontWeight: 600,
              }}
            >
              Commit SHA
            </label>
            <input
              type="text"
              value={commitSha}
              onChange={(e) => setCommitSha(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: `1px solid ${token.border}`,
                background: 'rgba(0,0,0,0.3)',
                color: 'white',
                fontSize: '0.9rem',
                fontFamily: '"Fira Code", monospace',
              }}
              placeholder="abc123def456"
            />
          </div>

          {/* Commit Message */}
          <div style={{ marginBottom: '24px' }}>
            <label
              style={{
                display: 'block',
                color: token.textMuted,
                fontSize: '0.875rem',
                marginBottom: '8px',
                fontWeight: 600,
              }}
            >
              Commit Message
            </label>
            <textarea
              value={commitMessage}
              onChange={(e) => setCommitMessage(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: `1px solid ${token.border}`,
                background: 'rgba(0,0,0,0.3)',
                color: 'white',
                fontSize: '0.9rem',
                fontFamily: 'inherit',
                minHeight: '80px',
                resize: 'vertical',
              }}
              placeholder="Describe the changes..."
            />
          </div>

          {/* Error Message */}
          {error && (
            <div
              style={{
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: '8px',
                padding: '12px',
                color: '#fca5a5',
                marginBottom: '24px',
                fontSize: '0.875rem',
              }}
            >
              ❌ {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '14px',
              borderRadius: '8px',
              background: loading
                ? 'rgba(124, 58, 237, 0.5)'
                : 'linear-gradient(135deg, #7c3aed, #4f46e5)',
              color: 'white',
              border: 'none',
              fontSize: '1rem',
              fontWeight: 700,
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s',
              boxShadow: loading
                ? 'none'
                : '0 0 24px rgba(124,58,237,0.35)',
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.target.style.boxShadow = '0 0 40px rgba(124,58,237,0.55)';
              }
            }}
            onMouseLeave={(e) => {
              if (!loading) {
                e.target.style.boxShadow = '0 0 24px rgba(124,58,237,0.35)';
              }
            }}
          >
            {loading ? '⏳ Running Tests...' : '▶️ Run Tests'}
          </button>

          <button
            type="button"
            disabled={loading}
            onClick={handleDiscover}
            style={{
              width: '100%',
              marginTop: '12px',
              padding: '14px',
              borderRadius: '8px',
              background: loading
                ? 'rgba(99, 102, 241, 0.5)'
                : 'linear-gradient(135deg, #2563eb, #0891b2)',
              color: 'white',
              border: 'none',
              fontSize: '1rem',
              fontWeight: 700,
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s',
            }}
          >
            {loading ? '⏳ Discovering Endpoints...' : '🔎 Discover Endpoints from Repo URL'}
          </button>
        </form>
      </div>

      {/* Results Section */}
      {currentExecution && (
        <div
          style={{
            maxWidth: '900px',
            margin: '0 auto',
          }}
        >
          <h2
            style={{
              color: 'white',
              marginBottom: '24px',
              fontSize: '1.5rem',
              fontWeight: 700,
            }}
          >
            📊 Execution Results
          </h2>

          {/* Status Card */}
          <div
            style={{
              background: token.cardBg,
              border: `1px solid ${token.border}`,
              borderRadius: '16px',
              padding: '24px',
              marginBottom: '24px',
              backdropFilter: 'blur(12px)',
            }}
          >
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
              <div>
                <div style={{ color: token.textDim, fontSize: '0.875rem', marginBottom: '8px' }}>
                  Repository
                </div>
                <div style={{ color: 'white', fontSize: '1.1rem', fontWeight: 600 }}>
                  {currentExecution.repo}
                </div>
              </div>

              <div>
                <div style={{ color: token.textDim, fontSize: '0.875rem', marginBottom: '8px' }}>
                  Commit
                </div>
                <div
                  style={{
                    color: 'white',
                    fontSize: '1.1rem',
                    fontWeight: 600,
                    fontFamily: '"Fira Code", monospace',
                  }}
                >
                  {currentExecution.commit}
                </div>
              </div>

              <div>
                <div style={{ color: token.textDim, fontSize: '0.875rem', marginBottom: '8px' }}>
                  Status
                </div>
                <div
                  style={{
                    color:
                      currentExecution.status === 'completed'
                        ? token.success
                        : currentExecution.status === 'pending' || currentExecution.status === 'processing'
                          ? '#fbbf24'
                          : token.danger,
                    fontSize: '1.1rem',
                    fontWeight: 600,
                  }}
                >
                  {currentExecution.status === 'pending' && '⏳ Pending'}
                  {currentExecution.status === 'processing' && '⚙️ Processing'}
                  {currentExecution.status === 'completed' && '✅ Completed'}
                  {(currentExecution.status === 'failed' || currentExecution.success === false) && '❌ Failed'}
                </div>
              </div>

              <div>
                <div style={{ color: token.textDim, fontSize: '0.875rem', marginBottom: '8px' }}>
                  Timestamp
                </div>
                <div style={{ color: 'white', fontSize: '0.95rem' }}>
                  {currentExecution.timestamp
                    ? new Date(currentExecution.timestamp).toLocaleString()
                    : 'Running...'}
                </div>
              </div>
            </div>
          </div>

          {/* Summary Stats */}
          {currentExecution.summary && (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: '16px',
                marginBottom: '24px',
              }}
            >
              <div
                style={{
                  background: token.cardBg,
                  border: `1px solid ${token.border}`,
                  borderRadius: '12px',
                  padding: '16px',
                  textAlign: 'center',
                  backdropFilter: 'blur(12px)',
                }}
              >
                <div style={{ color: token.textDim, fontSize: '0.8rem', marginBottom: '8px' }}>Total Tests</div>
                <div style={{ color: 'white', fontSize: '1.8rem', fontWeight: 700 }}>
                  {currentExecution.summary.total_tests}
                </div>
              </div>

              <div
                style={{
                  background: 'rgba(16, 185, 129, 0.1)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  borderRadius: '12px',
                  padding: '16px',
                  textAlign: 'center',
                  backdropFilter: 'blur(12px)',
                }}
              >
                <div style={{ color: token.textDim, fontSize: '0.8rem', marginBottom: '8px' }}>
                  Passed
                </div>
                <div style={{ color: token.success, fontSize: '1.8rem', fontWeight: 700 }}>
                  {currentExecution.summary.passed}
                </div>
              </div>

              <div
                style={{
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  borderRadius: '12px',
                  padding: '16px',
                  textAlign: 'center',
                  backdropFilter: 'blur(12px)',
                }}
              >
                <div style={{ color: token.textDim, fontSize: '0.8rem', marginBottom: '8px' }}>
                  Failed
                </div>
                <div style={{ color: token.danger, fontSize: '1.8rem', fontWeight: 700 }}>
                  {currentExecution.summary.failed}
                </div>
              </div>

              <div
                style={{
                  background: token.cardBg,
                  border: `1px solid ${token.border}`,
                  borderRadius: '12px',
                  padding: '16px',
                  textAlign: 'center',
                  backdropFilter: 'blur(12px)',
                }}
              >
                <div style={{ color: token.textDim, fontSize: '0.8rem', marginBottom: '8px' }}>
                  Success Rate / Endpoints
                </div>
                <div style={{ color: token.violet, fontSize: '1.8rem', fontWeight: 700 }}>
                  {currentExecution.summary.endpoints_found
                    ? currentExecution.summary.endpoints_found
                    : `${currentExecution.summary.success_rate.toFixed(1)}%`}
                </div>
              </div>
            </div>
          )}

          {/* Endpoints */}
          {currentExecution.endpoints && currentExecution.endpoints.length > 0 && (
            <div
              style={{
                background: token.cardBg,
                border: `1px solid ${token.border}`,
                borderRadius: '16px',
                padding: '24px',
                marginBottom: '24px',
                backdropFilter: 'blur(12px)',
              }}
            >
              <h3 style={{ color: 'white', marginBottom: '16px', fontSize: '1.1rem' }}>
                🔗 Tested Endpoints
              </h3>

              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(3, minmax(0, 1fr))',
                  gap: '12px',
                  marginBottom: '16px',
                }}
              >
                <select
                  value={methodFilter}
                  onChange={(e) => setMethodFilter(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: '8px',
                    border: `1px solid ${token.border}`,
                    background: 'rgba(0,0,0,0.25)',
                    color: 'white',
                  }}
                >
                  <option value="ALL">All Methods</option>
                  <option value="GET">GET</option>
                  <option value="POST">POST</option>
                  <option value="PUT">PUT</option>
                  <option value="PATCH">PATCH</option>
                  <option value="DELETE">DELETE</option>
                  <option value="ANY">ANY</option>
                  <option value="ROUTE">ROUTE</option>
                </select>

                <select
                  value={frameworkFilter}
                  onChange={(e) => setFrameworkFilter(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: '8px',
                    border: `1px solid ${token.border}`,
                    background: 'rgba(0,0,0,0.25)',
                    color: 'white',
                  }}
                >
                  <option value="ALL">All Frameworks</option>
                  {frameworkOptions.map((framework) => (
                    <option key={framework} value={framework}>
                      {framework}
                    </option>
                  ))}
                </select>

                <select
                  value={authFilter}
                  onChange={(e) => setAuthFilter(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    borderRadius: '8px',
                    border: `1px solid ${token.border}`,
                    background: 'rgba(0,0,0,0.25)',
                    color: 'white',
                  }}
                >
                  <option value="ALL">All Access</option>
                  <option value="AUTH">Auth Required</option>
                  <option value="PUBLIC">Public</option>
                </select>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {filteredEndpoints.map((endpoint, i) => (
                  <div
                    key={i}
                    style={{
                      display: 'grid',
                      gridTemplateColumns: '1fr auto',
                      gap: '12px',
                      padding: '12px',
                      background: 'rgba(0,0,0,0.2)',
                      borderRadius: '8px',
                    }}
                  >
                    <div>
                      <span
                        style={{
                          display: 'inline-block',
                          background:
                            endpoint.method === 'POST'
                              ? 'rgba(59, 130, 246, 0.2)'
                              : endpoint.method === 'GET'
                                ? 'rgba(34, 197, 94, 0.2)'
                                : 'rgba(168, 85, 247, 0.2)',
                          color:
                            endpoint.method === 'POST'
                              ? '#60a5fa'
                              : endpoint.method === 'GET'
                                ? '#4ade80'
                                : '#d8b4fe',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          marginRight: '12px',
                        }}
                      >
                        {endpoint.method}
                      </span>
                      <span style={{ color: 'white', fontFamily: '"Fira Code", monospace' }}>
                        {endpoint.path}
                      </span>

                      <div style={{ marginTop: '8px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                        <span
                          style={{
                            fontSize: '0.72rem',
                            color: '#93c5fd',
                            background: 'rgba(59, 130, 246, 0.15)',
                            border: '1px solid rgba(59, 130, 246, 0.35)',
                            borderRadius: '999px',
                            padding: '2px 8px',
                          }}
                        >
                          {endpoint.framework || 'Unknown'}
                        </span>
                        <span
                          style={{
                            fontSize: '0.72rem',
                            color: token.textMuted,
                            background: 'rgba(255,255,255,0.05)',
                            border: `1px solid ${token.border}`,
                            borderRadius: '999px',
                            padding: '2px 8px',
                            fontFamily: '"Fira Code", monospace',
                          }}
                        >
                          {endpoint.file || 'source: n/a'}
                        </span>
                        {typeof endpoint.confidence === 'number' && (
                          <span
                            style={{
                              fontSize: '0.72rem',
                              color: '#fcd34d',
                              background: 'rgba(234, 179, 8, 0.15)',
                              border: '1px solid rgba(234, 179, 8, 0.3)',
                              borderRadius: '999px',
                              padding: '2px 8px',
                            }}
                          >
                            {(endpoint.confidence * 100).toFixed(0)}% confidence
                          </span>
                        )}
                      </div>
                    </div>
                    <div style={{ color: token.textMuted, fontSize: '0.875rem' }}>
                      {endpoint.auth_required ? '🔐 Auth Required' : '🔓 Public'}
                    </div>
                  </div>
                ))}

                {filteredEndpoints.length === 0 && (
                  <div
                    style={{
                      padding: '16px',
                      borderRadius: '8px',
                      border: `1px dashed ${token.border}`,
                      color: token.textMuted,
                      textAlign: 'center',
                    }}
                  >
                    No endpoints match the current filters.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Failures */}
          {currentExecution.failures && currentExecution.failures.length > 0 && (
            <div
              style={{
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: '16px',
                padding: '24px',
                marginBottom: '24px',
              }}
            >
              <h3 style={{ color: token.danger, marginBottom: '16px', fontSize: '1.1rem' }}>
                ⚠️ Failures & Fixes ({currentExecution.failures.length})
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {currentExecution.failures.map((failure, i) => (
                  <div
                    key={i}
                    style={{
                      background: 'rgba(0,0,0,0.2)',
                      borderLeft: '4px solid ' + token.danger,
                      padding: '16px',
                      borderRadius: '8px',
                    }}
                  >
                    <div style={{ color: 'white', fontWeight: 600, marginBottom: '8px' }}>
                      {failure.test_name}
                    </div>
                    <div
                      style={{
                        color: token.textMuted,
                        fontSize: '0.875rem',
                        marginBottom: '12px',
                      }}
                    >
                      <strong>Error:</strong> {failure.error}
                    </div>
                    <div
                      style={{
                        color: token.textMuted,
                        fontSize: '0.875rem',
                        marginBottom: '12px',
                      }}
                    >
                      <strong>Root Cause:</strong> {failure.root_cause}
                    </div>
                    <div
                      style={{
                        background: 'rgba(0,0,0,0.3)',
                        padding: '12px',
                        borderRadius: '6px',
                        color: token.success,
                        fontSize: '0.85rem',
                        fontFamily: '"Fira Code", monospace',
                        marginBottom: '12px',
                      }}
                    >
                      <strong>💡 Suggested Fix:</strong>
                      <div style={{ marginTop: '8px' }}>{failure.suggested_fix}</div>
                    </div>
                    <div
                      style={{
                        display: 'flex',
                        gap: '16px',
                        fontSize: '0.875rem',
                        color: token.textMuted,
                      }}
                    >
                      <span>
                        <strong>File:</strong> {failure.affected_file}
                      </span>
                      <span>
                        <strong>Line:</strong> {failure.line_number}
                      </span>
                      <span>
                        <strong>Severity:</strong> {failure.severity}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Markdown Report */}
          {currentExecution.report_markdown && (
            <div
              style={{
                background: token.cardBg,
                border: `1px solid ${token.border}`,
                borderRadius: '16px',
                padding: '24px',
                backdropFilter: 'blur(12px)',
              }}
            >
              <h3 style={{ color: 'white', marginBottom: '16px', fontSize: '1.1rem' }}>
                📄 Full Report
              </h3>
              <pre
                style={{
                  background: 'rgba(0,0,0,0.3)',
                  padding: '16px',
                  borderRadius: '8px',
                  color: token.textMuted,
                  overflow: 'auto',
                  fontSize: '0.8rem',
                  lineHeight: 1.6,
                  maxHeight: '400px',
                }}
              >
                {currentExecution.report_markdown}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
