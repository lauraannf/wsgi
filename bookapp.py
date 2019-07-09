import re
import traceback

from bookdb import BookDB

DB = BookDB()


def book(book_id):
    page = """
<h1>{title}</h1>
<table>
    <tr><th>Author</th><td>{author}</td></tr>
    <tr><th>Publisher</th><td>{publisher}</td></tr>
    <tr><th>ISBN</th><td>{isbn}</td></tr>
</table>
<a href="/">Back to the list</a>
"""
    book = DB.title_info(book_id)
    if book is None:
        raise NameError
    return page.format(**book)

def books():
    all_books = DB.titles()  # grab all the books
    body = ['<h1>My Bookshelf</h1>', '<ul>']  # start body as header
    item_template = '<li><a href="/book/{id}">{title}</a></li>' # unordered list
    for book in all_books:
        body.append(item_template.format(**book)) # add each item to body, ** unpacks the id and title for each dictionary(book)
    body.append('</ul>')

    return '\n'.join(body)


def resolve_path(path):
    funcs = {
            '': books,
            'book': book,
            }
    
    path = path.strip('/').split('/')  # break up path
    
    func_name = path[0]  #first element is function name
    args = path[1:]  # remainder are arguments to the function
    
    try:
        func = funcs[func_name]
    except KeyError:
        raise NameError

    return func, args


def application(environ, start_response):
    headers = [('Content-type', 'text/html')]
    try:
        path = environ.get('PATH_INFO', None) # retrieve the path
        if path is None:
            raise NameError
        func, args = resolve_path(path)  # use resolve path to get the function and args
        body = func(*args) # try to call the function to get body
        status = "200 OK" # if everything is ok
    except NameError:
        status = "404 Not Found"
        body = "<h1> Not Found </h1>"
    except Exception:
        status = "500 Internal Error"
        body = "<h1> Internal Server Error </h1>"
        print(traceback.format_exc()) #print traceback in terminal for debugging
    finally:
        headers.append(('Content-length', str(len(body)))) # return the generated body to server
        start_response(status, headers)
    return [body.encode('utf8')]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, application)
    srv.serve_forever()
