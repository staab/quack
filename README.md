# Quack

It's a DSL for full-stack web development that compiles to python, html, and tiny bits of javascript.

Features/Goals:

- Extensibility (use js, html, md, py functions to escape to whatever native nonsense you want)
- Beginner-friendly syntax. Inspired by python, but with less syntax to trip beginners up.
- Easy to learn, powerful enough for experienced developers (on small projects).
- Dynamic rather than lexical scoping for less boilerplate. Use it wisely!

Right now, it's very much in the exploratory phase. See the `example` directory for an example real-world app modeled after my [disc golf PWA](https://duthie-park.anhyzer.io/). See below for a teeny tiny example.

The big idea here is to use dynamic scope for all state. I'm not sure if I'll introduce syntax to explicitly denote where the state is supposed to come from, but the idea is that if the framework does its job by handling form state, loading state, error state, etc, there will be far less bookkeeping to do, and state variables can be focused on a well-defined domain, for which (hopefully) there is a well-defined vocabulary.

# Tiny example

```
App
  # Declare a variable and load the whole todos table
  data todos
    all todos

  # If you want, just write html
  html "components/header.html"

  # Tell quack where to put the pages
  slot page

# A model determines a database model. This is automatically exposed for simple
# CRUD operations, but for more sophisticated access patterns use views and actions.
Model todo todos
  title = text
  completed? = boolean

# Declare a route
Page /
  # Iterate over data declared in some parent scope
  each todos as todo
    # The show function renders a component. There are builtins that can be themed,
    # and the Component block lets you declare custom ones.
    show row
      show cell
        show checkbox
          # When value changes, todo is mutated, affecting todos data
          value = todo.completed?
          # Action is debounced, occurs after todo is modified.
          # The save built-in action persists the new value of the todo to the database.
          action = save todo
      show cell
        show input
          value = todo.title
          action = save todo

  show button
    text = "Add Todo"
    action = add_todo

# Custom actions can be defined. While this is executing, a loading state will be shown
# on the button that triggered it.
Action add_todo
  # Construct a new associative data structure local to the action
  data todo
    title = "New Todo"
    completed? = false

  # Append is a built-in function adding the todo to the todos data declared in app
  append todos todo

  # Save the todo to the database. Actions are transactional, so if this fails, the todos
  # array won't be mutated and an error will be shown (by default maybe a toast?)
  save todo
```
