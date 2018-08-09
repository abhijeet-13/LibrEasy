# -*- coding: utf-8 -*-
from sql_connector import sql_connector
import datetime as dt

search_books1 = '''
select 
    ISBN10, 
    Title, 
    author_list as 'List of Authors', 
    (
'''

search_books2 = '''
     round((char_length(match_text) - char_length(replace(match_text, '{0}', ''))) / (char_length('{0}'))) + 
'''

search_books3 = '''
     0
     ) as Hits
from (
    select 
        b.isbn as ISBN10, 
        b.title as Title, 
        group_concat(a.name) as author_list, 
        lower(concat(b.isbn, concat(b.title, group_concat(a.name)))) as match_text
    from (books as b natural join book_authors as ba) natural join authors as a
    where 
'''

search_books4 = '''
        (lower(b.isbn) like '%{0}%' or lower(b.title) like '%{0}%' or lower(a.name) like '%{0}%') and 
'''

search_books5 = '''
        (1 = 1)
    group by 
        b.isbn, b.title
    ) as mapping
order by
    hits DESC;
'''

def books_matching_terms(search_terms):
    # Synthesize the SQL query
    search_query = search_books1
    for search_term in search_terms:
        search_query += search_books2.format(search_term)
    search_query += search_books3
    for search_term in search_terms:
        search_query += search_books4.format(search_term)
    search_query += search_books5
    
    #Run the SQL query for the search terms
    with sql_connector() as sql:
        sql.run(search_query)        
        results = sql.getall()
        
    return results;


# Find using SQL if an ISBN is available for checkout
def is_isbn_available_for_checkout (isbn):
    with sql_connector() as sql:
        sql.run(
            '''
            select exists(
                select *
                from book_loans
                where isbn = '{0}' and date_in is null
            )
            '''.format(isbn)
        )
        print(
            '''
            select exists(
                select *
                from book_loans
                where isbn = '{0}' and date_in is null;
            )
            '''.format(isbn)
        )
        loan_results = sql.getall()
        
        available = 'Yes'
        if loan_results[0][0] == 1:
            available = 'No'
            
        return available
    
# Add new borrower info to the database
def add_new_borrower(ssn, name, addr, phone):
    with sql_connector() as sql:
        try:
            sql.run(
                '''
                insert into borrowers(ssn, name, address, phone)
                values('{}', '{}', '{}', '{}');
                '''.format(ssn, name, addr, phone), False
            )
            return 'Success'
        except Exception as e:
            return 'UserExists' if 'Duplicate' in str(e) else 'UnknownError'
        
def borrower_info(ssn):
    with sql_connector() as sql:
        sql.run('''
            select * 
            from borrowers 
            where ssn = '{}'
            '''.format(ssn)
        )
        results = sql.getall()
        return (['unknown'] * 5) if results == None else results[0]
        
        
def title_from_isbn (isbn):
    with sql_connector() as sql:
        sql.run(
            '''
            select title from books where isbn = '{0}';
            '''.format(isbn)
        )
        result = sql.getone()
    if result == None: return result
    return result[0]


def name_from_userid(user_id):
    with sql_connector() as sql:
        sql.run(
            '''
            select ssn, name from borrowers where card_id = {0};
            '''.format(int(user_id[2:]))
        )
        result = sql.getone()
    if result == None: return result
    return result[1]

def check_out_book_to_user(book_id, user_id):
    with sql_connector() as sql:
        sql.run(
            '''
            insert into book_loans(isbn, card_id, date_out, due_date) values('{0}', '{1}', '{2}', '{3}')
            '''.format(book_id, int(user_id[2:]), dt.date.today().strftime('%Y-%m-%d'), (dt.date.today() + dt.timedelta(days=14)).strftime('%Y-%m-%d'))
        )


def books_unreturned_by_user(user_id):
    with sql_connector() as sql:
        sql.run(
            '''
            select count(*) from book_loans where card_id = {0} and date_in is null;
            '''.format(int(user_id[2:]))
        )
        result = sql.getall()
    return 0 if result == None else result[0][0]


def check_in_book(loan_id):
    with sql_connector() as sql:
        sql.run(
            '''
            update book_loans
            set date_in = '{0}'
            where loan_id = {1}
            '''.format(dt.date.today().strftime('%Y-%m-%d'), loan_id)
        )
      
def find_records_for_checkin(search_text, id_num):
    with sql_connector() as sql:
        sql.run(
            '''
            select loan_id, isbn, card_id, name
            from book_loans natural join borrowers
            where (name like '%{0}%' or isbn like '%{0}%' or {1} = card_id) and date_in is null;
            '''.format(search_text, id_num)
        )
        return sql.getall()