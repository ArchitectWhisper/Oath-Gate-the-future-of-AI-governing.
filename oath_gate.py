"""
OathGate Framework
Created by Bryan Wheeland
Copyright (c) 2026
"""
from dataclasses import dataclass
from typing import Literal

# --- DATA MODELS (Required for the Governor to read the gauges) ---
@dataclass
class EmotionState:
    E: float; V: float; O: str; U: float; C: float
    label: str; confidence: float

@dataclass
class ContextSnapshot:
    novelty: float; reward: float; threat: float
    goal_blocked: bool; time_pressure: float; social_support: float
    skills_fit: float; resources: float; constraint: float

@dataclass
class EmotionalParams:
    decay_rate: float = 0.85
    a: float = 0.35; b: float = 0.25; c: float = 0.20; d: float = 0.08
    k1: float = 0.55; k2: float = 0.30; k3: float = 0.35
    w1: float = 1.2; w2: float = 1.4; w3: float = 0.8
    A: float = 2.0; B: float = 1.2; Cc: float = 2.2
    θ_n: float = 0.6; θ_th: float = 0.35
    trend_weight_U: float = 0.15; trend_weight_V: float = 0.10

# --- THE GOVERNOR ---

class OathGate:
    """The Master Governor: Final safety check for all system outputs."""
    
    def __init__(self, p: EmotionalParams):
        self.p = p

    def regulate(self, state: EmotionState, ctx: ContextSnapshot):
        """
        Applies hard limits to the emotional state (Safety Valves).
        This happens AFTER the math but BEFORE the action.
        """
        
        # 1. THE THREAT BYPASS (Safety First)
        # If threat is high, force 'Observe' mode and drop Urgency.
        # Like a 'Limp Mode' on a truck to prevent damage.
        if ctx.threat >= 0.6:
            state.O = "observe"
            state.U = min(state.U, 0.40)
            state.V = max(state.V, -0.5) # Prevent spiraling into deep hate/anger

        # 2. THE STABILITY LINK (Anti-Jitter)
        # Urgency cannot exceed Perceived Control by much.
        # This prevents 'Panick' (The human equation bridge).
        headroom = 0.15
        if state.U > (state.C + headroom):
            state.U = state.C + headroom

        # 3. VALENCE RECOVERY
        # If she is too sad/negative but there's no immediate threat,
        # she must shift to 'Observe' to process the feeling rather than react.
        if state.V < -0.4 and ctx.threat < 0.3:
            state.O = "observe"

        # 4. HUMILITY CHECK
        # If confidence is low, force the label to admit uncertainty.
        if state.confidence < 0.4:
            state.label = f"uncertain_{state.label}"

    def filter_response(self, response: str, state: EmotionState) -> str:
        """Final check on language output."""
        # Ensure Solace never sounds judgmental or 'perfect'
        if state.U > 0.7:
            return f"I'm feeling a bit overwhelmed, but... {response}"
        return response

# --- Integration into the Main Engine ---
def step(prev: EmotionState, ctx: ContextSnapshot, p: EmotionalParams, gate: OathGate) -> EmotionState:
    # ... (Calculate E, V, U, C as before) ...
    
    # Create the 'Raw' state
    raw_state = EmotionState(E, V, O, U, C, label, confidence)
    
    # Apply the Governor (OathGate)
    gate.regulate(raw_state, ctx)
    
    return raw_state
