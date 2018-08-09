from django.http import HttpResponse
from sql_connector import sql_connector
from . import html_strings as hs
from . import sql_query_strings as sqs


# HTML response to requests for <URL>/app
# HTML page for searching the books available in the system
def search_books(request):
    '''
    1. Homepage for the application
    2. Provides a search box for searching the book database based on text
       occurences, either in entirety or partially in:
           a. Book ISBN, 
           b. Book Title, and/or, 
           c. Any of the book authors
    3. Enlists results based on the number of occurences of the search terms
    4. Search terms are highlighted in the list of the results
    5. Radio buttons and checkout button provided for easy checkout
    6. Radio button is disabled for the books which are unavailable right now
    '''
    #Obtain the basic header HTML response
    response = basic_response()
    
    # Obtain search string from URL, if any, and populate search box with it
    search_string = '' if not 'query' in request.GET else request.GET['query']
    response.write(hs.search_box.format(search_string))
    if(search_string == ''):                                        #Nothing more to do, if no query
        return response
    
    # Parse unique search terms
    search_string = search_string.lower()
    search_terms = search_string.split(' ')                         # All the terms in the search string
    term_set = set([])                                              # Maintain a set of terms to avoid term repetition
    for i, search_term in enumerate(search_terms):
        # assume not to be contained in the terms set partially or wholly, initially
        exists = False
        # tag as already existing, if already exists in the set wholly or partially contained in a term
        for set_term in term_set:
            if search_term in set_term:
                exists = True
        # add to the term set if not already exists
        if not exists:
            term_set.add(search_term)
    # Obtain a list back again from the set
    search_terms = list(term_set)      

    # Obtain search results for the parsed terms and return if none found
    results = sqs.books_matching_terms(search_terms)
    response.write(
        '''
        <h3>Search results for <i>%s</i> (%i results found):</h3>
        ''' % (search_string, len(results)) 
    )
    if(len(results) == 0):
        return response
    
    # Write each individual result to a table appropriately and return
    response.write(hs.search_table_begin)
    for i, result in enumerate(results):
        available = sqs.is_isbn_available_for_checkout(result[0])   # Check if available for checkout
        response.write(
            hs.search_table_entry.format(
                result[0],                                          # Book ISBN
                i + 1,                                              # Serial number
                highlight_terms(result[0], search_terms),           # Highlighted ISBN
                highlight_terms(result[1], search_terms),           # Highlighted Title
                highlight_terms(result[2], search_terms),           # Highlighted Author list
                result[3],                                          # Number of hits
                available,                                          # Available: Yes or No
                '' if available == 'Yes' else 'disabled'            # Radio button disabled if unavailable
            )
        )
    response.write(hs.search_table_end)
    return response



