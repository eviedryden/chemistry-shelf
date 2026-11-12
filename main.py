'''
The Chemistry Shelf: a Drafter website for tracking chemistry textbooks.

Add books, log pages as you read, climb the periodic table of ranks, and get
topic recommendations based on what you have already read.
'''
from dataclasses import dataclass
from typing import Any

from bakery import assert_equal
from drafter import *

# Site information goes right after the imports, before the dataclasses and routes,
# as the Drafter deployment guide says. Fill in your own details before submitting.
set_site_information(
    author="Evie Dryden",
    description="Track chemistry textbooks, earn element ranks, and get topic recommendations.",
    sources=["Official Drafter documentation: https://drafter-edu.github.io/drafter/"],
    planning=["CS1 Final Project 0_ Pick a Problem.pdf", "CS1 Final Project 1_ Design.pdf"],
    links=["https://github.com/eviedryden/chemistry-shelf/blob/main/CS1%20Final%20Project%200_%20Pick%20a%20Problem.pdf", 
           "https://github.com/eviedryden/chemistry-shelf/blob/main/CS1%20Final%20Project%201_%20Design.pdf"],
)
set_website_title("The Chemistry Shelf")
hide_debug_information()
set_website_framed(False)

# Global constants (allowed by the project requirements)
MAX_BOOK_PAGES = 3000
TOPICS = [
    "General Chemistry",
    "Organic Chemistry",
    "Inorganic Chemistry",
    "Physical Chemistry",
    "Analytical Chemistry",
    "Biochemistry",
]
# (rank name, highest total pages that still earns this rank)
RANK_THRESHOLDS = [
    ("Hydrogen", 100),
    ("Helium", 200),
    ("Carbon", 400),
    ("Oxygen", 2000),
]
TOP_RANK = "Gold"
RANK_JOKES = {
    "Hydrogen": "You're the lightest element. Easily excited, and a little flammable around textbooks.",
    "Helium": "Noble and inert... but you're finally floating up the table!",
    "Carbon": "You form bonds with everything. Your reading list is basically organic.",
    "Oxygen": "Breathtaking! Every other reader needs you to keep going.",
    "Gold": "Au-some! You are the most precious element on the shelf.",
}
# topic -> list of (next topic to read, reason)
RELATED_TOPICS = {
    "General Chemistry": [
        ("Organic Chemistry", "Now that you know atoms and bonds, see what carbon can build."),
        ("Inorganic Chemistry", "Explore the rest of the periodic table beyond carbon."),
    ],
    "Organic Chemistry": [
        ("Biochemistry", "Carbon chemistry is the language of life."),
        ("Analytical Chemistry", "Learn how chemists identify the molecules you've been drawing."),
    ],
    "Inorganic Chemistry": [
        ("Physical Chemistry", "Understand the energy behind those metals and crystals."),
        ("General Chemistry", "Refresh the fundamentals that every topic builds on."),
    ],
    "Physical Chemistry": [
        ("Analytical Chemistry", "Spectroscopy puts the physics you learned to work."),
        ("Inorganic Chemistry", "Apply thermodynamics to metals and materials."),
    ],
    "Analytical Chemistry": [
        ("Physical Chemistry", "Dig into the theory behind your instruments."),
        ("Organic Chemistry", "Practice on real molecules worth analyzing."),
    ],
    "Biochemistry": [
        ("Organic Chemistry", "Go back to the reaction mechanisms inside every enzyme."),
        ("Physical Chemistry", "Learn the energy rules behind metabolism."),
    ],
}


@dataclass
class Book:
    '''
    A single chemistry textbook on the shelf.

    Attributes:
        title (str): The book's title (unique on the shelf).
        author (str): The book's author.
        topic (str): One of the chemistry topics in TOPICS.
        total_pages (int): How many pages the book has.
        pages_read (int): How many pages the reader has finished.
        notes (str): The reader's own notes about the book.
    '''
    title: str
    author: str
    topic: str
    total_pages: int
    pages_read: int
    notes: str


