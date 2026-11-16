
import customtkinter as ctk
from tkinter import messagebox
from api_client import (start_revision_session, get_questions, save_answer_attempt, 
complete_revision_session,get_topic_details,get_revision_history, get_revision_session_details,get_revision_subjects,
get_revision_topics,get_topic_performance)
from my_subjects_ui import show_my_subjects
import time



# ---------------- REVISION FUNCTIONS ----------------

def handle_start_revision():

    # Temporary test IDs
    user_id = 1
    topic_id = 1

    result = start_revision_session(user_id, topic_id)

    if "error" in result:
        messagebox.showerror(
            "Error",
            str(result["error"])
        )

    else:
        session_id = result["session"]["session_id"]

        messagebox.showinfo(
            "Success",
            f"Revision session started!\nSession ID: {session_id}"
        )

# revsion mode popup

def show_revision_mode_popup():

    popup = ctk.CTkToplevel(app)
    popup.title("Choose Revision Mode")
    popup.geometry("400x350")
    popup.resizable(False, False)
    popup.grab_set()

    ctk.CTkLabel(
        popup,
        text="Choose Your Revision Mode",
        font=("Arial", 22, "bold"),
        text_color=TEXT
    ).pack(pady=(25, 10))

    ctk.CTkLabel(
        popup,
        text="How would you like to revise today?",
        font=("Arial", 13),
        text_color=MUTED
    ).pack(pady=5)

    ctk.CTkButton(
        popup,
        text="Smart Revision",
        height=45,
        fg_color=PURPLE,
        command=lambda: select_revision_mode("SCHEDULED", popup)
    ).pack(fill="x", padx=35, pady=10)

    ctk.CTkButton(
        popup,
        text="Topic Practice",
        height=45,
        fg_color=PURPLE,
        command=lambda: select_revision_mode("TOPIC_PRACTICE", popup)
    ).pack(fill="x", padx=35, pady=10)

    ctk.CTkButton(
        popup,
        text="Mixed Revision",
        height=45,
        fg_color=PURPLE,
        command=lambda: select_revision_mode("MIXED", popup)
    ).pack(fill="x", padx=35, pady=10)

#select revision mode

# Select Revision Mode
def select_revision_mode(mode, popup):

    popup.destroy()

    if mode == "TOPIC_PRACTICE":

        from my_subjects_ui import show_subjects_for_practice

        show_subjects_for_practice(
            main,
            start_topic_practice
        )

    elif mode == "SCHEDULED":

        start_smart_revision()

    elif mode == "MIXED":

        from my_subjects_ui import show_subjects_for_practice

        show_subjects_for_practice(
            main,
            lambda topic_id: start_selected_revision(
                topic_id, mode
            )
        )

# ---------------- SMART REVISION ----------------

