import pandas as pd
from sql_connector import sql_connector
import install_config as ic
import datetime as dt

#TODO: Delete in order of foreign key

if ic.install_data1 == True:
    # Read the book data into a pandas dataframe
    data_file_path = 'data/books.csv'
    book_data = pd.read_table(data_file_path, encoding = 'latin-1')
    
    # Drop the existing tables for a clean install
    with sql_connector() as sql:
        # in order of constraints
        sql.run('drop table fines')
        sql.run('drop table book_loans')
        sql.run('drop table authors')
        sql.run('drop table books_raw')
        sql.run('drop table books')
    
    
    # Create the authors table
    with sql_connector() as sql:
        # Create the authors table
        sql.run(
        '''
        create table authors(
            author_id int not null auto_increment, 
            name varchar(50) not null, 
            primary key (author_id),
            unique (name));
        ''')
        
        # Create the temporary books table
        sql.run(
        '''
        create table books_raw(
            isbn char(10) not null,
            title varchar(255) not null,
            author_name varchar(50) not null,
            constraint isbn_value check (char_length(isbn) = 10)
        );
        ''')
        
        insert_author_name = 'insert into authors(name) values("%s")'
        insert_book_info = 'insert into books_raw values("%s", "%s", "%s")'
        
        loop = True
        for i, book_info in book_data.iterrows():
            namelist = book_info.loc['Authro']
            isbn = book_info.loc['ISBN10']
            title = book_info.loc['Title']
            
            if(pd.isnull(title)):
                continue
            title = title.replace('"', '')
            
            if(pd.isnull(isbn) or len(isbn) != 10):
                continue
            
            if(pd.isnull(namelist)):
                continue
            
            names = namelist.split(',')
            for name in names:
                name = name.replace('"', '')
                
                try:
                    sql.run(insert_author_name % name, ignore_error=True)
                except Exception as e:
                    if 'Duplicate entry' in str(e):
                        pass
                    else:
                        print(name)
                        print(insert_author_name % name)
                        loop = False
                        break
                #if sql.run(insert_author_name % name) == -1:
                    #print('The name', name, 'probably already exists!')
                    #pass
                
                try:
                    sql.run(insert_book_info % (isbn, title, name), ignore_error=True)
                except:
                    print(isbn)
                    print(title)
                    print(name)
                    print (insert_book_info % (isbn, title, name))
                    loop = False
                    break
                #if sql.run(insert_book_info % (isbn, title, name)) == -1:
                    #print('Something must have been wrong')
                    #pass
            if loop == False:
                break
    
    print('Authors table created')
    
    with sql_connector() as sql:
        # Create table for books
        sql.run(
        '''
        create table books (
            isbn char(10),
            title varchar(255) not null,
            constraint isbn_value check (char_length(isbn) = 10),
            primary key (isbn)
        );
        ''')
                
        # Fill the books table
        sql.run(
        '''
        insert into books 
        select distinct isbn, title 
        from books_raw 
        order by title;
        ''')
        
        # Create the table for book authors
        sql.run(
        '''
        create table book_authors(
            author_id int not null,
            isbn char(10) not null,
            constraint isbn_value check (char_length(isbn) = 10),
            constraint book_author unique(isbn, author_id),
            foreign key (isbn) references books (isbn),
            foreign key (author_id) references authors (author_id)
        );
        ''')
        
        # Fill the authors table 
        sql.run(
        '''
        insert into book_authors 
        select distinct authors.author_id, books_raw.isbn 
        from books_raw 
        join authors on books_raw.author_name = authors.name;
        ''')
        
        # Drop the temporary table, as no more required
        sql.run('drop table books_raw')
        
        
    print('Books table created and updated')
    
    
if ic.install_data2 == True:
    # Read the book data into a pandas dataframe
    data_file_path = 'data/borrowers.csv'
    borrowers_data = pd.read_csv(data_file_path)
    
    
    # Drop the existing tables for a clean install
    with sql_connector() as sql:
        try:
            
            sql.run('drop table borrowers', False)
        except Exception as e:
            print("Error dropping borrowers: ", str(e))
        
        sql.run(
        '''
        create table borrowers(
            card_id int auto_increment,
            primary key (card_id),
            
            ssn char(11) not null,
            unique (ssn),
            constraint ssn_domain check (char_length(ssn) = 11),
            
            name varchar(255) not null,
            
            address varchar(255) not null,
            
            phone char(14),
            constraint phone_domain check (char_length(phone) = 14)
        );
        ''')
    print('borrowers table created')
    
    for i, borrower in borrowers_data.iterrows():
        numeric_id = int(borrower['ID0000id'][2:])
        ssn = borrower['ssn']   #TODO: Check if valid SSN
        name = borrower['first_name'] + ' ' + borrower['last_name']
        addr = borrower['address'] + ', ' + borrower['city'] + ', ' + borrower['state']
        phone = borrower['phone']   #TODO: Check if valid phone
        
        #print(numeric_id, name, ssn)
        #print(addr, phone)
        
        with sql_connector() as sql:
            try:
                sql.run('''
                        insert into borrowers() values({}, '{}', '{}', '{}', '{}')
                        '''.format(numeric_id, ssn, name, addr, phone), False
                )
            except Exception as e:
                break
    print('Borrowers table updated')

#Creating remaining tables
print('Creating remaining tables')
with sql_connector() as sql:
    
    
    sql.run(
    '''
    create table book_loans( 
        loan_id int auto_increment,  
        primary key(loan_id),   
    
        isbn char(10) not null,  
        foreign key (isbn) references books(isbn),  
    
        card_id int not null,  
        foreign key (card_id) references borrowers(card_id), 
    
        date_out date not null, 
        due_date date not null, 
    
        date_in date);
    ''')
    
    sql.run(
    '''
    create table fines(
        loan_id int,
        primary key (loan_id),
        foreign key (loan_id) references book_loans (loan_id),
    
        fine_amt double(5,2) not null,
    
        paid bit not null
    );
    '''
    )
    
print('Remaining tables created')
print('Install finished')
