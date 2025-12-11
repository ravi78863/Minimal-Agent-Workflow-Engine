#  Agent Workflow Engine (FastAPI)
A clean, beginner‑friendly workflow engine built as part of the **AI Engineering Internship Backend Assignment**.  
This project focuses on clarity, structure, and demonstrating strong backend fundamentals — exactly what the assignment expects.

The engine behaves like a tiny, simplified version of **LangGraph**, allowing you to define steps (nodes), connect them, and execute workflows with a shared state.

No frontend.  
No machine learning.  
Just pure backend logic and clean system design. 

---

# 1 What This Project Is About

The internship assignment requires building a workflow engine that:

- Runs a sequence of steps (nodes)
- Maintains shared state between nodes
- Supports branching and looping
- Uses a tool registry (Python functions)  
- Exposes FastAPI endpoints to run the workflow

This project implements **Option B: Summarization + Refinement**, one of the sample workflows suggested.

---

# 2 What This Engine Can Do

### * Workflow Execution  
Nodes = Python functions that read & modify shared state.

Supports:
- Sequential execution  
- Conditional branching  
- Looping until a condition is satisfied  
- Step‑by‑step run logs  

### * Tool Registry  
All workflow actions are stored like this:

```python
tools = {
    "split_text": split_text,
    "generate_summaries": generate_summaries,
    "merge_summaries": merge_summaries,
    "refine_summary": refine_summary
}
```

Nodes reference tools by **name**, making the system extremely easy to extend.

### * FastAPI Endpoints  
| Endpoint | Purpose |
|---------|----------|
| `POST /graph/create` | Create a graph workflow |
| `POST /graph/run` | Run the workflow |
| `GET /graph/state/{run_id}` | Fetch workflow run progress |
| `GET /graph/example` | Get pre-built summarization workflow |

Everything is stored in memory → super lightweight and fast.

---

# 3 Implemented Workflow: Option B — Summarization + Refinement

The sample workflow follows these steps:

### **Step 1 — Split Text**
Break large text into chunks of `max_chunk_size`.

### **Step 2 — Generate Summaries**
Truncate each chunk to create “summaries”.

### **Step 3 — Merge Summaries**
Combine all summaries into a single long summary.

### **Step 4 — Refine Summary**
Trim summary to meet `summary_char_limit`.

### **Stopping Condition**
Workflow loops until:

```
summary_length <= summary_char_limit
```

This demonstrates:
- Proper looping  
- Clean state management  
- Node transitions  
- Modular tool design  

---

# 4 Project Structure

```
app/
│── main.py        # FastAPI app & API routing
│── engine.py      # Core workflow execution engine
│── models.py      # Pydantic request/response models
│── store.py       # In-memory storage (graphs + runs)
│── tools.py       # Tools + Example workflow definition
README.md
```

---

# 5 How to Run This Project (VERY IMPORTANT)

This section is written with **extra clarity** so that anyone — even someone new — can run the workflow successfully.

---

## * Step 1: Create your virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

⚠️ *Make sure your terminal is inside the project folder before running this.*

---

## * Step 2: Install required packages
```bash
pip install fastapi uvicorn
```

These are the only dependencies needed.

---

## * Step 3: Start FastAPI Server
```bash
uvicorn app.main:app --reload
```

If this runs without errors, you’ll see:
```
Uvicorn running on http://127.0.0.1:8000
```

---

## * Step 4: Open Swagger Docs  
Go to:

👉 http://127.0.0.1:8000/docs

This is where you will **interact with the workflow engine**.

---

# 6 Running the Workflow (What YOU actually did!)

Here is exactly how the workflow can be tested — the same steps you used while running it:

---

##  Step A — Fetch Example Workflow
```
GET /graph/example
```

This returns:
- Node definitions  
- Edges  
- Start node  
- A unique `graph_id`  

This `graph_id` is required for the next step.

---

##  Step B — Execute Workflow
Use:

```
POST /graph/run
```

Example Body:
```json
{
  "graph_id": "YOUR_GRAPH_ID",
  "initial_state": {
    "text": "Your long text...",
    "max_chunk_size": 100,
    "summary_char_limit": 120
  }
}
```

---

##  Step C — What You Receive as Output

You will get:

### * `final_state`  
Contains:
- chunks  
- summaries  
- merged summary  
- refined summary  
- final summary length  

### * `log`  
Every step executed with:
- node name  
- tool used  
- next node  
- state after each step  

### * `run_id`  
Useful for checking state again via:

```
GET /graph/state/{run_id}
```

This makes your workflow **fully observable**, which is exactly what the assignment expects.

---
🎉 Thank you for reviewing this project!  
If you want to add diagrams, explanations, or GIF-based demos to this README, just ask.  




