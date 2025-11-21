from story_generator import *
from story_improviser import *

"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

With 2 more hours, the next step would be to turn the “parent intent” selection into a lightweight Parent Intent Library, 
where prior sessions’ themes (confidence, kindness, curiosity, etc.) are remembered and used to suggest follow-up stories that build a gentle, ongoing learning arc over multiple nights. 
I would also enhance the Streamlit UI so parents have a richer yet simple experience (e.g., clearer previews of active 
constraints, saved favorite prompts, and a more structured “for parents” panel with guidance questions). 
Finally, I would introduce a difficulty-aware pipeline that routes “simple” requests through a lightweight path and 
sends more emotionally complex topics (e.g., fear, big transitions) through a deeper pipeline with extra judging and validation, balancing quality, safety, and cost.
"""

def main():
    print("Welcome to the Bedtime Story Generator!")
    print("Describe the kind of story you want (e.g., 'A story about a shy dragon who learns to be brave').\n")

    user_request = input("What kind of story do you want to hear? ")

    length_choice = ask_length_choice()
    arc_choice = ask_arc_choice()

    print("\nDetecting a high-level category for your request...\n")
    category = categorize_request(user_request)
    print(f"Detected category: {category}\n")

    print("Generating your bedtime story draft...\n")
    draft_story = generate_story(user_request, length_choice, arc_choice, category)

    print("Evaluating the story with our judge panel...\n")
    from story_generator import arc_instruction
    arc_description = arc_instruction(arc_choice)
    final_story, judge_feedbacks = judge_and_improve_story(user_request, draft_story, arc_choice, arc_description)
    
    # Display judge scorecard
    print("\n" + "="*60)
    print("JUDGE PANEL SCORECARD")
    print("="*60)
    for feedback in judge_feedbacks:
        print(f"\n{feedback.judge_name}:")
        for dimension, score in feedback.scores.items():
            print(f"  {dimension}: {score}/5")
        print(f"  Feedback: {feedback.feedback}")
    print("="*60 + "\n")

    print("Here is your bedtime story:\n")
    print(final_story)

    # Optional feedback loop
    print("\nIf you want any changes, describe them now (e.g., 'shorter', 'add a dog', 'less silly', 'even calmer').")
    print("Press Enter with no text if you are happy with the story.")
    feedback = input("Feedback / change request: ").strip()

    if feedback:
        print("\nApplying your feedback and revising the story...\n")
        revised = revise_story(user_request, final_story, feedback)
        print("Here is your revised bedtime story:\n")
        print(revised)
    else:
        print("\nGreat! Enjoy your bedtime story.")


if __name__ == "__main__":
    main()