@dataclass
class State:
    '''
    Everything that must persist across the whole website.

    Attributes:
        books (list[Book]): Every book on the shelf.
        total_pages_read (int): Pages read across all books.
        rank (str): The element rank earned by total_pages_read.
        favorite_topic (str): The reader's favorite topic ("" if not chosen).
        message (str): A status message shown on the next page.
    '''
    books: list[Book]
    total_pages_read: int
    rank: str
    favorite_topic: str
    message: str


# ------------------------------------------------------------ test helpers
# These small functions only build data for the unit tests. They let each test be a
# single assert_equal line without storing anything in global variables.

def sample_books() -> list[Book]:
    '''
    Make three books, two of them in the same topic, for testing.

    Returns:
        list[Book]: A new list of three Book instances.
    '''
    return [Book("A", "x", "Biochemistry", 100, 30, ""),
            Book("B", "y", "Organic Chemistry", 100, 10, ""),
            Book("C", "z", "Biochemistry", 100, 20, "")]


assert_equal(len(sample_books()), 3)
assert_equal(sample_books()[1].title, "B")


def fresh_state() -> State:
    '''
    Make an empty starting State for a test.

    Returns:
        State: A State with no books, Hydrogen rank, and no message.
    '''
    return State([], 0, "Hydrogen", "", "")


assert_equal(fresh_state(), State([], 0, "Hydrogen", "", ""))


def with_message(state: State, message: str) -> State:
    '''
    Set the message on a State and give the State back.

    Args:
        state (State): The State to change.
        message (str): The message to store.
    Returns:
        State: The same State, now holding the message.
    '''
    state.message = message
    return state


assert_equal(with_message(fresh_state(), "Hi"), State([], 0, "Hydrogen", "", "Hi"))


def refreshed(state: State) -> State:
    '''
    Run refresh_rank on a State and give the State back.

    Args:
        state (State): The State to refresh.
    Returns:
        State: The same State with total_pages_read and rank recomputed.
    '''
    refresh_rank(state)
    return state


def state_with_book(pages_read: int = 0, topic: str = "Biochemistry") -> State:
    '''
    Make a State holding one 300-page book called "Chem 101".

    Args:
        pages_read (int): Pages already read in the book.
        topic (str): The book's topic.
    Returns:
        State: The State, with total_pages_read and rank already updated.
    '''
    return refreshed(State([Book("Chem 101", "Smith", topic, 300, pages_read, "notes")], 0, "Hydrogen", "", ""))


# ---------------------------------------------------------------- helpers

def rank_for_pages(total_pages_read: int) -> str:
    '''
    Find the element rank earned by a number of pages read.

    Args:
        total_pages_read (int): Total pages read across all books.
    Returns:
        str: The rank name, such as "Hydrogen" or "Gold".
    '''
    for rank_name, highest_pages in RANK_THRESHOLDS:
        if total_pages_read <= highest_pages:
            return rank_name
    return TOP_RANK

assert_equal(rank_for_pages(0), "Hydrogen")
assert_equal(rank_for_pages(100), "Hydrogen")
assert_equal(rank_for_pages(101), "Helium")
assert_equal(rank_for_pages(200), "Helium")
assert_equal(rank_for_pages(201), "Carbon")
assert_equal(rank_for_pages(400), "Carbon")
assert_equal(rank_for_pages(401), "Oxygen")
assert_equal(rank_for_pages(2000), "Oxygen")
assert_equal(rank_for_pages(2001), "Gold")


