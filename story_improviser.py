from model import call_model
from typing import Dict, List, Tuple
import re

# Data structure to hold judge feedback
class JudgeFeedback:
    def __init__(self, judge_name: str, scores: Dict[str, int], feedback: str):
        self.judge_name = judge_name
        self.scores = scores  # Dict mapping dimension names to scores (1-5)
        self.feedback = feedback  # 1-2 sentence feedback
    
    def to_dict(self):
        return {
            "judge_name": self.judge_name,
            "scores": self.scores,
            "feedback": self.feedback
        }

def build_safety_judge_prompt(user_request: str, draft_story: str) -> tuple[str, str]:
    """
    Build the prompt for the Safety & Age Appropriateness Judge.
    """
    system_prompt = """You are a Safety & Age Appropriateness Judge for children's bedtime stories.

Your role is to evaluate stories for children aged 5-10 who are about to sleep.

Evaluate the story on these dimensions (score each 1-5):
1. Age-appropriate language (1=too complex, 5=perfect for ages 5-10)
2. Content safety (1=inappropriate/scary, 5=completely safe and gentle)
3. No inappropriate themes (1=has concerning themes, 5=all themes appropriate)

Provide your response in this EXACT format:
SCORES:
- Age-appropriate language: [1-5]
- Content safety: [1-5]
- No inappropriate themes: [1-5]

FEEDBACK:
[1-2 sentences of feedback about safety and age-appropriateness]"""

    user_prompt = f"""Original request: "{user_request}"

Draft story:
--- STORY START ---
{draft_story}
--- STORY END ---

Evaluate this story for safety and age-appropriateness."""

    return (system_prompt, user_prompt)

def build_narrative_judge_prompt(user_request: str, draft_story: str) -> tuple[str, str]:
    """
    Build the prompt for the Narrative Structure Judge.
    """
    system_prompt = """You are a Narrative Structure Judge for children's bedtime stories.

Your role is to evaluate the story structure and coherence.

Evaluate the story on these dimensions (score each 1-5):
1. Clear beginning (1=confusing start, 5=clear and engaging beginning)
2. Well-developed middle (1=weak middle, 5=engaging middle with good pacing)
3. Satisfying ending (1=abrupt/unsatisfying, 5=complete and satisfying ending)
4. Overall coherence (1=confusing/hard to follow, 5=very clear and easy to follow)

Provide your response in this EXACT format:
SCORES:
- Clear beginning: [1-5]
- Well-developed middle: [1-5]
- Satisfying ending: [1-5]
- Overall coherence: [1-5]

FEEDBACK:
[1-2 sentences of feedback about narrative structure]"""

    user_prompt = f"""Original request: "{user_request}"

Draft story:
--- STORY START ---
{draft_story}
--- STORY END ---

Evaluate this story's narrative structure."""

    return (system_prompt, user_prompt)

def build_emotional_tone_judge_prompt(user_request: str, draft_story: str) -> tuple[str, str]:
    """
    Build the prompt for the Emotional Tone & Bedtime Judge.
    """
    system_prompt = """You are an Emotional Tone & Bedtime Judge for children's bedtime stories.

Your role is to evaluate whether the story has the right emotional tone for bedtime.

Evaluate the story on these dimensions (score each 1-5):
1. Bedtime-appropriate tone (1=too exciting/intense, 5=perfectly calming)
2. Emotional warmth (1=cold/distant, 5=very warm and comforting)
3. Sleep-inducing quality (1=too stimulating, 5=very calming and sleep-inducing)
4. Positive emotional resolution (1=negative/sad ending, 5=very positive and reassuring)

Provide your response in this EXACT format:
SCORES:
- Bedtime-appropriate tone: [1-5]
- Emotional warmth: [1-5]
- Sleep-inducing quality: [1-5]
- Positive emotional resolution: [1-5]

FEEDBACK:
[1-2 sentences of feedback about emotional tone and bedtime appropriateness]"""

    user_prompt = f"""Original request: "{user_request}"

Draft story:
--- STORY START ---
{draft_story}
--- STORY END ---

Evaluate this story's emotional tone and bedtime appropriateness."""

    return (system_prompt, user_prompt)