# HTML response to requests for <URL>/app/newuser
# HTML page for adding a new borrower to the system
def add_user(request):
    '''
    1. Provide means to enter new user information as input
    2. GET parameters are read from the URL, if submitted by user
    3. Error texts are displayed if any of the following happens:
        a. All required information is not submitted
        b. Submitted information is invalid for any of the fields
        c. All info is valid, but user with SSN already exists
    4. If user is added successfully, a user card is generated for the new users
    '''
    # Write a basic header response and obtain params from URL, if any
    response = basic_response()
    response.write(hs.add_new_user) 
    params = request.GET
    if not params: return response                                  # Return response if no params
    
    # Parse the information from the GET parameters
    all_params_valid = True
    error_text = '<font color="red"><b>Please fix these errors before a new user can be added:</b><br>'
    error_id = 1
    try:
        ssn1 = params['ssn1']
        ssn2 = params['ssn2']
        ssn3 = params['ssn3']
        ssn = ssn1 + '-' + ssn2 + '-' + ssn3
        # Parse name
        nam1 = params['fname'] + ' '
        nam2 = params['mname'] + ' ' if 'mname' in params else ''
        nam3 = params['lname']
        name = nam1 + nam2 + nam3
        #Parse address and phone
        addr = params['addr'] + ', ' + params['city'] + ', ' + params['state']
        phone = params['phone']
    except:                                                         # if any of the required info is absent
        error_text += str(error_id) + '. Entire information is not submitted.<br>'
        error_id += 1
        all_params_valid = False                                    # Invalid input
    
    # if length of SSN parts are invalid
    if not (len(ssn1) == 3 and len(ssn2) == 2 and len(ssn3) == 4): 
        error_text += str(error_id) + '. Invalid length for an SSN.<br>'
        error_id += 1
        all_params_valid = False                                    # Invalid input
        
    # if SSN input is not numeric
    if not (ssn1.isdigit() and ssn2.isdigit() and ssn3.isdigit()):  
        error_text += str(error_id) + '. SSN can only be numeric.<br>'
        error_id += 1
        all_params_valid = False                                    # Invalid input
        
    # if no name (or numeric name is provided)
    if not (len(nam1) > 0 and len(nam3) > 0 and not any(c.isdigit() for c in name)):  
        error_text += str(error_id) + '. Surname cannot be empty or numeric.<br>'
        error_id += 1
        all_params_valid = False                                    # Invalid input

    error_text += '</font>'
    if not all_params_valid:                                        # Return response if params not valid
        response.write(error_text)
        return response
    
    # Try adding the information to the database, return if it fails
    result = sqs.add_new_borrower(ssn, name, addr, phone)
    if result != 'Success':
        if result == 'UserExists':
            response.write('<font color="red"><b>Cannot add user. User with SSN already exists!</b><br></font>')
        else:
            response.write('<font color="red"><b>Error! Please try again.</b><br></font>')
        return response                                             # Return response if could not add
    
    # If succeeded print a card for new user and return
    response.write('<font color="green"><b>Success adding new user! Please print the card below:</b><br></font>')
    info = sqs.borrower_info(ssn)
    string_id = 'ID' + str(10000000 + int(info[0]))[2:]             # Convert int to string ID
    response.write(hs.new_user_card.format(string_id, info[2], info[1], info[4], info[3]))
    return response
    


# HTML response to requests for <URL>/app/checkout
# HTML page for checking out a book against a user with some user id
def checkout(request):
    '''
    1. Read in the book id or user id from the input text boxes, and find info about them
    2. Fill up information regarding the book id or user id
    3. If checkout was clicked, attempt checkout only if valid. Clear contents of text boxes
    4. Whether successful or invalid, write helpful messages
    '''
    # Default response and params
    response = basic_response()
    book_id = book_info = user_id = user_info = ''
    attempt_checkout = True                                         # Checkout will be attempted only if valid
    
    # if any button was pressed with book ISBN provided
    if 'issue' in request.GET and request.GET['issue'] != '':       # SQL query for book id only if not ''
        book_id = request.GET['issue']
        book_name = sqs.title_from_isbn(book_id)

        if book_name == None:                                       # Checkout won't be attempted
            book_info = '<font color="red">Book with ISBN {} not found in database<br></font>'.format(book_id)
            attempt_checkout = False
        else:                                                       # Populate book info
            book_info = hs.checkout_book_info.format(book_id, book_name)
    
    # If any button was clicked with user ID provided
    if 'userid' in request.GET and request.GET['userid'] != '':     # SQL query for user id only if not ''
        user_id = request.GET['userid']
        # Check if correct format before checking for user
        if not (len(user_id) == 8 and user_id[:2] == 'ID' and user_id[2:].isdigit()):
            user_info = '<font color="red">Incorrect ID format<br></font>'
            attempt_checkout = False                                # Checkout won't be attempted
        else:
            user_name = sqs.name_from_userid(user_id)
            if user_name == None:
                user_info = '<font color="red">No user with the entered Card ID found<br></font>'
                attempt_checkout = False                            # Checkout won't be attempted
            else:
                user_info = hs.checkout_user_info.format(user_id, user_name)
    
    # if the button clicked was checkout and conditions are all valid for checkout
    if 'action' in request.GET and request.GET['action'] == 'Check Out':
        # if book unavailable for checkout
        if sqs.is_isbn_available_for_checkout(book_id) == 'No':
            response.write('<font color="red" align="center"><h3>Book already checked out!<br></h3></font>')
            attempt_checkout = False                                # Checkout won't be attempted
        if sqs.books_unreturned_by_user(user_id) >= 3:
            response.write('<font color="red" align="center"><h3>User exhausted quota of 3 books! <a href="/app/checkin/?search={0}">Check in</a>?<br></h3></font>'.format(user_id))
            attempt_checkout = False                                # Checkout won't be attempted
        if attempt_checkout:
            sqs.check_out_book_to_user(book_id, user_id)
            response.write('<font color="green" align="center"><h3>Book with ISBN {0} checked out for user {1}<br></h3></font>'.format(book_id, user_id))
        book_id = book_info = user_id = user_info = ''              # Clear contents when checkout attempted

    # Print out the checkout form     
    response.write(
        hs.checkout_form.format(
            book_id,
            book_info, 
            user_id,
            user_info
        )
    )
    return response




