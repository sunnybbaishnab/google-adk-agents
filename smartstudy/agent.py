from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.tools.tool_context import ToolContext

MODEL = "gemini-3.1-flash-lite"

# ---------- Tool used by the Review Agent to stop the loop ----------
def exit_loop(tool_context: ToolContext) -> dict:
    """Call this ONLY when the study plan passes every review check."""
    tool_context.actions.escalate = True
    return {"status": "approved"}


# ---------- 1. Coordinator Agent ----------
coordinator_agent = Agent(
    name="coordinator_agent",
    model=MODEL,
    description="""Receives the student's request and extracts
    the key details.""",
    instruction=(
        """You are the Coordinator of a study-planning team. Read the student's
        message and extract exactly these fields:
        - Subject
        - Exam date / days remaining
        - Topics (list)
        - Current level
        - Available study time per day
        Output only this clean summary. Do NOT create a study plan."""
    ),
    output_key="student_request",
)


# ---------- 2. Planning Agent ----------
planning_agent = Agent(
    name="planning_agent",
    model=MODEL,
    description="Prepares requirements for the three analysis agents.",
    instruction=(
        """You are the Planning Agent. Student details:\n{student_request}\n\n
        Prepare a short requirements brief that the Topic, Practice and
        Schedule agents will use. State: total days, hours per day, total
        study hours available, the topic list and the student's level.
        Do NOT create the study plan itself."""
    ),
    output_key="planning_requirements",
)


# ---------- 3, 4, 5. Parallel agents ----------
topic_agent = Agent(
    name="topic_agent",
    model=MODEL,
    description="Analyzes each topic.",
    instruction=(
        """You are the Topic Agent. Requirements:\n{planning_requirements}\n\n
        For EACH topic give: Priority (High/Medium/Low), Difficulty, and 
        Recommended study focus. Present it as a short table or list."""
    ),
    output_key="topic_analysis",
)


practice_agent = Agent(
    name="practice_agent",
    model=MODEL,
    description="Decides practice amount and type per topic.",
    instruction=(
        """You are the Practice Agent. Requirements:\n{planning_requirements}\n\n
        For EACH topic decide how many practice problems to solve (for 
        example Arrays 5, Linked Lists 5, Trees 8, Graphs 8, Dynamic 
        Programming 10) and the practice type: Concept Questions, Coding 
        Problems, Mixed Practice, or Mock Test. Adjust to the student's level."""
    ),
    output_key="practice_plan",
)


schedule_agent = Agent(
    name="schedule_agent",
    model=MODEL,
    description="Builds a realistic day-wise schedule.",
    instruction=(
        """You are the Schedule Agent. Requirements:\n{planning_requirements}\n\n
        Create a day-wise schedule covering ALL days. Each day's hours must
        not exceed the daily study time. Include revision and practice days,
        not only new topics. Make the last day light revision plus a mock
        test, not new material."""
    ),
    output_key="schedule",
)


parallel_analysis = ParallelAgent(
    name="parallel_analysis",
    sub_agents=[topic_agent, practice_agent, schedule_agent],
    description="Runs the Topic, Practice and Schedule agents at the same time.",
)


# ---------- 6. Study Plan Writer ----------
writer_agent = Agent(
    name="writer_agent",
    model=MODEL,
    description="Combines the analyses into one complete study plan.",
    instruction=(
        """You are the Study Plan Writer. Combine these into ONE complete "
        day-wise study plan.\n\n
        Topic analysis:\n{topic_analysis}\n\n
        Practice plan:\n{practice_plan}\n\n
        Schedule:\n{schedule}\n\n
        Previous draft (may be empty):\n{draft_plan?}\n\n
        Reviewer feedback (may be empty):\n{review_feedback?}\n\n
        If there is reviewer feedback, fix every issue in it and produce the
        improved full plan. The plan must include: day-wise schedule, topics
        to study, practice to complete, revision, and mock test / final
        preparation. Output the full plan every time."""
    ),
    output_key="draft_plan",
)


# ---------- 7. Review Agent ----------
review_agent = Agent(
    name="review_agent",
    model=MODEL,
    description="Reviews the draft plan and approves or requests improvements.",
    instruction=(
        """You are the Review Agent. Draft plan:\n{draft_plan}\n\n
        Previous review feedback (empty on the first round):\n{review_feedback?}\n\n
        Check:\n
        1. Are all topics covered?\n
        2. Does it fit within the available study time each day?\n
        3. Is sufficient practice included?\n
        4. Is revision included?\n
        5. Is the final day suitable for exam preparation?\n\n
        If ALL checks pass: call the exit_loop tool, then output
        'APPROVED' followed by the complete final study plan.\n
        If something fails AND this is the first round: do NOT call
        exit_loop. Output 'NEEDS IMPROVEMENT' and a numbered list of exact fixes.\n
        If previous feedback exists (this is the final round): fix any small
        remaining issues yourself, call exit_loop, and output 'APPROVED'
        followed by the complete final study plan."""
    ),
    tools=[exit_loop],
    output_key="review_feedback",
)


# ---------- Loop: Writer -> Reviewer, max 2 iterations ----------
review_loop = LoopAgent(
    name="review_loop",
    sub_agents=[writer_agent, review_agent],
    max_iterations=2,
    description="Writer drafts, Reviewer checks, repeat at most twice.",
)


# ---------- Root: the Sequential pipeline ----------
root_agent = SequentialAgent(
    name="smartstudy_pipeline",
    sub_agents=[coordinator_agent, planning_agent, parallel_analysis, review_loop],
    description="Coordinator, then Planning, then parallel analysis, then writer/reviewer loop.",
)