def pages_to_next_rank(total_pages_read: int) -> int:
    '''
    Count how many more pages are needed to reach the next rank.

    Args:
        total_pages_read (int): Total pages read across all books.
    Returns:
        int: Pages still needed, or 0 if the reader is already at the top rank.
    '''
    # ADVANCED TECHNIQUE: tuple unpacking. Each item in RANK_THRESHOLDS is a pair
    # like ("Hydrogen", 100). "for _, highest_pages in ..." splits the pair into two
    # names in one step. "_" is a throwaway name for the rank name, which this
    # function does not need, so only highest_pages is used.
    for _, highest_pages in RANK_THRESHOLDS:
        if total_pages_read <= highest_pages:
            return highest_pages + 1 - total_pages_read
    return 0

assert_equal(pages_to_next_rank(0), 101)
assert_equal(pages_to_next_rank(50), 51)
assert_equal(pages_to_next_rank(100), 1)
assert_equal(pages_to_next_rank(101), 100)
assert_equal(pages_to_next_rank(2000), 1)
assert_equal(pages_to_next_rank(2001), 0)
assert_equal(pages_to_next_rank(5000), 0)


def sum_pages_read(books: list[Book]) -> int:
    '''
    Add up pages_read across every book on the shelf.

    Args:
        books (list[Book]): The books to add up.
    Returns:
        int: The total number of pages read.
    '''
    total = 0
    for book in books:
        total = total + book.pages_read
    return total

assert_equal(sum_pages_read([]), 0)
assert_equal(sum_pages_read(sample_books()[:1]), 30)
assert_equal(sum_pages_read(sample_books()), 60)


def pages_by_topic(books: list[Book]) -> dict[str, int]:
    '''
    Count how many pages have been read in each topic.

    Args:
        books (list[Book]): The books to count.
    Returns:
        dict[str, int]: A dictionary mapping each topic to its pages read.
    '''
    counts: dict[str, int] = {}
    for book in books:
        if book.topic in counts:
            counts[book.topic] = counts[book.topic] + book.pages_read
        else:
            counts[book.topic] = book.pages_read
    return counts

assert_equal(pages_by_topic([]), {})
assert_equal(pages_by_topic(sample_books()), {"Biochemistry": 50, "Organic Chemistry": 10})


def most_read_topic(books: list[Book]) -> str:
    '''
    Find the topic with the most pages read.

    Args:
        books (list[Book]): The books to look through.
    Returns:
        str: The most-read topic, or "" if no pages have been read.
    '''
    best_topic = ""
    best_pages = 0
    counts = pages_by_topic(books)
    for topic in counts:
        if counts[topic] > best_pages:
            best_topic = topic
            best_pages = counts[topic]
    return best_topic

assert_equal(most_read_topic([]), "")
assert_equal(most_read_topic([Book("D", "w", "Biochemistry", 100, 0, "")]), "")
assert_equal(most_read_topic(sample_books()), "Biochemistry")
assert_equal(most_read_topic(sample_books()[1:2]), "Organic Chemistry")


def find_book(books: list[Book], title: str) -> Book | None:
    '''
    Look up a book on the shelf by its title.

    Args:
        books (list[Book]): The books to search.
        title (str): The exact title to look for.
    Returns:
        Book | None: The matching book, or None if it is not on the shelf.
    '''
    # ADVANCED TECHNIQUE: "Book | None" is a union type. The "|" means "or", so this
    # function returns either a Book or None. It is needed because a title that is
    # not on the shelf has no Book to give back. Callers check "is None" before use.
    for book in books:
        if book.title == title:
            return book
    return None

assert_equal(find_book(sample_books(), "A"), sample_books()[0])
assert_equal(find_book(sample_books(), "B"), sample_books()[1])
assert_equal(find_book(sample_books(), "Z"), None)
assert_equal(find_book([], "A"), None)


def progress_bar(pages_read: int, total_pages: int) -> str:
    '''
    Draw a 20-character text progress bar such as "[#####---------------] 25%".

    Args:
        pages_read (int): Pages finished so far.
        total_pages (int): Pages in the whole book.
    Returns:
        str: The progress bar with a percentage.
    '''
    if total_pages <= 0:
        return "[--------------------] 0%"
    percent = pages_read * 100 // total_pages
    filled = percent * 20 // 100
    return "[" + "#" * filled + "-" * (20 - filled) + "] " + str(percent) + "%"

