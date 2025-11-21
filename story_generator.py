from model import call_model

def ask_length_choice() -> str:
    """
    Ask the user to choose story length.
    Returns one of: "short", "medium", "long".
    """
    print("Choose story length:")
    print("  1) Short  (about 300–500 words)")
    print("  2) Medium (about 600–900 words)")
    print("  3) Long   (about 1000–1300 words)")

    choice = input("Enter 1, 2, or 3: ").strip()
    mapping = {"1": "short", "2": "medium", "3": "long"}
    return mapping.get(choice, "medium")


def ask_arc_choice() -> str:
    """
    Ask the parent what they want today's story to help their child feel or learn.
    Returns an arc key string.
    """
    print("\nWhat would you like today's story to help your child feel or learn?")
    print("  1) Confidence / Overcoming Fear")
    print("  2) Kindness & Empathy")
    print("  3) Friendship & Cooperation")
    print("  4) Curiosity & Love of Learning")
    print("  5) Calm & Relaxation for Bedtime")
    print("  6) Responsibility & Independence")
    print("  7) Silly, Creative Fun")

    choice = input("Enter 1, 2, 3, 4, 5, 6, or 7: ").strip()
    mapping = {
        "1": "confidence_overcoming_fear",
        "2": "kindness_empathy",
        "3": "friendship_cooperation",
        "4": "curiosity_learning",
        "5": "calming_bedtime",
        "6": "responsibility_independence",
        "7": "silly_creative_fun",
    }
    return mapping.get(choice, "calming_bedtime")

def categorize_request(user_request: str) -> str:
    """
    Use the LLM as a classifier to categorize the request into a high-level theme.
    Returns one of a small set of category labels.
    """
    system_prompt = """You are a classifier for children's bedtime story requests.

Given a request, choose exactly ONE category from this list:
- adventure
- friendship
- overcoming_fear
- animals
- bedtime_calming
- silly_fun

Return ONLY the category name, with no explanation."""

    user_prompt = f'REQUEST:\n"{user_request}"'

    raw = call_model(system_prompt, user_prompt, max_tokens=20, temperature=0.0).strip().lower()

    valid = {"adventure", "friendship", "overcoming_fear", "animals", "bedtime_calming", "silly_fun"}
    if raw in valid:
        return raw
    
    for v in valid:
        if v in raw:
            return v
        
    return "adventure"  # default fallback


def length_instruction(length_choice: str) -> str:
    """
    Map the length choice to a textual instruction.
    """
    if length_choice == "short":
        return "Length: around 300 to 500 words."
    if length_choice == "long":
        return "Length: around 1000 to 1300 words."
    return "Length: around 600 to 900 words."  # medium default


def arc_instruction(arc_choice: str) -> str:
    """
    Provide a textual description of the chosen parent-intent story arc.
    """
    if arc_choice == "confidence_overcoming_fear":
        return (
            "Focus on building confidence and gently overcoming fear:\n"
            "- Beginning: show the child character and something they feel unsure or afraid about.\n"
            "- Middle: they receive support, try small steps, and slowly feel braver.\n"
            "- End: they discover that they can handle this challenge, feeling safe, proud, and reassured."
        )
    if arc_choice == "kindness_empathy":
        return (
            "Focus on kindness and empathy:\n"
            "- Beginning: introduce characters and a situation where someone has a need or big feelings.\n"
            "- Middle: the main character practices listening, caring, and helping.\n"
            "- End: everyone feels understood and cared for, and the story highlights how kindness matters."
        )
    if arc_choice == "friendship_cooperation":
        return (
            "Focus on friendship and cooperation:\n"
            "- Beginning: show friends spending time together.\n"
            "- Middle: they face a small problem or disagreement and learn to communicate, share, and work together.\n"
            "- End: the friends solve the problem and feel even closer than before."
        )
    if arc_choice == "curiosity_learning":
        return (
            "Focus on curiosity and love of learning:\n"
            "- Beginning: introduce a curious child or creature who loves to ask questions.\n"
            "- Middle: they explore, experiment, or discover something new in a safe, imaginative way.\n"
            "- End: they feel excited about learning and fall asleep with happy, curious thoughts."
        )
    if arc_choice == "calming_bedtime":
        return (
            "Focus on calm, relaxation, and winding down for sleep:\n"
            "- Beginning: describe a gentle evening or bedtime routine with cozy details.\n"
            "- Middle: include a small, soothing event (a quiet adventure, a comforting conversation, or a peaceful moment).\n"
            "- End: everything slows down, the characters feel sleepy and safe, and the final moments are very calming."
        )
    if arc_choice == "responsibility_independence":
        return (
            "Focus on responsibility and independence:\n"
            "- Beginning: show the child character wanting to try a new task or take on more responsibility.\n"
            "- Middle: they practice, make small mistakes, and keep trying with support.\n"
            "- End: they succeed or make clear progress, feeling proud and capable, with a gentle reminder that effort matters."
        )
    if arc_choice == "silly_creative_fun":
        return (
            "Focus on silly, creative fun while still ending in a calm way:\n"
            "- Beginning: introduce playful characters and a funny or imaginative situation.\n"
            "- Middle: let harmless, light-hearted chaos unfold (jokes, funny surprises, creative twists).\n"
            "- End: things settle down into a peaceful ending so the child still feels relaxed and ready for sleep."
        )
    return ""