def start_smart_revision():

    user_id = 1

    # Step 1: Get all subjects
    subject_result = get_revision_subjects(user_id)

    if "error" in subject_result:
        messagebox.showerror(
            "Error",
            str(subject_result["error"])
        )
        return

    subjects = subject_result.get("subjects", [])

    if not subjects:
        messagebox.showinfo(
            "Smart Revision",
            "No subjects available. Please add subjects first."
        )
        return

    topic_list = []

    # Step 2: Get topics under every subject
    for subject in subjects:

        topic_result = get_revision_topics(
            user_id,
            subject
        )

        if "error" in topic_result:
            continue

        topics = topic_result.get("topics", [])

        for topic in topics:

            topic_id = topic["revision_topic_id"]

            # Step 3: Get topic performance
            performance = get_topic_performance(
                user_id,
                topic_id
            )

            if "error" in performance:
                continue

            topic_list.append({
                "topic_id": topic_id,
                "topic_name": topic["topic_name"],
                "subject_name": subject,
                "accuracy": performance["accuracy"],
                "priority": performance["revision_priority"]
            })

    if not topic_list:
        messagebox.showinfo(
            "Smart Revision",
            "No topics available for revision."
        )
        return

    # Step 4: Sort topics by revision priority
    priority_order = {
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3,
        "NOT_AVAILABLE": 4
    }

    topic_list.sort(
        key=lambda topic: (
            priority_order.get(topic["priority"], 5),
            topic["accuracy"]
        )
    )

    # Step 5: Find the highest-priority topic with questions
    selected_topic = None
    questions = []

    for topic in topic_list:

        question_result = get_questions(topic["topic_id"])

        if "error" in question_result:
            continue

        available_questions = question_result.get(
            "questions", []
        )

        if available_questions:
            selected_topic = topic
            questions = available_questions
            break

    if not selected_topic:
        messagebox.showinfo(
            "Smart Revision",
            "No questions available in your topics."
        )
        return

    # Step 6: Start revision session
    result = start_revision_session(
        user_id,
        selected_topic["topic_id"],
        "SCHEDULED"
    )

    if "error" in result:
        messagebox.showerror(
            "Error",
            str(result["error"])
        )
        return

    session_id = result["session"]["session_id"]

    messagebox.showinfo(
        "Smart Revision",
        f"Selected Topic: {selected_topic['topic_name']}\n"
        f"Subject: {selected_topic['subject_name']}\n"
        f"Accuracy: {selected_topic['accuracy']}%\n"
        f"Priority: {selected_topic['priority']}"
    )

    # Step 7: Open revision screen
    show_question_screen(
        questions,
        session_id,
        "SCHEDULED",
        selected_topic["topic_id"]
    )
    print("\n--- SMART REVISION TOPIC ANALYSIS ---")

    for topic in topic_list:
        print(
            f"Topic: {topic['topic_name']} | "
            f"Accuracy: {topic['accuracy']}% | "
            f"Priority: {topic['priority']}"
        )

# Start Smart Revision and Mixed Revision
def start_selected_revision(topic_id, mode):

    user_id = 1

    # Create revision session
    result = start_revision_session(
        user_id,
        topic_id,
        mode
    )

    if "error" in result:
        messagebox.showerror("Error", str(result["error"]))
        return

    session_id = result["session"]["session_id"]

    # Get questions for selected topic
    question_result = get_questions(topic_id)

    if "error" in question_result:
        messagebox.showerror("Error", str(question_result["error"]))
        return

    questions = question_result.get("questions", [])

    if not questions:
        messagebox.showinfo(
            "No Questions",
            "No questions available for this topic."
        )
        return

    # Display questions
    show_question_screen(questions, session_id, mode, topic_id)

    
# Start Topic Practice
def start_topic_practice(topic_id):

    user_id = 1
    mode = "TOPIC_PRACTICE"

    # Create revision session
    result = start_revision_session(
        user_id,
        topic_id,
        mode
    )

    if "error" in result:
        messagebox.showerror("Error", str(result["error"]))
        return

    session_id = result["session"]["session_id"]

    # Retrieve questions for selected topic
    question_result = get_questions(topic_id)

    if "error" in question_result:
        messagebox.showerror(
            "Error",
            str(question_result["error"])
        )
        return

    questions = question_result.get("questions", [])

    if not questions:
        messagebox.showinfo(
            "No Questions",
            "No questions available for this topic."
        )
        return

    # Open question screen
    show_question_screen(
    questions,
    session_id,
    "TOPIC_PRACTICE",
    topic_id
)