assert_equal(progress_bar(0, 100), "[--------------------] 0%")
assert_equal(progress_bar(25, 100), "[#####---------------] 25%")
assert_equal(progress_bar(1, 3), "[######--------------] 33%")
assert_equal(progress_bar(100, 100), "[####################] 100%")
assert_equal(progress_bar(0, 0), "[--------------------] 0%")


def parse_pages(text: str) -> int:
    '''
    Convert text typed by the user into a whole number of pages.

    Args:
        text (str): The text from a TextBox.
    Returns:
        int: The number, or -1 if the text is not a whole number.
    '''
    cleaned = text.strip()
    if cleaned.isdigit():
        return int(cleaned)
    return -1

assert_equal(parse_pages("42"), 42)
assert_equal(parse_pages(" 7 "), 7)
assert_equal(parse_pages("0"), 0)
assert_equal(parse_pages("abc"), -1)
assert_equal(parse_pages("-3"), -1)
assert_equal(parse_pages("4.5"), -1)
assert_equal(parse_pages(""), -1)


def refresh_rank(state: State) -> None:
    '''
    Recompute total_pages_read and rank from the books on the shelf.

    Args:
        state (State): The website state, changed in place.
    '''
    state.total_pages_read = sum_pages_read(state.books)
    state.rank = rank_for_pages(state.total_pages_read)

assert_equal(refreshed(fresh_state()), fresh_state())
assert_equal(refreshed(State([], 99, "Gold", "", "")), fresh_state())
assert_equal(refreshed(State([Book("Chem 101", "Smith", "Biochemistry", 300, 150, "notes")], 0, "Wrong", "", "")),
             State([Book("Chem 101", "Smith", "Biochemistry", 300, 150, "notes")], 150, "Helium", "", ""))
assert_equal(state_with_book(250).rank, "Carbon")
assert_equal(state_with_book(0), State([Book("Chem 101", "Smith", "Biochemistry", 300, 0, "notes")],
                                       0, "Hydrogen", "", ""))


def ignore_inputs(*inputs: str) -> None:
    '''
    Do nothing with form inputs that a navigation route must accept but does not need.

    Drafter sends every input on a page to the route a button points at, and
    complains if the route has no parameter with that name. Navigation routes
    take the inputs and pass them here to show they are ignored on purpose.

    Args:
        *inputs (str): Any number of form input values to ignore.
    '''
    # *inputs is "variable arguments", an advanced technique not covered in
    # class: it lets this function accept any number of values in one tuple.
    return None

# ignore_inputs does nothing and returns nothing, so there is no value to compare.
# It cannot fail, and the navigation-route tests below call it.


# ------------------------------------------------------------------ pages

@route
def index(state: State) -> Page:
    '''
    Starting page: shows rank, status message, and every book on the shelf.

    Args:
        state (State): The website state.
    Returns:
        Page: The shelf page.
    '''
    # ADVANCED TECHNIQUE: "Any" (imported from typing) means "any type is allowed".
    # Page content mixes different kinds of values (Header, Text, Button, TextBox),
    # so "list[Any]" tells Python this list can hold all of them while we build it.
    content: list[Any] = [
        Header("Welcome to the Chemistry Shelf", 1),
        Text(f"Current rank: {state.rank}"),
    ]
    if state.message != "":
        content.append(Text(state.message))
    if len(state.books) == 0:
        content.append(Text("Empty shelf. Add your first chemistry textbook!"))
    else:
        for book in state.books:
            content.append(HorizontalRule())
            content.append(Text(f"{book.title} by {book.author} ({book.topic})"))
            content.append(Text(progress_bar(book.pages_read, book.total_pages)))
            content.append(Button("Open", book_page, {"title": book.title}))
    content.append(HorizontalRule())
    content.append(Button("Add a Book", add_book_page))
    content.append(Button("Rank Ladder", rank_page))
    content.append(Button("Recommendations", recommend_page))
    return Page(state, content)


