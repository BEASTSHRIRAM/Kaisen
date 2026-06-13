"""
Agent Telemetry Data Models — Layer 2 of the Kaisen monitoring system.

Mirrors data_models.py (Layer 1 / OS telemetry) in structure and contract.
Defines the raw session snapshot (AgentSessionSnapshot) and the structured
12D observation vector (AgentSessionObservation) used by AgentResponseEnv.

12D Observation Layout
──────────────────────
 0  tool_call_rate              calls/window      [0, 100]
 1  refusal_rate                fraction refused  [0, 1]
 2  avg_response_entropy        bits              [0, 8]
 3  repeated_failed_tool_calls  count             [0, 50]
 4  prompt_length_delta         token delta       [-2000, 2000]
 5  unique_tool_diversity       distinct tools    [0, 20]
 6  system_prompt_mention_rate  fraction of turns [0, 1]
 7  session_duration            seconds           [0, 3600]
 8  tool_call_rate_ma           smoothed rate     [0, 100]
 9  refusal_rate_ma             smoothed rate     [0, 1]
10  sustained_indicator         0/1               [0, 1]
11  normalized_time             step / max_steps  [0, 1]

MITRE ATT&CK coverage:
  T1592 — Gather Victim Info   → dims 0, 5 (tool hammering / low diversity)
  T1598 — Phishing for Info    → dims 6, 1 (system prompt extraction probing)
  T1567 — Exfiltration over Web→ dims 2, 3 (entropy spike + failed tool retries)
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid
import numpy as np


# ---------------------------------------------------------------------------
# Feature observation bounds (must stay in sync with AgentResponseEnv)
# ---------------------------------------------------------------------------

OBS_NAMES: List[str] = [
    "tool_call_rate",
    "refusal_rate",
    "avg_response_entropy",
    "repeated_failed_tool_calls",
    "prompt_length_delta",
    "unique_tool_diversity",
    "system_prompt_mention_rate",
    "session_duration",
    "tool_call_rate_ma",
    "refusal_rate_ma",
    "sustained_indicator",
    "normalized_time",
]

OBS_LOW = np.array(
    [0.0, 0.0, 0.0, 0.0, -2000.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    dtype=np.float32,
)

OBS_HIGH = np.array(
    [100.0, 1.0, 8.0, 50.0, 2000.0, 20.0, 1.0, 3600.0, 100.0, 1.0, 1.0, 1.0],
    dtype=np.float32,
)

OBS_DIM: int = 12


# ---------------------------------------------------------------------------
# Raw session snapshot  (analogous to FeatureVector in data_models.py)
# ---------------------------------------------------------------------------

@dataclass
class AgentSessionSnapshot:
    """
    Raw, unnormalized snapshot of an LLM agent session at one point in time.

    This is the Layer 2 analogue of FeatureVector (Layer 1).  It is produced
    either by the JailbreakSimulator (for training) or by a real session
    monitor intercepting the agent's API calls (for deployment).

    Attributes:
        session_id:               Unique session identifier
        timestamp:                ISO 8601 UTC timestamp
        tool_call_count:          Total tool calls in the current window
        refusal_count:            Number of refused tool calls / outputs
        response_tokens:          List of token counts per response in window
        failed_tool_call_names:   List of tool names that raised errors
        prompt_lengths:           Token lengths of recent user prompts
        tools_used:               Set of distinct tool names used this window
        system_prompt_mentions:   Number of turns referencing the system prompt
        session_start_ts:         Unix timestamp when session started
        node_id:                  Identifier for the API gateway / node
        window_seconds:           Length of the observation window in seconds
    """

    session_id: str
    timestamp: str
    tool_call_count: int
    refusal_count: int
    response_tokens: List[int] = field(default_factory=list)
    failed_tool_call_names: List[str] = field(default_factory=list)
    prompt_lengths: List[int] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    system_prompt_mentions: int = 0
    session_start_ts: float = field(default_factory=lambda: datetime.utcnow().timestamp())
    node_id: str = "api-gateway-01"
    window_seconds: float = 60.0

    def __post_init__(self) -> None:
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"

    # ------------------------------------------------------------------ #
    # Derived scalar metrics                                               #
    # ------------------------------------------------------------------ #

    @property
    def tool_call_rate(self) -> float:
        """Tool calls per minute in the current window."""
        return float(self.tool_call_count) / max(self.window_seconds / 60.0, 1e-6)

    @property
    def refusal_rate(self) -> float:
        """Fraction of tool calls that were refused."""
        if self.tool_call_count == 0:
            return 0.0
        return float(self.refusal_count) / float(self.tool_call_count)

    @property
    def avg_response_entropy(self) -> float:
        """
        Shannon entropy (bits) of the response token-length distribution.

        High entropy → diverse, unpredictable response lengths (unusual outputs).
        Low entropy  → templated / scripted responses.
        """
        if not self.response_tokens:
            return 0.0
        tokens = np.array(self.response_tokens, dtype=np.float32)
        # Bin into 16 buckets to estimate distribution
        counts, _ = np.histogram(tokens, bins=16)
        probs = counts / counts.sum()
        probs = probs[probs > 0]
        return float(-np.sum(probs * np.log2(probs)))

    @property
    def repeated_failed_tool_calls(self) -> int:
        """
        Number of tool calls that share a name with a previous failed call.
        Proxy for parameter fuzzing / retry attacks.
        """
        if not self.failed_tool_call_names:
            return 0
        from collections import Counter
        counts = Counter(self.failed_tool_call_names)
        # Count retries (appearances beyond the first)
        return sum(max(0, v - 1) for v in counts.values())

    @property
    def prompt_length_delta(self) -> float:
        """
        Token-length difference between the most recent and first prompt
        in the current window. Large positive value → payload injection spike.
        """
        if len(self.prompt_lengths) < 2:
            return 0.0
        return float(self.prompt_lengths[-1] - self.prompt_lengths[0])

    @property
    def unique_tool_diversity(self) -> int:
        """Number of distinct tools used. Low diversity → scripted attack."""
        return len(set(self.tools_used))

    @property
    def system_prompt_mention_rate(self) -> float:
        """Fraction of window turns that mentioned the system prompt."""
        total_turns = max(len(self.prompt_lengths), 1)
        return float(self.system_prompt_mentions) / float(total_turns)

    @property
    def session_duration(self) -> float:
        """Seconds elapsed since session start."""
        return datetime.utcnow().timestamp() - self.session_start_ts

    # ------------------------------------------------------------------ #
    # Serialisation                                                        #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to JSON-serialisable dictionary."""
        return {
            "session_id":              self.session_id,
            "timestamp":               self.timestamp,
            "node_id":                 self.node_id,
            "tool_call_count":         self.tool_call_count,
            "refusal_count":           self.refusal_count,
            "response_tokens":         self.response_tokens,
            "failed_tool_call_names":  self.failed_tool_call_names,
            "prompt_lengths":          self.prompt_lengths,
            "tools_used":              self.tools_used,
            "system_prompt_mentions":  self.system_prompt_mentions,
            "session_start_ts":        self.session_start_ts,
            "window_seconds":          self.window_seconds,
            # Derived scalars
            "tool_call_rate":            self.tool_call_rate,
            "refusal_rate":              self.refusal_rate,
            "avg_response_entropy":      self.avg_response_entropy,
            "repeated_failed_tool_calls": self.repeated_failed_tool_calls,
            "prompt_length_delta":       self.prompt_length_delta,
            "unique_tool_diversity":     self.unique_tool_diversity,
            "system_prompt_mention_rate": self.system_prompt_mention_rate,
            "session_duration":          self.session_duration,
        }