# Fetch questions and show question screen
def show_question_screen(questions, session_id, mode, topic_id):

    if not questions:
        messagebox.showinfo(
            "No Questions",
            "No questions are available for this revision."
        )
        show_page("Start Revision")
        return

    current_index = 0
    score = 0
    total_questions = len(questions)

    question_start_time = time.time()
    user_id = 1  # Temporary test user ID

    selected_answer = ctk.StringVar(value="")

    def clear_main():
        for widget in main.winfo_children():
            widget.destroy()

    # DISPLAY QUESTION
    def display_question():

        nonlocal question_start_time

        clear_main()

        question = questions[current_index]

        selected_answer.set("")
        question_start_time = time.time()

        ctk.CTkLabel(
            main,
            text=mode.replace('_', ' ').title(),
            font=("Arial", 16, "bold"),
            text_color=PURPLE
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            main,
            text=f"Question {current_index + 1} of {total_questions}",
            font=("Arial", 20, "bold"),
            text_color=TEXT
        ).pack(pady=15)

        ctk.CTkLabel(
            main,
            text=question["question_text"],
            font=("Arial", 18),
            text_color=TEXT,
            wraplength=750
        ).pack(pady=20)

        options = question.get("options_json") or {}

        for letter, option_text in options.items():

            ctk.CTkRadioButton(
                main,
                text=f"{letter}. {option_text}",
                variable=selected_answer,
                value=letter,
                font=("Arial", 15),
                text_color=TEXT
            ).pack(anchor="w", padx=100, pady=10)

        ctk.CTkButton(
            main,
            text="Submit Answer",
            fg_color=PURPLE,
            hover_color="#5745C5",
            height=40,
            command=submit_answer
        ).pack(pady=25)

    # SUBMIT ANSWER
    def submit_answer():

        nonlocal score

        answer = selected_answer.get()

        if not answer:
            messagebox.showwarning(
                "Select Answer",
                "Please select an answer first."
            )
            return

        question = questions[current_index]

        time_taken = round(
            time.time() - question_start_time, 2
        )

        # Save answer through Django
        result = save_answer_attempt(
            user_id,
            session_id,
            question["question_id"],
            answer,
            time_taken
        )

        # Handle API errors
        if "error" in result:
            messagebox.showerror(
                "Save Error",
                f"Could not save your answer:\n{result['error']}"
            )
            return

        # Get correctness from Django
        is_correct = result["is_correct"]

        if is_correct:
            score += 1
            feedback = "Correct Answer!"
            feedback_color = "#2EAD63"

        else:
            feedback = "Incorrect Answer!"
            feedback_color = "#E5484D"

        correct_answer = question["correct_answer"].strip()

        clear_main()

        # Feedback
        ctk.CTkLabel(
            main,
            text=feedback,
            font=("Arial", 24, "bold"),
            text_color=feedback_color
        ).pack(pady=25)

        # Correct answer
        ctk.CTkLabel(
            main,
            text=f"Correct Answer: {correct_answer}",
            font=("Arial", 16, "bold"),
            text_color=TEXT
        ).pack(pady=10)

        # Explanation
        ctk.CTkLabel(
            main,
            text=question.get("explanation") or
                 "No explanation available.",
            font=("Arial", 15),
            text_color=TEXT,
            wraplength=750
        ).pack(pady=20)

        # Next question
        ctk.CTkButton(
            main,
            text="Next Question",
            fg_color=PURPLE,
            hover_color="#5745C5",
            height=40,
            command=next_question
        ).pack(pady=25)

    # NEXT QUESTION
    def next_question():

        nonlocal current_index

        current_index += 1

        if current_index < total_questions:
            display_question()

        else:
            show_revision_result()

    # FINAL RESULT
    def show_revision_result():
        completion_result = complete_revision_session(session_id)
        total_duration = completion_result.get("duration","Not available")
        total_seconds = completion_result.get("total_seconds", 0)

        average_time = total_seconds / total_questions
        topic_details = get_topic_details(topic_id)

        topic_name = (
            topic_details["topic_name"]
            if topic_details else "Unknown Topic"
        )

        if "error" in completion_result:
            messagebox.showerror(
                "Error",
                str(completion_result["error"])
            )
            return

        clear_main()

        accuracy = (score / total_questions) * 100

        ctk.CTkLabel(
            main,
            text="Revision Completed!",
            font=("Arial", 28, "bold"),
            text_color=PURPLE
        ).pack(pady=30)

        ctk.CTkLabel(
            main,
            text=f"Session ID: {session_id}",
            font=("Arial", 15),
            text_color=MUTED
        ).pack(pady=10)
        ctk.CTkLabel(
        main,
        text=f"Revision Mode: {mode.replace('_', ' ').title()}",
        font=("Arial", 16),
        text_color=TEXT
        ).pack(pady=10)
        ctk.CTkLabel(
        main,
        text=f"Topic: {topic_name}",
        font=("Arial", 16),
        text_color=TEXT
        ).pack(pady=10)

        ctk.CTkLabel(
            main,
            text=f"Total Questions: {total_questions}",
            font=("Arial", 18),
            text_color=TEXT
        ).pack(pady=10)

        ctk.CTkLabel(
            main,
            text=f"Correct Answers: {score}",
            font=("Arial", 18, "bold"),
            text_color="#2EAD63"
        ).pack(pady=10)

        ctk.CTkLabel(
            main,
            text=f"Incorrect Answers: {total_questions - score}",
            font=("Arial", 18, "bold"),
            text_color="#E5484D"
        ).pack(pady=10)

        ctk.CTkLabel(
            main,
            text=f"Accuracy: {accuracy:.1f}%",
            font=("Arial", 22, "bold"),
            text_color=PURPLE
        ).pack(pady=20)
        # Total Time Taken
        ctk.CTkLabel(
            main,
            text=f"Total Time Taken: {total_duration}",
            font=("Arial", 18, "bold"),
            text_color=TEXT
        ).pack(pady=10)
        ctk.CTkLabel(
        main,
        text=f"Average Time per Question: {average_time:.1f} sec",
        font=("Arial", 18),
        text_color=TEXT
        ).pack(pady=10)

        # Back to Home
        ctk.CTkButton(
            main,
            text="Back to Home",
            fg_color=PURPLE,
            hover_color="#5745C5",
            height=45,
            width=180,
            command=lambda: show_page("Start Revision")
        ).pack(pady=25)

    display_question()