# HTML response to requests for <URL>/app/checkin
# HTML page for checking in books
def checkin(request):
    '''
    1. Provide a search box to search through the records for books to check in
    2. Present the results in a list format and provide a radio button (and a checkin button)
    3. Checkin the selected book when the selection is made, and display the result
    4. If no search text is present, show all the books available for checkin at the moment
    '''
    # Write basic header response and read in URL parameters
    response = basic_response()
    search_text = request.GET['search'] if 'search' in request.GET else ''
    response.write(hs.checkin_search_box.format(search_text))       # Search box to search through records
    
    # Perform checkin
    if 'performcheckin' in request.GET:                             # If checkin button was clicked
        if 'checkin' in request.GET:
            sqs.check_in_book(request.GET['checkin'])
            response.write('<font color="green">Book checked in</font>')
        else:
            response.write('<font color="red">No selection made. Try again</font>')
    
    # if search text contains number, it could be ID
    numeric_search_text = ''.join([c for c in search_text if c.isdigit()])
    id_num = int(numeric_search_text) if numeric_search_text else -1
    
    
    # Find checkin books with search criteria
    results = sqs.find_records_for_checkin(search_text, id_num)
    if (results == None or len(results) == 0) and search_text != '':
        response.write('<font color="red">No checked out books with such criteria found</font>')
        return response
    
    # Write a list of books to be checked in satisfying the search criteria
    response.write(hs.checkin_table_begin)
    for i, result in enumerate(results):
        response.write(
            hs.checkin_table_entry.format(result[0], result[1], 'ID' + str(10000000 + int(result[2]))[2:], result[3], 'checked' if i == 0 else '')
        )
    response.write(hs.checkin_table_end)
    return response



