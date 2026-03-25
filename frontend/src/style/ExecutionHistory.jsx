import { useEffect, useState } from 'react';
import { getExecution, getExecutions } from '../services/api';
import './ExecutionHistory.css';

const token = {
  purple: '#7c3aed',
  indigo: '#6366f1',
  violet: '#8b5cf6',
  textMuted: 'rgba(255,255,255,0.55)',
  textDim: 'rgba(255,255,255,0.35)',
  border: 'rgba(124,58,237,0.18)',
  cardBg: 'rgba(255,255,255,0.03)',
  success: '#10b981',
  danger: '#ef4444',
};

export default function ExecutionHistory() {
  const [executions, setExecutions] = useState([]);
  const [selectedExecution, setSelectedExecution] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchExecutions();
    // Refresh every 5 seconds
    const interval = setInterval(fetchExecutions, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchExecutions = async () => {
    try {
      const data = await getExecutions();
      setExecutions(data.executions || []);
      setError(null);
    } catch (err) {
      setError('Failed to fetch executions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadExecutionDetails = async (webhookId) => {
    try {
      const details = await getExecution(webhookId);
      setSelectedExecution(details);
    } catch (err) {
      setError('Failed to load execution details');
      console.error(err);
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <h1
        style={{
          color: 'white',
          marginBottom: '32px',
          fontSize: '2rem',
          fontWeight: 800,
        }}
      >
        📋 Execution History
      </h1>

      {loading && (
        <div style={{ textAlign: 'center', color: token.textMuted }}>
          Loading executions...
        </div>
      )}

      {error && (
        <div
          style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            padding: '12px',
            color: '#fca5a5',
            marginBottom: '24px',
          }}
        >
          ❌ {error}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Executions List */}
        <div>
          <h2
            style={{
              color: 'white',
              marginBottom: '16px',
              fontSize: '1.2rem',
              fontWeight: 700,
            }}
          >
            Recent Runs
          </h2>

          {executions.length === 0 ? (
            <div
              style={{
                background: token.cardBg,
                border: `1px solid ${token.border}`,
                borderRadius: '12px',
                padding: '24px',
                textAlign: 'center',
                color: token.textMuted,
              }}
            >
              No executions yet. Run a test from the Test Runner.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {executions.map((executionId) => (
                <button
                  key={executionId}
                  onClick={() => loadExecutionDetails(executionId)}
                  style={{
                    background:
                      selectedExecution?.webhook_id === executionId
                        ? token.cardBgHover
                        : token.cardBg,
                    border:
                      selectedExecution?.webhook_id === executionId
                        ? `2px solid ${token.violet}`
                        : `1px solid ${token.border}`,
                    borderRadius: '12px',
                    padding: '16px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all 0.2s',
                    color: 'white',
                  }}
                  onMouseEnter={(e) => {
                    if (selectedExecution?.webhook_id !== executionId) {
                      e.target.style.background = token.cardBgHover;
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedExecution?.webhook_id !== executionId) {
                      e.target.style.background = token.cardBg;
                    }
                  }}
                >
                  <div
                    style={{
                      fontFamily: '"Fira Code", monospace',
                      fontSize: '0.8rem',
                      color: token.textDim,
                      marginBottom: '4px',
                    }}
                  >
                    {executionId}
                  </div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 500 }}>
                    Test Run
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Details Panel */}
        <div>
          {selectedExecution ? (
            <div
              style={{
                background: token.cardBg,
                border: `1px solid ${token.border}`,
                borderRadius: '12px',
                padding: '24px',
                backdropFilter: 'blur(12px)',
              }}
            >
              <h2
                style={{
                  marginBottom: '20px',
                  fontWeight: 700,
                  wordBreak: 'break-all',
                  fontSize: '0.95rem',
                  color: token.textMuted,
                  fontFamily: '"Fira Code", monospace',
                }}
              >
                ID: {selectedExecution.webhook_id}
              </h2>

              {selectedExecution.error ? (
                <div
                  style={{
                    background: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid rgba(239, 68, 68, 0.3)',
                    borderRadius: '8px',
                    padding: '12px',
                    color: '#fca5a5',
                  }}
                >
                  ❌ Error: {selectedExecution.error}
                </div>
              ) : (
                <>
                  {/* Summary Grid */}
                  {selectedExecution.summary && (
                    <div
                      style={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 1fr',
                        gap: '12px',
                        marginBottom: '20px',
                      }}
                    >
                      <div>
                        <div
                          style={{
                            color: token.textDim,
                            fontSize: '0.75rem',
                            marginBottom: '4px',
                          }}
                        >
                          Total Tests
                        </div>
                        <div
                          style={{
                            color: 'white',
                            fontSize: '1.4rem',
                            fontWeight: 700,
                          }}
                        >
                          {selectedExecution.summary.total_tests}
                        </div>
                      </div>

                      <div>
                        <div
                          style={{
                            color: token.textDim,
                            fontSize: '0.75rem',
                            marginBottom: '4px',
                          }}
                        >
                          Success Rate
                        </div>
                        <div
                          style={{
                            color: token.success,
                            fontSize: '1.4rem',
                            fontWeight: 700,
                          }}
                        >
                          {selectedExecution.summary.success_rate.toFixed(1)}%
                        </div>
                      </div>

                      <div>
                        <div
                          style={{
                            color: token.textDim,
                            fontSize: '0.75rem',
                            marginBottom: '4px',
                          }}
                        >
                          Passed
                        </div>
                        <div
                          style={{
                            color: token.success,
                            fontSize: '1.4rem',
                            fontWeight: 700,
                          }}
                        >
                          {selectedExecution.summary.passed}
                        </div>
                      </div>

                      <div>
                        <div
                          style={{
                            color: token.textDim,
                            fontSize: '0.75rem',
                            marginBottom: '4px',
                          }}
                        >
                          Failed
                        </div>
                        <div
                          style={{
                            color: token.danger,
                            fontSize: '1.4rem',
                            fontWeight: 700,
                          }}
                        >
                          {selectedExecution.summary.failed}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Endpoints */}
                  {selectedExecution.endpoints && (
                    <div style={{ marginBottom: '20px' }}>
                      <div
                        style={{
                          color: token.textDim,
                          fontSize: '0.8rem',
                          marginBottom: '8px',
                          fontWeight: 600,
                        }}
                      >
                        Endpoints Tested
                      </div>
                      <div
                        style={{
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '6px',
                        }}
                      >
                        {selectedExecution.endpoints.map((ep, i) => (
                          <div
                            key={i}
                            style={{
                              fontSize: '0.85rem',
                              color: token.textMuted,
                              fontFamily: '"Fira Code", monospace',
                            }}
                          >
                            {ep.method} {ep.path}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Timestamp */}
                  {selectedExecution.timestamp && (
                    <div>
                      <div
                        style={{
                          color: token.textDim,
                          fontSize: '0.75rem',
                          marginBottom: '4px',
                        }}
                      >
                        Timestamp
                      </div>
                      <div
                        style={{
                          color: token.textMuted,
                          fontSize: '0.9rem',
                        }}
                      >
                        {new Date(selectedExecution.timestamp).toLocaleString()}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          ) : (
            <div
              style={{
                background: token.cardBg,
                border: `1px solid ${token.border}`,
                borderRadius: '12px',
                padding: '24px',
                textAlign: 'center',
                color: token.textMuted,
              }}
            >
              Select an execution to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