# ---------------- CONFIGURATION ----------------

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("RecallBox | Smart Revision System")
app.geometry("1200x750")
app.minsize(1000, 650)


# Colours
BG = "#F7F7FC"
SIDEBAR = "#FFFFFF"
PURPLE = "#6957D8"
LIGHT_PURPLE = "#EEEAFE"
TEXT = "#25243A"
MUTED = "#85849A"
WHITE = "#FFFFFF"

app.configure(fg_color=BG)


# ---------------- SIDEBAR ----------------

sidebar = ctk.CTkFrame(
    app,
    width=230,
    corner_radius=0,
    fg_color=SIDEBAR
)

sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)


logo = ctk.CTkLabel(
    sidebar,
    text="✦ RecallBox",
    font=("Arial", 25, "bold"),
    text_color=PURPLE
)

logo.pack(pady=(35, 45))


menu_items = [
    "Dashboard",
    "Start Revision",
    "My Subjects",
    "Revision Schedule",
    "Revision History",
    "Analytics"
]


# Store sidebar buttons
sidebar_buttons = {}


for item in menu_items:

    active = item == "Start Revision"

    button = ctk.CTkButton(
        sidebar,
        text="   " + item,
        height=45,
        corner_radius=10,
        anchor="w",
        fg_color=LIGHT_PURPLE if active else SIDEBAR,
        hover_color=LIGHT_PURPLE,
        text_color=PURPLE if active else MUTED,
        font=("Arial", 14, "bold" if active else "normal"),
        command=lambda name=item: show_page(name)
    )

    button.pack(fill="x", padx=18, pady=5)

    sidebar_buttons[item] = button


# ---------------- MAIN CONTENT ----------------

main = ctk.CTkFrame(
    app,
    fg_color=BG,
    corner_radius=0
)

main.pack(
    side="left",
    fill="both",
    expand=True,
    padx=30,
    pady=25
)


def clear_main():

    for widget in main.winfo_children():
        widget.destroy()


# ---------------- SIDEBAR NAVIGATION ----------------

def update_sidebar(selected_page):

    for item, button in sidebar_buttons.items():

        if item == selected_page:

            button.configure(
                fg_color=LIGHT_PURPLE,
                text_color=PURPLE,
                font=("Arial", 14, "bold")
            )

        else:

            button.configure(
                fg_color=SIDEBAR,
                text_color=MUTED,
                font=("Arial", 14, "normal")
            )