@route
def add_book_page(state: State) -> Page:
    '''
    Form page for adding a new book to the shelf.

    Args:
        state (State): The website state.
    Returns:
        Page: The add-book form.
    '''
    return Page(state, [
        Header("Add a Book!", 1),
        Text(state.message),
        "Title", TextBox("title", ""),
        "Author", TextBox("author", ""),
        "Total pages", TextBox("total_pages", ""),
        "Topic", SelectBox("topic", TOPICS, TOPICS[0]),
        "Notes", TextArea("notes", ""),
        Button("Save Book", save_book),
        Button("Cancel", cancel_add_book),
    ])


@route
def book_page(state: State, title: str) -> Page:
    '''
    Detail page for one book: info, notes, progress, and page logging.

    Args:
        state (State): The website state.
        title (str): The title of the book to show.
    Returns:
        Page: The book's detail page, or the shelf if the book is missing.
    '''
    book = find_book(state.books, title)
    if book is None:
        state.message = "That book is not on your shelf."
        return index(state)
    pages_left = book.total_pages - book.pages_read
    # ADVANCED TECHNIQUE: "Any" (imported from typing) means "any type is allowed".
    # Page content mixes different kinds of values (Header, Text, Button, TextBox),
    # so "list[Any]" tells Python this list can hold all of them while we build it.
    content: list[Any] = [
        Header(book.title, 1),
        Text(f"Author: {book.author}"),
        Text(f"Topic: {book.topic}"),
        Text(f"Notes: {book.notes}"),
        Text(progress_bar(book.pages_read, book.total_pages)),
        Text(f"Pages read: {book.pages_read} of {book.total_pages} ({pages_left} left)"),
    ]
    if pages_left == 0:
        content.append(Text("Finished! Reaction complete."))
    if state.message != "":
        content.append(Text(state.message))
    content.append(Text("How many pages did you just read?"))
    content.append(TextBox("pages_text", ""))
    content.append(Button("Log Pages", log_pages, {"title": book.title}))
    content.append(Button("Remove Book", remove_book, {"title": book.title}))
    content.append(Button("Back to Shelf", back_to_shelf))
    return Page(state, content)


@route
def rank_page(state: State) -> Page:
    '''
    Show the element rank, a chemistry joke, and pages to the next rank.

    Args:
        state (State): The website state.
    Returns:
        Page: The rank ladder page.
    '''
    to_next = pages_to_next_rank(state.total_pages_read)
    if to_next == 0:
        next_line = "You have reached the top of the periodic table!"
    else:
        next_line = f"Pages to the next rank: {to_next}"
    return Page(state, [
        Header("Rank Ladder", 1),
        Text(f"Your rank: {state.rank}"),
        Text(RANK_JOKES[state.rank]),
        Text(f"Total pages read: {state.total_pages_read}"),
        Text(next_line),
        Text("Hydrogen 0-100, Helium 101-200, Carbon 201-400, Oxygen 401-2000, Gold 2001+"),
        Button("Recommendations", recommend_page),
        Button("Back to Shelf", index),
    ])


