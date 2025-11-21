from story_generator import *
from story_improviser import *

"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

If given 2 more hours, I would add a simple GUI or web interface where parents can
select today's learning focus (confidence, kindness, curiosity, etc.) with icons and
save their child's favorite characters. I would also log which themes are chosen most
often and adapt future stories to revisit key lessons in new situations, building a
gentle, personalized learning journey over time.
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

    print("Improving the story for clarity, age-appropriateness, and bedtime tone...\n")
    final_story = judge_and_improve_story(user_request, draft_story)

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