# ---------------- REVISION HISTORY ----------------
# ---------------- REVISION SESSION DETAILS ----------------

def show_session_details(session_id):

    clear_main()

    ctk.CTkLabel(
        main,
        text=f"Session #{session_id} Details",
        font=("Arial", 30, "bold"),
        text_color=TEXT
    ).pack(anchor="w", pady=(15, 5))

    ctk.CTkLabel(
        main,
        text="Review your answers and performance.",
        font=("Arial", 14),
        text_color=MUTED
    ).pack(anchor="w", pady=(0, 20))

    result = get_revision_session_details(session_id)

    if "error" in result:
        messagebox.showerror("Error", str(result["error"]))
        return

    questions = result.get("questions", [])
    total_questions = len(questions)

    correct_count = sum(
        1 for q in questions if q["is_correct"]
    )

    incorrect_count = total_questions - correct_count

    accuracy = (
        (correct_count / total_questions) * 100
        if total_questions > 0 else 0
    )
    total_time = sum(
    float(q["time_taken"] or 0) for q in questions
)

    average_time = (
        total_time / total_questions
        if total_questions > 0 else 0
    )

    if not questions:
        ctk.CTkLabel(
            main,
            text="No question attempts found for this session.",
            font=("Arial", 16),
            text_color=MUTED
        ).pack(pady=30)

    else:

    # Performance Summary
        summary_frame = ctk.CTkFrame(
            main,
            fg_color="transparent"
        )
        summary_frame.pack(fill="x", pady=10)

        stats = [
    ("Total Questions", total_questions),
    ("Correct Answers", correct_count),
    ("Incorrect Answers", incorrect_count),
    ("Accuracy", f"{accuracy:.1f}%"),
    ("Total Time", f"{total_time:.1f} sec"),
    ("Avg. Time / Question", f"{average_time:.1f} sec")
]

        for title, value in stats:

            card = ctk.CTkFrame(
                summary_frame,
                fg_color=WHITE,
                corner_radius=12
            )
            card.pack(
                side="left",
                expand=True,
                fill="both",
                padx=6,
                pady=5
            )

            ctk.CTkLabel(
                card,
                text=title,
                font=("Arial", 13),
                text_color=MUTED
            ).pack(pady=(15, 5))

            ctk.CTkLabel(
                card,
                text=str(value),
                font=("Arial", 24, "bold"),
                text_color=PURPLE
            ).pack(pady=(0, 15))

        # Question Details
        question_frame = ctk.CTkScrollableFrame(
            main,
            fg_color="transparent"
        )
        question_frame.pack(fill="both", expand=True, pady=10)
        question_frame.pack(fill="both", expand=True, pady=10)

        for index, question in enumerate(questions, start=1):

            card = ctk.CTkFrame(
                question_frame,
                fg_color=WHITE,
                corner_radius=15
            )
            card.pack(fill="x", pady=8, padx=5)

            status_text = (
                "Correct Answer"
                if question["is_correct"]
                else "Incorrect Answer"
            )

            status_color = (
                "#2E9D50"
                if question["is_correct"]
                else "#E04444"
            )

            ctk.CTkLabel(
                card,
                text=f"Question {index}",
                font=("Arial", 19, "bold"),
                text_color=PURPLE
            ).pack(anchor="w", padx=20, pady=(15, 5))

            ctk.CTkLabel(
                card,
                text=question["question_text"],
                font=("Arial", 15),
                text_color=TEXT,
                wraplength=900,
                justify="left"
            ).pack(anchor="w", padx=20, pady=8)

            answer_details = (
                f"Your Answer: {question['selected_answer']}\n"
                f"Correct Answer: {question['correct_answer']}\n"
                f"Time Taken: {question['time_taken']} seconds"
            )

            ctk.CTkLabel(
                card,
                text=answer_details,
                font=("Arial", 14),
                text_color=TEXT,
                justify="left"
            ).pack(anchor="w", padx=20, pady=5)

            ctk.CTkLabel(
                card,
                text=status_text,
                font=("Arial", 15, "bold"),
                text_color=status_color
            ).pack(anchor="w", padx=20, pady=5)

            ctk.CTkLabel(
                card,
                text=f"Explanation: {question['explanation'] or 'No explanation available.'}",
                font=("Arial", 14),
                text_color=MUTED,
                wraplength=900,
                justify="left"
            ).pack(anchor="w", padx=20, pady=(5, 15))

    ctk.CTkButton(
        main,
        text="Back to Revision History",
        fg_color=PURPLE,
        hover_color="#5544C7",
        command=show_revision_history
    ).pack(anchor="w", pady=15)
