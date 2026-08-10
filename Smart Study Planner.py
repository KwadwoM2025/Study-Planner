# Create a study planner
# Import datetime from datetime library. This is to help know the time and day a subject was planned to be studied.

from datetime import datetime as dt
import customtkinter as ctk
import json
import os
from tkinter import messagebox

DATA_FILE = os.path.join(os.path.dirname(__file__), "planner_data.json")


class Topic:
    def __init__(self, name, difficulty, study_time):
        self.name = name
        self.difficulty = difficulty
        self.study_time = study_time
        self.completed = False
        self.sessions = []

    def mark_completed_topic(self):
        self.completed = True

    def add_session(self, study_duration):
        self.sessions.append({"date": dt.now(), "duration": study_duration})

    def total_study_time(self):
        return sum(session["duration"] for session in self.sessions)

    def to_dict(self):
        return {
            "name": self.name,
            "difficulty": self.difficulty,
            "study_time": self.study_time,
            "completed": self.completed,
            "sessions": [
                {"date": session["date"].isoformat(), "duration": session["duration"]}
                for session in self.sessions
            ]
        }

    @classmethod
    def from_dict(cls, data):
        topic = cls(data["name"], data["difficulty"], data["study_time"])
        topic.completed = data.get("completed", False)
        topic.sessions = [
            {"date": dt.fromisoformat(session["date"]), "duration": session["duration"]}
            for session in data.get("sessions", [])
        ]
        return topic

    def __str__(self):
        status = "Completed" if self.completed else "Not Completed"
        return (
            f"{self.name} | "
            f"Difficulty: {self.difficulty} | "
            f"Study time: {self.study_time} mins | "
            f"Status: {status}"
        )


class Subject:
    def __init__(self, name):
        self.name = name
        self.topics = []

    def add_topic(self, topic):
        self.topics.append(topic)

    def to_dict(self):
        return {
            "name": self.name,
            "topics": [topic.to_dict() for topic in self.topics]
        }

    @classmethod
    def from_dict(cls, data):
        subject = cls(data["name"])
        subject.topics = [Topic.from_dict(topic_data) for topic_data in data.get("topics", [])]
        return subject

    def show_topics(self):
        if not self.topics:
            print("No topics has been added yet")
            return
        for n, topic in enumerate(self.topics, start=1):
            print(f"{n}. {topic}")