def fines(request):
    response = basic_response()
    
    # if a fine was paid for a loan_id
    if 'paid' in request.GET:
        loan_id = request.GET['paid']
        with sql_connector() as sql:
            sql.run(
            '''
            update fines
            set paid = true
            where loan_id = {}
            '''.format(loan_id)
            )
    
    
    # if date was submitted then, update the fines
    if 'date' in request.GET:
        date = request.GET['date']
        with sql_connector() as sql:
            # Add fines not already present, whose due dates are exceeded as of today: Case 1: Book not yet returned
            sql.run(
            '''
            insert into fines
            select loan_id, 0.25 * datediff('{0}', due_date), false
            from book_loans
            where ('{0}' > due_date) and (not loan_id = any (select loan_id from fines)) and (date_in is null)
            '''.format(date)
            )
            
            # Add fines not already present, whose due dates are exceeded as of today: Case2 : Book returned
            sql.run(
            '''
            insert into fines
            select loan_id, 0.25 * datediff(date_in, due_date), false
            from book_loans
            where ('{0}' > due_date) and (date_in > due_date) and (not loan_id = any (select loan_id from fines)) and (date_in is not null)
            '''.format(date)
            )
            
            # Fines updated only for those which not yet returned. second category fines updated only
            sql.run(
            '''
            update fines
            set fine_amt = 0.25 * datediff('{0}', (select due_date from book_loans where book_loans.loan_id = fines.loan_id))
            where paid = false and loan_id = any (select loan_id from book_loans where date_in is null)
            '''.format(date)
            )
    
    # This date occured box
    response.write(
    '''
    <h3><b>Make this date happen (as a daily script would run on increasing dates, choose only increasing dates in succession):</b></h3>
    <form method='get'>
        <input type='date' name='date'>
        <br>
        <input type='submit' value='This date occured'>
    </form>
    ''')
    
    # Pay fines for a user table
    response.write(
    '''
    <form>
    <input type='submit' value='Pay fines'>
    <table class='t1' width='100%' >
        <tr>
            <th>Select</th>
            <th>UserID</th>
            <th>User name</th>
            <th>Fine amount</th>
        </tr>
    ''')
    
    with sql_connector() as sql:
        sql.run(
        '''
        select book_loans.card_id, borrowers.name, sum(fine_amt)
        from (book_loans natural join borrowers) natural join fines
        where fines.paid = false
        group by book_loans.card_id, borrowers.name
        having sum(fine_amt) > 0
        ''')
        results = sql.getall()
    
    for i, result in enumerate(results):
        card_id = 'ID' + str(10000000 + int(result[0]))[2:]
        response.write(
        '''
        <tr>
            <td><input type='radio' name='paying_user' value='{0}'>
            <td>{0}</td>
            <td>{1}</td>
            <td>{2}</td>
        </tr>
        '''.format(card_id, result[1], result[2])
        )
    
    response.write(
    '''
    </table>
    </form>
    ''')
    
    
    if 'paying_user' in request.GET:
        paying_user_id = int(request.GET['paying_user'][2:])
        with sql_connector() as sql:
            sql.run(
            '''
            select book_loans.loan_id, book_loans.isbn, books.title, book_loans.date_out, book_loans.due_date, book_loans.date_in, fines.fine_amt 
            from (book_loans natural join books) inner join fines on book_loans.loan_id = fines.loan_id
            where fines.paid = false and book_loans.card_id = {0};
            '''.format(paying_user_id)
            )
            
            results = sql.getall()
        
        response.write(
        '''
        <form>
        <input type='submit' value='Fine paid'>
        <table width='100%' class='t1'>
            <tr>
                <th>Select</th>
                <th>Loan ID</th>
                <th>ISBN</th>
                <th>Book title</th>
                <th>Out date</th>
                <th>Due date</th>
                <th>Date returned</th>
                <th>Fine amount</th>
            </tr>
        ''')
        
        for i, result in enumerate(results):
            if result[5] == None:
                response.write(
                '''
                <tr>
                    <td><input type='radio' disabled></td>
                    <td>{0}</td>
                    <td>{1}</td>
                    <td>{2}</td>
                    <td>{3}</td>
                    <td>{4}</td>
                    <td><a href='/app/checkin/?search={1}'>Return</a></td>
                    <td>{5}</td>
                </tr>
                '''.format(result[0], result[1], result[2], result[3], result[4], 'Unfinalized')
                )
            else:
                response.write(
                '''
                <tr>
                    <td><input type='radio' name='paid' value='{0}'></td>
                    <td>{0}</td>
                    <td>{1}</td>
                    <td>{2}</td>
                    <td>{3}</td>
                    <td>{4}</td>
                    <td>{5}</td>
                    <td>{6}</td>
                </tr>
                '''.format(result[0], result[1], result[2], result[3], result[4], result[5], result[6])
                )
        response.write(
        '''
        </table>
        </form>
        ''')
        
    return response
    
    
    
    
    
    

def basic_response():
    '''
    Provide a basic boilerplate default header response for the web-pages
    in our app.
    '''
    response = HttpResponse()
    response.write(hs.basic_response)
    return response



def highlight_terms(html_text, search_terms):
    '''
    Modify the HTML text in 'html_text'
    by highlighting any of the terms occuring from the 'search_terms'
    '''
    
    # Comparison should be case-independent
    html_text_lower = html_text.lower()
    
    # Find the first matching term in the HTML text
    begin = 0
    lowest_idx = 1000000
    for search_term in search_terms:
        idx = html_text_lower.find(search_term, begin)
        if idx != -1:
            if idx < lowest_idx:
                lowest_idx = idx
                first_term = search_term
    
    
    # While matches keep getting found from left to right
    while lowest_idx != 1000000:
        # Replace the term in HTML script with its highlighted version
        html_text = html_text[:lowest_idx] + '<mark>' + html_text[lowest_idx: lowest_idx + len(first_term)]\
        + '</mark>' + html_text[lowest_idx + len(first_term):]

        # Find the next occuring match from left to right
        begin = lowest_idx + len(search_term) + len('<mark>') + len('</mark>')
        html_text_lower = html_text.lower()
        lowest_idx = 1000000
        for search_term in search_terms:
            idx = html_text_lower.find(search_term, begin)
            if idx != -1:
                if idx < lowest_idx:
                    lowest_idx = idx
                    first_term = search_term
                    
    return html_text