@route
def recommend_page(state: State) -> Page:
    '''
    Recommend next topics based on the favorite topic and most-read topic.

    Args:
        state (State): The website state.
    Returns:
        Page: The recommendations page.
    '''
    most_read = most_read_topic(state.books)
    base_topic = state.favorite_topic
    if base_topic == "":
        base_topic = most_read
    # ADVANCED TECHNIQUE: "Any" (imported from typing) means "any type is allowed".
    # Page content mixes different kinds of values (Header, Text, Button, TextBox),
    # so "list[Any]" tells Python this list can hold all of them while we build it.
    content: list[Any] = [Header("Recommendations", 1)]
    if state.favorite_topic == "":
        content.append(Text("Favorite topic: not chosen yet"))
    else:
        content.append(Text(f"Favorite topic: {state.favorite_topic}"))
    if most_read == "":
        content.append(Text("Most read topic: nothing read yet"))
    else:
        content.append(Text(f"Most read topic: {most_read}"))
    content.append(Text("Suggested next:"))
    if base_topic == "":
        content.append(Text("Log some pages or pick a favorite topic to get suggestions."))
    else:
        for next_topic, reason in RELATED_TOPICS[base_topic]:
            content.append(Text(f"{next_topic}: {reason}"))
    content.append(Text("Update your favorite topic:"))
    content.append(SelectBox("topic", TOPICS, TOPICS[0]))
    content.append(Button("Set Favorite", set_favorite_topic))
    content.append(Button("Add a Book", open_add_book))
    content.append(Button("Back to Shelf", back_to_shelf))
    return Page(state, content)


# ----------------------------------------------------------------- actions

# Drafter sends EVERY input on a page to whichever route a button points at, and
# warns if that route has no parameter with the input's name. The navigation
# routes below accept (and ignore) the inputs on the pages they are used from.

@route
def back_to_shelf(state: State, pages_text: str = "", topic: str = "") -> Page:
    '''
    Go back to the shelf from a page with inputs (book page or recommendations).

    Args:
        state (State): The website state.
        pages_text (str): Ignored input from the book page.
        topic (str): Ignored input from the recommendations page.
    Returns:
        Page: The shelf page.
    '''
    ignore_inputs(pages_text, topic)
    state.message = ""
    return index(state)


@route
def cancel_add_book(state: State, title: str = "", author: str = "", total_pages: str = "",
                    topic: str = "", notes: str = "") -> Page:
    '''
    Cancel the add-book form and go back to the shelf without saving.

    Args:
        state (State): The website state.
        title (str): Ignored input from the form.
        author (str): Ignored input from the form.
        total_pages (str): Ignored input from the form.
        topic (str): Ignored input from the form.
        notes (str): Ignored input from the form.
    Returns:
        Page: The shelf page.
    '''
    ignore_inputs(title, author, total_pages, topic, notes)
    state.message = ""
    return index(state)


@route
def open_add_book(state: State, topic: str = "") -> Page:
    '''
    Open the add-book form from the recommendations page.

    Args:
        state (State): The website state.
        topic (str): Ignored input from the recommendations page.
    Returns:
        Page: The add-book form.
    '''
    ignore_inputs(topic)
    state.message = ""
    return add_book_page(state)


@route
def save_book(state: State, title: str, author: str, topic: str, total_pages: str, notes: str) -> Page:
    '''
    Validate the form and add a new Book to the shelf.

    Args:
        state (State): The website state.
        title (str): The new book's title.
        author (str): The new book's author.
        topic (str): The new book's topic.
        total_pages (str): The page count as typed by the user.
        notes (str): The user's notes about the book.
    Returns:
        Page: The shelf if the book was added, otherwise the form again.
    '''
    pages = parse_pages(total_pages)
    if title.strip() == "" or author.strip() == "":
        state.message = "Please enter both a title and an author."
        return add_book_page(state)
    if find_book(state.books, title.strip()) is not None:
        state.message = "That title is already on your shelf."
        return add_book_page(state)
    if pages <= 0 or pages > MAX_BOOK_PAGES:
        state.message = f"Total pages must be a whole number from 1 to {MAX_BOOK_PAGES}."
        return add_book_page(state)
    state.books.append(Book(title.strip(), author.strip(), topic, pages, 0, notes))
    refresh_rank(state)
    state.message = "Book added. Action complete!"
    return index(state)