class StudyPlanner:
    def __init__(self, data_file=None):
        self.subjects = []
        self.data_file = data_file or DATA_FILE
        self.load()

    def add_subject(self, name):
        subject = Subject(name)
        self.subjects.append(subject)
        self.save()

    def find_subject(self, name):
        for subject in self.subjects:
            if subject.name.lower() == name.lower():
                return subject
        return None

    def total_topics(self):
        return sum(len(subject.topics) for subject in self.subjects)

    def completed_topics(self):
        return sum(
            1
            for subject in self.subjects
            for topic in subject.topics
            if topic.completed
        )

    def total_study_time(self):
        return sum(
            topic.total_study_time() for subject in self.subjects
            for topic in subject.topics
        )

    def to_dict(self):
        return {"subjects": [subject.to_dict() for subject in self.subjects]}

    def save(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as file:
                json.dump(self.to_dict(), file, indent=2)
        except OSError:
            pass

    def load(self):
        if not os.path.exists(self.data_file):
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.subjects = [Subject.from_dict(subject_data) for subject_data in data.get("subjects", [])]
        except (OSError, ValueError):
            self.subjects = []

    def delete_subject(self, subject):
        self.subjects.remove(subject)
        self.save()

    def clear_all_data(self):
        self.subjects = []
        if os.path.exists(self.data_file):
            try:
                os.remove(self.data_file)
            except OSError:
                pass
        self.save()

    def all_topics(self):
        return [topic for subject in self.subjects for topic in subject.topics]


class StudyPlannerApp(ctk.CTk):

    def __init__(self, planner):
        super().__init__()

        self.planner = planner
        self.open_windows = []

        self.title("Smart Study Planner")
        self.geometry("1120x720")
        self.minsize(850, 550)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.create_sidebar()
        self.create_main_area()
        self.show_dashboard()

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        title = ctk.CTkLabel(
            self.sidebar,
            text="Study Planner",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(30, 40))

        self.dashboard_button = ctk.CTkButton(
            self.sidebar,
            text="Dashboard",
            command=self.show_dashboard
        )
        self.dashboard_button.pack(padx=20, pady=8, fill="x")

        self.subject_button = ctk.CTkButton(
            self.sidebar,
            text="Subjects",
            command=self.show_subjects
        )
        self.subject_button.pack(padx=20, pady=8, fill="x")

        self.add_subject_button = ctk.CTkButton(
            self.sidebar,
            text="Add Subject",
            command=self.add_subject_window
        )
        self.add_subject_button.pack(padx=20, pady=8, fill="x")

        self.add_topic_button = ctk.CTkButton(
            self.sidebar,
            text="Add Topic",
            command=self.add_topic_window
        )
        self.add_topic_button.pack(padx=20, pady=8, fill="x")

        self.clear_data_button = ctk.CTkButton(
            self.sidebar,
            text="Clear Data",
            command=self.clear_data_confirmation
        )
        self.clear_data_button.pack(padx=20, pady=8, fill="x")

        self.study_button = ctk.CTkButton(
            self.sidebar,
            text="Study Session",
            command=self.study_session_window
        )
        self.study_button.pack(padx=20, pady=8, fill="x")

        self.progress_button = ctk.CTkButton(
            self.sidebar,
            text="Progress",
            command=self.show_progress
        )
        self.progress_button.pack(padx=20, pady=8, fill="x")

    def create_main_area(self):
        self.main_area = ctk.CTkFrame(self, corner_radius=0)
        self.main_area.pack(side="right", fill="both", expand=True)

    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_main_area()

        title = ctk.CTkLabel(
            self.main_area,
            text="Dashboard",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(anchor="w", padx=40, pady=(35, 10))

        subtitle = ctk.CTkLabel(
            self.main_area,
            text="Your study overview",
            font=ctk.CTkFont(size=16)
        )
        subtitle.pack(anchor="w", padx=40)

        cards_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        cards_frame.pack(fill="x", padx=30, pady=40)

        total_subjects = len(self.planner.subjects)
        total_topics = self.planner.total_topics()
        completed = self.planner.completed_topics()
        study_time = self.planner.total_study_time()

        self.create_card(cards_frame, "Subjects", total_subjects, 0)
        self.create_card(cards_frame, "Topics", total_topics, 1)
        self.create_card(cards_frame, "Completed", completed, 2)
        self.create_card(cards_frame, "Study Time", f"{study_time} min", 3)

    def create_card(self, parent, title, value, column):
        card = ctk.CTkFrame(parent, width=160, height=130)
        card.grid(row=0, column=column, padx=10, sticky="nsew")
        parent.grid_columnconfigure(column, weight=1)

        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=16))
        title_label.pack(pady=(25, 10))

        value_label = ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=18, weight="bold"))
        value_label.pack()

    def show_subjects(self):
        self.clear_main_area()

        title = ctk.CTkLabel(
            self.main_area,
            text="Your Subjects",
            font=ctk.CTkFont(size=30, weight="bold")
        )
        title.pack(anchor="w", padx=40, pady=(35, 40))

        if not self.planner.subjects:
            empty = ctk.CTkLabel(
                self.main_area,
                text="You haven't added any subjects yet",
                font=ctk.CTkFont(size=18)
            )
            empty.pack(anchor="w", padx=40, pady=20)
            return

        for subject in self.planner.subjects:
            subject_frame = ctk.CTkFrame(self.main_area)
            subject_frame.pack(fill="x", padx=40, pady=8)

            subject_label = ctk.CTkLabel(
                subject_frame,
                text=subject.name,
                font=ctk.CTkFont(size=18, weight="bold")
            )
            subject_label.pack(side="left", padx=20, pady=15)

            delete_button = ctk.CTkButton(
                subject_frame,
                text="Delete",
                width=90,
                fg_color="#d9534f",
                hover_color="#c9302c",
                command=lambda s=subject: self.delete_subject_confirmation(s)
            )
            delete_button.pack(side="right", padx=10)

            view_button = ctk.CTkButton(
                subject_frame,
                text="View Topics",
                width=100,
                command=lambda s=subject: self.view_subject(s)
            )
            view_button.pack(side="right", padx=10)

            topic_count = ctk.CTkLabel(
                subject_frame,
                text=f"{len(subject.topics)} topics"
            )
            topic_count.pack(side="right", padx=20)

    def view_subject(self, subject):
        self.clear_main_area()

        title = ctk.CTkLabel(
            self.main_area,
            text=subject.name,
            font=ctk.CTkFont(size=30, weight="bold")
        )
        title.pack(anchor="w", padx=40, pady=(35, 20))

        if not subject.topics:
            label = ctk.CTkLabel(self.main_area, text="No topics added yet")
            label.pack(pady=40)
            return

        for topic in subject.topics:
            frame = ctk.CTkFrame(self.main_area)
            frame.pack(fill="x", padx=40, pady=7)

            status = "Completed" if topic.completed else "Not Completed"
            text = (
                f"{status} - {topic.name}\n"
                f"Difficulty: {topic.difficulty}\n"
                f"Recommended: {topic.study_time} min\n"
                f"Studied: {topic.total_study_time()} min"
            )

            label = ctk.CTkLabel(frame, text=text, justify="left", anchor="w")
            label.pack(side="left", padx=20, pady=12)

            if not topic.completed:
                button = ctk.CTkButton(
                    frame,
                    text="Complete",
                    width=100,
                    command=lambda t=topic, s=subject: self.complete_topic(t, s)
                )
                button.pack(side="right", padx=15)

    def complete_topic(self, topic, subject):
        topic.mark_completed_topic()
        self.planner.save()
        messagebox.showinfo("Success", f"'{topic.name}' marked completed")
        self.view_subject(subject)

    def add_subject_window(self):
        window = ctk.CTkToplevel(self)
        self.open_windows.append(window)
        window.title("Add Subject")
        window.geometry("400x250")
        window.transient(self)
        window.lift()
        window.grab_set()

        def close_window():
            if window in self.open_windows:
                self.open_windows.remove(window)
            window.grab_release()
            window.destroy()

        window.protocol("WM_DELETE_WINDOW", close_window)

        label = ctk.CTkLabel(
            window,
            text="Add New Subject",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        label.pack(pady=30)

        entry = ctk.CTkEntry(window, placeholder_text="Subject name")
        entry.pack(padx=40, fill="x")

        def save():
            name = entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Subject name cannot be empty")
                return
            if self.planner.find_subject(name):
                messagebox.showerror("Error", "That subject already exists")
                return
            self.planner.add_subject(name)
            messagebox.showinfo("Success", f"{name} added successfully")
            entry.delete(0, "end")
            self.show_subjects()

        button = ctk.CTkButton(window, text="Add Subject", command=save)
        button.pack(pady=30)

    def add_topic_window(self):
        if not self.planner.subjects:
            messagebox.showwarning("No subjects", "Add a subject first")
            return

        window = ctk.CTkToplevel(self)
        self.open_windows.append(window)
        window.title("Add Topic")
        window.geometry("450x450")
        window.transient(self)
        window.lift()
        window.grab_set()

        def close_window():
            if window in self.open_windows:
                self.open_windows.remove(window)
            window.grab_release()
            window.destroy()

        window.protocol("WM_DELETE_WINDOW", close_window)

        title = ctk.CTkLabel(
            window,
            text="Add new Topic",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=25)

        subject_menu = ctk.CTkOptionMenu(
            window,
            values=[subject.name for subject in self.planner.subjects]
        )
        subject_menu.pack(padx=40, pady=10, fill="x")

        topic_entry = ctk.CTkEntry(window, placeholder_text="Topic name")
        topic_entry.pack(padx=40, pady=10, fill="x")

        difficulty_menu = ctk.CTkOptionMenu(
            window, values=["Easy", "Medium", "Difficult"])
        difficulty_menu.pack(padx=40, pady=10, fill="x")

        time_entry = ctk.CTkEntry(window, placeholder_text="Study time(minutes)")
        time_entry.pack(padx=40, pady=10, fill="x")

        def save_topic():
            topic_name = topic_entry.get().strip()
            if not topic_name:
                messagebox.showerror("Error", "Topic name cannot be empty")
                return
            try:
                study_time = int(time_entry.get())
                if study_time <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Enter a valid positive number for study time")
                return

            subject = self.planner.find_subject(subject_menu.get())
            if not subject:
                messagebox.showerror("Error", "Select a valid subject")
                return

            topic = Topic(topic_name, difficulty_menu.get(), study_time)
            subject.add_topic(topic)
            self.planner.save()
            messagebox.showinfo("Success", f"{topic_name} added!")
            topic_entry.delete(0, "end")
            time_entry.delete(0, "end")
            difficulty_menu.set("Easy")
            subject_menu.set(subject.name)
            self.show_subjects()

        button = ctk.CTkButton(window, text="Add Topic", command=save_topic)
        button.pack(pady=25)

    def study_session_window(self):
        if not self.planner.subjects:
            messagebox.showwarning("No subjects", "Add a subject and topic before logging a study session")
            return

        window = ctk.CTkToplevel(self)
        window.title("Study Session")
        window.geometry("450x420")

        title = ctk.CTkLabel(
            window,
            text="Add Study Session",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=25)

        subject_menu = ctk.CTkOptionMenu(
            window,
            values=[subject.name for subject in self.planner.subjects]
        )
        subject_menu.pack(padx=40, pady=10, fill="x")

        topic_menu = ctk.CTkOptionMenu(window, values=[])
        topic_menu.pack(padx=40, pady=10, fill="x")

        duration_entry = ctk.CTkEntry(window, placeholder_text="Study duration (minutes)")
        duration_entry.pack(padx=40, pady=10, fill="x")

        def update_topic_menu(option_menu, selected_subject_name):
            subject = self.planner.find_subject(selected_subject_name)
            if subject and subject.topics:
                option_menu.configure(values=[topic.name for topic in subject.topics])
                option_menu.set(subject.topics[0].name)
            else:
                option_menu.configure(values=[])
                option_menu.set("")

        def on_subject_change(choice):
            update_topic_menu(topic_menu, choice)

        subject_menu.configure(command=on_subject_change)
        if self.planner.subjects:
            subject_menu.set(self.planner.subjects[0].name)
            update_topic_menu(topic_menu, self.planner.subjects[0].name)

        subject_menu.configure(command=on_subject_change)
        if self.planner.subjects:
            update_topic_menu(topic_menu, self.planner.subjects[0].name)

        def save_session():
            subject_name = subject_menu.get()
            topic_name = topic_menu.get()
            try:
                duration = int(duration_entry.get())
                if duration <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Enter a valid positive number for duration")
                return

            subject = self.planner.find_subject(subject_name)
            if not subject:
                messagebox.showerror("Error", "Select a valid subject")
                return

            topic = next((topic for topic in subject.topics if topic.name == topic_name), None)
            if not topic:
                messagebox.showerror("Error", "Select a valid topic")
                return

            topic.add_session(duration)
            self.planner.save()
            messagebox.showinfo("Success", f"Logged {duration} minutes for '{topic.name}'")
            window.destroy()
            self.show_dashboard()

        button = ctk.CTkButton(window, text="Save Session", command=save_session)
        button.pack(pady=25)

    def delete_subject_confirmation(self, subject):
        if messagebox.askyesno("Delete Subject", f"Delete '{subject.name}' and all its topics?"):
            self.planner.delete_subject(subject)
            self.show_subjects()

    def clear_data_confirmation(self):
        if messagebox.askyesno("Clear Data", "Delete all subjects, topics, and study sessions?"):
            self.planner.clear_all_data()
            self.show_subjects()

    def show_progress(self):
        self.clear_main_area()

        title = ctk.CTkLabel(
            self.main_area,
            text="Progress",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(anchor="w", padx=40, pady=(35, 10))

        total_topics = self.planner.total_topics()
        completed_topics = self.planner.completed_topics()
        study_time = self.planner.total_study_time()
        percentage = int((completed_topics / total_topics) * 100) if total_topics else 0

        summary = ctk.CTkLabel(
            self.main_area,
            text=f"Completed {completed_topics} of {total_topics} topics ({percentage}%)\nTotal study time: {study_time} min",
            font=ctk.CTkFont(size=16),
            justify="left"
        )
        summary.pack(anchor="w", padx=40, pady=(0, 20))

        if not self.planner.subjects:
            empty = ctk.CTkLabel(self.main_area, text="No progress to show yet", font=ctk.CTkFont(size=18))
            empty.pack(anchor="w", padx=40, pady=20)
            return

        for subject in self.planner.subjects:
            completed = sum(1 for topic in subject.topics if topic.completed)
            total = len(subject.topics)
            if total == 0:
                continue
            progress = int((completed / total) * 100)

            subject_frame = ctk.CTkFrame(self.main_area)
            subject_frame.pack(fill="x", padx=40, pady=10)

            subject_label = ctk.CTkLabel(
                subject_frame,
                text=f"{subject.name}: {completed}/{total} topics completed ({progress}%)",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            subject_label.pack(anchor="w", padx=20, pady=(12, 8))

            progress_bar = ctk.CTkProgressBar(subject_frame)
            progress_bar.set(progress / 100)
            progress_bar.pack(fill="x", padx=20, pady=(0, 12))


if __name__ == "__main__":
    planner = StudyPlanner()
    app = StudyPlannerApp(planner)
    app.mainloop()

    



    
        