def category_instruction(category: str) -> str:
    """
    Provide extra, tailored guidance based on the automatically detected category.
    """
    if category == "adventure":
        return "Emphasize exploration, curiosity, and safe, imaginative adventures."
    if category == "friendship":
        return "Highlight kindness, listening, sharing, and how friends support each other."
    if category == "overcoming_fear":
        return (
            "Treat fear very gently. Show that it is okay to be scared and that support, "
            "understanding, and small steps can help the character feel braver."
        )
    if category == "animals":
        return "Use animal characters with clear personalities and gentle, playful behavior."
    if category == "bedtime_calming":
        return (
            "Focus strongly on calming images (stars, night sky, soft blankets, soothing sounds) "
            "and a slow, relaxing pace that makes listeners feel sleepy and safe."
        )
    if category == "silly_fun":
        return (
            "Include light-hearted jokes, funny misunderstandings, and playful details, "
            "but keep everything kind and never mean-spirited."
        )
    return ""

def build_storyteller_prompt(
    user_request: str,
    length_choice: str,
    arc_choice: str,
    category: str
) -> tuple[str, str]:
    """
    Build the prompt for the 'storyteller' agent, incorporating:
    - user request
    - length choice
    - parent-intent arc
    - category-specific instructions
    
    Returns a tuple of (system_prompt, user_prompt).
    """
    length_text = length_instruction(length_choice)
    arc_text = arc_instruction(arc_choice)
    category_text = category_instruction(category)

    system_prompt = f"""You are a warm and imaginative children's storyteller.

Your audience is children between 5 and 10 years old who are about to go to sleep.
An adult (a parent or caregiver) will read this story aloud to the child.

Story requirements:
- {length_text}
- Use simple, clear language suitable for ages 5–10.
- Keep the tone gentle, cozy, and reassuring (no graphic or intense content).
- Give the story a clear beginning, middle, and end.
- Ensure the story is easy to follow when read aloud.
- Include a positive, comforting ending.
- End with a short, explicit moral stated in one or two sentences.

Parent-intent story arc guidance:
{arc_text}

Category guidance (from an internal classifier):
Category = {category}
{category_text}"""

    user_prompt = f"""Here is the adult's request for the story:
"{user_request}"

Now write the complete bedtime story."""

    return (system_prompt, user_prompt)
    
def generate_story(user_request: str, length_choice: str, arc_choice: str, category: str) -> str:
    """
    Use the storyteller prompt to generate an initial draft of the story.
    """
    system_prompt, user_prompt = build_storyteller_prompt(user_request, length_choice, arc_choice, category)
    story = call_model(system_prompt, user_prompt, max_tokens=1500, temperature=0.85)
    return story