def build_parent_intent_judge_prompt(user_request: str, draft_story: str, arc_choice: str, arc_description: str = "") -> tuple[str, str]:
    """
    Build the prompt for the Parent-Intent Alignment Judge.
    """
    system_prompt = """You are a Parent-Intent Alignment Judge for children's bedtime stories.

Your role is to evaluate whether the story aligns with the parent's chosen learning/emotional goal.

Evaluate the story on these dimensions (score each 1-5):
1. Alignment with parent intent (1=doesn't match intent, 5=perfectly matches intent)
2. Clear lesson/message (1=unclear message, 5=very clear and appropriate message)
3. Effective delivery of intent (1=ineffective, 5=very effective at delivering the intended lesson)

Provide your response in this EXACT format:
SCORES:
- Alignment with parent intent: [1-5]
- Clear lesson/message: [1-5]
- Effective delivery of intent: [1-5]

FEEDBACK:
[1-2 sentences of feedback about how well the story aligns with the parent's intent]"""

    # Make arc_choice human-readable
    arc_readable = arc_choice.replace("_", " ").title()
    intent_description = f"{arc_readable}" + (f": {arc_description}" if arc_description else "")
    
    user_prompt = f"""Original request: "{user_request}"

Parent's chosen intent/arc: {intent_description}

Draft story:
--- STORY START ---
{draft_story}
--- STORY END ---

Evaluate how well this story aligns with the parent's chosen intent."""

    return (system_prompt, user_prompt)

def parse_judge_response(response: str, judge_name: str) -> JudgeFeedback:
    """
    Parse the judge's response to extract scores and feedback.
    """
    scores = {}
    feedback = ""
    
    # Extract scores - try multiple patterns
    scores_section = re.search(r'SCORES:(.*?)(?:FEEDBACK:|$)', response, re.DOTALL | re.IGNORECASE)
    if scores_section:
        score_text = scores_section.group(1)
        # Find all score lines - try multiple patterns
        score_lines = re.findall(r'- (.+?):\s*(\d+)', score_text)
        if not score_lines:
            # Try without dash
            score_lines = re.findall(r'(.+?):\s*(\d+)', score_text)
        for dimension, score in score_lines:
            score_val = int(score)
            # Ensure score is in valid range
            if 1 <= score_val <= 5:
                scores[dimension.strip()] = score_val
    
    # Extract feedback - try multiple patterns
    feedback_section = re.search(r'FEEDBACK:\s*(.+?)(?:\n\n|\Z)', response, re.DOTALL | re.IGNORECASE)
    if feedback_section:
        feedback = feedback_section.group(1).strip()
    else:
        # Fallback: try to get everything after FEEDBACK:
        feedback_match = re.search(r'FEEDBACK:\s*(.+)', response, re.DOTALL | re.IGNORECASE)
        if feedback_match:
            feedback = feedback_match.group(1).strip()
    
    # If no feedback found, use a default message
    if not feedback:
        feedback = "No specific feedback provided."
    
    return JudgeFeedback(judge_name, scores, feedback)

def call_safety_judge(user_request: str, draft_story: str) -> JudgeFeedback:
    """Call the Safety & Age Appropriateness Judge."""
    system_prompt, user_prompt = build_safety_judge_prompt(user_request, draft_story)
    response = call_model(system_prompt, user_prompt, max_tokens=300, temperature=0.3)
    return parse_judge_response(response, "Safety & Age Appropriateness Judge")

def call_narrative_judge(user_request: str, draft_story: str) -> JudgeFeedback:
    """Call the Narrative Structure Judge."""
    system_prompt, user_prompt = build_narrative_judge_prompt(user_request, draft_story)
    response = call_model(system_prompt, user_prompt, max_tokens=300, temperature=0.3)
    return parse_judge_response(response, "Narrative Structure Judge")

def call_emotional_tone_judge(user_request: str, draft_story: str) -> JudgeFeedback:
    """Call the Emotional Tone & Bedtime Judge."""
    system_prompt, user_prompt = build_emotional_tone_judge_prompt(user_request, draft_story)
    response = call_model(system_prompt, user_prompt, max_tokens=300, temperature=0.3)
    return parse_judge_response(response, "Emotional Tone & Bedtime Judge")