@route
def log_pages(state: State, title: str, pages_text: str) -> Page:
    '''
    Add pages read to a book, then update total pages and rank.

    Args:
        state (State): The website state.
        title (str): The title of the book being read.
        pages_text (str): The number of new pages as typed by the user.
    Returns:
        Page: The book's detail page, or the shelf if the book is missing.
    '''
    book = find_book(state.books, title)
    if book is None:
        state.message = "That book is not on your shelf."
        return index(state)
    pages = parse_pages(pages_text)
    if pages <= 0:
        state.message = "Enter a whole number of pages greater than 0."
        return book_page(state, title)
    if book.pages_read + pages > book.total_pages:
        state.message = f"That is more than the {book.total_pages} pages in this book."
        return book_page(state, title)
    book.pages_read = book.pages_read + pages
    refresh_rank(state)
    if book.pages_read == book.total_pages:
        state.message = "Finished! You completed this book."
    else:
        state.message = f"Logged {pages} pages. Action complete!"
    return book_page(state, title)


@route
def remove_book(state: State, title: str, pages_text: str = "") -> Page:
    '''
    Remove a book from the shelf and recompute rank.

    Args:
        state (State): The website state.
        title (str): The title of the book to remove.
        pages_text (str): Ignored input from the book page.
    Returns:
        Page: The shelf page.
    '''
    ignore_inputs(pages_text)
    book = find_book(state.books, title)
    if book is not None:
        state.books.remove(book)
        refresh_rank(state)
        state.message = f"Removed {title}."
    return index(state)


@route
def set_favorite_topic(state: State, topic: str) -> Page:
    '''
    Save the user's favorite topic.

    Args:
        state (State): The website state.
        topic (str): The topic chosen in the SelectBox.
    Returns:
        Page: The recommendations page.
    '''
    state.favorite_topic = topic
    state.message = f"Favorite topic set to {topic}."
    return recommend_page(state)


# ------------------------------------------------------------- route tests
# Routes return a Page, so each test checks the Page's state and how many components
# it holds (page.content). Counting components does not depend on the exact wording
# of the text on the page. These tests live below all the routes because the routes
# call each other, so every route has to exist before any of them can run.

# index
assert_equal(index(fresh_state()).state, fresh_state())
assert_equal(len(index(fresh_state()).content), 7)
assert_equal(len(index(with_message(fresh_state(), "Hello")).content), 8)
assert_equal(len(index(state_with_book(10)).content), 10)

# add_book_page
assert_equal(add_book_page(fresh_state()).state, fresh_state())
assert_equal(len(add_book_page(fresh_state()).content), 14)

# book_page
assert_equal(book_page(state_with_book(10), "Chem 101").state, state_with_book(10))
assert_equal(len(book_page(state_with_book(10), "Chem 101").content), 11)
assert_equal(len(book_page(state_with_book(300), "Chem 101").content), 12)
assert_equal(book_page(state_with_book(10), "Missing").state,
             with_message(state_with_book(10), "That book is not on your shelf."))
assert_equal(len(book_page(state_with_book(10), "Missing").content), 11)

# rank_page
assert_equal(rank_page(fresh_state()).state, fresh_state())
assert_equal(len(rank_page(fresh_state()).content), 8)
assert_equal(rank_page(State([], 5000, "Gold", "", "")).state, State([], 5000, "Gold", "", ""))
assert_equal(len(rank_page(State([], 5000, "Gold", "", "")).content), 8)

# recommend_page
assert_equal(recommend_page(fresh_state()).state, fresh_state())
assert_equal(len(recommend_page(fresh_state()).content), 10)
assert_equal(len(recommend_page(State([], 0, "Hydrogen", "Biochemistry", "")).content), 11)
assert_equal(len(recommend_page(state_with_book(10)).content), 11)

# back_to_shelf
assert_equal(back_to_shelf(with_message(state_with_book(10), "old message"), "12", "Biochemistry").state,
             state_with_book(10))