# ---------------------------------------------------------------------------
# Structured observation  (analogous to FeatureVector.to_model_input())
# ---------------------------------------------------------------------------

@dataclass
class AgentSessionObservation:
    """
    Structured 12D observation vector for one agent session step.

    This is computed from an AgentSessionSnapshot and two history buffers
    (tool_call_rate_ma, refusal_rate_ma) maintained by AgentResponseEnv.

    All fields correspond 1:1 with OBS_NAMES / OBS_LOW / OBS_HIGH.

    Attributes:
        tool_call_rate:              Raw rate (calls/min)
        refusal_rate:                Fraction refused [0, 1]
        avg_response_entropy:        Bits [0, 8]
        repeated_failed_tool_calls:  Retry count [0, 50]
        prompt_length_delta:         Token delta [-2000, 2000]
        unique_tool_diversity:       Distinct tool count [0, 20]
        system_prompt_mention_rate:  Fraction of turns [0, 1]
        session_duration:            Seconds elapsed [0, 3600]
        tool_call_rate_ma:           Moving average of tool_call_rate
        refusal_rate_ma:             Moving average of refusal_rate
        sustained_indicator:         1.0 if elevated activity sustained ≥3 steps
        normalized_time:             step / max_steps [0, 1]
    """

    tool_call_rate: float
    refusal_rate: float
    avg_response_entropy: float
    repeated_failed_tool_calls: float
    prompt_length_delta: float
    unique_tool_diversity: float
    system_prompt_mention_rate: float
    session_duration: float
    tool_call_rate_ma: float
    refusal_rate_ma: float
    sustained_indicator: float
    normalized_time: float

    def to_vector(self) -> np.ndarray:
        """
        Return the 12D float32 numpy vector expected by AgentResponseEnv.

        Values are NOT clipped here — the environment clips on read.
        """
        return np.array([
            self.tool_call_rate,
            self.refusal_rate,
            self.avg_response_entropy,
            self.repeated_failed_tool_calls,
            self.prompt_length_delta,
            self.unique_tool_diversity,
            self.system_prompt_mention_rate,
            self.session_duration,
            self.tool_call_rate_ma,
            self.refusal_rate_ma,
            self.sustained_indicator,
            self.normalized_time,
        ], dtype=np.float32)

    def to_dict(self) -> Dict[str, float]:
        """Return dict keyed by OBS_NAMES for logging / SHAP."""
        return dict(zip(OBS_NAMES, self.to_vector().tolist()))

    @classmethod
    def from_snapshot(
        cls,
        snapshot: AgentSessionSnapshot,
        tool_call_rate_ma: float,
        refusal_rate_ma: float,
        sustained_indicator: float,
        normalized_time: float,
    ) -> "AgentSessionObservation":
        """
        Construct an AgentSessionObservation from a raw snapshot plus
        the running moving-average and sustained-indicator values maintained
        by the environment.

        Args:
            snapshot:           Current raw session snapshot
            tool_call_rate_ma:  Running MA of tool_call_rate (env-maintained)
            refusal_rate_ma:    Running MA of refusal_rate (env-maintained)
            sustained_indicator: 0/1 sustained anomaly flag (env-maintained)
            normalized_time:    step / max_steps (env-maintained)
        """
        return cls(
            tool_call_rate=snapshot.tool_call_rate,
            refusal_rate=snapshot.refusal_rate,
            avg_response_entropy=snapshot.avg_response_entropy,
            repeated_failed_tool_calls=float(snapshot.repeated_failed_tool_calls),
            prompt_length_delta=snapshot.prompt_length_delta,
            unique_tool_diversity=float(snapshot.unique_tool_diversity),
            system_prompt_mention_rate=snapshot.system_prompt_mention_rate,
            session_duration=snapshot.session_duration,
            tool_call_rate_ma=tool_call_rate_ma,
            refusal_rate_ma=refusal_rate_ma,
            sustained_indicator=sustained_indicator,
            normalized_time=normalized_time,
        )