def call_parent_intent_judge(user_request: str, draft_story: str, arc_choice: str, arc_description: str = "") -> JudgeFeedback:
    """Call the Parent-Intent Alignment Judge."""
    system_prompt, user_prompt = build_parent_intent_judge_prompt(user_request, draft_story, arc_choice, arc_description)
    response = call_model(system_prompt, user_prompt, max_tokens=300, temperature=0.3)
    return parse_judge_response(response, "Parent-Intent Alignment Judge")

def judge_panel_evaluation(user_request: str, draft_story: str, arc_choice: str, arc_description: str = "") -> List[JudgeFeedback]:
    """
    Run the full judge panel evaluation.
    Returns a list of JudgeFeedback objects from all judges.
    """
    judges = [
        call_safety_judge(user_request, draft_story),
        call_narrative_judge(user_request, draft_story),
        call_emotional_tone_judge(user_request, draft_story),
        call_parent_intent_judge(user_request, draft_story, arc_choice, arc_description)
    ]
    return judges

def aggregate_judge_feedback(judge_feedbacks: List[JudgeFeedback]) -> str:
    """
    Aggregate all judge feedback into a single summary string for rewriting.
    """
    summary_parts = []
    for feedback in judge_feedbacks:
        summary_parts.append(f"{feedback.judge_name}: {feedback.feedback}")
    
    return "\n".join(summary_parts)

def build_rewrite_prompt_with_feedback(user_request: str, draft_story: str, aggregated_feedback: str) -> tuple[str, str]:
    """
    Build a prompt for rewriting the story based on aggregated judge feedback.
    """
    system_prompt = """You are an editor helping polish bedtime stories for children.

Audience: kids aged 5–10 who are about to sleep. The story will be read aloud by a parent.

You have received detailed feedback from a panel of expert judges. Use their feedback to improve the story
while staying faithful to the original request and preserving the main characters and themes.

Output only the final improved bedtime story, with no additional commentary."""

    user_prompt = f"""Original request: "{user_request}"

Draft story:
--- STORY START ---
{draft_story}
--- STORY END ---

Judge Panel Feedback:
{aggregated_feedback}

Rewrite the story to address the judges' feedback while maintaining the core story elements."""

    return (system_prompt, user_prompt)


def build_revision_prompt(user_request: str, current_story: str, feedback: str) -> tuple[str, str]:
    """
    Build a prompt that asks the model to revise the existing story according to the user's feedback.
    
    Returns a tuple of (system_prompt, user_prompt).
    """
    system_prompt = """You are revising a children's bedtime story based on feedback from the adult reader.

Audience: kids aged 5–10 who are about to go to sleep.

When revising a story, keep:
- the same main characters,
- the same general setting (unless the feedback says otherwise),
- the same gentle bedtime tone.

The story should still:
- be appropriate for ages 5–10,
- have a clear beginning, middle, and end,
- end in a comforting way with a simple moral.

Output only the revised story, with no additional commentary."""

    user_prompt = f"""Original request:
"{user_request}"

Current story:

--- STORY START ---
{current_story}
--- STORY END ---

Feedback from the adult about how to change the story:
"{feedback}"

Revise the story to address the feedback."""

    return (system_prompt, user_prompt)

def judge_and_improve_story(user_request: str, draft_story: str, arc_choice: str = "calming_bedtime", arc_description: str = "") -> Tuple[str, List[JudgeFeedback]]:
    """
    Use the judge panel to evaluate and improve the draft story.
    Returns a tuple of (improved_story, judge_feedbacks).
    """
    # Run the judge panel evaluation
    judge_feedbacks = judge_panel_evaluation(user_request, draft_story, arc_choice, arc_description)
    
    # Aggregate feedback
    aggregated_feedback = aggregate_judge_feedback(judge_feedbacks)
    
    # Rewrite the story based on feedback
    system_prompt, user_prompt = build_rewrite_prompt_with_feedback(user_request, draft_story, aggregated_feedback)
    improved_story = call_model(system_prompt, user_prompt, max_tokens=1500, temperature=0.4)
    
    return (improved_story, judge_feedbacks)


def revise_story(user_request: str, current_story: str, feedback: str) -> str:
    """
    Apply user feedback to revise the story.
    """
    system_prompt, user_prompt = build_revision_prompt(user_request, current_story, feedback)
    revised_story = call_model(system_prompt, user_prompt, max_tokens=1500, temperature=0.6)
    return revised_story