# ---------------- REVISION HISTORY ----------------

# ---------------- REVISION HISTORY ----------------

def show_revision_history():

    clear_main()

    ctk.CTkLabel(
        main,
        text="Revision History",
        font=("Arial", 30, "bold"),
        text_color=TEXT
    ).pack(anchor="w", pady=(15, 5))

    ctk.CTkLabel(
        main,
        text="Track your previous revision sessions.",
        font=("Arial", 14),
        text_color=MUTED
    ).pack(anchor="w", pady=(0, 20))

    result = get_revision_history(1)

    if "error" in result:
        messagebox.showerror("Error", str(result["error"]))
        return

    history = result.get("history", [])

    # Search and filter section
    filter_frame = ctk.CTkFrame(
        main,
        fg_color="transparent"
    )
    filter_frame.pack(fill="x", pady=10)

    search_entry = ctk.CTkEntry(
        filter_frame,
        placeholder_text="Search by topic name...",
        width=300,
        height=40
    )
    search_entry.pack(side="left", padx=(0, 15))

    mode_filter = ctk.CTkOptionMenu(
        filter_frame,
        values=[
            "All Modes",
            "Topic Practice",
            "Smart Revision",
            "Mixed Revision"
        ],
        width=180,
        height=40
    )
    mode_filter.pack(side="left")

    history_frame = ctk.CTkScrollableFrame(
        main,
        fg_color="transparent"
    )
    history_frame.pack(fill="both", expand=True)

    def display_history():

        # Clear previous cards
        for widget in history_frame.winfo_children():
            widget.destroy()

        search_text = search_entry.get().lower().strip()
        selected_mode = mode_filter.get()

        filtered_history = []

        for session in history:

            topic = session["topic_name"].lower()

            mode = session["revision_mode"]

            display_mode = mode.replace(
                "_", " "
            ).title()

            # Search by topic
            if search_text and search_text not in topic:
                continue

            # Filter by mode
            if selected_mode != "All Modes":

                if display_mode != selected_mode:
                    continue

            filtered_history.append(session)

        if not filtered_history:

            ctk.CTkLabel(
                history_frame,
                text="No matching revision sessions found.",
                font=("Arial", 17),
                text_color=MUTED
            ).pack(pady=40)

            return

        for session in filtered_history:

            card = ctk.CTkFrame(
                history_frame,
                fg_color=WHITE,
                corner_radius=15
            )
            card.pack(fill="x", pady=8, padx=5)

            date = str(session["date"]).replace(
                "T", " "
            )[:19]

            total_seconds = session["total_seconds"]

            minutes = total_seconds // 60
            seconds = total_seconds % 60

            details = (
                f"Date: {date}\n"
                f"Mode: {session['revision_mode'].replace('_', ' ').title()}\n"
                f"Topic: {session['topic_name']}\n"
                f"Status: {session['status']}\n"
                f"Total Questions: {session['total_questions']}\n"
                f"Correct: {session['correct_answers']}   "
                f"Incorrect: {session['incorrect_answers']}\n"
                f"Accuracy: {session['accuracy']}%\n"
                f"Time Taken: {minutes} min {seconds} sec"
            )

            ctk.CTkLabel(
                card,
                text=f"Session #{session['session_id']}",
                font=("Arial", 19, "bold"),
                text_color=PURPLE
            ).pack(anchor="w", padx=20, pady=(15, 5))

            ctk.CTkLabel(
                card,
                text=details,
                font=("Arial", 14),
                text_color=TEXT,
                justify="left"
            ).pack(anchor="w", padx=20, pady=(5, 15))
            ctk.CTkButton(
            card,
            text="View Details",
            fg_color=PURPLE,
            hover_color="#5544C7",
            command=lambda sid=session["session_id"]: show_session_details(sid)
            ).pack(anchor="e", padx=20, pady=(0, 15))

    # Update results automatically
    search_entry.bind(
        "<KeyRelease>",
        lambda event: display_history()
    )

    mode_filter.configure(
        command=lambda choice: display_history()
    )

    display_history()