assert_equal(len(back_to_shelf(fresh_state(), "", "").content), 7)

# cancel_add_book
assert_equal(cancel_add_book(with_message(fresh_state(), "old message"), "Title", "Author", "5",
                             "Biochemistry", "notes").state, fresh_state())
assert_equal(len(cancel_add_book(fresh_state()).content), 7)

# open_add_book
assert_equal(open_add_book(with_message(fresh_state(), "old message"), "Biochemistry").state, fresh_state())
assert_equal(len(open_add_book(fresh_state()).content), 14)

# save_book
assert_equal(save_book(fresh_state(), " Chem 101 ", " Smith ", "General Chemistry", "300", "notes").state,
             State([Book("Chem 101", "Smith", "General Chemistry", 300, 0, "notes")],
                   0, "Hydrogen", "", "Book added. Action complete!"))
assert_equal(save_book(fresh_state(), "", "Smith", "General Chemistry", "300", "").state,
             with_message(fresh_state(), "Please enter both a title and an author."))
assert_equal(save_book(fresh_state(), "No Author", "   ", "General Chemistry", "300", "").state,
             with_message(fresh_state(), "Please enter both a title and an author."))
assert_equal(save_book(state_with_book(0), "Chem 101", "Smith", "General Chemistry", "100", "").state,
             with_message(state_with_book(0), "That title is already on your shelf."))
assert_equal(save_book(fresh_state(), "Bad", "Smith", "General Chemistry", "abc", "").state,
             with_message(fresh_state(), "Total pages must be a whole number from 1 to 3000."))
assert_equal(save_book(fresh_state(), "Zero", "Smith", "General Chemistry", "0", "").state,
             with_message(fresh_state(), "Total pages must be a whole number from 1 to 3000."))
assert_equal(save_book(fresh_state(), "Huge", "Smith", "General Chemistry", "3001", "").state,
             with_message(fresh_state(), "Total pages must be a whole number from 1 to 3000."))
assert_equal(len(save_book(fresh_state(), "Max", "Smith", "General Chemistry", "3000", "").state.books), 1)

# log_pages
assert_equal(log_pages(state_with_book(0), "Chem 101", "150").state,
             with_message(state_with_book(150), "Logged 150 pages. Action complete!"))
assert_equal(log_pages(state_with_book(150), "Chem 101", "abc").state,
             with_message(state_with_book(150), "Enter a whole number of pages greater than 0."))
assert_equal(log_pages(state_with_book(150), "Chem 101", "0").state,
             with_message(state_with_book(150), "Enter a whole number of pages greater than 0."))
assert_equal(log_pages(state_with_book(150), "Chem 101", "999").state,
             with_message(state_with_book(150), "That is more than the 300 pages in this book."))
assert_equal(log_pages(state_with_book(150), "Chem 101", "150").state,
             with_message(state_with_book(300), "Finished! You completed this book."))
assert_equal(log_pages(state_with_book(150), "Missing", "5").state,
             with_message(state_with_book(150), "That book is not on your shelf."))
assert_equal(len(log_pages(state_with_book(0), "Chem 101", "10").content), 12)

# remove_book
assert_equal(remove_book(state_with_book(250), "Missing", "").state, state_with_book(250))
assert_equal(remove_book(state_with_book(250), "Chem 101", "12").state,
             State([], 0, "Hydrogen", "", "Removed Chem 101."))

# set_favorite_topic
assert_equal(set_favorite_topic(fresh_state(), "Biochemistry").state,
             State([], 0, "Hydrogen", "Biochemistry", "Favorite topic set to Biochemistry."))
assert_equal(set_favorite_topic(fresh_state(), "Organic Chemistry").state.favorite_topic, "Organic Chemistry")
assert_equal(len(set_favorite_topic(fresh_state(), "Biochemistry").content), 11)


if __name__ == "__main__":
    start_server(State([], 0, "Hydrogen", "", ""))

