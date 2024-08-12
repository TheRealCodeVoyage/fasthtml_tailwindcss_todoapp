from fasthtml.common import *
import uuid


globalcss = Style('.htmx-swapping{opacity: 0;transition: opacity 1s ease-out;}')
app = FastHTML(hdrs=[Script(code='', src='https://cdn.tailwindcss.com'),globalcss])
db = database('todos.db')
if 'Todo' not in db.t:
    db.create_table('Todo', {"id":uuid.UUID, "title":str, "done":bool}, pk='id')

# Task component
def new_task(task_id:uuid.UUID, task_text:str, task_completed=False):
    # Components
    checkbox = Checkbox(task_completed, cls='form-checkbox h-4 w-4 text-blue-600' ,hx_patch=f'/update-task/{task_id}')
    delete_button = Button('Delete', cls='text-red-600 hover:text-red-800', hx_delete=f'/delete-task/{task_id}',hx_target=f"#task-{task_id}", hx_confirm="Are you sure you want to delete this task?", hx_swap="outerHTML swap:1s")
    # Component Packaged
    return Div(checkbox, task_text, delete_button, cls='flex items-center gap-x-2 p-2 bg-gray-100 rounded-md shadow-sm hover:bg-gray-200', id=f"task-{task_id}")

# Main page
@app.get("/")
def main_page():
    # Components
    title = H2('To-Do List', cls='text-2xl font-bold text-center mb-4')
    inp = Input(id="new-task", name="task", placeholder="Enter a task", cls='w-full px-4 py-2 border rounded-md focus:outline-none focus:ring focus:ring-blue-500')
    add = Form(Group(inp, Button("Add Task", cls='px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600'), cls='flex items-center gap-x-2'), hx_post='/add-task', target_id='todo-list', hx_swap="afterbegin", cls='container')

    # Fetch tasks from DB
    todos = db.query("select * from Todo")
    todo_list = [new_task(todo['id'], todo['title'], todo['done']) for todo in todos] if todos else []
    all_todos = Div(*todo_list, id='todo-list')

    return Title('To-Do List'), Main(title, add, all_todos, cls='max-w-lg mx-auto mt-10 p-4 bg-white shadow-md rounded-md')

@app.post('/add-task')
def add_task(task:str):
    id = uuid.uuid1()
    db.table('Todo').insert({"id":id, "title":task, "done":False}, pk='id')
    return new_task(id, task)

@app.patch('/update-task/{task_id}')
def update_task(task_id:str):
    todo = db.table('Todo').get(task_id)
    todo['done'] = not todo['done']
    db.table('Todo').update(todo)
    return new_task(task_id, todo['title'], todo['done'])

@app.delete('/delete-task/{task_id}')
def delete_task(task_id:str):
    db.table('Todo').delete(task_id)
    return

serve()