# ---------------- PAGE NAVIGATION ----------------

def show_page(page_name):

    # Update selected sidebar button
    update_sidebar(page_name)

    clear_main()

    if page_name == "My Subjects":

        show_my_subjects(main)
    elif page_name == "Revision History":

        show_revision_history()

    elif page_name == "Start Revision":

        heading = ctk.CTkLabel(
            main,
            text=page_name,
            font=("Arial", 30, "bold"),
            text_color=TEXT
        )

        heading.pack(anchor="w", pady=(15, 5))

        subtitle = ctk.CTkLabel(
            main,
            text="Manage your learning and improve your memory.",
            font=("Arial", 14),
            text_color=MUTED
        )

        subtitle.pack(anchor="w", pady=(0, 25))

        show_revision_home()

    else:

        heading = ctk.CTkLabel(
            main,
            text=page_name,
            font=("Arial", 30, "bold"),
            text_color=TEXT
        )

        heading.pack(anchor="w", pady=(15, 5))

        placeholder = ctk.CTkLabel(
            main,
            text=f"{page_name} page coming soon!",
            font=("Arial", 18),
            text_color=MUTED
        )

        placeholder.pack(pady=100)


# ---------------- START REVISION HOME ----------------

def show_revision_home():

    # Welcome Card
    welcome = ctk.CTkFrame(
        main,
        fg_color=PURPLE,
        corner_radius=18,
        height=180
    )

    welcome.pack(fill="x", pady=(0, 25))
    welcome.pack_propagate(False)

    ctk.CTkLabel(
        welcome,
        text="Ready to strengthen your memory?",
        font=("Arial", 23, "bold"),
        text_color=WHITE
    ).pack(anchor="w", padx=25, pady=(20, 8))

    ctk.CTkLabel(
        welcome,
        text="Small revisions today lead to better learning tomorrow.",
        font=("Arial", 14),
        text_color="#E8E3FF"
    ).pack(anchor="w", padx=25)

    # Start Revision Button
    ctk.CTkButton(
        welcome,
        text="Start Revision",
        fg_color="#FFFFFF",
        text_color=PURPLE,
        hover_color="#E8E3FF",
        command=show_revision_mode_popup
    ).pack(anchor="w", padx=25, pady=12)

    # Statistics
    stats = ctk.CTkFrame(
        main,
        fg_color="transparent"
    )

    stats.pack(fill="x", pady=5)

    cards = [
        ("Questions", "120", "Total questions"),
        ("Accuracy", "85%", "Overall performance"),
        ("Topics Due", "08", "Need revision"),
    ]

    for title, value, description in cards:

        card = ctk.CTkFrame(
            stats,
            fg_color=WHITE,
            corner_radius=15,
            height=125
        )

        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=7
        )

        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 14),
            text_color=MUTED
        ).pack(anchor="w", padx=18, pady=(15, 3))

        ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 27, "bold"),
            text_color=PURPLE
        ).pack(anchor="w", padx=18)

        ctk.CTkLabel(
            card,
            text=description,
            font=("Arial", 11),
            text_color=MUTED
        ).pack(anchor="w", padx=18)


# ---------------- START APPLICATION ----------------

show_page("Start Revision")

app.mainloop()