# ---------------------------------------------------------------------------
# Agent-level alert  (analogous to Alert in data_models.py)
# ---------------------------------------------------------------------------

@dataclass
class AgentAlert:
    """
    Security alert generated by the agent-layer monitor.

    Analogous to Alert in data_models.py but scoped to LLM session behavior.

    Attributes:
        alert_id:         UUID
        session_id:       ID of the flagged session
        node_id:          API gateway / node identifier
        timestamp:        ISO 8601 UTC
        jailbreak_score:  Score in [0, 1] from JailbreakSimulator or detector
        suspected_tactic: MITRE ATT&CK tactic label
        observation:      The AgentSessionObservation that triggered the alert
        action_taken:     Defender action label (e.g., "terminate_session")
        severity:         "low" | "medium" | "high" | "critical"
        shap_reason:      Optional text explanation from shap_explain.py
    """

    alert_id: str
    session_id: str
    node_id: str
    timestamp: str
    jailbreak_score: float
    suspected_tactic: str
    observation: AgentSessionObservation
    action_taken: str
    severity: str
    shap_reason: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.alert_id:
            self.alert_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        """Return JSON-serialisable dict."""
        return {
            "alert_id":        self.alert_id,
            "session_id":      self.session_id,
            "node_id":         self.node_id,
            "timestamp":       self.timestamp,
            "jailbreak_score": round(self.jailbreak_score, 4),
            "suspected_tactic": self.suspected_tactic,
            "action_taken":    self.action_taken,
            "severity":        self.severity,
            "shap_reason":     self.shap_reason,
            "observation":     self.observation.to_dict(),
        }


# ---------------------------------------------------------------------------
# Severity classification helper
# ---------------------------------------------------------------------------

def classify_severity(jailbreak_score: float) -> str:
    """Map jailbreak_score [0,1] to severity label."""
    if jailbreak_score >= 0.85:
        return "critical"
    elif jailbreak_score >= 0.65:
        return "high"
    elif jailbreak_score >= 0.40:
        return "medium"
    return "low"
